import json
import math
import os
import socket
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ubicaciones import ErrorConsultaUbicacion, buscar_ubicacion


URL_OSRM_PREDETERMINADA = "https://router.project-osrm.org"
URL_OPENSTREETMAP = "https://www.openstreetmap.org/directions"
AGENTE_USUARIO = (
    "EduIA/1.4 (https://github.com/IsaacAnd222/EduIA)"
)
TIEMPO_ESPERA = 12
PERFIL_PREDETERMINADO = "driving"
PERFILES_PERMITIDOS = {"driving"}
MAXIMO_INSTRUCCIONES = 10

_CACHE = {}


class ErrorConsultaRuta(Exception):
    """Error controlado al buscar o presentar una ruta."""


def obtener_url_osrm():
    return os.environ.get(
        "EDUIA_OSRM_URL",
        URL_OSRM_PREDETERMINADA,
    ).strip().rstrip("/")


def _validar_coordenadas(latitud, longitud):
    try:
        latitud = float(latitud)
        longitud = float(longitud)
    except (TypeError, ValueError) as error:
        raise ErrorConsultaRuta(
            "La ubicación no contiene coordenadas válidas."
        ) from error

    if not math.isfinite(latitud) or not -90 <= latitud <= 90:
        raise ErrorConsultaRuta(
            "La ubicación no contiene una latitud válida."
        )

    if not math.isfinite(longitud) or not -180 <= longitud <= 180:
        raise ErrorConsultaRuta(
            "La ubicación no contiene una longitud válida."
        )

    return latitud, longitud


def _normalizar_ubicacion(ubicacion, etiqueta):
    if not isinstance(ubicacion, dict):
        raise ErrorConsultaRuta(
            f"No se pudo determinar {etiqueta}."
        )

    latitud, longitud = _validar_coordenadas(
        ubicacion.get("latitud"),
        ubicacion.get("longitud"),
    )
    nombre = str(
        ubicacion.get("nombre")
        or ubicacion.get("direccion_completa")
        or etiqueta.capitalize()
    ).strip()

    return {
        **ubicacion,
        "nombre": nombre,
        "latitud": latitud,
        "longitud": longitud,
    }


def construir_url_ruta(
    origen,
    destino,
    perfil=PERFIL_PREDETERMINADO,
):
    if perfil not in PERFILES_PERMITIDOS:
        raise ErrorConsultaRuta(
            "Por ahora solo están disponibles las rutas en automóvil."
        )

    origen = _normalizar_ubicacion(origen, "el origen")
    destino = _normalizar_ubicacion(destino, "el destino")
    url_base = obtener_url_osrm()

    if not url_base:
        raise ErrorConsultaRuta(
            "No está configurado el servicio de rutas."
        )

    coordenadas = (
        f"{origen['longitud']},{origen['latitud']};"
        f"{destino['longitud']},{destino['latitud']}"
    )
    parametros = urlencode(
        {
            "alternatives": "false",
            "steps": "true",
            "overview": "false",
        }
    )

    return (
        f"{url_base}/route/v1/{perfil}/"
        f"{coordenadas}?{parametros}"
    )


def construir_enlace_mapa(origen, destino):
    origen = _normalizar_ubicacion(origen, "el origen")
    destino = _normalizar_ubicacion(destino, "el destino")
    parametros = urlencode(
        {
            "engine": "fossgis_osrm_car",
            "route": (
                f"{origen['latitud']},{origen['longitud']};"
                f"{destino['latitud']},{destino['longitud']}"
            ),
        }
    )
    return f"{URL_OPENSTREETMAP}?{parametros}"


