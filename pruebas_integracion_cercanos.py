from unittest.mock import patch

import eduia


ESTUDIANTE = {
    "matricula": "2026001",
    "semestre": 7,
}

RESULTADO_CERCANOS = {
    "categoria": "farmacia",
    "categoria_plural": "farmacias",
    "ubicacion": {
        "nombre": "Salamanca",
        "latitud": 20.571358,
        "longitud": -101.192444,
    },
    "radio_m": 5000,
    "lugares": [
        {
            "nombre": "FARMACIA ISSEG",
            "distancia_m": 2300,
            "direccion": None,
            "enlace": "https://www.openstreetmap.org/way/1217897894",
        }
    ],
    "fuente": "© OpenStreetMap contributors mediante Overpass API",
}


def probar_deteccion_de_lugares_cercanos():
    consultas = (
        "¿Qué hospitales hay cerca del Instituto Irapuato?",
        "Busca farmacias cerca de Salamanca, Guanajuato",
        "¿Hay cafeterías cerca de Plaza Cibeles?",
        "Muéstrame restaurantes cerca de aquí",
        "Bancos cercanos a Plaza Cibeles",
        "Escuelas alrededor de Salamanca",
        "¿Qué lugares cercanos hay?",
        "Busca paradas de autobuses cerca del Instituto Irapuato",
    )

    assert all(
        eduia.es_consulta_cercanos(consulta)
        for consulta in consultas
    )


def probar_consultas_ajenas_no_son_cercanos():
    consultas = (
        "¿Dónde está la cafetería?",
        "¿Dónde está la biblioteca?",
        "¿Cómo está el clima en Salamanca?",
        "Muéstrame la ruta de Salamanca a Irapuato",
        "Busca en Wikipedia qué es OpenStreetMap",
        "¿Cuál es mi horario?",
    )

    assert not any(
        eduia.es_consulta_cercanos(consulta)
        for consulta in consultas
    )


def probar_extraccion_de_categoria():
    casos = {
        "Hospitales cerca del Instituto Irapuato": "hospital",
        "Busca farmacias cerca de Salamanca": "farmacia",
        "Cafés cercanos a Plaza Cibeles": "cafeteria",
        "Cajeros automáticos alrededor de Irapuato": "cajero",
        "Paradas de camión cerca de aquí": "parada_autobus",
        "Paradas de autobuses cerca del Instituto Irapuato": "parada_autobus",
    }

    for consulta, categoria in casos.items():
        assert (
            eduia.extraer_categoria_cercanos(consulta)
            == categoria
        )


def probar_extraccion_de_ubicacion():
    casos = {
        "Hospitales cerca del Instituto Irapuato": "Instituto Irapuato",
        "Farmacias cerca de Salamanca, Guanajuato": "Salamanca, Guanajuato",
        "Cafeterías cercanas a Plaza Cibeles": "Plaza Cibeles",
        "Escuelas alrededor de León, Guanajuato": "León, Guanajuato",
        "Restaurantes cerca de aquí": "Irapuato",
    }

    for consulta, ubicacion in casos.items():
        assert (
            eduia.extraer_ubicacion_cercanos(consulta)
            == ubicacion
        )


def probar_procesamiento_de_lugares_cercanos():
    contexto = eduia.crear_contexto_conversacional()

    with (
        patch.object(
            eduia,
            "buscar_cerca_de",
            return_value=RESULTADO_CERCANOS,
        ) as buscar,
        patch.object(
            eduia,
            "formatear_resultado_cercanos",
            return_value="Farmacias encontradas",
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=301,
        ) as guardar,
    ):
        resultado = eduia.procesar_consulta_cercanos(
            "Busca farmacias cerca de Salamanca, Guanajuato",
            ESTUDIANTE,
            contexto,
        )

    buscar.assert_called_once_with(
        "farmacia",
        "Salamanca, Guanajuato",
    )
    assert resultado == (
        "Farmacias encontradas",
        "externa",
        "cercanos",
        1.0,
        301,
    )
    assert contexto["ultima_categoria"] == "cercanos"
    assert contexto["ultima_intencion"] == "cercanos"
    assert contexto["ultimo_tema"] == "farmacias cerca de Salamanca"
    guardar.assert_called_once()


