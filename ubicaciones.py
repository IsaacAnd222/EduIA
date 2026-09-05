import json
import os
import re
import socket
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


URL_NOMINATIM_PREDETERMINADA = (
    "https://nominatim.openstreetmap.org/search"
)
URL_OPENSTREETMAP = "https://www.openstreetmap.org"
AGENTE_USUARIO = (
    "EduIA/1.3 (https://github.com/IsaacAnd222/EduIA)"
)
TIEMPO_ESPERA = 10
INTERVALO_SOLICITUDES = 1.0

_CACHE = {}
_BLOQUEO_SOLICITUD = threading.Lock()
_ULTIMA_SOLICITUD = 0.0


class ErrorConsultaUbicacion(Exception):
    """Error controlado al consultar una ubicación."""


def obtener_url_nominatim():
    return os.environ.get(
        "EDUIA_NOMINATIM_URL",
        URL_NOMINATIM_PREDETERMINADA,
    ).strip()


def _construir_url(url_base, parametros):
    return f"{url_base}?{urlencode(parametros)}"


def _normalizar_consulta(consulta):
    return " ".join(
        str(consulta).casefold().split()
    )


def generar_consultas_alternativas(consulta):
    """Genera variantes prudentes sin convertir la búsqueda en autocompletado."""
    consulta = " ".join(str(consulta).strip().split())

    if not consulta:
        return []

    alternativas = [consulta]

    consulta_con_comas = re.sub(
        r"\s+en\s+",
        ", ",
        consulta,
        count=1,
        flags=re.IGNORECASE,
    )

    if consulta_con_comas != consulta:
        alternativas.append(consulta_con_comas)

    coincidencia_campus = re.match(
        r"^(.+?)\s+campus\s+(.+)$",
        consulta,
        flags=re.IGNORECASE,
    )

    if coincidencia_campus:
        institucion = coincidencia_campus.group(1).strip(" ,-")
        nombres_campus = re.split(
            r"\s*[-/]\s*|\s+y\s+",
            coincidencia_campus.group(2).strip(),
            flags=re.IGNORECASE,
        )

        for nombre_campus in nombres_campus:
            nombre_campus = nombre_campus.strip(" ,-")

            if nombre_campus:
                alternativas.append(
                    f"{institucion}, {nombre_campus}"
                )

    unicas = []
    claves = set()

    for alternativa in alternativas:
        clave = _normalizar_consulta(alternativa)

        if clave not in claves:
            claves.add(clave)
            unicas.append(alternativa)

    return unicas[:4]


def _respetar_limite_solicitudes():
    global _ULTIMA_SOLICITUD

    with _BLOQUEO_SOLICITUD:
        ahora = time.monotonic()
        espera = INTERVALO_SOLICITUDES - (
            ahora - _ULTIMA_SOLICITUD
        )

        if espera > 0:
            time.sleep(espera)

        _ULTIMA_SOLICITUD = time.monotonic()


def _solicitar_json(url, timeout=TIEMPO_ESPERA):
    solicitud = Request(
        url,
        headers={
            "User-Agent": AGENTE_USUARIO,
            "Accept-Language": "es-MX,es;q=0.9",
        },
    )

    try:
        with urlopen(solicitud, timeout=timeout) as respuesta:
            contenido_bytes = respuesta.read()
    except HTTPError as error:
        raise ErrorConsultaUbicacion(
            "OpenStreetMap no pudo procesar la consulta. "
            f"Código HTTP: {error.code}."
        ) from error
    except (URLError, TimeoutError, socket.timeout) as error:
        raise ErrorConsultaUbicacion(
            "No fue posible consultar OpenStreetMap. "
            "Revisa tu conexión a Internet."
        ) from error

    try:
        contenido = contenido_bytes.decode("utf-8")
        datos = json.loads(contenido)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ErrorConsultaUbicacion(
            "OpenStreetMap devolvió una respuesta inválida."
        ) from error

    if not isinstance(datos, list):
        raise ErrorConsultaUbicacion(
            "OpenStreetMap devolvió una respuesta inválida."
        )

    return datos


