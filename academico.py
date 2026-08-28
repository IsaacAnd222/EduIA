from sklearn.feature_extraction.text import (
    TfidfVectorizer,
)
from sklearn.metrics.pairwise import cosine_similarity

from base_datos import (
    crear_base_datos,
    obtener_contenidos_academicos,
)


UMBRAL_TEMA_ACADEMICO = 0.20

PALABRAS_IGNORADAS_ACADEMICAS = [
    "que",
    "como",
    "cual",
    "es",
    "son",
    "el",
    "la",
    "los",
    "las",
    "un",
    "una",
    "de",
    "del",
    "con",
    "sobre",
    "tema",
    "explicame",
    "ayudame",
    "estudiar",
    "entiendo",
    "necesito",
    "quiero",
]


def buscar_contenido_academico(pregunta):
    contenidos = obtener_contenidos_academicos()

    if not contenidos:
        return None, 0.0

    documentos = [
        (
            f"{contenido['tema']} "
            f"{contenido['materia']} "
            f"{contenido['palabras_clave']}"
        )
        for contenido in contenidos
    ]

    vectorizador = TfidfVectorizer(
        strip_accents="unicode",
        stop_words=PALABRAS_IGNORADAS_ACADEMICAS,
        ngram_range=(1, 2),
    )

    matriz_contenidos = vectorizador.fit_transform(
        documentos
    )

    vector_pregunta = vectorizador.transform(
        [pregunta]
    )

    similitudes = cosine_similarity(
        vector_pregunta,
        matriz_contenidos,
    )[0]

    indice_mejor_resultado = similitudes.argmax()
    confianza = float(
        similitudes[indice_mejor_resultado]
    )

    if confianza < UMBRAL_TEMA_ACADEMICO:
        return None, confianza

    return (
        contenidos[indice_mejor_resultado],
        confianza,
    )


def listar_temas_disponibles():
    contenidos = obtener_contenidos_academicos()

    lineas = ["Puedo ayudarte con estos temas:"]

    for contenido in contenidos:
        lineas.append(
            f"- {contenido['tema']} "
            f"({contenido['materia']})"
        )

    return "\n".join(lineas)


def responder_consulta_academica(pregunta):
    contenido, confianza = (
        buscar_contenido_academico(pregunta)
    )

    if contenido is None:
        respuesta = (
            "No identifiqué un tema académico "
            "específico.\n"
            f"{listar_temas_disponibles()}"
        )

        return respuesta, confianza, None

    lineas = [
        f"Tema: {contenido['tema']}",
        f"Materia: {contenido['materia']}",
        (
            "Semestre recomendado: "
            f"{contenido['semestre_recomendado']}.º"
        ),
        "",
        f"Explicación: {contenido['explicacion']}",
        "",
        f"Ejemplo: {contenido['ejemplo']}",
        "",
        f"Ejercicio: {contenido['ejercicio']}",
    ]

    respuesta = "\n".join(lineas)

    return respuesta, confianza, contenido["tema"]


if __name__ == "__main__":
    crear_base_datos()

    print("PRUEBA DEL MÓDULO ACADÉMICO")
    print("Escribe 'salir' para terminar.")

    while True:
        pregunta = input(
            "\nEscribe una consulta académica: "
        ).strip()

        if pregunta.casefold() == "salir":
            print("Hasta luego.")
            break

        respuesta, confianza, tema = (
            responder_consulta_academica(pregunta)
        )

        print(f"\nEduIA: {respuesta}")
        print(
            f"Confianza del tema: "
            f"{confianza:.0%}"
        )

        if tema is not None:
            print(f"Tema identificado: {tema}")