from unittest.mock import patch

import eduia


ESTUDIANTE = {
    "matricula": "2026001",
    "semestre": 7,
}


def probar_deteccion_de_ordenes():
    consultas = (
        "Busca en Internet protocolo CAN",
        "Busca en Wikipedia qué es Arduino",
        "Buscar información sobre redes neuronales",
        "Investiga en Internet sistemas embebidos",
        "Investiga sobre inteligencia artificial",
        "Consulta en Wikipedia arquitectura de computadoras",
        "Dame información de Wikipedia sobre álgebra lineal",
    )

    assert all(
        eduia.es_consulta_internet(consulta)
        for consulta in consultas
    )


def probar_consultas_locales_no_activan_internet():
    consultas = (
        "¿Cuáles son mis calificaciones?",
        "¿Dónde está la biblioteca?",
        "¿Qué es el protocolo CAN?",
        "Busca mis calificaciones",
        "¿Qué clima habrá mañana?",
    )

    assert not any(
        eduia.es_consulta_internet(consulta)
        for consulta in consultas
    )


def probar_deteccion_sin_acentos_y_mayusculas():
    assert eduia.es_consulta_internet(
        "CONSULTA EN WIKIPEDIA QUÉ ES UN RTOS"
    )
    assert eduia.es_consulta_internet(
        "busca informacion sobre arduino"
    )


def probar_extraccion_del_tema():
    casos = {
        "Busca en Wikipedia qué es Protocolo CAN?": (
            "protocolo can"
        ),
        "Busca información sobre redes neuronales": (
            "redes neuronales"
        ),
        "Investiga en Internet quién es Alan Turing": (
            "alan turing"
        ),
        "Consulta en Wikipedia acerca de Arduino Uno": (
            "arduino uno"
        ),
    }

    for consulta, esperado in casos.items():
        assert (
            eduia.extraer_tema_busqueda(consulta)
            == esperado
        )


def probar_procesamiento_correcto():
    contexto = eduia.crear_contexto_conversacional()
    resultado_wikipedia = {
        "titulo": "Bus CAN",
        "resumen": "CAN es un protocolo de comunicación.",
        "enlace": "https://es.wikipedia.org/wiki/Bus_CAN",
    }

    with (
        patch.object(
            eduia,
            "buscar_en_wikipedia",
            return_value=resultado_wikipedia,
        ) as buscar,
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=81,
        ) as guardar,
    ):
        resultado = eduia.procesar_consulta_internet(
            "Busca en Wikipedia protocolo CAN",
            ESTUDIANTE,
            contexto,
        )

    respuesta, tipo, categoria, confianza, historial_id = resultado

    buscar.assert_called_once_with("protocolo can")
    assert respuesta.startswith("Bus CAN\n\n")
    assert "Fuente: Wikipedia" in respuesta
    assert tipo == "externa"
    assert categoria == "internet"
    assert confianza == 1.0
    assert historial_id == 81
    assert contexto["ultima_categoria"] == "internet"
    assert contexto["ultimo_tema"] == "Bus CAN"
    assert contexto["ultima_intencion"] == "busqueda"
    guardar.assert_called_once()


def probar_datos_guardados_en_historial():
    with (
        patch.object(
            eduia,
            "buscar_en_wikipedia",
            return_value={
                "titulo": "Arduino",
                "resumen": "Arduino es una plataforma.",
                "enlace": "https://es.wikipedia.org/wiki/Arduino",
            },
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=82,
        ) as guardar,
    ):
        resultado = eduia.procesar_consulta_internet(
            "Investiga sobre Arduino",
            ESTUDIANTE,
        )

    argumentos = guardar.call_args.args
    assert argumentos[0] == "2026001"
    assert argumentos[1] == "Investiga sobre Arduino"
    assert "Arduino es una plataforma" in argumentos[2]
    assert argumentos[3:] == (
        "externa",
        "internet",
        1.0,
    )
    assert resultado[-1] == 82


def probar_error_controlado():
    contexto = eduia.crear_contexto_conversacional()
    mensaje = (
        "No fue posible consultar Wikipedia. "
        "Revisa tu conexión a Internet."
    )

    with (
        patch.object(
            eduia,
            "buscar_en_wikipedia",
            side_effect=eduia.ErrorConsultaInternet(
                mensaje
            ),
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=83,
        ) as guardar,
    ):
        resultado = eduia.procesar_consulta_internet(
            "Busca en Internet Arduino",
            ESTUDIANTE,
            contexto,
        )

    assert resultado == (
        mensaje,
        "externa",
        "internet",
        0.0,
        83,
    )
    assert contexto["ultima_categoria"] is None
    assert contexto["ultima_pregunta"] == (
        "Busca en Internet Arduino"
    )
    guardar.assert_called_once()


def probar_tema_faltante():
    consulta = "Busca en Wikipedia "

    assert eduia.es_consulta_internet(consulta)
    assert eduia.extraer_tema_busqueda(consulta) == ""

    with (
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=84,
        ),
        patch.object(
            eduia,
            "buscar_en_wikipedia",
            side_effect=eduia.ErrorConsultaInternet(
                "Indica el tema que deseas buscar."
            ),
        ) as buscar,
    ):
        resultado = eduia.procesar_consulta_internet(
            consulta,
            ESTUDIANTE,
        )

    buscar.assert_called_once_with("")
    assert resultado[0] == (
        "Indica el tema que deseas buscar."
    )
    assert resultado[3] == 0.0


PRUEBAS = [
    (
        "Detecta órdenes explícitas de búsqueda",
        probar_deteccion_de_ordenes,
    ),
    (
        "Mantiene las consultas locales fuera de Internet",
        probar_consultas_locales_no_activan_internet,
    ),
    (
        "Tolera mayúsculas y acentos",
        probar_deteccion_sin_acentos_y_mayusculas,
    ),
    (
        "Extrae correctamente el tema",
        probar_extraccion_del_tema,
    ),
    (
        "Procesa y clasifica la respuesta externa",
        probar_procesamiento_correcto,
    ),
    (
        "Guarda la búsqueda en el historial",
        probar_datos_guardados_en_historial,
    ),
    (
        "Controla errores de conexión",
        probar_error_controlado,
    ),
    (
        "Solicita el tema cuando está ausente",
        probar_tema_faltante,
    ),
]


def main():
    correctas = 0
    errores = []

    for nombre, prueba in PRUEBAS:
        try:
            prueba()
            correctas += 1
            print(f"[CORRECTA] {nombre}")
        except Exception as error:
            errores.append((nombre, error))
            print(f"[ERROR] {nombre}: {error}")

    print("\n" + "=" * 70)
    print("RESUMEN DE INTEGRACIÓN CON WIKIPEDIA")
    print("=" * 70)
    print(f"Total de pruebas: {len(PRUEBAS)}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {len(errores)}")
    print(
        "Precisión: "
        f"{correctas / len(PRUEBAS):.2%}"
    )

    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
