import json
import socket
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


URL_GEOCODIFICACION = (
    "https://geocoding-api.open-meteo.com/v1/search"
)
URL_PRONOSTICO = "https://api.open-meteo.com/v1/forecast"
URL_FUENTE = "https://open-meteo.com/"
AGENTE_USUARIO = (
    "EduIA/1.2 (https://github.com/IsaacAnd222/EduIA)"
)
TIEMPO_ESPERA = 10


class ErrorConsultaClima(Exception):
    """Error controlado al consultar Open-Meteo."""


DESCRIPCIONES_CODIGO = {
    0: "Cielo despejado",
    1: "Mayormente despejado",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Niebla",
    48: "Niebla con escarcha",
    51: "Llovizna ligera",
    53: "Llovizna moderada",
    55: "Llovizna intensa",
    56: "Llovizna helada ligera",
    57: "Llovizna helada intensa",
    61: "Lluvia ligera",
    63: "Lluvia moderada",
    65: "Lluvia intensa",
    66: "Lluvia helada ligera",
    67: "Lluvia helada intensa",
    71: "Nevada ligera",
    73: "Nevada moderada",
    75: "Nevada intensa",
    77: "Granos de nieve",
    80: "Chubascos ligeros",
    81: "Chubascos moderados",
    82: "Chubascos intensos",
    85: "Chubascos de nieve ligeros",
    86: "Chubascos de nieve intensos",
    95: "Tormenta eléctrica",
    96: "Tormenta con granizo ligero",
    99: "Tormenta con granizo intenso",
}


def describir_codigo_clima(codigo):
    try:
        codigo = int(codigo)
    except (TypeError, ValueError):
        return "Condición meteorológica no disponible"

    return DESCRIPCIONES_CODIGO.get(
        codigo,
        "Condición meteorológica no disponible",
    )


def _construir_url(url_base, parametros):
    return f"{url_base}?{urlencode(parametros)}"


def _solicitar_json(url, timeout=TIEMPO_ESPERA):
    solicitud = Request(
        url,
        headers={"User-Agent": AGENTE_USUARIO},
    )

    try:
        with urlopen(solicitud, timeout=timeout) as respuesta:
            contenido_bytes = respuesta.read()
    except HTTPError as error:
        raise ErrorConsultaClima(
            "Open-Meteo no pudo procesar la consulta. "
            f"Código HTTP: {error.code}."
        ) from error
    except (URLError, TimeoutError, socket.timeout) as error:
        raise ErrorConsultaClima(
            "No fue posible consultar el clima. "
            "Revisa tu conexión a Internet."
        ) from error

    try:
        contenido = contenido_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ErrorConsultaClima(
            "Open-Meteo devolvió una respuesta inválida."
        ) from error

    try:
        datos = json.loads(contenido)
    except json.JSONDecodeError as error:
        raise ErrorConsultaClima(
            "Open-Meteo devolvió una respuesta inválida."
        ) from error

    if not isinstance(datos, dict):
        raise ErrorConsultaClima(
            "Open-Meteo devolvió una respuesta inválida."
        )

    if datos.get("error"):
        razon = datos.get("reason")
        mensaje = "Open-Meteo rechazó la consulta."

        if razon:
            mensaje = f"{mensaje} {razon}"

        raise ErrorConsultaClima(mensaje)

    return datos


def buscar_ubicacion(nombre, codigo_pais="MX"):
    nombre = str(nombre).strip()

    if not nombre:
        raise ErrorConsultaClima(
            "Indica la ciudad cuyo clima deseas consultar."
        )

    parametros = {
        "name": nombre,
        "count": 1,
        "language": "es",
        "format": "json",
    }

    if codigo_pais:
        parametros["countryCode"] = str(
            codigo_pais
        ).upper()

    url = _construir_url(
        URL_GEOCODIFICACION,
        parametros,
    )
    datos = _solicitar_json(url)
    resultados = datos.get("results") or []

    if not resultados:
        raise ErrorConsultaClima(
            f'No encontré la ubicación "{nombre}".'
        )

    resultado = resultados[0]
    campos_obligatorios = (
        "name",
        "latitude",
        "longitude",
    )

    if not all(
        campo in resultado
        for campo in campos_obligatorios
    ):
        raise ErrorConsultaClima(
            "La ubicación encontrada no tiene "
            "coordenadas válidas."
        )

    try:
        latitud, longitud = _validar_coordenadas(
            resultado["latitude"],
            resultado["longitude"],
        )
    except ErrorConsultaClima as error:
        raise ErrorConsultaClima(
            "La ubicación encontrada no tiene "
            "coordenadas válidas."
        ) from error

    return {
        "nombre": resultado["name"],
        "estado": resultado.get("admin1"),
        "pais": resultado.get("country"),
        "codigo_pais": resultado.get("country_code"),
        "latitud": latitud,
        "longitud": longitud,
        "zona_horaria": resultado.get("timezone"),
    }