def probar_historial_de_lugares_cercanos():
    pregunta = "Farmacias cerca de Salamanca"

    with (
        patch.object(
            eduia,
            "buscar_cerca_de",
            return_value=RESULTADO_CERCANOS,
        ),
        patch.object(
            eduia,
            "formatear_resultado_cercanos",
            return_value="Farmacias encontradas",
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=302,
        ) as guardar,
    ):
        resultado = eduia.procesar_consulta_cercanos(
            pregunta,
            ESTUDIANTE,
        )

    assert guardar.call_args.args == (
        "2026001",
        pregunta,
        "Farmacias encontradas",
        "externa",
        "cercanos",
        1.0,
    )
    assert resultado[-1] == 302


def probar_error_controlado_del_servicio():
    mensaje = "El servicio de lugares cercanos está ocupado."

    with (
        patch.object(
            eduia,
            "buscar_cerca_de",
            side_effect=eduia.ErrorConsultaCercanos(mensaje),
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=303,
        ),
    ):
        resultado = eduia.procesar_consulta_cercanos(
            "Hospitales cerca del Instituto Irapuato",
            ESTUDIANTE,
        )

    assert resultado == (
        mensaje,
        "externa",
        "cercanos",
        0.0,
        303,
    )


def probar_solicitud_sin_categoria():
    with (
        patch.object(eduia, "buscar_cerca_de") as buscar,
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=304,
        ),
    ):
        resultado = eduia.procesar_consulta_cercanos(
            "¿Qué lugares cercanos hay?",
            ESTUDIANTE,
        )

    buscar.assert_not_called()
    assert "qué tipo de lugar" in resultado[0]
    assert resultado[1:4] == (
        "externa",
        "cercanos",
        0.0,
    )


def probar_solicitud_sin_ubicacion():
    with (
        patch.object(eduia, "buscar_cerca_de") as buscar,
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=305,
        ),
    ):
        resultado = eduia.procesar_consulta_cercanos(
            "Busca hospitales cercanos",
            ESTUDIANTE,
        )

    buscar.assert_not_called()
    assert "cerca de qué lugar" in resultado[0]
    assert resultado[3] == 0.0


def probar_formato_del_modulo_independiente():
    texto = eduia.formatear_resultado_cercanos(
        RESULTADO_CERCANOS
    )

    assert texto.startswith("Farmacias cerca de Salamanca")
    assert "1. FARMACIA ISSEG (2.3 km)" in texto
    assert "Fuente: © OpenStreetMap contributors" in texto
    assert "distancias son aproximadas" in texto


PRUEBAS = [
    ("Detecta preguntas naturales de lugares cercanos", probar_deteccion_de_lugares_cercanos),
    ("Mantiene consultas ajenas fuera de lugares cercanos", probar_consultas_ajenas_no_son_cercanos),
    ("Extrae correctamente las categorías", probar_extraccion_de_categoria),
    ("Extrae correctamente las ubicaciones", probar_extraccion_de_ubicacion),
    ("Procesa y clasifica lugares cercanos", probar_procesamiento_de_lugares_cercanos),
    ("Guarda la búsqueda en el historial", probar_historial_de_lugares_cercanos),
    ("Controla errores del servicio", probar_error_controlado_del_servicio),
    ("Solicita una categoría cuando falta", probar_solicitud_sin_categoria),
    ("Solicita una ubicación cuando falta", probar_solicitud_sin_ubicacion),
    ("Conserva el formato del módulo", probar_formato_del_modulo_independiente),
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
    print("RESUMEN DE INTEGRACIÓN DE LUGARES CERCANOS")
    print("=" * 70)
    print(f"Total de pruebas: {len(PRUEBAS)}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {len(errores)}")
    print(f"Precisión: {correctas / len(PRUEBAS):.2%}")

    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
