from enlaces import crear_acciones_enlaces, extraer_enlaces
from rutas import formatear_duracion


def probar_extraccion_de_enlaces():
    texto = (
        "Fuente: OpenStreetMap\n"
        "https://www.openstreetmap.org/node/123\n"
        "https://www.openstreetmap.org/node/123"
    )
    assert extraer_enlaces(texto) == [
        "https://www.openstreetmap.org/node/123"
    ]


def probar_limpieza_de_puntuacion():
    assert extraer_enlaces("Consulta (https://example.com/ruta).") == [
        "https://example.com/ruta"
    ]


def probar_etiquetas_de_fuentes():
    texto = (
        "https://es.wikipedia.org/wiki/Universidad\n"
        "https://open-meteo.com/"
    )
    assert crear_acciones_enlaces(texto) == [
        (
            "Abrir Wikipedia",
            "https://es.wikipedia.org/wiki/Universidad",
        ),
        ("Abrir Open-Meteo", "https://open-meteo.com/"),
    ]


def probar_boton_de_ruta():
    enlace = (
        "https://www.openstreetmap.org/directions?"
        "engine=fossgis_osrm_car&route=20,-101;21,-102"
    )
    assert crear_acciones_enlaces(enlace) == [
        ("Abrir ruta", enlace)
    ]


def probar_numeracion_de_lugares():
    texto = (
        "https://www.openstreetmap.org/node/1\n"
        "https://www.openstreetmap.org/way/2"
    )
    assert [
        etiqueta for etiqueta, _ in crear_acciones_enlaces(texto)
    ] == ["Abrir lugar 1", "Abrir lugar 2"]


def probar_formato_de_duracion_amigable():
    assert formatear_duracion(408) == "6 h 48 min"


PRUEBAS = (
    ("Extrae enlaces sin duplicarlos", probar_extraccion_de_enlaces),
    ("Limpia puntuación al final del enlace", probar_limpieza_de_puntuacion),
    ("Etiqueta las fuentes externas", probar_etiquetas_de_fuentes),
    ("Identifica el botón para abrir rutas", probar_boton_de_ruta),
    ("Numera varios lugares de OpenStreetMap", probar_numeracion_de_lugares),
    ("Presenta duraciones largas en horas", probar_formato_de_duracion_amigable),
)


def main():
    correctas = 0

    for nombre, prueba in PRUEBAS:
        try:
            prueba()
            correctas += 1
            print(f"[CORRECTA] {nombre}")
        except Exception as error:
            print(f"[ERROR] {nombre}: {error}")

    total = len(PRUEBAS)
    errores = total - correctas

    print("\n" + "=" * 70)
    print("RESUMEN DE MEJORAS DE EXPERIENCIA EXTERNA")
    print("=" * 70)
    print(f"Total de pruebas: {total}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {errores}")
    print(f"Precisión: {correctas / total:.2%}")

    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
