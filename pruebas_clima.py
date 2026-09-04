import io
import json
from contextlib import redirect_stdout
from unittest.mock import patch
from urllib.error import URLError
from urllib.parse import parse_qs, urlparse

import clima


UBICACION_API = {
    "results": [
        {
            "name": "Irapuato",
            "latitude": 20.67675,
            "longitude": -101.35628,
            "country_code": "MX",
            "country": "México",
            "admin1": "Guanajuato",
            "timezone": "America/Mexico_City",
        }
    ]
}


PRONOSTICO_API = {
    "timezone": "America/Mexico_City",
    "current": {
        "time": "2026-09-04T12:00",
        "temperature_2m": 24.6,
        "apparent_temperature": 25.1,
        "relative_humidity_2m": 63,
        "precipitation": 0.0,
        "weather_code": 2,
        "wind_speed_10m": 8.4,
    },
    "daily": {
        "time": [
            "2026-09-04",
            "2026-09-05",
            "2026-09-06",
        ],
        "weather_code": [2, 61, 95],
        "temperature_2m_max": [27.2, 25.0, 24.1],
        "temperature_2m_min": [15.3, 14.8, 14.2],
        "precipitation_probability_max": [20, 70, 85],
        "precipitation_sum": [0.0, 4.2, 12.5],
    },
}


class RespuestaSimulada:
    def __init__(self, contenido):
        self.contenido = contenido

    def __enter__(self):
        return self

    def __exit__(self, tipo, valor, traceback):
        return False

    def read(self):
        return self.contenido


def probar_codificacion_de_ubicacion():
    url = clima._construir_url(
        clima.URL_GEOCODIFICACION,
        {
            "name": "León de los Aldama",
            "countryCode": "MX",
        },
    )
    parametros = parse_qs(urlparse(url).query)

    assert parametros["name"] == ["León de los Aldama"]
    assert parametros["countryCode"] == ["MX"]


def probar_rechazo_de_ubicacion_vacia():
    try:
        clima.buscar_ubicacion("   ")
    except clima.ErrorConsultaClima as error:
        assert "Indica la ciudad" in str(error)
    else:
        raise AssertionError("No se rechazó la ubicación vacía")


def probar_procesamiento_de_ubicacion():
    with patch.object(
        clima,
        "_solicitar_json",
        return_value=UBICACION_API,
    ) as solicitar:
        resultado = clima.buscar_ubicacion("Irapuato")

    assert resultado["nombre"] == "Irapuato"
    assert resultado["estado"] == "Guanajuato"
    assert resultado["latitud"] == 20.67675
    assert resultado["longitud"] == -101.35628

    url = solicitar.call_args.args[0]
    parametros = parse_qs(urlparse(url).query)
    assert parametros["language"] == ["es"]
    assert parametros["countryCode"] == ["MX"]


def probar_ubicacion_no_encontrada():
    with patch.object(
        clima,
        "_solicitar_json",
        return_value={"results": []},
    ):
        try:
            clima.buscar_ubicacion("Ciudad inexistente")
        except clima.ErrorConsultaClima as error:
            assert "No encontré" in str(error)
        else:
            raise AssertionError("No se controló la búsqueda vacía")


def probar_ubicacion_con_coordenadas_invalidas():
    respuesta = {
        "results": [
            {
                "name": "Ubicación defectuosa",
                "latitude": None,
                "longitude": -101.35,
            }
        ]
    }

    with patch.object(
        clima,
        "_solicitar_json",
        return_value=respuesta,
    ):
        try:
            clima.buscar_ubicacion("Ubicación defectuosa")
        except clima.ErrorConsultaClima as error:
            assert "coordenadas válidas" in str(error)
        else:
            raise AssertionError("No se validaron las coordenadas encontradas")


