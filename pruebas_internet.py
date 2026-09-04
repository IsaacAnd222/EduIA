import json
from unittest.mock import MagicMock, patch
from urllib.error import URLError

import internet


def crear_respuesta_simulada(datos):
    respuesta = MagicMock()
    respuesta.__enter__.return_value = respuesta
    respuesta.__exit__.return_value = False

    return respuesta, patch.object(
        internet.json,
        "load",
        return_value=datos,
    )


def probar_url_codificada():
    url = internet.construir_url(
        "protocolo CAN"
    )

    assert url.startswith(
        "https://es.wikipedia.org/w/api.php?"
    )
    assert "gsrsearch=protocolo+CAN" in url
    assert "gsrlimit=1" in url
    assert "explaintext=1" in url


def probar_resumen_breve():
    resultado = internet.limitar_resumen(
        "Texto   breve.\nCon espacios."
    )

    assert resultado == (
        "Texto breve. Con espacios."
    )


def probar_resumen_largo_en_oracion():
    texto = (
        "Primera oración suficientemente larga. "
        "Segunda oración que supera el límite."
    )
    resultado = internet.limitar_resumen(
        texto,
        longitud_maxima=42,
    )

    assert resultado == (
        "Primera oración suficientemente larga."
    )


def probar_resumen_largo_sin_punto():
    resultado = internet.limitar_resumen(
        "palabra " * 30,
        longitud_maxima=50,
    )

    assert resultado.endswith("...")
    assert len(resultado) <= 53


def probar_tema_vacio():
    try:
        internet.buscar_en_wikipedia("   ")
    except internet.ErrorConsultaInternet as error:
        assert str(error) == (
            "Indica el tema que deseas buscar."
        )
    else:
        raise AssertionError(
            "La consulta vacía debía generar un error."
        )


def probar_resultado_correcto():
    datos = {
        "query": {
            "pages": [
                {
                    "title": "Bus CAN",
                    "extract": (
                        "CAN es un protocolo de comunicación."
                    ),
                    "fullurl": (
                        "https://es.wikipedia.org/wiki/Bus_CAN"
                    ),
                }
            ]
        }
    }
    respuesta, cargar_json = (
        crear_respuesta_simulada(datos)
    )

    with (
        patch.object(
            internet,
            "urlopen",
            return_value=respuesta,
        ) as abrir,
        cargar_json,
    ):
        resultado = internet.buscar_en_wikipedia(
            "protocolo CAN"
        )

    assert resultado == {
        "titulo": "Bus CAN",
        "resumen": (
            "CAN es un protocolo de comunicación."
        ),
        "enlace": (
            "https://es.wikipedia.org/wiki/Bus_CAN"
        ),
    }
    assert abrir.call_args.kwargs["timeout"] == 10


def probar_resultado_inexistente():
    respuesta, cargar_json = (
        crear_respuesta_simulada({})
    )

    with (
        patch.object(
            internet,
            "urlopen",
            return_value=respuesta,
        ),
        cargar_json,
    ):
        try:
            internet.buscar_en_wikipedia(
                "tema inexistente"
            )
        except internet.ErrorConsultaInternet as error:
            assert "No encontré información" in str(error)
        else:
            raise AssertionError(
                "La ausencia de resultados debía generar un error."
            )


def probar_resultado_sin_resumen():
    datos = {
        "query": {
            "pages": [
                {
                    "title": "Artículo sin resumen",
                    "extract": "",
                    "fullurl": "https://example.com",
                }
            ]
        }
    }
    respuesta, cargar_json = (
        crear_respuesta_simulada(datos)
    )

    with (
        patch.object(
            internet,
            "urlopen",
            return_value=respuesta,
        ),
        cargar_json,
    ):
        try:
            internet.buscar_en_wikipedia(
                "artículo"
            )
        except internet.ErrorConsultaInternet as error:
            assert "no tiene un resumen" in str(error)
        else:
            raise AssertionError(
                "El resumen vacío debía generar un error."
            )


def probar_error_de_conexion():
    with patch.object(
        internet,
        "urlopen",
        side_effect=URLError(
            "Sin conexión simulada"
        ),
    ):
        try:
            internet.buscar_en_wikipedia(
                "Arduino"
            )
        except internet.ErrorConsultaInternet as error:
            assert "Revisa tu conexión" in str(error)
        else:
            raise AssertionError(
                "La falla de conexión debía controlarse."
            )


def probar_json_invalido():
    respuesta = MagicMock()
    respuesta.__enter__.return_value = respuesta

    with (
        patch.object(
            internet,
            "urlopen",
            return_value=respuesta,
        ),
        patch.object(
            internet.json,
            "load",
            side_effect=json.JSONDecodeError(
                "JSON inválido",
                "",
                0,
            ),
        ),
    ):
        try:
            internet.buscar_en_wikipedia(
                "Inteligencia artificial"
            )
        except internet.ErrorConsultaInternet as error:
            assert "no pudo procesarse" in str(error)
        else:
            raise AssertionError(
                "El JSON inválido debía controlarse."
            )


def probar_formato_del_resultado():
    texto = internet.formatear_resultado(
        {
            "titulo": "Arduino",
            "resumen": "Arduino es una plataforma.",
            "enlace": "https://es.wikipedia.org/wiki/Arduino",
        }
    )

    assert texto.startswith(
        "Arduino\n\nArduino es una plataforma."
    )
    assert "Fuente: Wikipedia" in texto
    assert texto.endswith(
        "https://es.wikipedia.org/wiki/Arduino"
    )


PRUEBAS = [
    ("Codifica correctamente la URL", probar_url_codificada),
    ("Normaliza resúmenes breves", probar_resumen_breve),
    (
        "Corta resúmenes al final de una oración",
        probar_resumen_largo_en_oracion,
    ),
    (
        "Limita textos largos sin puntuación",
        probar_resumen_largo_sin_punto,
    ),
    ("Rechaza temas vacíos", probar_tema_vacio),
    (
        "Procesa resultados válidos",
        probar_resultado_correcto,
    ),
    (
        "Controla búsquedas sin resultados",
        probar_resultado_inexistente,
    ),
    (
        "Controla artículos sin resumen",
        probar_resultado_sin_resumen,
    ),
    (
        "Controla errores de conexión",
        probar_error_de_conexion,
    ),
    (
        "Controla respuestas JSON inválidas",
        probar_json_invalido,
    ),
    (
        "Presenta título, fuente y enlace",
        probar_formato_del_resultado,
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
    print("RESUMEN DE BÚSQUEDAS CONTROLADAS")
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
