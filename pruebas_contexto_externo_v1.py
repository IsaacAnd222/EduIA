from unittest.mock import patch

import eduia


ESTUDIANTE = {
    "matricula": "2026001",
    "semestre": 7,
}

REFERENCIA = {
    "nombre": "Instituto Irapuato",
    "latitud": 20.67025,
    "longitud": -101.37516,
    "enlace": "https://www.openstreetmap.org/way/610291911",
}

LUGARES = [
    {
        "nombre": "ISSSTE",
        "latitud": 20.685,
        "longitud": -101.37,
        "distancia_m": 2100,
        "direccion": "Irapuato, Guanajuato",
        "enlace": "https://www.openstreetmap.org/way/591424763",
    },
    {
        "nombre": "IMSS",
        "latitud": 20.69,
        "longitud": -101.36,
        "distancia_m": 2400,
        "direccion": None,
        "enlace": "https://www.openstreetmap.org/node/1719089047",
    },
]

RESULTADO_CERCANOS = {
    "categoria": "hospital",
    "categoria_plural": "hospitales",
    "ubicacion": REFERENCIA,
    "radio_m": 5000,
    "lugares": LUGARES,
    "fuente": "© OpenStreetMap contributors mediante Overpass API",
}

RESULTADO_RUTA = {
    "origen": REFERENCIA,
    "destino": LUGARES[0],
    "perfil": "driving",
    "distancia_km": 2.5,
    "duracion_min": 6,
    "instrucciones": [],
    "fuente": "OSRM y © OpenStreetMap contributors",
    "enlace": "https://www.openstreetmap.org/directions",
}


def crear_contexto_con_lugares():
    contexto = eduia.crear_contexto_conversacional()
    contexto["ultima_ubicacion_referencia"] = dict(REFERENCIA)
    contexto["ultimos_lugares_cercanos"] = [
        dict(lugar) for lugar in LUGARES
    ]
    contexto["ultima_categoria"] = "cercanos"
    contexto["ultima_intencion"] = "cercanos"
    return contexto


def probar_contexto_inicial_externo():
    contexto = eduia.crear_contexto_conversacional()

    assert contexto["ultima_ubicacion_referencia"] is None
    assert contexto["ultimos_lugares_cercanos"] == []
    assert contexto["ultimo_lugar_seleccionado"] is None
    assert contexto["ultima_ruta"] is None


def probar_guardado_de_resultados_cercanos():
    contexto = eduia.crear_contexto_conversacional()

    with (
        patch.object(
            eduia,
            "buscar_cerca_de",
            return_value=RESULTADO_CERCANOS,
        ),
        patch.object(
            eduia,
            "formatear_resultado_cercanos",
            return_value="Hospitales encontrados",
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=401,
        ),
    ):
        eduia.procesar_consulta_cercanos(
            "Hospitales cerca del Instituto Irapuato",
            ESTUDIANTE,
            contexto,
        )

    assert contexto["ultima_ubicacion_referencia"] == REFERENCIA
    assert contexto["ultimos_lugares_cercanos"] == LUGARES
    assert contexto["ultimo_lugar_seleccionado"] is None


def probar_referencias_ordinales():
    contexto = crear_contexto_con_lugares()

    assert eduia.resolver_lugar_externo_contextual(
        "¿Cómo llego al primero?", contexto
    )["nombre"] == "ISSSTE"
    assert eduia.resolver_lugar_externo_contextual(
        "¿Dónde está el segundo?", contexto
    )["nombre"] == "IMSS"
    assert eduia.resolver_lugar_externo_contextual(
        "Dame la ruta al más cercano", contexto
    )["nombre"] == "ISSSTE"
    assert eduia.resolver_lugar_externo_contextual(
        "¿Dónde está el último?", contexto
    )["nombre"] == "IMSS"


def probar_clasificacion_contextual():
    contexto = crear_contexto_con_lugares()

    assert eduia.clasificar_consulta_externa_contextual(
        "¿Cómo llego al primero?", contexto
    ) == "ruta"
    assert eduia.clasificar_consulta_externa_contextual(
        "¿Dónde está el segundo?", contexto
    ) == "ubicacion"
    assert eduia.clasificar_consulta_externa_contextual(
        "¿Cuál es mi horario?", contexto
    ) is None


