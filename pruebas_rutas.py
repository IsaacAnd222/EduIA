import io
import json
from contextlib import redirect_stdout
from unittest.mock import patch
from urllib.error import URLError
from urllib.parse import parse_qs, urlparse

import rutas


ORIGEN = {
    "nombre": "Instituto Irapuato",
    "direccion_completa": "Instituto Irapuato, Irapuato, México",
    "latitud": 20.67025,
    "longitud": -101.37516,
}
DESTINO = {
    "nombre": "Plaza Cibeles",
    "direccion_completa": "Plaza Cibeles, Irapuato, México",
    "latitud": 20.680538,
    "longitud": -101.380945,
}
RESPUESTA_OSRM = {
    "code": "Ok",
    "routes": [
        {
            "distance": 3200.5,
            "duration": 510.0,
            "legs": [
                {
                    "steps": [
                        {
                            "distance": 250.0,
                            "duration": 40.0,
                            "name": "Prolongación Lázaro Cárdenas",
                            "maneuver": {
                                "type": "depart",
                                "modifier": "right",
                            },
                        },
                        {
                            "distance": 1300.0,
                            "duration": 190.0,
                            "name": "Avenida Guerrero",
                            "maneuver": {
                                "type": "turn",
                                "modifier": "left",
                            },
                        },
                        {
                            "distance": 0.0,
                            "duration": 0.0,
                            "name": "",
                            "maneuver": {"type": "arrive"},
                        },
                    ]
                }
            ],
        }
    ],
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


def ejecutar_consulta_simulada(datos=None):
    rutas.limpiar_cache()

    if datos is None:
        datos = RESPUESTA_OSRM

    with patch.object(
        rutas,
        "_solicitar_json",
        return_value=datos,
    ) as solicitar:
        resultado = rutas.consultar_ruta_coordenadas(
            ORIGEN,
            DESTINO,
        )

    return resultado, solicitar


def probar_construccion_url():
    url = rutas.construir_url_ruta(ORIGEN, DESTINO)
    analisis = urlparse(url)
    parametros = parse_qs(analisis.query)

    ruta_coordenadas = f"{analisis.path};{analisis.params}"
    assert ruta_coordenadas.endswith(
        "/route/v1/driving/"
        "-101.37516,20.67025;-101.380945,20.680538"
    )
    assert parametros == {
        "alternatives": ["false"],
        "steps": ["true"],
        "overview": ["false"],
    }


def probar_perfil_controlado():
    try:
        rutas.construir_url_ruta(
            ORIGEN,
            DESTINO,
            perfil="walking",
        )
    except rutas.ErrorConsultaRuta as error:
        assert "automóvil" in str(error)
    else:
        raise AssertionError("No se rechazó el perfil")


def probar_coordenadas_invalidas():
    casos = (
        ({"latitud": "x", "longitud": -101}, "coordenadas"),
        ({"latitud": 91, "longitud": -101}, "latitud"),
        ({"latitud": 20, "longitud": -181}, "longitud"),
        ({"latitud": float("inf"), "longitud": -101}, "latitud"),
    )

    for ubicacion, fragmento in casos:
        try:
            rutas.construir_url_ruta(ubicacion, DESTINO)
        except rutas.ErrorConsultaRuta as error:
            assert fragmento in str(error)
        else:
            raise AssertionError("No se rechazaron coordenadas inválidas")


def probar_servidor_configurable():
    with patch.dict(
        "os.environ",
        {"EDUIA_OSRM_URL": "https://rutas.ejemplo.test/"},
    ):
        assert rutas.obtener_url_osrm() == (
            "https://rutas.ejemplo.test"
        )


def probar_servidor_vacio():
    with patch.dict("os.environ", {"EDUIA_OSRM_URL": " "}):
        try:
            rutas.construir_url_ruta(ORIGEN, DESTINO)
        except rutas.ErrorConsultaRuta as error:
            assert "configurado" in str(error)
        else:
            raise AssertionError("No se detectó el servidor vacío")


def probar_identificacion_http():
    contenido = json.dumps(RESPUESTA_OSRM).encode("utf-8")
    respuesta = RespuestaSimulada(contenido)

    with patch.object(
        rutas,
        "urlopen",
        return_value=respuesta,
    ) as abrir:
        rutas._solicitar_json("https://ejemplo.test")

    solicitud = abrir.call_args.args[0]
    assert solicitud.get_header("User-agent") == rutas.AGENTE_USUARIO
    assert solicitud.get_header("Accept") == "application/json"


def probar_procesamiento_ruta():
    resultado, _ = ejecutar_consulta_simulada()

    assert resultado["origen"]["nombre"] == "Instituto Irapuato"
    assert resultado["destino"]["nombre"] == "Plaza Cibeles"
    assert resultado["distancia_km"] == 3.2005
    assert resultado["duracion_min"] == 8.5
    assert len(resultado["instrucciones"]) == 3
    assert resultado["instrucciones"][1]["indicacion"] == (
        "Gira a la izquierda por Avenida Guerrero"
    )


def probar_traduccion_natural_de_maniobras():
    assert rutas._descripcion_maniobra(
        {"type": "turn", "modifier": "straight"},
        "Boulevard Principal",
    ) == "Continúa recto por Boulevard Principal"
    assert rutas._descripcion_maniobra(
        {"type": "continue", "modifier": "uturn"},
        "Avenida Central",
    ) == "Da vuelta en U por Avenida Central"
    assert rutas._descripcion_maniobra(
        {"type": "roundabout", "exit": 2},
        "",
    ) == "Entra en la glorieta y toma la salida 2"


def probar_enlace_mapa():
    enlace = rutas.construir_enlace_mapa(ORIGEN, DESTINO)
    parametros = parse_qs(urlparse(enlace).query)

    assert parametros["engine"] == ["fossgis_osrm_car"]
    assert parametros["route"] == [
        "20.67025,-101.37516;20.680538,-101.380945"
    ]


def probar_ruta_inexistente():
    try:
        rutas._procesar_respuesta(
            {"code": "NoRoute"},
            ORIGEN,
            DESTINO,
            "driving",
        )
    except rutas.ErrorConsultaRuta as error:
        assert "No encontré una ruta" in str(error)
    else:
        raise AssertionError("No se controló NoRoute")


def probar_error_informado_por_osrm():
    try:
        rutas._procesar_respuesta(
            {"code": "InvalidQuery", "message": "Consulta inválida"},
            ORIGEN,
            DESTINO,
            "driving",
        )
    except rutas.ErrorConsultaRuta as error:
        assert str(error) == "Consulta inválida"
    else:
        raise AssertionError("No se controló el error de OSRM")


def probar_ruta_incompleta():
    for datos in (
        {"code": "Ok", "routes": []},
        {"code": "Ok", "routes": [None]},
        {"code": "Ok", "routes": [{"duration": 5}]},
        {"code": "Ok", "routes": [{"distance": 5}]},
    ):
        try:
            rutas._procesar_respuesta(
                datos,
                ORIGEN,
                DESTINO,
                "driving",
            )
        except rutas.ErrorConsultaRuta:
            pass
        else:
            raise AssertionError("No se rechazó una ruta incompleta")


def probar_error_de_conexion():
    with patch.object(
        rutas,
        "urlopen",
        side_effect=URLError("sin conexión"),
    ):
        try:
            rutas._solicitar_json("https://ejemplo.test")
        except rutas.ErrorConsultaRuta as error:
            assert "conexión a Internet" in str(error)
        else:
            raise AssertionError("No se controló la conexión")


def probar_json_invalido():
    respuesta = RespuestaSimulada(b"no es json")

    with patch.object(rutas, "urlopen", return_value=respuesta):
        try:
            rutas._solicitar_json("https://ejemplo.test")
        except rutas.ErrorConsultaRuta as error:
            assert "respuesta inválida" in str(error)
        else:
            raise AssertionError("No se controló el JSON")


def probar_estructura_json_invalida():
    respuesta = RespuestaSimulada(b"[]")

    with patch.object(rutas, "urlopen", return_value=respuesta):
        try:
            rutas._solicitar_json("https://ejemplo.test")
        except rutas.ErrorConsultaRuta as error:
            assert "respuesta inválida" in str(error)
        else:
            raise AssertionError("No se controló la estructura")


def probar_cache():
    rutas.limpiar_cache()

    with patch.object(
        rutas,
        "_solicitar_json",
        return_value=RESPUESTA_OSRM,
    ) as solicitar:
        primero = rutas.consultar_ruta_coordenadas(ORIGEN, DESTINO)
        segundo = rutas.consultar_ruta_coordenadas(ORIGEN, DESTINO)

    assert primero == segundo
    assert solicitar.call_count == 1


def probar_busqueda_de_lugares():
    with (
        patch.object(
            rutas,
            "buscar_ubicacion",
            side_effect=[ORIGEN, DESTINO],
        ) as buscar,
        patch.object(
            rutas,
            "consultar_ruta_coordenadas",
            return_value={"ruta": "simulada"},
        ) as consultar,
    ):
        resultado = rutas.calcular_ruta(
            "Instituto Irapuato",
            "Plaza Cibeles",
        )

    assert [llamada.args[0] for llamada in buscar.call_args_list] == [
        "Instituto Irapuato",
        "Plaza Cibeles",
    ]
    consultar.assert_called_once_with(ORIGEN, DESTINO, "driving")
    assert resultado == {"ruta": "simulada"}


def probar_origen_y_destino_obligatorios():
    for origen, destino, esperado in (
        ("", "Plaza Cibeles", "origen"),
        ("Instituto Irapuato", "", "destino"),
    ):
        try:
            rutas.calcular_ruta(origen, destino)
        except rutas.ErrorConsultaRuta as error:
            assert esperado in str(error)
        else:
            raise AssertionError("No se validó origen o destino")


def probar_error_de_geocodificacion():
    with patch.object(
        rutas,
        "buscar_ubicacion",
        side_effect=rutas.ErrorConsultaUbicacion("Lugar inexistente"),
    ):
        try:
            rutas.calcular_ruta("Origen", "Destino")
        except rutas.ErrorConsultaRuta as error:
            assert str(error) == "Lugar inexistente"
        else:
            raise AssertionError("No se convirtió el error")


def probar_formato():
    resultado, _ = ejecutar_consulta_simulada()
    texto = rutas.formatear_resultado_ruta(resultado)

    assert texto.startswith(
        "Ruta de Instituto Irapuato a Plaza Cibeles"
    )
    assert "Distancia por carretera: 3.2 km" in texto
    assert "Duración aproximada: 9 min" in texto
    assert "Indicaciones principales:" in texto
    assert "1. Sal de tu ubicación" in texto
    assert "2. Gira a la izquierda" in texto
    assert "Fuente: OSRM y © OpenStreetMap contributors" in texto
    assert "openstreetmap.org/directions" in texto


def probar_formato_de_duraciones_largas():
    assert rutas.formatear_duracion(8.5) == "9 min"
    assert rutas.formatear_duracion(60) == "1 h"
    assert rutas.formatear_duracion(408) == "6 h 48 min"
    assert rutas.formatear_duracion(564) == "9 h 24 min"


def probar_limite_de_instrucciones():
    resultado, _ = ejecutar_consulta_simulada()
    resultado["instrucciones"] = [
        {"indicacion": f"Paso {indice}", "distancia_m": 100}
        for indice in range(12)
    ]
    texto = rutas.formatear_resultado_ruta(resultado)

    assert "10. Paso 9" in texto
    assert "11. Paso 10" not in texto
    assert "ver todas las indicaciones" in texto


def probar_programa_principal_con_error():
    salida = io.StringIO()

    with (
        patch("builtins.input", side_effect=["", "Destino"]),
        redirect_stdout(salida),
    ):
        rutas.main()

    assert "ERROR: Indica el lugar de origen" in salida.getvalue()


PRUEBAS = [
    ("Construye correctamente la URL", probar_construccion_url),
    ("Limita la primera versión al automóvil", probar_perfil_controlado),
    ("Valida las coordenadas", probar_coordenadas_invalidas),
    ("Permite cambiar el servidor", probar_servidor_configurable),
    ("Detecta una configuración vacía", probar_servidor_vacio),
    ("Identifica las solicitudes de EduIA", probar_identificacion_http),
    ("Procesa una ruta válida", probar_procesamiento_ruta),
    ("Traduce naturalmente las maniobras", probar_traduccion_natural_de_maniobras),
    ("Construye el enlace de OpenStreetMap", probar_enlace_mapa),
    ("Controla rutas inexistentes", probar_ruta_inexistente),
    ("Controla errores informados por OSRM", probar_error_informado_por_osrm),
    ("Detecta rutas incompletas", probar_ruta_incompleta),
    ("Controla errores de conexión", probar_error_de_conexion),
    ("Controla respuestas JSON inválidas", probar_json_invalido),
    ("Controla estructuras inválidas", probar_estructura_json_invalida),
    ("Evita consultas repetidas con caché", probar_cache),
    ("Obtiene las coordenadas de ambos lugares", probar_busqueda_de_lugares),
    ("Exige origen y destino", probar_origen_y_destino_obligatorios),
    ("Controla errores al buscar lugares", probar_error_de_geocodificacion),
    ("Presenta distancia, duración e instrucciones", probar_formato),
    ("Presenta naturalmente las duraciones largas", probar_formato_de_duraciones_largas),
    ("Limita las instrucciones mostradas", probar_limite_de_instrucciones),
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
    print("RESUMEN DE RUTAS CON OSRM")
    print("=" * 70)
    print(f"Total de pruebas: {len(PRUEBAS)}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {len(errores)}")
    print(f"Precisión: {correctas / len(PRUEBAS):.2%}")

    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
