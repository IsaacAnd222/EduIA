import json
import math
import os
import socket
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ubicaciones import ErrorConsultaUbicacion, buscar_ubicacion


URL_OVERPASS_PREDETERMINADA = (
    "https://overpass-api.de/api/interpreter"
)
URL_OPENSTREETMAP = "https://www.openstreetmap.org"
AGENTE_USUARIO = (
    "EduIA/1.5 (https://github.com/IsaacAnd222/EduIA)"
)
TIEMPO_ESPERA = 25
RADIO_PREDETERMINADO = 5000
RADIO_MINIMO = 100
RADIO_MAXIMO = 10000
LIMITE_PREDETERMINADO = 5
LIMITE_MAXIMO = 15

CATEGORIAS = {
    "hospital": {
        "plural": "hospitales",
        "filtros": (("amenity", "hospital"),),
        "sinonimos": ("hospital", "hospitales"),
    },
    "clinica": {
        "plural": "clínicas",
        "filtros": (("amenity", "clinic"),),
        "sinonimos": ("clinica", "clinicas"),
    },
    "farmacia": {
        "plural": "farmacias",
        "filtros": (("amenity", "pharmacy"),),
        "sinonimos": ("farmacia", "farmacias"),
    },
    "cafeteria": {
        "plural": "cafeterías",
        "filtros": (("amenity", "cafe"),),
        "sinonimos": ("cafeteria", "cafeterias", "cafe", "cafes"),
    },
    "restaurante": {
        "plural": "restaurantes",
        "filtros": (("amenity", "restaurant"),),
        "sinonimos": ("restaurante", "restaurantes"),
    },
    "escuela": {
        "plural": "escuelas",
        "filtros": (("amenity", "school"),),
        "sinonimos": ("escuela", "escuelas", "colegio", "colegios"),
    },
    "universidad": {
        "plural": "universidades",
        "filtros": (
            ("amenity", "university"),
            ("amenity", "college"),
        ),
        "sinonimos": (
            "universidad",
            "universidades",
            "campus",
        ),
    },
    "banco": {
        "plural": "bancos",
        "filtros": (("amenity", "bank"),),
        "sinonimos": ("banco", "bancos"),
    },
    "cajero": {
        "plural": "cajeros automáticos",
        "filtros": (("amenity", "atm"),),
        "sinonimos": (
            "cajero",
            "cajeros",
            "cajero automatico",
            "cajeros automaticos",
            "atm",
        ),
    },
    "gasolinera": {
        "plural": "gasolineras",
        "filtros": (("amenity", "fuel"),),
        "sinonimos": (
            "gasolinera",
            "gasolineras",
            "estacion de servicio",
        ),
    },
    "estacionamiento": {
        "plural": "estacionamientos",
        "filtros": (("amenity", "parking"),),
        "sinonimos": (
            "estacionamiento",
            "estacionamientos",
            "parking",
        ),
    },
    "parada_autobus": {
        "plural": "paradas de autobús",
        "filtros": (
            ("highway", "bus_stop"),
            ("public_transport", "platform"),
        ),
        "sinonimos": (
            "parada de autobus",
            "paradas de autobus",
            "parada de autobuses",
            "paradas de autobuses",
            "parada de camion",
            "paradas de camion",
            "parada de camiones",
            "paradas de camiones",
            "paradero de autobus",
            "paraderos de autobus",
            "paradero de autobuses",
            "paraderos de autobuses",
        ),
    },
}

_CACHE = {}


class ErrorConsultaCercanos(Exception):
    """Error controlado al buscar lugares cercanos."""


def normalizar_texto(texto):
    texto = unicodedata.normalize("NFD", str(texto).casefold())
    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )
    return " ".join(texto.split())


def obtener_url_overpass():
    return os.environ.get(
        "EDUIA_OVERPASS_URL",
        URL_OVERPASS_PREDETERMINADA,
    ).strip()


