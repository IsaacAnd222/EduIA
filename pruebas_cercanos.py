import io
import json
from contextlib import redirect_stdout
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs

import cercanos


UBICACION = {
    "nombre": "Instituto Irapuato",
    "latitud": 20.67025,
    "longitud": -101.37516,
}
ELEMENTOS = [
    {
        "type": "node",
        "id": 100,
        "lat": 20.672,
        "lon": -101.375,
        "tags": {
            "name": "Farmacia Cercana",
            "amenity": "pharmacy",
            "addr:street": "Avenida Principal",
            "addr:housenumber": "10",
            "addr:city": "Irapuato",
        },
    },
    {
        "type": "way",
        "id": 200,
        "center": {
            "lat": 20.68,
            "lon": -101.38,
        },
        "tags": {
            "brand": "Farmacias Ejemplo",
            "amenity": "pharmacy",
        },
    },
]


class RespuestaSimulada:
    def __init__(self, contenido):
        self.contenido = contenido

    def __enter__(self):
        return self

    def __exit__(self, tipo, valor, traceback):
        return False

    def read(self):
        return self.contenido


def ejecutar_busqueda(datos=None):
    cercanos.limpiar_cache()

    if datos is None:
        datos = {"elements": ELEMENTOS}

    with patch.object(
        cercanos,
        "_solicitar_json",
        return_value=datos,
    ) as solicitar:
        resultado = cercanos.buscar_lugares_cercanos(
            "farmacias",
            UBICACION,
        )

    return resultado, solicitar


def probar_categorias_y_sinonimos():
    casos = {
        "hospitales": "hospital",
        "clínicas": "clinica",
        "farmacia": "farmacia",
        "cafés": "cafeteria",
        "restaurantes": "restaurante",
        "colegios": "escuela",
        "campus": "universidad",
        "bancos": "banco",
        "ATM": "cajero",
        "gasolineras": "gasolinera",
        "parking": "estacionamiento",
        "paradas de camión": "parada_autobus",
        "paradas de autobuses": "parada_autobus",
        "paraderos de autobuses": "parada_autobus",
    }

    for texto, esperado in casos.items():
        assert cercanos.resolver_categoria(texto) == esperado


def probar_categoria_no_disponible():
    try:
        cercanos.resolver_categoria("tiendas de videojuegos")
    except cercanos.ErrorConsultaCercanos as error:
        assert "todavía no está disponible" in str(error)
        assert "hospitales" in str(error)
    else:
        raise AssertionError("No se rechazó la categoría")


def probar_consulta_overpass():
    consulta = cercanos.construir_consulta_overpass(
        "universidades",
        20.67,
        -101.37,
        2500,
    )

    assert consulta.startswith("[out:json][timeout:20];")
    assert 'nwr(around:2500,20.67,-101.37)["amenity"="university"]' in consulta
    assert 'nwr(around:2500,20.67,-101.37)["amenity"="college"]' in consulta
    assert consulta.endswith("out center tags;")


def probar_radio_controlado():
    for radio in (99, 10001, 2.5):
        try:
            cercanos.construir_consulta_overpass(
                "hospital",
                20,
                -101,
                radio,
            )
        except cercanos.ErrorConsultaCercanos as error:
            assert "radio" in str(error)
        else:
            raise AssertionError("No se rechazó el radio")


def probar_limite_controlado():
    for limite in (0, 16, 2.5):
        try:
            cercanos.buscar_lugares_cercanos(
                "hospital",
                UBICACION,
                limite=limite,
            )
        except cercanos.ErrorConsultaCercanos as error:
            assert "resultados" in str(error)
        else:
            raise AssertionError("No se rechazó el límite")


def probar_coordenadas_invalidas():
    for ubicacion in (
        {"latitud": "x", "longitud": -101},
        {"latitud": 91, "longitud": -101},
        {"latitud": 20, "longitud": -181},
    ):
        try:
            cercanos.buscar_lugares_cercanos(
                "hospital",
                ubicacion,
            )
        except cercanos.ErrorConsultaCercanos:
            pass
        else:
            raise AssertionError("No se rechazaron las coordenadas")


