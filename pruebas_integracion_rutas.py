from unittest.mock import patch

import eduia


ESTUDIANTE = {
    "matricula": "2026001",
    "semestre": 7,
}
RESULTADO_RUTA = {
    "origen": {
        "nombre": "Instituto Irapuato",
        "latitud": 20.67025,
        "longitud": -101.37516,
    },
    "destino": {
        "nombre": "Plaza Cibeles",
        "latitud": 20.680538,
        "longitud": -101.380945,
    },
    "perfil": "driving",
    "distancia_km": 2.4,
    "duracion_min": 5,
    "instrucciones": [],
    "fuente": "OSRM y © OpenStreetMap contributors",
    "enlace": "https://www.openstreetmap.org/directions",
}


def probar_deteccion_de_rutas():
    consultas = (
        "¿Cómo llego del Instituto Irapuato a Plaza Cibeles?",
        "¿Cómo llegar desde Salamanca hasta Instituto Irapuato?",
        "Dame la ruta desde Plaza Cibeles hasta el Instituto Irapuato",
        "Muéstrame la ruta de Irapuato a Salamanca",
        "Ruta de Salamanca a Irapuato",
        "Ruta entre Salamanca y Irapuato",
        "Distancia entre Salamanca y Irapuato",
        "Distancia entre Salamanca e Irapuato",
        "¿Cuánto hay de Salamanca al Instituto Irapuato?",
        "¿Cuánto se tarda de Salamanca a Irapuato?",
        "Origen Salamanca y el destino Irapuato",
    )

    assert all(
        eduia.es_consulta_ruta(consulta)
        for consulta in consultas
    )


def probar_consultas_ajenas_no_son_rutas():
    consultas = (
        "¿Cuánto cuesta un taco?",
        "¿Cómo está el clima en Salamanca?",
        "¿Dónde está el Instituto Irapuato?",
        "Busca en Wikipedia qué es OSRM",
        "¿Cuál es mi horario?",
    )

    assert not any(
        eduia.es_consulta_ruta(consulta)
        for consulta in consultas
    )


def probar_extraccion_de_origen_y_destino():
    casos = {
        "¿Cómo llego del Instituto Irapuato a Plaza Cibeles?": (
            "Instituto Irapuato",
            "Plaza Cibeles",
        ),
        "¿Cómo llegar desde Salamanca, Guanajuato hasta Instituto Irapuato?": (
            "Salamanca, Guanajuato",
            "Instituto Irapuato",
        ),
        "Dame la ruta desde Plaza Cibeles hasta el Instituto Irapuato": (
            "Plaza Cibeles",
            "Instituto Irapuato",
        ),
        "¿Cuánto hay de Salamanca al Instituto Irapuato?": (
            "Salamanca",
            "Instituto Irapuato",
        ),
        "Distancia entre Salamanca y Irapuato": (
            "Salamanca",
            "Irapuato",
        ),
        "Distancia entre Salamanca e Irapuato": (
            "Salamanca",
            "Irapuato",
        ),
        "Muéstrame la ruta de Irapuato a Salamanca": (
            "Irapuato",
            "Salamanca",
        ),
        "Origen Salamanca y el destino Irapuato": (
            "Salamanca",
            "Irapuato",
        ),
    }

    for consulta, esperado in casos.items():
        assert eduia.extraer_lugares_ruta(consulta) == esperado


def probar_procesamiento_de_ruta():
    contexto = eduia.crear_contexto_conversacional()

    with (
        patch.object(
            eduia,
            "calcular_ruta",
            return_value=RESULTADO_RUTA,
        ) as calcular,
        patch.object(
            eduia,
            "formatear_resultado_ruta",
            return_value="Ruta encontrada",
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=201,
        ) as guardar,
    ):
        resultado = eduia.procesar_consulta_ruta(
            "¿Cómo llego del Instituto Irapuato a Plaza Cibeles?",
            ESTUDIANTE,
            contexto,
        )

    calcular.assert_called_once_with(
        "Instituto Irapuato",
        "Plaza Cibeles",
    )
    assert resultado == (
        "Ruta encontrada",
        "externa",
        "ruta",
        1.0,
        201,
    )
    assert contexto["ultima_categoria"] == "ruta"
    assert contexto["ultima_intencion"] == "ruta"
    assert contexto["ultimo_tema"] == (
        "Instituto Irapuato a Plaza Cibeles"
    )
    guardar.assert_called_once()


def probar_historial_de_ruta():
    pregunta = "Ruta de Salamanca a Irapuato"

    with (
        patch.object(
            eduia,
            "calcular_ruta",
            return_value=RESULTADO_RUTA,
        ),
        patch.object(
            eduia,
            "formatear_resultado_ruta",
            return_value="Ruta encontrada",
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=202,
        ) as guardar,
    ):
        resultado = eduia.procesar_consulta_ruta(
            pregunta,
            ESTUDIANTE,
        )

    assert guardar.call_args.args == (
        "2026001",
        pregunta,
        "Ruta encontrada",
        "externa",
        "ruta",
        1.0,
    )
    assert resultado[-1] == 202


def probar_error_controlado_de_ruta():
    mensaje = "No encontré una ruta por carretera."

    with (
        patch.object(
            eduia,
            "calcular_ruta",
            side_effect=eduia.ErrorConsultaRuta(mensaje),
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=203,
        ),
    ):
        resultado = eduia.procesar_consulta_ruta(
            "Ruta de Origen a Destino",
            ESTUDIANTE,
        )

    assert resultado == (
        mensaje,
        "externa",
        "ruta",
        0.0,
        203,
    )


def probar_solicitud_incompleta():
    with (
        patch.object(eduia, "calcular_ruta") as calcular,
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=204,
        ),
    ):
        resultado = eduia.procesar_consulta_ruta(
            "Dame la ruta",
            ESTUDIANTE,
        )

    calcular.assert_not_called()
    assert "origen y el destino" in resultado[0]
    assert resultado[1:4] == (
        "externa",
        "ruta",
        0.0,
    )


def probar_formato_del_modulo_independiente():
    texto = eduia.formatear_resultado_ruta(RESULTADO_RUTA)

    assert texto.startswith(
        "Ruta de Instituto Irapuato a Plaza Cibeles"
    )
    assert "Distancia por carretera: 2.4 km" in texto
    assert "Duración aproximada: 5 min" in texto
    assert "Fuente: OSRM y © OpenStreetMap contributors" in texto


PRUEBAS = [
    ("Detecta preguntas naturales de rutas", probar_deteccion_de_rutas),
    ("Mantiene consultas ajenas fuera de rutas", probar_consultas_ajenas_no_son_rutas),
    ("Extrae origen y destino", probar_extraccion_de_origen_y_destino),
    ("Procesa y clasifica la ruta", probar_procesamiento_de_ruta),
    ("Guarda la ruta en el historial", probar_historial_de_ruta),
    ("Controla errores del servicio", probar_error_controlado_de_ruta),
    ("Solicita origen y destino cuando faltan", probar_solicitud_incompleta),
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
    print("RESUMEN DE INTEGRACIÓN DE RUTAS")
    print("=" * 70)
    print(f"Total de pruebas: {len(PRUEBAS)}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {len(errores)}")
    print(f"Precisión: {correctas / len(PRUEBAS):.2%}")

    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
