from unittest.mock import patch

import eduia


ESTUDIANTE = {
    "matricula": "2026001",
    "semestre": 7,
}


RESULTADO_CLIMA = {
    "ubicacion": {
        "nombre": "Salamanca",
        "estado": "Estado de Guanajuato",
        "pais": "México",
        "latitud": 20.57,
        "longitud": -101.19,
    },
    "actual": {
        "codigo": 1,
        "temperatura": 23.4,
        "sensacion_termica": 24.0,
        "humedad": 65,
        "precipitacion": 0.0,
        "viento": 6.2,
    },
    "pronostico": [
        {
            "fecha": "2026-09-04",
            "codigo": 1,
            "temperatura_maxima": 28.0,
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
    "fuente": "Open-Meteo",
    "enlace": "https://open-meteo.com/",
}


def probar_deteccion_de_consultas_climaticas():
    consultas = (
        "¿Cómo está el clima en Irapuato?",
        "¿Qué clima habrá mañana en Salamanca?",
        "Dame el pronóstico de Celaya",
        "¿Cuál es la temperatura en León?",
        "¿Lloverá mañana en Irapuato?",
        "¿Va a llover en Salamanca?",
        "¿Habrá lluvia en Celaya?",
        "Probabilidad de lluvia en León",
    )

    assert all(
        eduia.es_consulta_clima(consulta)
        for consulta in consultas
    )


def probar_consultas_ajenas_no_activan_clima():
    consultas = (
        "¿Cuál es mi horario?",
        "¿Cuáles son mis calificaciones?",
        "¿Qué es el clima?",
        "Temperatura del procesador",
        "Busca en Wikipedia qué es el clima",
        "Marvel",
    )

    assert not any(
        eduia.es_consulta_clima(consulta)
        for consulta in consultas
    )


def probar_extraccion_de_ubicaciones():
    casos = {
        "¿Cómo está el clima en Irapuato?": "Irapuato",
        "¿Lloverá mañana en Salamanca?": "Salamanca",
        "Dame el pronóstico de Celaya": "Celaya",
        "Temperatura para León": "León",
        "Clima en Silao mañana": "Silao",
    }

    for consulta, esperado in casos.items():
        assert (
            eduia.extraer_ubicacion_clima(consulta)
            == esperado
        )


def probar_ubicacion_predeterminada():
    consultas = (
        "¿Cómo está el clima?",
        "¿Lloverá mañana?",
        "Dame el pronóstico de mañana",
    )

    assert all(
        eduia.extraer_ubicacion_clima(consulta)
        == "Irapuato"
        for consulta in consultas
    )


def probar_procesamiento_correcto():
    contexto = eduia.crear_contexto_conversacional()

    with (
        patch.object(
            eduia,
            "consultar_clima",
            return_value=RESULTADO_CLIMA,
        ) as consultar,
        patch.object(
            eduia,
            "formatear_resultado_clima",
            return_value="Clima en Salamanca\n\nFuente: Open-Meteo",
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=91,
        ) as guardar,
    ):
        resultado = eduia.procesar_consulta_clima(
            "¿Cómo está el clima en Salamanca?",
            ESTUDIANTE,
            contexto,
        )

    consultar.assert_called_once_with(
        "Salamanca",
        dias=3,
    )
    assert resultado == (
        "Clima en Salamanca\n\nFuente: Open-Meteo",
        "externa",
        "clima",
        1.0,
        91,
    )
    assert contexto["ultima_categoria"] == "clima"
    assert contexto["ultimo_tema"] == "Salamanca"
    assert contexto["ultima_intencion"] == "clima"
    guardar.assert_called_once()


def probar_datos_guardados_en_historial():
    with (
        patch.object(
            eduia,
            "consultar_clima",
            return_value=RESULTADO_CLIMA,
        ),
        patch.object(
            eduia,
            "formatear_resultado_clima",
            return_value="Pronóstico de Salamanca",
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=92,
        ) as guardar,
    ):
        resultado = eduia.procesar_consulta_clima(
            "¿Lloverá mañana en Salamanca?",
            ESTUDIANTE,
        )

    assert guardar.call_args.args == (
        "2026001",
        "¿Lloverá mañana en Salamanca?",
        "Pronóstico de Salamanca",
        "externa",
        "clima",
        1.0,
    )
    assert resultado[-1] == 92


def probar_error_controlado():
    contexto = eduia.crear_contexto_conversacional()
    mensaje = (
        "No fue posible consultar el clima. "
        "Revisa tu conexión a Internet."
    )

    with (
        patch.object(
            eduia,
            "consultar_clima",
            side_effect=eduia.ErrorConsultaClima(
                mensaje
            ),
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=93,
        ) as guardar,
    ):
        resultado = eduia.procesar_consulta_clima(
            "¿Cómo está el clima en Irapuato?",
            ESTUDIANTE,
            contexto,
        )

    assert resultado == (
        mensaje,
        "externa",
        "clima",
        0.0,
        93,
    )
    assert contexto["ultima_categoria"] is None
    assert contexto["ultima_pregunta"] == (
        "¿Cómo está el clima en Irapuato?"
    )
    guardar.assert_called_once()


def probar_formateo_real_del_modulo():
    texto = eduia.formatear_resultado_clima(
        RESULTADO_CLIMA
    )

    assert texto.startswith(
        "Clima en Salamanca, Estado de Guanajuato, México"
    )
    assert "Temperatura: 23.4 °C" in texto
    assert "Mañana: lluvia ligera" in texto
    assert "Fuente: Open-Meteo" in texto


PRUEBAS = [
    (
        "Detecta preguntas naturales del clima",
        probar_deteccion_de_consultas_climaticas,
    ),
    (
        "Mantiene consultas ajenas fuera del clima",
        probar_consultas_ajenas_no_activan_clima,
    ),
    (
        "Extrae correctamente las ciudades",
        probar_extraccion_de_ubicaciones,
    ),
    (
        "Usa Irapuato como ubicación predeterminada",
        probar_ubicacion_predeterminada,
    ),
    (
        "Procesa y clasifica la respuesta del clima",
        probar_procesamiento_correcto,
    ),
    (
        "Guarda la consulta climática en el historial",
        probar_datos_guardados_en_historial,
    ),
    (
        "Controla errores de conexión",
        probar_error_controlado,
    ),
    (
        "Conserva el formato del módulo independiente",
        probar_formateo_real_del_modulo,
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
    print("RESUMEN DE INTEGRACIÓN DEL CLIMA")
    print("=" * 70)
    print(f"Total de pruebas: {len(PRUEBAS)}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {len(errores)}")
    print(f"Precisión: {correctas / len(PRUEBAS):.2%}")

    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
