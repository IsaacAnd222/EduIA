import json
import os
from pathlib import Path
import secrets
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from configuracion_red import cargar_configuracion_servidor


if getattr(sys, "frozen", False):
    carpeta_local = Path(
        os.getenv("LOCALAPPDATA", Path.home())
    ) / "EduIA" / "Servidor" / "data"
    os.environ.setdefault("EDUIA_CARPETA_DATOS", str(carpeta_local))


import base_datos


OPERACIONES_PERMITIDAS = {
    "crear_base_datos": base_datos.crear_base_datos,
    "buscar_estudiante": base_datos.buscar_estudiante,
    "obtener_materias_por_semestre": base_datos.obtener_materias_por_semestre,
    "obtener_todas_las_materias": base_datos.obtener_todas_las_materias,
    "obtener_asignaciones_por_semestre": base_datos.obtener_asignaciones_por_semestre,
    "obtener_horario_por_estudiante": base_datos.obtener_horario_por_estudiante,
    "obtener_calificaciones_por_estudiante": base_datos.obtener_calificaciones_por_estudiante,
    "obtener_examenes_por_estudiante": base_datos.obtener_examenes_por_estudiante,
    "obtener_avisos_por_estudiante": base_datos.obtener_avisos_por_estudiante,
    "obtener_contenidos_academicos": base_datos.obtener_contenidos_academicos,
    "guardar_consulta_historial": base_datos.guardar_consulta_historial,
    "obtener_historial_por_estudiante": base_datos.obtener_historial_por_estudiante,
    "guardar_retroalimentacion": base_datos.guardar_retroalimentacion,
}

MAXIMO_SOLICITUD_BYTES = 1_000_000


class ServidorEduIA(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, direccion, token):
        super().__init__(direccion, ManejadorEduIA)
        self.token = token


class ManejadorEduIA(BaseHTTPRequestHandler):
    server_version = "ServidorEduIA/1.0"

    def _responder(self, codigo, contenido):
        datos = json.dumps(
            contenido,
            ensure_ascii=False,
        ).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(datos)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(datos)

    def _esta_autorizado(self):
        token_recibido = self.headers.get("X-EduIA-Token", "")
        return secrets.compare_digest(token_recibido, self.server.token)

    def do_GET(self):
        if self.path != "/api/v1/salud":
            self._responder(404, {"ok": False, "error": "Ruta no encontrada."})
            return

        if not self._esta_autorizado():
            self._responder(401, {"ok": False, "error": "Acceso no autorizado."})
            return

        self._responder(
            200,
            {
                "ok": True,
                "servicio": "Servidor EduIA",
                "version_api": 1,
            },
        )

    def do_POST(self):
        if self.path != "/api/v1/datos":
            self._responder(404, {"ok": False, "error": "Ruta no encontrada."})
            return

        if not self._esta_autorizado():
            self._responder(401, {"ok": False, "error": "Acceso no autorizado."})
            return

        try:
            longitud = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            longitud = 0

        if not 0 < longitud <= MAXIMO_SOLICITUD_BYTES:
            self._responder(400, {"ok": False, "error": "Solicitud inválida."})
            return

        try:
            contenido = json.loads(self.rfile.read(longitud).decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            self._responder(400, {"ok": False, "error": "JSON inválido."})
            return

        operacion = contenido.get("operacion") if isinstance(contenido, dict) else None
        argumentos = contenido.get("argumentos", []) if isinstance(contenido, dict) else []
        parametros = contenido.get("parametros", {}) if isinstance(contenido, dict) else {}
        funcion = OPERACIONES_PERMITIDAS.get(operacion)

        if funcion is None:
            self._responder(400, {"ok": False, "error": "Operación no permitida."})
            return
        if not isinstance(argumentos, list) or not isinstance(parametros, dict):
            self._responder(400, {"ok": False, "error": "Parámetros inválidos."})
            return

        try:
            resultado = funcion(*argumentos, **parametros)
        except (TypeError, ValueError) as error:
            self._responder(400, {"ok": False, "error": str(error)})
            return
        except Exception:
            self._responder(
                500,
                {"ok": False, "error": "Ocurrió un problema interno en el servidor."},
            )
            return

        self._responder(200, {"ok": True, "resultado": resultado})

    def log_message(self, formato, *argumentos):
        print(
            f"[{self.log_date_time_string()}] "
            f"{self.client_address[0]} - {formato % argumentos}"
        )


def main():
    configuracion = cargar_configuracion_servidor()
    base_datos.crear_base_datos()
    servidor = ServidorEduIA(
        (configuracion["host"], configuracion["puerto"]),
        configuracion["token"],
    )

    print("=" * 70)
    print("SERVIDOR CENTRAL DE EDUIA")
    print("=" * 70)
    print(f"Puerto: {configuracion['puerto']}")
    print(f"Base de datos: {base_datos.RUTA_BASE_DATOS}")
    print("Estado: listo para recibir conexiones")
    print("Presiona Ctrl+C para detenerlo.")

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo el servidor de EduIA...")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
