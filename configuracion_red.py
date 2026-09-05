import json
import os
from pathlib import Path
import sys


NOMBRE_CONFIGURACION_CLIENTE = "configuracion_cliente.json"
NOMBRE_CONFIGURACION_SERVIDOR = "configuracion_servidor.json"

CONFIGURACION_CLIENTE_PREDETERMINADA = {
    "modo": "local",
    "servidor_url": "http://127.0.0.1:8765",
    "token": "eduia-demostracion-2026",
    "timeout_segundos": 8,
}

CONFIGURACION_SERVIDOR_PREDETERMINADA = {
    "host": "0.0.0.0",
    "puerto": 8765,
    "token": "eduia-demostracion-2026",
}


def carpeta_aplicacion():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


def _cargar_configuracion(nombre, valores_predeterminados):
    configuracion = dict(valores_predeterminados)
    ruta = carpeta_aplicacion() / nombre

    if ruta.is_file():
        try:
            contenido = json.loads(ruta.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ValueError(
                f"No se pudo leer correctamente {nombre}."
            ) from error

        if not isinstance(contenido, dict):
            raise ValueError(f"{nombre} debe contener un objeto JSON.")

        configuracion.update(contenido)

    return configuracion


def cargar_configuracion_cliente():
    configuracion = _cargar_configuracion(
        NOMBRE_CONFIGURACION_CLIENTE,
        CONFIGURACION_CLIENTE_PREDETERMINADA,
    )

    modo_entorno = os.getenv("EDUIA_MODO_DATOS")
    url_entorno = os.getenv("EDUIA_SERVIDOR_URL")
    token_entorno = os.getenv("EDUIA_TOKEN")

    if modo_entorno:
        configuracion["modo"] = modo_entorno
    if url_entorno:
        configuracion["servidor_url"] = url_entorno
    if token_entorno:
        configuracion["token"] = token_entorno

    modo = str(configuracion.get("modo", "local")).strip().casefold()

    if modo not in {"local", "remoto"}:
        raise ValueError("El modo de datos debe ser 'local' o 'remoto'.")

    configuracion["modo"] = modo
    configuracion["servidor_url"] = str(
        configuracion.get("servidor_url", "")
    ).strip().rstrip("/")
    configuracion["token"] = str(
        configuracion.get("token", "")
    ).strip()
    configuracion["timeout_segundos"] = max(
        1,
        min(30, int(configuracion.get("timeout_segundos", 8))),
    )

    if modo == "remoto" and not configuracion["servidor_url"]:
        raise ValueError("Falta la dirección del servidor de EduIA.")

    return configuracion


def cargar_configuracion_servidor():
    configuracion = _cargar_configuracion(
        NOMBRE_CONFIGURACION_SERVIDOR,
        CONFIGURACION_SERVIDOR_PREDETERMINADA,
    )
    configuracion["host"] = str(
        configuracion.get("host", "0.0.0.0")
    ).strip()
    configuracion["puerto"] = int(configuracion.get("puerto", 8765))
    configuracion["token"] = str(
        configuracion.get("token", "")
    ).strip()

    if not configuracion["host"]:
        raise ValueError("Falta la dirección de escucha del servidor.")
    if not 1 <= configuracion["puerto"] <= 65535:
        raise ValueError("El puerto del servidor no es válido.")
    if len(configuracion["token"]) < 8:
        raise ValueError("El token del servidor debe tener al menos 8 caracteres.")

    return configuracion
