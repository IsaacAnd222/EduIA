import io
import json
from contextlib import redirect_stdout
from unittest.mock import patch
from urllib.error import URLError
from urllib.parse import parse_qs, urlparse

import ubicaciones


RESULTADO_API = {
    "place_id": 12345,
    "osm_type": "node",
    "osm_id": 98765,
    "lat": "20.6767500",
    "lon": "-101.3562800",
    "category": "amenity",
    "type": "university",
    "addresstype": "amenity",
    "name": "Instituto Irapuato",
    "display_name": (
        "Instituto Irapuato, Irapuato, "
        "Estado de Guanajuato, México"
    ),
    "address": {
        "amenity": "Instituto Irapuato",
        "city": "Irapuato",
        "state": "Estado de Guanajuato",
        "country": "México",
        "country_code": "mx",
        "postcode": "36670",
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


def ejecutar_busqueda_simulada(
    consulta="Instituto Irapuato",
    datos=None,
    limite=1,
    codigo_pais="mx",
):
    ubicaciones.limpiar_cache()

    if datos is None:
        datos = [RESULTADO_API]

    with (
        patch.object(
            ubicaciones,
            "_respetar_limite_solicitudes",
        ),
        patch.object(
            ubicaciones,
            "_solicitar_json",
            return_value=datos,
        ) as solicitar,
    ):
        resultados = ubicaciones.buscar_ubicaciones(
            consulta,
            limite=limite,
            codigo_pais=codigo_pais,
        )

    return resultados, solicitar


def probar_codificacion_de_consulta():
    url = ubicaciones._construir_url(
        ubicaciones.URL_NOMINATIM_PREDETERMINADA,
        {
            "q": "Instituto Irapuato, Guanajuato",
            "format": "jsonv2",
        },
    )
    parametros = parse_qs(urlparse(url).query)

    assert parametros["q"] == [
        "Instituto Irapuato, Guanajuato"
    ]
    assert parametros["format"] == ["jsonv2"]


def probar_consulta_vacia():
    try:
        ubicaciones.buscar_ubicaciones("   ")
    except ubicaciones.ErrorConsultaUbicacion as error:
        assert "Indica el lugar" in str(error)
    else:
        raise AssertionError("No se rechazó la consulta vacía")


def probar_consultas_alternativas():
    alternativas = ubicaciones.generar_consultas_alternativas(
        "Universidad de Guanajuato Campus Irapuato-Salamanca"
    )

    assert alternativas == [
        "Universidad de Guanajuato Campus Irapuato-Salamanca",
        "Universidad de Guanajuato, Irapuato",
        "Universidad de Guanajuato, Salamanca",
    ]

    assert ubicaciones.generar_consultas_alternativas(
        "Centro Histórico en León, Guanajuato"
    ) == [
        "Centro Histórico en León, Guanajuato",
        "Centro Histórico, León, Guanajuato",
    ]


def probar_busqueda_alternativa_si_no_hay_resultados():
    ubicaciones.limpiar_cache()

    with (
        patch.object(
            ubicaciones,
            "_respetar_limite_solicitudes",
        ),
        patch.object(
            ubicaciones,
            "_solicitar_json",
            side_effect=[[], [RESULTADO_API]],
        ) as solicitar,
    ):
        resultado = ubicaciones.buscar_ubicacion(
            "Centro Histórico en León, Guanajuato"
        )

    consultas = [
        parse_qs(urlparse(llamada.args[0]).query)["q"][0]
        for llamada in solicitar.call_args_list
    ]

    assert consultas == [
        "Centro Histórico en León, Guanajuato",
        "Centro Histórico, León, Guanajuato",
    ]
    assert resultado["nombre"] == "Instituto Irapuato"


def probar_limite_de_resultados():
    for limite in (0, 6, 2.5):
        try:
            ubicaciones.buscar_ubicaciones(
                "Irapuato",
                limite=limite,
            )
        except ubicaciones.ErrorConsultaUbicacion as error:
            assert "entre 1 y 5" in str(error)
        else:
            raise AssertionError("No se rechazó el límite")


def probar_parametros_de_busqueda():
    _, solicitar = ejecutar_busqueda_simulada(
        limite=1,
    )
    parametros = parse_qs(
        urlparse(solicitar.call_args.args[0]).query
    )

    assert parametros["q"] == ["Instituto Irapuato"]
    assert parametros["format"] == ["jsonv2"]
    assert parametros["addressdetails"] == ["1"]
    assert parametros["limit"] == ["1"]
    assert parametros["countrycodes"] == ["mx"]


def probar_busqueda_sin_filtro_de_pais():
    _, solicitar = ejecutar_busqueda_simulada(
        codigo_pais="",
    )
    parametros = parse_qs(
        urlparse(solicitar.call_args.args[0]).query
    )

    assert "countrycodes" not in parametros


def probar_procesamiento_de_resultado():
    resultados, _ = ejecutar_busqueda_simulada()
    resultado = resultados[0]

    assert resultado["nombre"] == "Instituto Irapuato"
    assert resultado["ciudad"] == "Irapuato"
    assert resultado["estado"] == "Estado de Guanajuato"
    assert resultado["latitud"] == 20.67675
    assert resultado["longitud"] == -101.35628
    assert resultado["tipo"] == "amenity"


def probar_ubicacion_no_encontrada():
    ubicaciones.limpiar_cache()

    with (
        patch.object(
            ubicaciones,
            "_respetar_limite_solicitudes",
        ),
        patch.object(
            ubicaciones,
            "_solicitar_json",
            return_value=[],
        ),
    ):
        try:
            ubicaciones.buscar_ubicacion("Lugar inexistente")
        except ubicaciones.ErrorConsultaUbicacion as error:
            assert "No encontré" in str(error)
        else:
            raise AssertionError("No se controló la búsqueda vacía")


def probar_resultados_invalidos():
    datos = [
        {"display_name": "Sin coordenadas"},
        {"lat": "20", "lon": "-101"},
    ]
    ubicaciones.limpiar_cache()

    with (
        patch.object(
            ubicaciones,
            "_respetar_limite_solicitudes",
        ),
        patch.object(
            ubicaciones,
            "_solicitar_json",
            return_value=datos,
        ),
    ):
        try:
            ubicaciones.buscar_ubicaciones("Lugar defectuoso")
        except ubicaciones.ErrorConsultaUbicacion as error:
            assert "ubicaciones válidas" in str(error)
        else:
            raise AssertionError("No se rechazaron los resultados inválidos")


def probar_resultados_validos_e_invalidos():
    datos = [
        {"display_name": "Sin coordenadas"},
        RESULTADO_API,
    ]
    resultados, _ = ejecutar_busqueda_simulada(
        datos=datos,
    )

    assert len(resultados) == 1
    assert resultados[0]["nombre"] == "Instituto Irapuato"


def probar_enlace_por_objeto_osm():
    enlace = ubicaciones.construir_enlace_mapa(
        {
            "osm_type": "way",
            "osm_id": 123,
            "latitud": 20,
            "longitud": -101,
        }
    )

    assert enlace == "https://www.openstreetmap.org/way/123"


def probar_enlace_por_coordenadas():
    enlace = ubicaciones.construir_enlace_mapa(
        {
            "latitud": 20.5,
            "longitud": -101.2,
        }
    )

    assert "mlat=20.5" in enlace
    assert "mlon=-101.2" in enlace
    assert "#map=17/20.5/-101.2" in enlace


def probar_cache_de_consultas():
    ubicaciones.limpiar_cache()

    with (
        patch.object(
            ubicaciones,
            "_respetar_limite_solicitudes",
        ) as limitar,
        patch.object(
            ubicaciones,
            "_solicitar_json",
            return_value=[RESULTADO_API],
        ) as solicitar,
    ):
        primero = ubicaciones.buscar_ubicacion(
            "Instituto Irapuato"
        )
        segundo = ubicaciones.buscar_ubicacion(
            "  INSTITUTO   IRAPUATO  "
        )

    assert primero == segundo
    assert solicitar.call_count == 1
    assert limitar.call_count == 1


def probar_intervalo_entre_solicitudes():
    with (
        patch.object(
            ubicaciones.time,
            "monotonic",
            side_effect=[10.4, 11.0],
        ),
        patch.object(
            ubicaciones.time,
            "sleep",
        ) as dormir,
    ):
        ubicaciones._ULTIMA_SOLICITUD = 10.0
        ubicaciones._respetar_limite_solicitudes()

    dormir.assert_called_once()
    assert abs(dormir.call_args.args[0] - 0.6) < 0.0001
    assert ubicaciones._ULTIMA_SOLICITUD == 11.0


def probar_identificacion_http():
    contenido = json.dumps([RESULTADO_API]).encode("utf-8")
    respuesta = RespuestaSimulada(contenido)

    with patch.object(
        ubicaciones,
        "urlopen",
        return_value=respuesta,
    ) as abrir:
        ubicaciones._solicitar_json("https://ejemplo.test")

    solicitud = abrir.call_args.args[0]
    assert solicitud.get_header("User-agent") == (
        ubicaciones.AGENTE_USUARIO
    )
    assert solicitud.get_header("Accept-language") == (
        "es-MX,es;q=0.9"
    )


def probar_url_configurable():
    with patch.dict(
        "os.environ",
        {"EDUIA_NOMINATIM_URL": "https://geocodificador.test/search"},
    ):
        assert ubicaciones.obtener_url_nominatim() == (
            "https://geocodificador.test/search"
        )


def probar_error_de_conexion():
    with patch.object(
        ubicaciones,
        "urlopen",
        side_effect=URLError("sin conexión"),
    ):
        try:
            ubicaciones._solicitar_json("https://ejemplo.test")
        except ubicaciones.ErrorConsultaUbicacion as error:
            assert "conexión a Internet" in str(error)
        else:
            raise AssertionError("No se controló el error de conexión")


def probar_respuesta_json_invalida():
    respuesta = RespuestaSimulada(b"no es json")

    with patch.object(
        ubicaciones,
        "urlopen",
        return_value=respuesta,
    ):
        try:
            ubicaciones._solicitar_json("https://ejemplo.test")
        except ubicaciones.ErrorConsultaUbicacion as error:
            assert "respuesta inválida" in str(error)
        else:
            raise AssertionError("No se controló el JSON inválido")


def probar_estructura_json_invalida():
    contenido = json.dumps({"error": "prueba"}).encode("utf-8")
    respuesta = RespuestaSimulada(contenido)

    with patch.object(
        ubicaciones,
        "urlopen",
        return_value=respuesta,
    ):
        try:
            ubicaciones._solicitar_json("https://ejemplo.test")
        except ubicaciones.ErrorConsultaUbicacion as error:
            assert "respuesta inválida" in str(error)
        else:
            raise AssertionError("No se controló la estructura inválida")


def probar_presentacion_individual():
    resultados, _ = ejecutar_busqueda_simulada()
    texto = ubicaciones.formatear_resultado_ubicacion(
        resultados[0]
    )

    assert texto.startswith("Instituto Irapuato\n")
    assert "Dirección: Instituto Irapuato" in texto
    assert "Coordenadas: 20.676750, -101.356280" in texto
    assert "© OpenStreetMap contributors" in texto
    assert "openstreetmap.org/node/98765" in texto


def probar_presentacion_multiple():
    resultados, _ = ejecutar_busqueda_simulada()
    texto = ubicaciones.formatear_resultados_ubicacion(
        resultados
    )

    assert texto.startswith("Ubicaciones encontradas:")
    assert "1. Instituto Irapuato" in texto
    assert "© OpenStreetMap contributors" in texto


def probar_programa_principal_con_error():
    salida = io.StringIO()

    with (
        patch("builtins.input", return_value=""),
        redirect_stdout(salida),
    ):
        ubicaciones.main()

    assert "ERROR: Indica el lugar" in salida.getvalue()


PRUEBAS = [
    ("Codifica correctamente la consulta", probar_codificacion_de_consulta),
    ("Rechaza consultas vacías", probar_consulta_vacia),
    ("Genera búsquedas alternativas prudentes", probar_consultas_alternativas),
    ("Reintenta cuando no encuentra resultados", probar_busqueda_alternativa_si_no_hay_resultados),
    ("Limita la cantidad de resultados", probar_limite_de_resultados),
    ("Construye los parámetros de búsqueda", probar_parametros_de_busqueda),
    ("Permite búsquedas internacionales", probar_busqueda_sin_filtro_de_pais),
    ("Procesa ubicaciones válidas", probar_procesamiento_de_resultado),
    ("Controla lugares inexistentes", probar_ubicacion_no_encontrada),
    ("Rechaza resultados inválidos", probar_resultados_invalidos),
    ("Conserva resultados válidos", probar_resultados_validos_e_invalidos),
    ("Construye enlaces de objetos OSM", probar_enlace_por_objeto_osm),
    ("Construye enlaces por coordenadas", probar_enlace_por_coordenadas),
    ("Evita consultas repetidas con caché", probar_cache_de_consultas),
    ("Respeta una solicitud por segundo", probar_intervalo_entre_solicitudes),
    ("Identifica las solicitudes de EduIA", probar_identificacion_http),
    ("Permite cambiar el servidor", probar_url_configurable),
    ("Controla errores de conexión", probar_error_de_conexion),
    ("Controla JSON inválido", probar_respuesta_json_invalida),
    ("Controla estructuras inválidas", probar_estructura_json_invalida),
    ("Presenta una ubicación y su fuente", probar_presentacion_individual),
    ("Presenta múltiples ubicaciones", probar_presentacion_multiple),
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
    print("RESUMEN DE BÚSQUEDAS EN OPENSTREETMAP")
    print("=" * 70)
    print(f"Total de pruebas: {len(PRUEBAS)}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {len(errores)}")
    print(f"Precisión: {correctas / len(PRUEBAS):.2%}")

    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