def resolver_categoria(texto):
    texto = normalizar_texto(texto).strip(" ¿?¡!.,;:")

    for clave, datos in CATEGORIAS.items():
        if texto == clave or texto in datos["sinonimos"]:
            return clave

    opciones = ", ".join(
        datos["plural"]
        for datos in CATEGORIAS.values()
    )
    raise ErrorConsultaCercanos(
        "La categoría solicitada todavía no está disponible. "
        f"Puedes buscar: {opciones}."
    )


def _validar_coordenadas(latitud, longitud):
    try:
        latitud = float(latitud)
        longitud = float(longitud)
    except (TypeError, ValueError) as error:
        raise ErrorConsultaCercanos(
            "La ubicación no contiene coordenadas válidas."
        ) from error

    if not math.isfinite(latitud) or not -90 <= latitud <= 90:
        raise ErrorConsultaCercanos(
            "La ubicación no contiene una latitud válida."
        )

    if not math.isfinite(longitud) or not -180 <= longitud <= 180:
        raise ErrorConsultaCercanos(
            "La ubicación no contiene una longitud válida."
        )

    return latitud, longitud


def _validar_radio(radio):
    if not isinstance(radio, int) or not RADIO_MINIMO <= radio <= RADIO_MAXIMO:
        raise ErrorConsultaCercanos(
            "El radio de búsqueda debe estar entre "
            f"{RADIO_MINIMO} y {RADIO_MAXIMO} metros."
        )
    return radio


def _validar_limite(limite):
    if not isinstance(limite, int) or not 1 <= limite <= LIMITE_MAXIMO:
        raise ErrorConsultaCercanos(
            "El número de resultados debe estar entre "
            f"1 y {LIMITE_MAXIMO}."
        )
    return limite


def construir_consulta_overpass(
    categoria,
    latitud,
    longitud,
    radio=RADIO_PREDETERMINADO,
):
    categoria = resolver_categoria(categoria)
    latitud, longitud = _validar_coordenadas(latitud, longitud)
    radio = _validar_radio(radio)
    consultas = []

    for clave, valor in CATEGORIAS[categoria]["filtros"]:
        consultas.append(
            f'nwr(around:{radio},{latitud},{longitud})'
            f'["{clave}"="{valor}"];'
        )

    return "\n".join(
        (
            "[out:json][timeout:20];",
            "(",
            *consultas,
            ");",
            "out center tags;",
        )
    )