def _validar_coordenadas(latitud, longitud):
    try:
        latitud = float(latitud)
        longitud = float(longitud)
    except (TypeError, ValueError) as error:
        raise ErrorConsultaClima(
            "Las coordenadas proporcionadas no son válidas."
        ) from error

    if not -90 <= latitud <= 90:
        raise ErrorConsultaClima(
            "La latitud debe estar entre -90 y 90."
        )

    if not -180 <= longitud <= 180:
        raise ErrorConsultaClima(
            "La longitud debe estar entre -180 y 180."
        )

    return latitud, longitud


def consultar_pronostico(latitud, longitud, dias=3):
    latitud, longitud = _validar_coordenadas(
        latitud,
        longitud,
    )

    if not isinstance(dias, int) or not 1 <= dias <= 7:
        raise ErrorConsultaClima(
            "El pronóstico debe solicitarse entre 1 y 7 días."
        )

    parametros = {
        "latitude": latitud,
        "longitude": longitud,
        "current": (
            "temperature_2m,apparent_temperature,"
            "relative_humidity_2m,precipitation,"
            "weather_code,wind_speed_10m"
        ),
        "daily": (
            "weather_code,temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max,"
            "precipitation_sum"
        ),
        "timezone": "auto",
        "forecast_days": dias,
    }

    url = _construir_url(
        URL_PRONOSTICO,
        parametros,
    )
    datos = _solicitar_json(url)

    actual = datos.get("current")
    diario = datos.get("daily")

    if not isinstance(actual, dict):
        raise ErrorConsultaClima(
            "Open-Meteo no devolvió el clima actual."
        )

    if not isinstance(diario, dict):
        raise ErrorConsultaClima(
            "Open-Meteo no devolvió el pronóstico diario."
        )

    campos_actuales = (
        "temperature_2m",
        "apparent_temperature",
        "relative_humidity_2m",
        "precipitation",
        "weather_code",
        "wind_speed_10m",
    )
    campos_diarios = (
        "time",
        "weather_code",
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_probability_max",
        "precipitation_sum",
    )

    if not all(
        campo in actual
        for campo in campos_actuales
    ):
        raise ErrorConsultaClima(
            "Los datos del clima actual están incompletos."
        )

    if not all(
        isinstance(diario.get(campo), list)
        for campo in campos_diarios
    ):
        raise ErrorConsultaClima(
            "Los datos del pronóstico están incompletos."
        )

    cantidad = len(diario["time"])

    if cantidad == 0 or any(
        len(diario[campo]) != cantidad
        for campo in campos_diarios
    ):
        raise ErrorConsultaClima(
            "Los datos del pronóstico están incompletos."
        )

    pronostico = []

    for indice in range(cantidad):
        pronostico.append(
            {
                "fecha": diario["time"][indice],
                "codigo": diario["weather_code"][indice],
                "temperatura_maxima": diario[
                    "temperature_2m_max"
                ][indice],
                "temperatura_minima": diario[
                    "temperature_2m_min"
                ][indice],
                "probabilidad_lluvia": diario[
                    "precipitation_probability_max"
                ][indice],
                "precipitacion": diario[
                    "precipitation_sum"
                ][indice],
            }
        )

    return {
        "actual": {
            "hora": actual.get("time"),
            "codigo": actual["weather_code"],
            "temperatura": actual["temperature_2m"],
            "sensacion_termica": actual[
                "apparent_temperature"
            ],
            "humedad": actual["relative_humidity_2m"],
            "precipitacion": actual["precipitation"],
            "viento": actual["wind_speed_10m"],
        },
        "pronostico": pronostico,
        "zona_horaria": datos.get("timezone"),
    }


