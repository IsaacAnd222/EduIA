import json
import os
from pathlib import Path
import tempfile
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import base_datos
from configuracion_red import cargar_configuracion_cliente
import repositorio_datos
from servidor_eduia import ServidorEduIA


TOKEN_PRUEBA = "token-pruebas-eduia"
SERVIDOR = None
URL_SERVIDOR = None


def configurar_entorno_remoto(token=TOKEN_PRUEBA, url=None):
    os.environ["EDUIA_MODO_DATOS"] = "remoto"
    os.environ["EDUIA_SERVIDOR_URL"] = url or URL_SERVIDOR
    os.environ["EDUIA_TOKEN"] = token


def probar_configuracion_remota_por_entorno():
    configurar_entorno_remoto()
    configuracion = cargar_configuracion_cliente()

    assert configuracion["modo"] == "remoto"
    assert configuracion["servidor_url"] == URL_SERVIDOR


def probar_estado_del_servidor():
    configurar_entorno_remoto()
    solicitud = Request(
        f"{URL_SERVIDOR}/api/v1/salud",
        headers={"X-EduIA-Token": TOKEN_PRUEBA},
    )

    with urlopen(solicitud, timeout=2) as respuesta:
        contenido = json.loads(respuesta.read().decode("utf-8"))

    assert contenido["ok"] is True
    assert contenido["version_api"] == 1


def probar_busqueda_remota_de_estudiante():
    configurar_entorno_remoto()
    estudiante = repositorio_datos.buscar_estudiante("2026001")

    assert estudiante["matricula"] == "2026001"
    assert estudiante["nombre"] == "Isaac Andrade Quiroz"


def probar_consulta_remota_de_materias():
    configurar_entorno_remoto()
    materias = repositorio_datos.obtener_materias_por_semestre(7)

    assert materias
    assert all(materia["semestre"] == 7 for materia in materias)


def probar_historial_y_retroalimentacion_compartidos():
    configurar_entorno_remoto()
    historial_id = repositorio_datos.guardar_consulta_historial(
        "2026001",
        "Consulta compartida de prueba",
        "Respuesta compartida de prueba",
        "escolar",
        "saludo",
        1.0,
    )
    repositorio_datos.guardar_retroalimentacion(historial_id, True)
    historial = repositorio_datos.obtener_historial_por_estudiante(
        "2026001",
        limite=10,
    )

    registro = next(
        elemento for elemento in historial
        if elemento["id"] == historial_id
    )
    assert registro["consulta"] == "Consulta compartida de prueba"
    assert registro["fue_util"] == 1


def probar_operacion_no_permitida():
    configurar_entorno_remoto()
    contenido = json.dumps(
        {
            "operacion": "eliminar_base_de_datos",
            "argumentos": [],
            "parametros": {},
        }
    ).encode("utf-8")
    solicitud = Request(
        f"{URL_SERVIDOR}/api/v1/datos",
        data=contenido,
        headers={
            "Content-Type": "application/json",
            "X-EduIA-Token": TOKEN_PRUEBA,
        },
        method="POST",
    )

    try:
        urlopen(solicitud, timeout=2)
    except HTTPError as error:
        assert error.code == 400
    else:
        raise AssertionError("El servidor aceptó una operación no permitida")


def probar_rechazo_de_token_incorrecto():
    configurar_entorno_remoto(token="token-incorrecto")

    try:
        repositorio_datos.buscar_estudiante("2026001")
    except repositorio_datos.ErrorServidorDatos as error:
        assert "autorizado" in str(error).casefold()
    else:
        raise AssertionError("El servidor aceptó un token incorrecto")


def probar_control_de_servidor_desconectado():
    configurar_entorno_remoto(url="http://127.0.0.1:1")

    try:
        repositorio_datos.buscar_estudiante("2026001")
    except repositorio_datos.ErrorServidorDatos as error:
        assert "conectar" in str(error).casefold()
    else:
        raise AssertionError("No se detectó la desconexión del servidor")


PRUEBAS = (
    ("Carga la configuración remota", probar_configuracion_remota_por_entorno),
    ("Publica el estado del servidor", probar_estado_del_servidor),
    ("Busca estudiantes mediante la API", probar_busqueda_remota_de_estudiante),
    ("Consulta materias mediante la API", probar_consulta_remota_de_materias),
    (
        "Comparte historial y retroalimentación",
        probar_historial_y_retroalimentacion_compartidos,
    ),
    ("Rechaza operaciones no permitidas", probar_operacion_no_permitida),
    ("Rechaza tokens incorrectos", probar_rechazo_de_token_incorrecto),
    ("Controla un servidor desconectado", probar_control_de_servidor_desconectado),
)


def main():
    global SERVIDOR, URL_SERVIDOR

    carpeta_original = base_datos.CARPETA_DATOS
    ruta_original = base_datos.RUTA_BASE_DATOS
    temporal = tempfile.TemporaryDirectory()
    base_datos.CARPETA_DATOS = Path(temporal.name) / "data"
    base_datos.RUTA_BASE_DATOS = base_datos.CARPETA_DATOS / "eduia.db"
    correctas = 0
    errores = []

    try:
        base_datos.crear_base_datos()
        SERVIDOR = ServidorEduIA(("127.0.0.1", 0), TOKEN_PRUEBA)
        URL_SERVIDOR = f"http://127.0.0.1:{SERVIDOR.server_port}"
        hilo = threading.Thread(target=SERVIDOR.serve_forever, daemon=True)
        hilo.start()

        for nombre, prueba in PRUEBAS:
            try:
                prueba()
                correctas += 1
                print(f"[CORRECTA] {nombre}")
            except Exception as error:
                errores.append((nombre, error))
                print(f"[ERROR] {nombre}: {error}")
    finally:
        if SERVIDOR is not None:
            SERVIDOR.shutdown()
            SERVIDOR.server_close()
            hilo.join(timeout=2)

        for variable in (
            "EDUIA_MODO_DATOS",
            "EDUIA_SERVIDOR_URL",
            "EDUIA_TOKEN",
        ):
            os.environ.pop(variable, None)

        base_datos.CARPETA_DATOS = carpeta_original
        base_datos.RUTA_BASE_DATOS = ruta_original
        temporal.cleanup()

    total = len(PRUEBAS)
    print("\n" + "=" * 70)
    print("RESUMEN DEL SERVIDOR COMPARTIDO")
    print("=" * 70)
    print(f"Total de pruebas: {total}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {len(errores)}")
    print(f"Precisión: {correctas / total:.2%}")

    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