def probar_validacion_de_coordenadas():
    casos = (
        ("norte", -101, "coordenadas"),
        (91, -101, "latitud"),
        (20, -181, "longitud"),
    )

    for latitud, longitud, fragmento in casos:
        try:
            clima.consultar_pronostico(latitud, longitud)
        except clima.ErrorConsultaClima as error:
            assert fragmento in str(error).lower()
        else:
            raise AssertionError("No se rechazaron las coordenadas")


def probar_validacion_de_dias():
    for dias in (0, 8, 2.5):
        try:
            clima.consultar_pronostico(20.67, -101.35, dias)
        except clima.ErrorConsultaClima as error:
            assert "entre 1 y 7 días" in str(error)
        else:
            raise AssertionError("No se rechazó el número de días")


def probar_parametros_del_pronostico():
    with patch.object(
        clima,
        "_solicitar_json",
        return_value=PRONOSTICO_API,
    ) as solicitar:
        clima.consultar_pronostico(20.67675, -101.35628, 3)

    url = solicitar.call_args.args[0]
    parametros = parse_qs(urlparse(url).query)
    assert parametros["timezone"] == ["auto"]
    assert parametros["forecast_days"] == ["3"]
    assert "temperature_2m" in parametros["current"][0]
    assert "precipitation_probability_max" in parametros["daily"][0]


def probar_procesamiento_del_pronostico():
    with patch.object(
        clima,
        "_solicitar_json",
        return_value=PRONOSTICO_API,
    ):
        resultado = clima.consultar_pronostico(
            20.67675,
            -101.35628,
            3,
        )

    assert resultado["actual"]["temperatura"] == 24.6
    assert resultado["actual"]["humedad"] == 63
    assert len(resultado["pronostico"]) == 3
    assert resultado["pronostico"][1][
        "probabilidad_lluvia"
    ] == 70


def probar_codigos_meteorologicos():
    assert clima.describir_codigo_clima(0) == "Cielo despejado"
    assert clima.describir_codigo_clima(61) == "Lluvia ligera"
    assert clima.describir_codigo_clima(95) == "Tormenta eléctrica"
    assert "no disponible" in clima.describir_codigo_clima(500).lower()
    assert "no disponible" in clima.describir_codigo_clima(None).lower()


def probar_datos_incompletos():
    respuesta = {
        "current": {"temperature_2m": 22},
        "daily": {"time": []},
    }

    with patch.object(
        clima,
        "_solicitar_json",
        return_value=respuesta,
    ):
        try:
            clima.consultar_pronostico(20.67, -101.35)
        except clima.ErrorConsultaClima as error:
            assert "incompletos" in str(error)
        else:
            raise AssertionError("No se detectaron datos incompletos")


def probar_error_de_conexion():
    with patch.object(
        clima,
        "urlopen",
        side_effect=URLError("sin conexión"),
    ):
        try:
            clima._solicitar_json("https://ejemplo.test")
        except clima.ErrorConsultaClima as error:
            assert "conexión a Internet" in str(error)
        else:
            raise AssertionError("No se controló el error de conexión")


def probar_json_invalido():
    respuesta = RespuestaSimulada(b"contenido que no es JSON")

    with patch.object(
        clima,
        "urlopen",
        return_value=respuesta,
    ):
        try:
            clima._solicitar_json("https://ejemplo.test")
        except clima.ErrorConsultaClima as error:
            assert "respuesta inválida" in str(error)
        else:
            raise AssertionError("No se controló el JSON inválido")


def probar_codificacion_invalida():
    respuesta = RespuestaSimulada(b"\xff\xfe\xfa")

    with patch.object(
        clima,
        "urlopen",
        return_value=respuesta,
    ):
        try:
            clima._solicitar_json("https://ejemplo.test")
        except clima.ErrorConsultaClima as error:
            assert "respuesta inválida" in str(error)
        else:
            raise AssertionError("No se controló la codificación inválida")


