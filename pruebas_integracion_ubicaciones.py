from unittest.mock import patch

import eduia


ESTUDIANTE = {
    "matricula": "2026001",
    "semestre": 7,
}


LUGAR = {
    "nombre": "Instituto Irapuato",
    "direccion_completa": (
        "Instituto Irapuato, Irapuato, "
        "Guanajuato, México"
    ),
    "latitud": 20.67025,
    "longitud": -101.37516,
    "estado": "Guanajuato",
    "pais": "México",
    "enlace": (
        "https://www.openstreetmap.org/way/610291911"
    ),
}


PRONOSTICO = {
    "actual": {
        "codigo": 1,
        "temperatura": 23.5,
        "sensacion_termica": 24.1,
        "humedad": 60,
        "precipitacion": 0.0,
        "viento": 4.2,
    },
    "pronostico": [
        {
            "fecha": "2026-09-04",
            "codigo": 1,
            "temperatura_maxima": 27.0,
            "temperatura_minima": 14.0,
            "probabilidad_lluvia": 20,
            "precipitacion": 0.0,
        },
        {
            "fecha": "2026-09-05",
            "codigo": 61,
            "temperatura_maxima": 26.0,
            "temperatura_minima": 15.0,
            "probabilidad_lluvia": 70,
            "precipitacion": 4.0,
        },
    ],
    "zona_horaria": "America/Mexico_City",
}


def probar_deteccion_de_ubicaciones():
    consultas = (
        "¿Dónde está el Instituto Irapuato?",
        "¿Dónde queda Plaza Cibeles?",
        "¿Cuáles son las coordenadas de Plaza Cibeles?",
        "Dirección de Instituto Irapuato",
        "Ubica Plaza Cibeles",
        "Localiza el Centro Histórico de León",
        "Busca Centro Histórico en León, Guanajuato",
    )

    assert all(
        eduia.es_consulta_ubicacion(consulta)
        for consulta in consultas
    )


def probar_consultas_escolares_no_salen_a_osm():
    consultas = (
        "¿Dónde está la biblioteca?",
        "¿Dónde se encuentra la cafetería?",
        "¿Dónde queda el laboratorio?",
        "¿Dónde está mi salón?",
        "¿Cuál es mi horario?",
        "Busca en Wikipedia qué es OpenStreetMap",
    )

    assert not any(
        eduia.es_consulta_ubicacion(consulta)
        for consulta in consultas
    )


def probar_extraccion_de_lugares():
    casos = {
        "¿Dónde está el Instituto Irapuato?": (
            "Instituto Irapuato"
        ),
        "¿Dónde queda Plaza Cibeles?": "Plaza Cibeles",
        "¿Cuáles son las coordenadas de Plaza Cibeles?": (
            "Plaza Cibeles"
        ),
        "Dirección de Instituto Irapuato": (
            "Instituto Irapuato"
        ),
        "Ubica la Plaza Cibeles": "Plaza Cibeles",
        "Busca Centro Histórico en León, Guanajuato": (
            "Centro Histórico, León, Guanajuato"
        ),
    }

    for consulta, esperado in casos.items():
        assert (
            eduia.extraer_busqueda_ubicacion(consulta)
            == esperado
        )


def probar_procesamiento_de_ubicacion():
    contexto = eduia.crear_contexto_conversacional()

    with (
        patch.object(
            eduia,
            "buscar_ubicacion",
            return_value=LUGAR,
        ) as buscar,
        patch.object(
            eduia,
            "formatear_resultado_ubicacion",
            return_value=(
                "Instituto Irapuato\n\n"
                "Fuente: © OpenStreetMap contributors"
            ),
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=101,
        ) as guardar,
    ):
        resultado = eduia.procesar_consulta_ubicacion(
            "¿Dónde está el Instituto Irapuato?",
            ESTUDIANTE,
            contexto,
        )

    buscar.assert_called_once_with("Instituto Irapuato")
    assert resultado == (
        (
            "Instituto Irapuato\n\n"
            "Fuente: © OpenStreetMap contributors"
        ),
        "externa",
        "ubicacion",
        1.0,
        101,
    )
    assert contexto["ultima_categoria"] == "ubicacion"
    assert contexto["ultimo_tema"] == "Instituto Irapuato"
    assert contexto["ultima_intencion"] == "ubicacion"
    guardar.assert_called_once()


def probar_historial_de_ubicacion():
    with (
        patch.object(
            eduia,
            "buscar_ubicacion",
            return_value=LUGAR,
        ),
        patch.object(
            eduia,
            "formatear_resultado_ubicacion",
            return_value="Ubicación encontrada",
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=102,
        ) as guardar,
    ):
        resultado = eduia.procesar_consulta_ubicacion(
            "Ubica el Instituto Irapuato",
            ESTUDIANTE,
        )

    assert guardar.call_args.args == (
        "2026001",
        "Ubica el Instituto Irapuato",
        "Ubicación encontrada",
        "externa",
        "ubicacion",
        1.0,
    )
    assert resultado[-1] == 102