def consultar_clima(lugar, dias=3, codigo_pais="MX"):
    ubicacion = buscar_ubicacion(
        lugar,
        codigo_pais=codigo_pais,
    )
    clima = consultar_pronostico(
        ubicacion["latitud"],
        ubicacion["longitud"],
        dias=dias,
    )

    return {
        "ubicacion": ubicacion,
        **clima,
        "fuente": "Open-Meteo",
        "enlace": URL_FUENTE,
    }


def _formatear_numero(valor, decimales=1):
    try:
        return f"{float(valor):.{decimales}f}"
    except (TypeError, ValueError):
        return "No disponible"


def _nombre_ubicacion(ubicacion):
    partes = []

    for campo in ("nombre", "estado", "pais"):
        valor = ubicacion.get(campo)

        if valor and valor not in partes:
            partes.append(valor)

    return ", ".join(partes)


def formatear_resultado_clima(resultado):
    ubicacion = resultado.get("ubicacion")
    actual = resultado.get("actual")
    pronostico = resultado.get("pronostico")

    if not isinstance(ubicacion, dict):
        raise ErrorConsultaClima(
            "No se pudo presentar la ubicación consultada."
        )

    if not isinstance(actual, dict):
        raise ErrorConsultaClima(
            "No se pudo presentar el clima actual."
        )

    if not isinstance(pronostico, list) or not pronostico:
        raise ErrorConsultaClima(
            "No se pudo presentar el pronóstico."
        )

    lineas = [
        f"Clima en {_nombre_ubicacion(ubicacion)}",
        "",
        (
            "Ahora: "
            f"{describir_codigo_clima(actual.get('codigo'))}."
        ),
        (
            "- Temperatura: "
            f"{_formatear_numero(actual.get('temperatura'))} °C"
        ),
        (
            "- Sensación térmica: "
            f"{_formatear_numero(actual.get('sensacion_termica'))} °C"
        ),
        f"- Humedad: {_formatear_numero(actual.get('humedad'), 0)} %",
        f"- Viento: {_formatear_numero(actual.get('viento'))} km/h",
        (
            "- Precipitación actual: "
            f"{_formatear_numero(actual.get('precipitacion'))} mm"
        ),
        "",
        "Pronóstico:",
    ]

    for indice, dia in enumerate(pronostico):
        if indice == 0:
            etiqueta_fecha = "Hoy"
        elif indice == 1:
            etiqueta_fecha = "Mañana"
        else:
            try:
                fecha = date.fromisoformat(dia["fecha"])
                etiqueta_fecha = fecha.strftime("%d/%m/%Y")
            except (KeyError, TypeError, ValueError):
                etiqueta_fecha = "Fecha no disponible"

        descripcion = describir_codigo_clima(
            dia.get("codigo")
        ).lower()
        maxima = _formatear_numero(
            dia.get("temperatura_maxima")
        )
        minima = _formatear_numero(
            dia.get("temperatura_minima")
        )
        probabilidad = _formatear_numero(
            dia.get("probabilidad_lluvia"),
            0,
        )

        lineas.append(
            f"- {etiqueta_fecha}: {descripcion}; "
            f"máxima {maxima} °C, mínima {minima} °C, "
            f"probabilidad de lluvia {probabilidad} %."
        )

    lineas.extend(
        (
            "",
            f"Fuente: {resultado.get('fuente', 'Open-Meteo')}",
            resultado.get("enlace", URL_FUENTE),
        )
    )

    return "\n".join(lineas)


def main():
    print("CONSULTA DEL CLIMA CON OPEN-METEO")
    lugar = input("Escribe una ciudad de México: ").strip()

    try:
        resultado = consultar_clima(lugar)
        print()
        print(formatear_resultado_clima(resultado))
    except ErrorConsultaClima as error:
        print()
        print(f"ERROR: {error}")


if __name__ == "__main__":
    main()