def probar_error_informado_por_api():
    contenido = json.dumps(
        {
            "error": True,
            "reason": "Parámetro incorrecto",
        }
    ).encode("utf-8")
    respuesta = RespuestaSimulada(contenido)

    with patch.object(
        clima,
        "urlopen",
        return_value=respuesta,
    ):
        try:
            clima._solicitar_json("https://ejemplo.test")
        except clima.ErrorConsultaClima as error:
            assert "Parámetro incorrecto" in str(error)
        else:
            raise AssertionError("No se controló el error de la API")


def probar_consulta_completa():
    with (
        patch.object(
            clima,
            "buscar_ubicacion",
            return_value={
                "nombre": "Irapuato",
                "estado": "Guanajuato",
                "pais": "México",
                "latitud": 20.67675,
                "longitud": -101.35628,
                "zona_horaria": "America/Mexico_City",
            },
        ) as buscar,
        patch.object(
            clima,
            "consultar_pronostico",
            return_value={
                "actual": {"temperatura": 24.6},
                "pronostico": [{"fecha": "2026-09-04"}],
                "zona_horaria": "America/Mexico_City",
            },
        ) as pronostico,
    ):
        resultado = clima.consultar_clima("Irapuato", dias=3)

    buscar.assert_called_once_with("Irapuato", codigo_pais="MX")
    pronostico.assert_called_once_with(
        20.67675,
        -101.35628,
        dias=3,
    )
    assert resultado["fuente"] == "Open-Meteo"


def probar_presentacion_del_resultado():
    with (
        patch.object(
            clima,
            "_solicitar_json",
            side_effect=[UBICACION_API, PRONOSTICO_API],
        ),
    ):
        resultado = clima.consultar_clima("Irapuato")

    texto = clima.formatear_resultado_clima(resultado)

    assert texto.startswith("Clima en Irapuato, Guanajuato, México")
    assert "Ahora: Parcialmente nublado." in texto
    assert "Temperatura: 24.6 °C" in texto
    assert "Mañana: lluvia ligera" in texto
    assert "probabilidad de lluvia 70 %" in texto
    assert "Fuente: Open-Meteo" in texto
    assert clima.URL_FUENTE in texto


def probar_programa_principal_con_error():
    salida = io.StringIO()

    with (
        patch("builtins.input", return_value=""),
        redirect_stdout(salida),
    ):
        clima.main()

    assert "ERROR: Indica la ciudad" in salida.getvalue()


PRUEBAS = [
    ("Codifica correctamente la ubicación", probar_codificacion_de_ubicacion),
    ("Rechaza ubicaciones vacías", probar_rechazo_de_ubicacion_vacia),
    ("Procesa ubicaciones válidas", probar_procesamiento_de_ubicacion),
    ("Controla ubicaciones inexistentes", probar_ubicacion_no_encontrada),
    ("Valida coordenadas encontradas", probar_ubicacion_con_coordenadas_invalidas),
    ("Valida las coordenadas", probar_validacion_de_coordenadas),
    ("Valida la cantidad de días", probar_validacion_de_dias),
    ("Construye la consulta meteorológica", probar_parametros_del_pronostico),
    ("Procesa el pronóstico", probar_procesamiento_del_pronostico),
    ("Traduce los códigos meteorológicos", probar_codigos_meteorologicos),
    ("Detecta respuestas incompletas", probar_datos_incompletos),
    ("Controla errores de conexión", probar_error_de_conexion),
    ("Controla respuestas JSON inválidas", probar_json_invalido),
    ("Controla codificaciones inválidas", probar_codificacion_invalida),
    ("Controla errores informados por la API", probar_error_informado_por_api),
    ("Combina ubicación y pronóstico", probar_consulta_completa),
    ("Presenta clima, pronóstico y fuente", probar_presentacion_del_resultado),
    ("Muestra errores desde el programa principal", probar_programa_principal_con_error),
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
    print("RESUMEN DE CONSULTAS DEL CLIMA")
    print("=" * 70)
    print(f"Total de pruebas: {len(PRUEBAS)}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {len(errores)}")
    print(f"Precisión: {correctas / len(PRUEBAS):.2%}")

    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
