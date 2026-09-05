import re


PATRON_ENLACE = re.compile(r"https?://[^\s]+")


def extraer_enlaces(texto):
    """Devuelve los enlaces únicos presentes en una respuesta."""
    enlaces = []

    for coincidencia in PATRON_ENLACE.findall(texto or ""):
        enlace = coincidencia.rstrip(".,;:!?)]}")

        if enlace and enlace not in enlaces:
            enlaces.append(enlace)

    return enlaces


def crear_acciones_enlaces(texto):
    """Asigna una etiqueta clara a cada enlace de la respuesta."""
    enlaces = extraer_enlaces(texto)
    cantidad_openstreetmap = sum(
        "openstreetmap.org" in enlace.casefold()
        and "/directions" not in enlace.casefold()
        for enlace in enlaces
    )
    numero_lugar = 0
    acciones = []

    for enlace in enlaces:
        enlace_normalizado = enlace.casefold()

        if "openstreetmap.org/directions" in enlace_normalizado:
            etiqueta = "Abrir ruta"
        elif "wikipedia.org" in enlace_normalizado:
            etiqueta = "Abrir Wikipedia"
        elif "open-meteo.com" in enlace_normalizado:
            etiqueta = "Abrir Open-Meteo"
        elif "openstreetmap.org" in enlace_normalizado:
            numero_lugar += 1
            etiqueta = (
                f"Abrir lugar {numero_lugar}"
                if cantidad_openstreetmap > 1
                else "Abrir en OpenStreetMap"
            )
        else:
            etiqueta = "Abrir fuente"

        acciones.append((etiqueta, enlace))

    return acciones