def probar_ruta_al_primer_resultado():
    contexto = crear_contexto_con_lugares()

    with (
        patch.object(
            eduia,
            "consultar_ruta_coordenadas",
            return_value=RESULTADO_RUTA,
        ) as consultar,
        patch.object(
            eduia,
            "formatear_resultado_ruta",
            return_value="Ruta al ISSSTE",
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=402,
        ),
    ):
        resultado = eduia.procesar_consulta_ruta(
            "¿Cómo llego al primero?",
            ESTUDIANTE,
            contexto,
        )

    consultar.assert_called_once_with(REFERENCIA, LUGARES[0])
    assert resultado[:4] == (
        "Ruta al ISSSTE",
        "externa",
        "ruta",
        1.0,
    )
    assert contexto["ultimo_lugar_seleccionado"]["nombre"] == "ISSSTE"
    assert contexto["ultima_ruta"]["destino"]["nombre"] == "ISSSTE"


def probar_continuacion_de_ultima_ruta():
    contexto = crear_contexto_con_lugares()
    contexto["ultima_ruta"] = {
        "origen": dict(REFERENCIA),
        "destino": dict(LUGARES[0]),
    }

    with (
        patch.object(
            eduia,
            "consultar_ruta_coordenadas",
            return_value=RESULTADO_RUTA,
        ) as consultar,
        patch.object(
            eduia,
            "formatear_resultado_ruta",
            return_value="Duración aproximada: 6 min",
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=403,
        ),
    ):
        resultado = eduia.procesar_consulta_ruta(
            "¿Cuánto tiempo tardaría?",
            ESTUDIANTE,
            contexto,
        )

    consultar.assert_called_once()
    assert resultado[0] == "Duración aproximada: 6 min"


def probar_ubicacion_del_segundo_resultado():
    contexto = crear_contexto_con_lugares()

    with (
        patch.object(
            eduia,
            "formatear_resultado_ubicacion",
            return_value="Ubicación exacta del IMSS",
        ) as formatear,
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=404,
        ),
    ):
        resultado = eduia.procesar_consulta_ubicacion(
            "¿Dónde está el segundo?",
            ESTUDIANTE,
            contexto,
        )

    dato_formateado = formatear.call_args.args[0]
    assert dato_formateado["nombre"] == "IMSS"
    assert dato_formateado["latitud"] == LUGARES[1]["latitud"]
    assert dato_formateado["direccion_completa"].startswith("Cerca de")
    assert resultado[0] == "Ubicación exacta del IMSS"
    assert contexto["ultimo_lugar_seleccionado"]["nombre"] == "IMSS"


def probar_clima_en_lugar_seleccionado():
    contexto = crear_contexto_con_lugares()
    contexto["ultimo_lugar_seleccionado"] = dict(LUGARES[0])
    pronostico = {
        "actual": {},
        "pronostico": [],
    }

    with (
        patch.object(
            eduia,
            "consultar_pronostico",
            return_value=pronostico,
        ) as consultar,
        patch.object(
            eduia,
            "formatear_resultado_clima",
            return_value="Clima en ISSSTE",
        ),
        patch.object(
            eduia,
            "guardar_consulta_historial",
            return_value=405,
        ),
    ):
        resultado = eduia.procesar_consulta_clima(
            "¿Cómo está el clima ahí?",
            ESTUDIANTE,
            contexto,
        )

    consultar.assert_called_once_with(
        LUGARES[0]["latitud"],
        LUGARES[0]["longitud"],
        dias=3,
    )
    assert resultado[0] == "Clima en ISSSTE"


def probar_contexto_no_fuerza_otro_tema():
    contexto = crear_contexto_con_lugares()

    consultas = (
        "¿Cuál es mi horario?",
        "¿Cuánto cuesta un taco?",
        "Busca en Wikipedia qué es un hospital",
    )

    assert all(
        eduia.clasificar_consulta_externa_contextual(
            consulta,
            contexto,
        ) is None
        for consulta in consultas
    )


PRUEBAS = [
    ("Inicia vacía la memoria de servicios externos", probar_contexto_inicial_externo),
    ("Guarda los resultados de lugares cercanos", probar_guardado_de_resultados_cercanos),
    ("Resuelve referencias ordinales", probar_referencias_ordinales),
    ("Clasifica continuaciones contextuales", probar_clasificacion_contextual),
    ("Calcula una ruta al primer resultado", probar_ruta_al_primer_resultado),
    ("Continúa la última ruta", probar_continuacion_de_ultima_ruta),
    ("Ubica el segundo resultado", probar_ubicacion_del_segundo_resultado),
    ("Consulta el clima en el lugar seleccionado", probar_clima_en_lugar_seleccionado),
    ("No fuerza el contexto sobre otro tema", probar_contexto_no_fuerza_otro_tema),
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
    print("RESUMEN DE CONTEXTO ENTRE SERVICIOS EXTERNOS")
    print("=" * 70)
    print(f"Total de pruebas: {len(PRUEBAS)}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {len(errores)}")
    print(f"Precisión: {correctas / len(PRUEBAS):.2%}")

    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