def probar_solicitud_post_identificada():
    contenido = json.dumps({"elements": []}).encode("utf-8")
    respuesta = RespuestaSimulada(contenido)

    with patch.object(
        cercanos,
        "urlopen",
        return_value=respuesta,
    ) as abrir:
        cercanos._solicitar_json("[out:json];out;")

    solicitud = abrir.call_args.args[0]
    cuerpo = parse_qs(solicitud.data.decode("utf-8"))
    assert solicitud.method == "POST"
    assert cuerpo["data"] == ["[out:json];out;"]
    assert solicitud.get_header("User-agent") == cercanos.AGENTE_USUARIO


def probar_servidor_configurable():
    with patch.dict(
        "os.environ",
        {"EDUIA_OVERPASS_URL": "https://overpass.ejemplo.test"},
    ):
        assert cercanos.obtener_url_overpass() == (
            "https://overpass.ejemplo.test"
        )


def probar_servidor_vacio():
    with patch.dict("os.environ", {"EDUIA_OVERPASS_URL": " "}):
        try:
            cercanos._solicitar_json("consulta")
        except cercanos.ErrorConsultaCercanos as error:
            assert "configurado" in str(error)
        else:
            raise AssertionError("No se detectó el servidor vacío")


def probar_procesamiento_y_orden():
    resultado, _ = ejecutar_busqueda()

    assert resultado["categoria"] == "farmacia"
    assert resultado["categoria_plural"] == "farmacias"
    assert len(resultado["lugares"]) == 2
    assert resultado["lugares"][0]["nombre"] == "Farmacia Cercana"
    assert resultado["lugares"][0]["direccion"] == (
        "Avenida Principal 10, Irapuato"
    )
    assert resultado["lugares"][1]["nombre"] == "Farmacias Ejemplo"
    assert resultado["lugares"][0]["distancia_m"] < (
        resultado["lugares"][1]["distancia_m"]
    )


def probar_elementos_invalidos_se_omiten():
    datos = {
        "elements": [
            {"type": "node", "id": 1},
            ELEMENTOS[0],
        ]
    }
    resultado, _ = ejecutar_busqueda(datos)
    assert len(resultado["lugares"]) == 1


def probar_busqueda_sin_resultados():
    try:
        ejecutar_busqueda({"elements": []})
    except cercanos.ErrorConsultaCercanos as error:
        assert "No encontré farmacias" in str(error)
        assert "5 km" in str(error)
    else:
        raise AssertionError("No se controló la búsqueda vacía")


def probar_limite_y_cache():
    cercanos.limpiar_cache()

    with patch.object(
        cercanos,
        "_solicitar_json",
        return_value={"elements": ELEMENTOS},
    ) as solicitar:
        primero = cercanos.buscar_lugares_cercanos(
            "farmacia",
            UBICACION,
            limite=1,
        )
        segundo = cercanos.buscar_lugares_cercanos(
            "farmacias",
            UBICACION,
            limite=1,
        )

    assert len(primero["lugares"]) == 1
    assert primero == segundo
    assert solicitar.call_count == 1


def probar_busqueda_por_nombre():
    with (
        patch.object(
            cercanos,
            "buscar_ubicacion",
            return_value=UBICACION,
        ) as buscar,
        patch.object(
            cercanos,
            "buscar_lugares_cercanos",
            return_value={"resultado": "simulado"},
        ) as cercanos_mock,
    ):
        resultado = cercanos.buscar_cerca_de(
            "hospitales",
            "Instituto Irapuato",
            radio=2000,
            limite=4,
        )

    buscar.assert_called_once_with("Instituto Irapuato")
    cercanos_mock.assert_called_once_with(
        "hospitales",
        UBICACION,
        2000,
        4,
    )
    assert resultado == {"resultado": "simulado"}


def probar_ubicacion_obligatoria():
    try:
        cercanos.buscar_cerca_de("hospital", " ")
    except cercanos.ErrorConsultaCercanos as error:
        assert "Indica la ubicación" in str(error)
    else:
        raise AssertionError("No se exigió la ubicación")


def probar_error_de_geocodificacion():
    with patch.object(
        cercanos,
        "buscar_ubicacion",
        side_effect=cercanos.ErrorConsultaUbicacion("Lugar inexistente"),
    ):
        try:
            cercanos.buscar_cerca_de("hospital", "Lugar")
        except cercanos.ErrorConsultaCercanos as error:
            assert str(error) == "Lugar inexistente"
        else:
            raise AssertionError("No se convirtió el error")