def _validar_coordenadas(latitud, longitud):
    try:
        latitud = float(latitud)
        longitud = float(longitud)
    except (TypeError, ValueError) as error:
        raise ErrorConsultaUbicacion(
            "La ubicación no contiene coordenadas válidas."
        ) from error

    if not -90 <= latitud <= 90:
        raise ErrorConsultaUbicacion(
            "La ubicación no contiene una latitud válida."
        )

    if not -180 <= longitud <= 180:
        raise ErrorConsultaUbicacion(
            "La ubicación no contiene una longitud válida."
        )

    return latitud, longitud


def construir_enlace_mapa(resultado):
    tipo_osm = str(
        resultado.get("osm_type", "")
    ).lower()
    identificador = resultado.get("osm_id")

    if (
        tipo_osm in {"node", "way", "relation"}
        and identificador is not None
    ):
        return (
            f"{URL_OPENSTREETMAP}/{tipo_osm}/"
            f"{identificador}"
        )

    latitud, longitud = _validar_coordenadas(
        resultado.get("latitud"),
        resultado.get("longitud"),
    )

    return (
        f"{URL_OPENSTREETMAP}/?mlat={latitud}"
        f"&mlon={longitud}#map=17/{latitud}/{longitud}"
    )


def _procesar_resultado(resultado):
    if not isinstance(resultado, dict):
        raise ErrorConsultaUbicacion(
            "OpenStreetMap devolvió una ubicación inválida."
        )

    nombre_completo = str(
        resultado.get("display_name", "")
    ).strip()

    if not nombre_completo:
        raise ErrorConsultaUbicacion(
            "OpenStreetMap devolvió una ubicación sin nombre."
        )

    latitud, longitud = _validar_coordenadas(
        resultado.get("lat"),
        resultado.get("lon"),
    )
    direccion = resultado.get("address")

    if not isinstance(direccion, dict):
        direccion = {}

    ubicacion = {
        "nombre": (
            resultado.get("name")
            or nombre_completo.split(",", 1)[0]
        ),
        "direccion_completa": nombre_completo,
        "latitud": latitud,
        "longitud": longitud,
        "categoria": (
            resultado.get("category")
            or resultado.get("class")
        ),
        "tipo": (
            resultado.get("addresstype")
            or resultado.get("type")
        ),
        "ciudad": (
            direccion.get("city")
            or direccion.get("town")
            or direccion.get("municipality")
            or direccion.get("village")
        ),
        "estado": direccion.get("state"),
        "pais": direccion.get("country"),
        "codigo_postal": direccion.get("postcode"),
        "osm_type": resultado.get("osm_type"),
        "osm_id": resultado.get("osm_id"),
    }
    ubicacion["enlace"] = construir_enlace_mapa(
        ubicacion
    )

    return ubicacion


def _seleccionar_resultado_principal(resultados):
    if not resultados:
        raise ErrorConsultaUbicacion(
            "OpenStreetMap no devolvió ubicaciones válidas."
        )

    primero = resultados[0]
    es_limite_administrativo = (
        str(primero.get("categoria", "")).lower() == "boundary"
        or str(primero.get("tipo", "")).lower() == "administrative"
    )

    if es_limite_administrativo:
        tipos_urbanos = {
            "city",
            "town",
            "village",
            "municipality",
        }

        for resultado in resultados[1:]:
            if (
                str(resultado.get("categoria", "")).lower() == "place"
                and str(resultado.get("tipo", "")).lower()
                in tipos_urbanos
            ):
                return resultado

    return primero