def _solicitar_json(url, timeout=TIEMPO_ESPERA):
    solicitud = Request(
        url,
        headers={
            "User-Agent": AGENTE_USUARIO,
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(solicitud, timeout=timeout) as respuesta:
            contenido_bytes = respuesta.read()
    except HTTPError as error:
        raise ErrorConsultaRuta(
            "El servicio de rutas no pudo procesar la consulta. "
            f"Código HTTP: {error.code}."
        ) from error
    except (URLError, TimeoutError, socket.timeout) as error:
        raise ErrorConsultaRuta(
            "No fue posible consultar el servicio de rutas. "
            "Revisa tu conexión a Internet."
        ) from error

    try:
        datos = json.loads(contenido_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ErrorConsultaRuta(
            "El servicio de rutas devolvió una respuesta inválida."
        ) from error

    if not isinstance(datos, dict):
        raise ErrorConsultaRuta(
            "El servicio de rutas devolvió una respuesta inválida."
        )

    return datos


def _numero_no_negativo(valor, descripcion):
    try:
        numero = float(valor)
    except (TypeError, ValueError) as error:
        raise ErrorConsultaRuta(
            f"La ruta no contiene {descripcion} válida."
        ) from error

    if not math.isfinite(numero) or numero < 0:
        raise ErrorConsultaRuta(
            f"La ruta no contiene {descripcion} válida."
        )

    return numero


def _descripcion_maniobra(maniobra, calle):
    tipo = str(maniobra.get("type", "continue")).lower()
    modificador = str(maniobra.get("modifier", "")).lower()
    lado = {
        "left": "a la izquierda",
        "right": "a la derecha",
        "slight left": "ligeramente a la izquierda",
        "slight right": "ligeramente a la derecha",
        "sharp left": "pronunciadamente a la izquierda",
        "sharp right": "pronunciadamente a la derecha",
        "straight": "recto",
        "uturn": "en retorno",
    }.get(modificador, "")

    if modificador == "uturn":
        texto = "Da vuelta en U"
    elif tipo == "depart":
        texto = "Sal de tu ubicación"
    elif tipo == "arrive":
        return "Llegaste a tu destino"
    elif tipo in {"turn", "end of road"}:
        if modificador == "straight":
            texto = "Continúa recto"
        else:
            texto = f"Gira {lado}" if lado else "Gira"
    elif tipo in {"merge", "on ramp", "off ramp"}:
        texto = f"Incorpórate {lado}" if lado else "Incorpórate"
    elif tipo == "fork":
        texto = f"Mantente {lado}" if lado else "Continúa por la bifurcación"
    elif tipo in {"roundabout", "rotary"}:
        texto = "Entra en la glorieta"
        salida = maniobra.get("exit")

        if isinstance(salida, int) and salida > 0:
            texto += f" y toma la salida {salida}"
    elif lado and lado != "recto":
        texto = f"Continúa {lado}"
    else:
        texto = "Continúa recto"

    if calle:
        texto += f" por {calle}"

    return texto


def _procesar_instrucciones(ruta):
    instrucciones = []
    tramos = ruta.get("legs", [])

    if not isinstance(tramos, list):
        return instrucciones

    for tramo in tramos:
        if not isinstance(tramo, dict):
            continue

        pasos = tramo.get("steps", [])

        if not isinstance(pasos, list):
            continue

        for paso in pasos:
            if not isinstance(paso, dict):
                continue

            distancia = _numero_no_negativo(
                paso.get("distance", 0),
                "distancia",
            )
            maniobra = paso.get("maneuver")

            if not isinstance(maniobra, dict):
                maniobra = {}

            instrucciones.append(
                {
                    "indicacion": _descripcion_maniobra(
                        maniobra,
                        str(paso.get("name", "")).strip(),
                    ),
                    "distancia_m": distancia,
                }
            )

    return instrucciones


def _procesar_respuesta(datos, origen, destino, perfil):
    codigo = datos.get("code")

    if codigo == "NoRoute":
        raise ErrorConsultaRuta(
            "No encontré una ruta por carretera entre esos lugares."
        )

    if codigo != "Ok":
        mensaje = str(datos.get("message", "")).strip()
        raise ErrorConsultaRuta(
            mensaje or "El servicio no pudo calcular la ruta."
        )

    rutas = datos.get("routes")

    if not isinstance(rutas, list) or not rutas:
        raise ErrorConsultaRuta(
            "El servicio no devolvió una ruta válida."
        )

    ruta = rutas[0]

    if not isinstance(ruta, dict):
        raise ErrorConsultaRuta(
            "El servicio no devolvió una ruta válida."
        )

    distancia_m = _numero_no_negativo(
        ruta.get("distance"),
        "distancia",
    )
    duracion_s = _numero_no_negativo(
        ruta.get("duration"),
        "duración",
    )

    return {
        "origen": origen,
        "destino": destino,
        "perfil": perfil,
        "distancia_km": distancia_m / 1000,
        "duracion_min": duracion_s / 60,
        "instrucciones": _procesar_instrucciones(ruta),
        "fuente": "OSRM y © OpenStreetMap contributors",
        "enlace": construir_enlace_mapa(origen, destino),
    }


def consultar_ruta_coordenadas(
    origen,
    destino,
    perfil=PERFIL_PREDETERMINADO,
):
    origen = _normalizar_ubicacion(origen, "el origen")
    destino = _normalizar_ubicacion(destino, "el destino")
    clave_cache = (
        perfil,
        origen["latitud"],
        origen["longitud"],
        destino["latitud"],
        destino["longitud"],
    )

    if clave_cache in _CACHE:
        return dict(_CACHE[clave_cache])

    url = construir_url_ruta(origen, destino, perfil)
    datos = _solicitar_json(url)
    resultado = _procesar_respuesta(
        datos,
        origen,
        destino,
        perfil,
    )
    _CACHE[clave_cache] = dict(resultado)
    return dict(resultado)


def calcular_ruta(
    nombre_origen,
    nombre_destino,
    perfil=PERFIL_PREDETERMINADO,
):
    nombre_origen = str(nombre_origen).strip()
    nombre_destino = str(nombre_destino).strip()

    if not nombre_origen:
        raise ErrorConsultaRuta(
            "Indica el lugar de origen."
        )

    if not nombre_destino:
        raise ErrorConsultaRuta(
            "Indica el lugar de destino."
        )

    try:
        origen = buscar_ubicacion(nombre_origen)
        destino = buscar_ubicacion(nombre_destino)
    except ErrorConsultaUbicacion as error:
        raise ErrorConsultaRuta(str(error)) from error

    return consultar_ruta_coordenadas(
        origen,
        destino,
        perfil,
    )


def _formatear_distancia_paso(distancia_m):
    if distancia_m >= 1000:
        return f"{distancia_m / 1000:.1f} km"
    return f"{distancia_m:.0f} m"


def formatear_resultado_ruta(resultado):
    if not isinstance(resultado, dict):
        raise ErrorConsultaRuta(
            "No se pudo presentar la ruta encontrada."
        )

    origen = resultado.get("origen")
    destino = resultado.get("destino")
    enlace = resultado.get("enlace")

    if not isinstance(origen, dict) or not isinstance(destino, dict):
        raise ErrorConsultaRuta(
            "La ruta encontrada está incompleta."
        )

    if not enlace:
        raise ErrorConsultaRuta(
            "La ruta encontrada no contiene un enlace válido."
        )

    distancia_km = _numero_no_negativo(
        resultado.get("distancia_km"),
        "distancia",
    )
    duracion_min = _numero_no_negativo(
        resultado.get("duracion_min"),
        "duración",
    )
    lineas = [
        f"Ruta de {origen['nombre']} a {destino['nombre']}",
        "",
        f"Distancia por carretera: {distancia_km:.1f} km",
        (
            "Duración aproximada: "
            f"{max(1, int(duracion_min + 0.5))} min"
        ),
    ]
    instrucciones = resultado.get("instrucciones", [])

    if instrucciones:
        lineas.extend(("", "Indicaciones principales:"))

        for numero, paso in enumerate(
            instrucciones[:MAXIMO_INSTRUCCIONES],
            start=1,
        ):
            lineas.append(
                f"{numero}. {paso['indicacion']} "
                f"({_formatear_distancia_paso(paso['distancia_m'])})."
            )

        if len(instrucciones) > MAXIMO_INSTRUCCIONES:
            lineas.append(
                "Consulta el enlace para ver todas las indicaciones."
            )

    lineas.extend(
        (
            "",
            f"Fuente: {resultado.get('fuente') or 'OSRM'}",
            str(enlace),
        )
    )
    return "\n".join(lineas)


def limpiar_cache():
    _CACHE.clear()


def main():
    print("RUTAS CON OPENSTREETMAP Y OSRM")
    origen = input("Escribe el lugar de origen: ")
    destino = input("Escribe el lugar de destino: ")

    try:
        resultado = calcular_ruta(origen, destino)
        print("\n" + formatear_resultado_ruta(resultado))
    except ErrorConsultaRuta as error:
        print(f"\nERROR: {error}")


if __name__ == "__main__":
    main()