def probar_error_de_conexion():
    with patch.object(
        cercanos,
        "urlopen",
        side_effect=URLError("sin conexión"),
    ):
        try:
            cercanos._solicitar_json("consulta")
        except cercanos.ErrorConsultaCercanos as error:
            assert "conexión a Internet" in str(error)
        else:
            raise AssertionError("No se controló la conexión")


def probar_servidor_ocupado():
    error_http = HTTPError(
        "https://ejemplo.test",
        429,
        "ocupado",
        None,
        None,
    )

    with patch.object(cercanos, "urlopen", side_effect=error_http):
        try:
            cercanos._solicitar_json("consulta")
        except cercanos.ErrorConsultaCercanos as error:
            assert "está ocupado" in str(error)
        else:
            raise AssertionError("No se controló HTTP 429")


def probar_json_invalido():
    respuesta = RespuestaSimulada(b"no es json")

    with patch.object(cercanos, "urlopen", return_value=respuesta):
        try:
            cercanos._solicitar_json("consulta")
        except cercanos.ErrorConsultaCercanos as error:
            assert "respuesta inválida" in str(error)
        else:
            raise AssertionError("No se controló el JSON")


def probar_estructura_invalida():
    respuesta = RespuestaSimulada(b"[]")

    with patch.object(cercanos, "urlopen", return_value=respuesta):
        try:
            cercanos._solicitar_json("consulta")
        except cercanos.ErrorConsultaCercanos as error:
            assert "respuesta inválida" in str(error)
        else:
            raise AssertionError("No se controló la estructura")


def probar_formato():
    resultado, _ = ejecutar_busqueda()
    texto = cercanos.formatear_resultado_cercanos(resultado)

    assert texto.startswith("Farmacias cerca de Instituto Irapuato:")
    assert "1. Farmacia Cercana" in texto
    assert "Dirección: Avenida Principal 10, Irapuato" in texto
    assert "openstreetmap.org/node/100" in texto
    assert "Fuente: © OpenStreetMap contributors" in texto
    assert "línea recta" in texto


def probar_programa_principal_con_error():
    salida = io.StringIO()

    with (
        patch("builtins.input", side_effect=["hospital", ""]),
        redirect_stdout(salida),
    ):
        cercanos.main()

    assert "ERROR: Indica la ubicación" in salida.getvalue()


PRUEBAS = [
    ("Reconoce categorías y sinónimos", probar_categorias_y_sinonimos),
    ("Rechaza categorías no disponibles", probar_categoria_no_disponible),
    ("Construye la consulta Overpass", probar_consulta_overpass),
    ("Limita el radio de búsqueda", probar_radio_controlado),
    ("Limita la cantidad de resultados", probar_limite_controlado),
    ("Valida las coordenadas", probar_coordenadas_invalidas),
    ("Envía una solicitud POST identificada", probar_solicitud_post_identificada),
    ("Permite cambiar el servidor", probar_servidor_configurable),
    ("Detecta una configuración vacía", probar_servidor_vacio),
    ("Procesa y ordena los resultados", probar_procesamiento_y_orden),
    ("Omite elementos inválidos", probar_elementos_invalidos_se_omiten),
    ("Controla búsquedas sin resultados", probar_busqueda_sin_resultados),
    ("Aplica límite y caché", probar_limite_y_cache),
    ("Busca alrededor de un lugar", probar_busqueda_por_nombre),
    ("Exige una ubicación", probar_ubicacion_obligatoria),
    ("Controla errores al localizar", probar_error_de_geocodificacion),
    ("Controla errores de conexión", probar_error_de_conexion),
    ("Controla servidores ocupados", probar_servidor_ocupado),
    ("Controla JSON inválido", probar_json_invalido),
    ("Controla estructuras inválidas", probar_estructura_invalida),
    ("Presenta lugares, distancias y fuente", probar_formato),
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
    print("RESUMEN DE LUGARES CERCANOS")
    print("=" * 70)
    print(f"Total de pruebas: {len(PRUEBAS)}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {len(errores)}")
    print(f"Precisión: {correctas / len(PRUEBAS):.2%}")

    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