def probar_error_controlado_de_ubicacion():
    mensaje = "No encontré la ubicación solicitada."

    with (
        patch.object(
            eduia,
            "buscar_ubicacion",
            side_effect=eduia.ErrorConsultaUbicacion(
                mensaje
            ),
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=103,
        ),
    ):
        resultado = eduia.procesar_consulta_ubicacion(
            "Ubica un lugar inexistente",
            ESTUDIANTE,
        )

    assert resultado == (
        mensaje,
        "externa",
        "ubicacion",
        0.0,
        103,
    )


def probar_ciudad_conserva_geocodificacion_climatica():
    resultado_esperado = {
        "ubicacion": {"nombre": "Salamanca"},
        "actual": {},
        "pronostico": [],
    }

    with (
        patch.object(
            eduia,
            "consultar_clima",
            return_value=resultado_esperado,
        ) as consultar,
        patch.object(
            eduia,
            "buscar_ubicacion",
        ) as buscar,
    ):
        resultado = eduia.consultar_clima_de_ubicacion(
            "Salamanca"
        )

    consultar.assert_called_once_with(
        "Salamanca",
        dias=3,
    )
    buscar.assert_not_called()
    assert resultado is resultado_esperado


def probar_lugar_utiliza_coordenadas_exactas():
    with (
        patch.object(
            eduia,
            "buscar_ubicacion",
            return_value=LUGAR,
        ) as buscar,
        patch.object(
            eduia,
            "consultar_pronostico",
            return_value=PRONOSTICO,
        ) as pronostico,
    ):
        resultado = eduia.consultar_clima_de_ubicacion(
            "Instituto Irapuato"
        )

    buscar.assert_called_once_with("Instituto Irapuato")
    pronostico.assert_called_once_with(
        20.67025,
        -101.37516,
        dias=3,
    )
    assert resultado["ubicacion"]["nombre"] == (
        "Instituto Irapuato"
    )
    assert "OpenStreetMap contributors" in resultado["fuente"]
    assert LUGAR["enlace"] in resultado["enlace"]


def probar_pregunta_climatica_de_lugar():
    pregunta = (
        "¿Cómo está el clima en el Instituto Irapuato?"
    )

    assert eduia.es_consulta_clima(pregunta)
    assert eduia.extraer_ubicacion_clima(pregunta) == (
        "Instituto Irapuato"
    )
    assert eduia.es_lugar_especifico_clima(
        "Instituto Irapuato"
    )


def probar_error_osm_durante_consulta_climatica():
    mensaje = "No fue posible consultar OpenStreetMap."

    with (
        patch.object(
            eduia,
            "buscar_ubicacion",
            side_effect=eduia.ErrorConsultaUbicacion(
                mensaje
            ),
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=104,
        ),
    ):
        resultado = eduia.procesar_consulta_clima(
            "¿Cómo está el clima en el Instituto Irapuato?",
            ESTUDIANTE,
        )

    assert resultado == (
        mensaje,
        "externa",
        "clima",
        0.0,
        104,
    )


PRUEBAS = [
    (
        "Detecta preguntas de ubicación",
        probar_deteccion_de_ubicaciones,
    ),
    (
        "Conserva ubicaciones escolares locales",
        probar_consultas_escolares_no_salen_a_osm,
    ),
    (
        "Extrae correctamente los lugares",
        probar_extraccion_de_lugares,
    ),
    (
        "Procesa y clasifica ubicaciones externas",
        probar_procesamiento_de_ubicacion,
    ),
    (
        "Guarda ubicaciones en el historial",
        probar_historial_de_ubicacion,
    ),
    (
        "Controla errores de ubicación",
        probar_error_controlado_de_ubicacion,
    ),
    (
        "Conserva el clima normal de ciudades",
        probar_ciudad_conserva_geocodificacion_climatica,
    ),
    (
        "Usa coordenadas exactas para lugares",
        probar_lugar_utiliza_coordenadas_exactas,
    ),
    (
        "Reconoce el clima de un lugar específico",
        probar_pregunta_climatica_de_lugar,
    ),
    (
        "Controla fallos de ubicación al consultar clima",
        probar_error_osm_durante_consulta_climatica,
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
    print("RESUMEN DE INTEGRACIÓN DE UBICACIONES")
    print("=" * 70)
    print(f"Total de pruebas: {len(PRUEBAS)}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {len(errores)}")
    print(f"Precisión: {correctas / len(PRUEBAS):.2%}")

    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
