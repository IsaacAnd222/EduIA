import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import base_datos as datos_locales
from configuracion_red import cargar_configuracion_cliente


class ErrorServidorDatos(RuntimeError):
    pass


def _invocar_remoto(operacion, *argumentos, **parametros):
    configuracion = cargar_configuracion_cliente()
    contenido = json.dumps(
        {
            "operacion": operacion,
            "argumentos": argumentos,
            "parametros": parametros,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    solicitud = Request(
        f"{configuracion['servidor_url']}/api/v1/datos",
        data=contenido,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "X-EduIA-Token": configuracion["token"],
        },
        method="POST",
    )

    try:
        with urlopen(
            solicitud,
            timeout=configuracion["timeout_segundos"],
        ) as respuesta:
            resultado = json.loads(respuesta.read().decode("utf-8"))
    except HTTPError as error:
        try:
            detalle = json.loads(error.read().decode("utf-8")).get(
                "error"
            )
        except Exception:
            detalle = None

        raise ErrorServidorDatos(
            detalle or "El servidor rechazó la solicitud."
        ) from error
    except (URLError, TimeoutError, OSError) as error:
        raise ErrorServidorDatos(
            "No se pudo conectar con el servidor de EduIA. "
            "Verifica que esté encendido y que ambos equipos "
            "estén conectados a la misma red."
        ) from error
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ErrorServidorDatos(
            "El servidor devolvió una respuesta que no se pudo entender."
        ) from error

    if not isinstance(resultado, dict) or not resultado.get("ok"):
        raise ErrorServidorDatos(
            resultado.get("error", "La respuesta del servidor es inválida.")
            if isinstance(resultado, dict)
            else "La respuesta del servidor es inválida."
        )

    return resultado.get("resultado")


def _invocar(operacion, *argumentos, **parametros):
    configuracion = cargar_configuracion_cliente()

    if configuracion["modo"] == "remoto":
        return _invocar_remoto(operacion, *argumentos, **parametros)

    funcion = getattr(datos_locales, operacion)
    return funcion(*argumentos, **parametros)


def crear_base_datos():
    return _invocar("crear_base_datos")


def buscar_estudiante(matricula):
    return _invocar("buscar_estudiante", matricula)


def obtener_materias_por_semestre(semestre):
    return _invocar("obtener_materias_por_semestre", semestre)


def obtener_todas_las_materias():
    return _invocar("obtener_todas_las_materias")


def obtener_asignaciones_por_semestre(semestre):
    return _invocar("obtener_asignaciones_por_semestre", semestre)


def obtener_horario_por_estudiante(matricula):
    return _invocar("obtener_horario_por_estudiante", matricula)


def obtener_calificaciones_por_estudiante(matricula):
    return _invocar("obtener_calificaciones_por_estudiante", matricula)


def obtener_examenes_por_estudiante(matricula):
    return _invocar("obtener_examenes_por_estudiante", matricula)


def obtener_avisos_por_estudiante(matricula):
    return _invocar("obtener_avisos_por_estudiante", matricula)


def obtener_contenidos_academicos():
    return _invocar("obtener_contenidos_academicos")


def guardar_consulta_historial(
    matricula,
    consulta,
    respuesta,
    tipo,
    categoria,
    confianza,
):
    return _invocar(
        "guardar_consulta_historial",
        matricula,
        consulta,
        respuesta,
        tipo,
        categoria,
        confianza,
    )


def obtener_historial_por_estudiante(matricula, limite=50):
    return _invocar(
        "obtener_historial_por_estudiante",
        matricula,
        limite=limite,
    )


def guardar_retroalimentacion(historial_id, fue_util):
    return _invocar(
        "guardar_retroalimentacion",
        historial_id,
        fue_util,
    )