def _solicitar_json(consulta, timeout=TIEMPO_ESPERA):
    url = obtener_url_overpass()

    if not url:
        raise ErrorConsultaCercanos(
            "No está configurado el servicio de lugares cercanos."
        )

    cuerpo = urlencode({"data": consulta}).encode("utf-8")
    solicitud = Request(
        url,
        data=cuerpo,
        headers={
            "User-Agent": AGENTE_USUARIO,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with urlopen(solicitud, timeout=timeout) as respuesta:
            contenido_bytes = respuesta.read()
    except HTTPError as error:
        if error.code in {429, 504}:
            mensaje = (
                "El servicio de lugares cercanos está ocupado. "
                "Intenta nuevamente en unos minutos."
            )
        else:
            mensaje = (
                "El servicio no pudo procesar la consulta. "
                f"Código HTTP: {error.code}."
            )
        raise ErrorConsultaCercanos(mensaje) from error
    except (URLError, TimeoutError, socket.timeout) as error:
        raise ErrorConsultaCercanos(
            "No fue posible consultar los lugares cercanos. "
            "Revisa tu conexión a Internet."
        ) from error

    try:
        datos = json.loads(contenido_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ErrorConsultaCercanos(
            "El servicio devolvió una respuesta inválida."
        ) from error

    if not isinstance(datos, dict) or not isinstance(
        datos.get("elements"),
        list,
    ):
        raise ErrorConsultaCercanos(
            "El servicio devolvió una respuesta inválida."
        )

    return datos


def _distancia_haversine(latitud_1, longitud_1, latitud_2, longitud_2):
    radio_tierra = 6371000
    latitud_1 = math.radians(latitud_1)
    latitud_2 = math.radians(latitud_2)
    diferencia_latitud = latitud_2 - latitud_1
    diferencia_longitud = math.radians(longitud_2 - longitud_1)
    componente = (
        math.sin(diferencia_latitud / 2) ** 2
        + math.cos(latitud_1)
        * math.cos(latitud_2)
        * math.sin(diferencia_longitud / 2) ** 2
    )
    return 2 * radio_tierra * math.asin(math.sqrt(componente))


def _extraer_coordenadas_elemento(elemento):
    latitud = elemento.get("lat")
    longitud = elemento.get("lon")

    if latitud is None or longitud is None:
        centro = elemento.get("center")

        if isinstance(centro, dict):
            latitud = centro.get("lat")
            longitud = centro.get("lon")

    return _validar_coordenadas(latitud, longitud)


def _construir_direccion(etiquetas):
    calle = etiquetas.get("addr:street")
    numero = etiquetas.get("addr:housenumber")
    ciudad = (
        etiquetas.get("addr:city")
        or etiquetas.get("addr:municipality")
    )
    partes = []

    if calle:
        partes.append(
            f"{calle} {numero}".strip()
            if numero
            else str(calle)
        )

    if ciudad:
        partes.append(str(ciudad))

    return ", ".join(partes)


def _construir_enlace(elemento, latitud, longitud):
    tipo = str(elemento.get("type", "")).lower()
    identificador = elemento.get("id")

    if tipo in {"node", "way", "relation"} and identificador is not None:
        return f"{URL_OPENSTREETMAP}/{tipo}/{identificador}"

    return (
        f"{URL_OPENSTREETMAP}/?mlat={latitud}"
        f"&mlon={longitud}#map=18/{latitud}/{longitud}"
    )


def _procesar_elemento(
    elemento,
    categoria,
    latitud_origen,
    longitud_origen,
):
    if not isinstance(elemento, dict):
        raise ErrorConsultaCercanos(
            "El servicio devolvió un lugar inválido."
        )

    latitud, longitud = _extraer_coordenadas_elemento(elemento)
    etiquetas = elemento.get("tags")

    if not isinstance(etiquetas, dict):
        etiquetas = {}

    nombre = str(
        etiquetas.get("name")
        or etiquetas.get("brand")
        or CATEGORIAS[categoria]["plural"].capitalize()
    ).strip()
    distancia_m = _distancia_haversine(
        latitud_origen,
        longitud_origen,
        latitud,
        longitud,
    )

    return {
        "nombre": nombre,
        "categoria": categoria,
        "latitud": latitud,
        "longitud": longitud,
        "distancia_m": distancia_m,
        "direccion": _construir_direccion(etiquetas),
        "telefono": etiquetas.get("contact:phone") or etiquetas.get("phone"),
        "sitio_web": (
            etiquetas.get("contact:website")
            or etiquetas.get("website")
        ),
        "osm_type": elemento.get("type"),
        "osm_id": elemento.get("id"),
        "enlace": _construir_enlace(elemento, latitud, longitud),
    }


def buscar_lugares_cercanos(
    categoria,
    ubicacion,
    radio=RADIO_PREDETERMINADO,
    limite=LIMITE_PREDETERMINADO,
):
    categoria = resolver_categoria(categoria)
    radio = _validar_radio(radio)
    limite = _validar_limite(limite)

    if not isinstance(ubicacion, dict):
        raise ErrorConsultaCercanos(
            "No se pudo determinar la ubicación de referencia."
        )

    latitud, longitud = _validar_coordenadas(
        ubicacion.get("latitud"),
        ubicacion.get("longitud"),
    )
    clave_cache = (
        categoria,
        round(latitud, 6),
        round(longitud, 6),
        radio,
        limite,
    )

    if clave_cache in _CACHE:
        return {
            **_CACHE[clave_cache],
            "lugares": [
                dict(lugar)
                for lugar in _CACHE[clave_cache]["lugares"]
            ],
        }

    consulta = construir_consulta_overpass(
        categoria,
        latitud,
        longitud,
        radio,
    )
    datos = _solicitar_json(consulta)
    lugares = []

    for elemento in datos["elements"]:
        try:
            lugares.append(
                _procesar_elemento(
                    elemento,
                    categoria,
                    latitud,
                    longitud,
                )
            )
        except ErrorConsultaCercanos:
            continue

    lugares.sort(key=lambda lugar: lugar["distancia_m"])
    lugares = lugares[:limite]

    if not lugares:
        plural = CATEGORIAS[categoria]["plural"]
        raise ErrorConsultaCercanos(
            f"No encontré {plural} dentro de {radio / 1000:g} km."
        )

    resultado = {
        "categoria": categoria,
        "categoria_plural": CATEGORIAS[categoria]["plural"],
        "ubicacion": {
            **ubicacion,
            "latitud": latitud,
            "longitud": longitud,
        },
        "radio_m": radio,
        "lugares": lugares,
        "fuente": "© OpenStreetMap contributors mediante Overpass API",
    }
    _CACHE[clave_cache] = {
        **resultado,
        "lugares": tuple(dict(lugar) for lugar in lugares),
    }
    return resultado


def buscar_cerca_de(
    categoria,
    nombre_ubicacion,
    radio=RADIO_PREDETERMINADO,
    limite=LIMITE_PREDETERMINADO,
):
    nombre_ubicacion = str(nombre_ubicacion).strip()

    if not nombre_ubicacion:
        raise ErrorConsultaCercanos(
            "Indica la ubicación donde deseas buscar."
        )

    try:
        ubicacion = buscar_ubicacion(nombre_ubicacion)
    except ErrorConsultaUbicacion as error:
        raise ErrorConsultaCercanos(str(error)) from error

    return buscar_lugares_cercanos(
        categoria,
        ubicacion,
        radio,
        limite,
    )


def _formatear_distancia(distancia_m):
    if distancia_m >= 1000:
        return f"{distancia_m / 1000:.1f} km"
    return f"{round(distancia_m)} m"


def formatear_resultado_cercanos(resultado):
    if not isinstance(resultado, dict):
        raise ErrorConsultaCercanos(
            "No se pudieron presentar los lugares encontrados."
        )

    ubicacion = resultado.get("ubicacion")
    lugares = resultado.get("lugares")

    if not isinstance(ubicacion, dict) or not isinstance(lugares, (list, tuple)):
        raise ErrorConsultaCercanos(
            "La búsqueda de lugares está incompleta."
        )

    nombre_ubicacion = str(
        ubicacion.get("nombre") or "la ubicación indicada"
    )
    lineas = [
        (
            f"{resultado['categoria_plural'].capitalize()} "
            f"cerca de {nombre_ubicacion}:"
        ),
        "",
    ]

    for numero, lugar in enumerate(lugares, start=1):
        lineas.append(
            f"{numero}. {lugar['nombre']} "
            f"({_formatear_distancia(lugar['distancia_m'])})"
        )

        if lugar.get("direccion"):
            lineas.append(f"   Dirección: {lugar['direccion']}")

        lineas.append(f"   {lugar['enlace']}")

    lineas.extend(
        (
            "",
            f"Fuente: {resultado.get('fuente')}",
            (
                "Las distancias son aproximadas en línea recta desde "
                "la ubicación de referencia."
            ),
        )
    )
    return "\n".join(lineas)


def limpiar_cache():
    _CACHE.clear()


def main():
    print("LUGARES CERCANOS CON OPENSTREETMAP")
    categoria = input("¿Qué deseas buscar?: ")
    ubicacion = input("¿Cerca de qué lugar?: ")

    try:
        resultado = buscar_cerca_de(categoria, ubicacion)
        print("\n" + formatear_resultado_cercanos(resultado))
    except ErrorConsultaCercanos as error:
        print(f"\nERROR: {error}")


if __name__ == "__main__":
    main()
