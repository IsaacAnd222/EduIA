import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


URL_API = "https://es.wikipedia.org/w/api.php"
AGENTE_USUARIO = (
    "EduIA/1.1 "
    "(https://github.com/IsaacAnd222/EduIA)"
)
TIEMPO_MAXIMO = 10
LONGITUD_MAXIMA = 1200


class ErrorConsultaInternet(Exception):
    """Error controlado al consultar información externa."""


def limitar_resumen(
    texto,
    longitud_maxima=LONGITUD_MAXIMA,
):
    texto = " ".join(texto.split())

    if len(texto) <= longitud_maxima:
        return texto

    posicion = texto.rfind(
        ".",
        0,
        longitud_maxima,
    )

    if posicion < longitud_maxima // 2:
        posicion = longitud_maxima
        resumen = texto[:posicion].rstrip()
        return f"{resumen}..."

    return texto[: posicion + 1].strip()


def construir_url(tema):
    parametros = {
        "action": "query",
        "generator": "search",
        "gsrsearch": tema,
        "gsrnamespace": 0,
        "gsrlimit": 1,
        "prop": "extracts|info",
        "exintro": 1,
        "explaintext": 1,
        "inprop": "url",
        "redirects": 1,
        "format": "json",
        "formatversion": 2,
        "utf8": 1,
    }

    return f"{URL_API}?{urlencode(parametros)}"


def buscar_en_wikipedia(tema):
    tema = str(tema).strip()

    if not tema:
        raise ErrorConsultaInternet(
            "Indica el tema que deseas buscar."
        )

    solicitud = Request(
        construir_url(tema),
        headers={
            "User-Agent": AGENTE_USUARIO,
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(
            solicitud,
            timeout=TIEMPO_MAXIMO,
        ) as respuesta:
            datos = json.load(respuesta)

    except (HTTPError, URLError, TimeoutError) as error:
        raise ErrorConsultaInternet(
            "No fue posible consultar Wikipedia. "
            "Revisa tu conexión a Internet."
        ) from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ErrorConsultaInternet(
            "Wikipedia devolvió una respuesta que no pudo procesarse."
        ) from error

    paginas = datos.get(
        "query",
        {},
    ).get(
        "pages",
        [],
    )

    if not paginas:
        raise ErrorConsultaInternet(
            f'No encontré información sobre "{tema}" en Wikipedia.'
        )

    pagina = paginas[0]
    titulo = pagina.get(
        "title",
        tema,
    )
    resumen = limitar_resumen(
        pagina.get(
            "extract",
            "",
        )
    )
    enlace = pagina.get(
        "fullurl",
        "",
    )

    if not resumen:
        raise ErrorConsultaInternet(
            f'Encontré "{titulo}", pero no tiene un resumen disponible.'
        )

    return {
        "titulo": titulo,
        "resumen": resumen,
        "enlace": enlace,
    }


def formatear_resultado(resultado):
    partes = [
        resultado["titulo"],
        "",
        resultado["resumen"],
        "",
        "Fuente: Wikipedia",
    ]

    if resultado.get("enlace"):
        partes.append(resultado["enlace"])

    return "\n".join(partes)


def main():
    print("BÚSQUEDA CONTROLADA EN WIKIPEDIA")
    tema = input("Escribe un tema: ").strip()

    try:
        resultado = buscar_en_wikipedia(tema)
        print("\n" + formatear_resultado(resultado))
    except ErrorConsultaInternet as error:
        print(f"\nERROR: {error}")


if __name__ == "__main__":
    main()