def buscar_ubicaciones(
    consulta,
    limite=5,
    codigo_pais="mx",
    conservar_duplicados=False,
):
    consulta = str(consulta).strip()

    if not consulta:
        raise ErrorConsultaUbicacion(
            "Indica el lugar que deseas buscar."
        )

    if not isinstance(limite, int) or not 1 <= limite <= 5:
        raise ErrorConsultaUbicacion(
            "El número de resultados debe estar entre 1 y 5."
        )

    codigo_pais = str(codigo_pais).strip().lower()
    clave_cache = (
        _normalizar_consulta(consulta),
        limite,
        codigo_pais,
        bool(conservar_duplicados),
    )

    if clave_cache in _CACHE:
        return [
            dict(resultado)
            for resultado in _CACHE[clave_cache]
        ]

    parametros = {
        "q": consulta,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": limite,
    }

    if codigo_pais:
        parametros["countrycodes"] = codigo_pais

    if conservar_duplicados:
        parametros["dedupe"] = 0

    url_base = obtener_url_nominatim()

    if not url_base:
        raise ErrorConsultaUbicacion(
            "No está configurado el servicio de ubicaciones."
        )

    url = _construir_url(url_base, parametros)
    _respetar_limite_solicitudes()
    datos = _solicitar_json(url)

    if not datos:
        raise ErrorConsultaUbicacion(
            f'No encontré la ubicación "{consulta}".'
        )

    resultados = []

    for dato in datos:
        try:
            resultados.append(
                _procesar_resultado(dato)
            )
        except ErrorConsultaUbicacion:
            continue

    if not resultados:
        raise ErrorConsultaUbicacion(
            "OpenStreetMap no devolvió ubicaciones válidas."
        )

    _CACHE[clave_cache] = tuple(
        dict(resultado)
        for resultado in resultados
    )

    return [
        dict(resultado)
        for resultado in resultados
    ]


def buscar_ubicacion(
    consulta,
    codigo_pais="mx",
):
    ultimo_error = None

    for alternativa in generar_consultas_alternativas(consulta):
        try:
            resultados = buscar_ubicaciones(
                alternativa,
                limite=5,
                codigo_pais=codigo_pais,
                conservar_duplicados=True,
            )
        except ErrorConsultaUbicacion as error:
            ultimo_error = error

            if not str(error).startswith("No encontré la ubicación"):
                raise

            continue

        return _seleccionar_resultado_principal(resultados)

    if ultimo_error is not None:
        raise ErrorConsultaUbicacion(
            f'No encontré la ubicación "{str(consulta).strip()}".'
        ) from ultimo_error

    raise ErrorConsultaUbicacion(
        "Indica el lugar que deseas buscar."
    )


def limpiar_cache():
    _CACHE.clear()


def formatear_resultado_ubicacion(resultado):
    if not isinstance(resultado, dict):
        raise ErrorConsultaUbicacion(
            "No se pudo presentar la ubicación encontrada."
        )

    direccion = resultado.get("direccion_completa")
    enlace = resultado.get("enlace")

    if not direccion or not enlace:
        raise ErrorConsultaUbicacion(
            "La ubicación encontrada está incompleta."
        )

    return "\n".join(
        (
            str(resultado.get("nombre") or "Ubicación encontrada"),
            "",
            f"Dirección: {direccion}",
            (
                "Coordenadas: "
                f"{resultado.get('latitud'):.6f}, "
                f"{resultado.get('longitud'):.6f}"
            ),
            "",
            "Fuente: © OpenStreetMap contributors",
            enlace,
        )
    )


def formatear_resultados_ubicacion(resultados):
    if not isinstance(resultados, list) or not resultados:
        raise ErrorConsultaUbicacion(
            "No hay ubicaciones para presentar."
        )

    lineas = ["Ubicaciones encontradas:"]

    for indice, resultado in enumerate(resultados, 1):
        lineas.extend(
            (
                "",
                f"{indice}. {resultado['nombre']}",
                f"   {resultado['direccion_completa']}",
                (
                    "   Coordenadas: "
                    f"{resultado['latitud']:.6f}, "
                    f"{resultado['longitud']:.6f}"
                ),
                f"   {resultado['enlace']}",
            )
        )

    lineas.extend(
        (
            "",
            "Fuente: © OpenStreetMap contributors",
        )
    )

    return "\n".join(lineas)


def main():
    print("BÚSQUEDA DE LUGARES CON OPENSTREETMAP")
    consulta = input("Escribe un lugar de México: ").strip()

    try:
        resultado = buscar_ubicacion(consulta)
        print()
        print(formatear_resultado_ubicacion(resultado))
    except ErrorConsultaUbicacion as error:
        print()
        print(f"ERROR: {error}")


if __name__ == "__main__":
    main()
