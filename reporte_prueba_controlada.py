import argparse
import csv
import sqlite3

from collections import Counter
from datetime import datetime
from pathlib import Path

from base_datos import RUTA_BASE_DATOS


CARPETA_PROYECTO = Path(__file__).resolve().parent
CARPETA_REPORTES = CARPETA_PROYECTO / "reportes"


def validar_fecha(valor):
    try:
        datetime.strptime(valor, "%Y-%m-%d")
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "La fecha debe escribirse como AAAA-MM-DD."
        ) from error

    return valor


def leer_argumentos():
    analizador = argparse.ArgumentParser(
        description=(
            "Exporta el historial y la retroalimentación de "
            "la prueba controlada de EduIA."
        )
    )

    analizador.add_argument(
        "--desde",
        type=validar_fecha,
        help="Fecha inicial en formato AAAA-MM-DD.",
    )
    analizador.add_argument(
        "--hasta",
        type=validar_fecha,
        help="Fecha final en formato AAAA-MM-DD.",
    )
    analizador.add_argument(
        "--matricula",
        help="Exporta únicamente las consultas de una matrícula.",
    )
    analizador.add_argument(
        "--ultimas",
        type=int,
        help="Exporta únicamente las últimas N consultas.",
    )

    argumentos = analizador.parse_args()

    if (
        argumentos.desde
        and argumentos.hasta
        and argumentos.desde > argumentos.hasta
    ):
        analizador.error(
            "La fecha inicial no puede ser posterior a la final."
        )

    if argumentos.ultimas is not None and argumentos.ultimas <= 0:
        analizador.error("El valor de --ultimas debe ser mayor que cero.")

    return argumentos


def obtener_consultas(
    desde=None,
    hasta=None,
    matricula=None,
    ultimas=None,
):
    condiciones = []
    parametros = []

    if desde:
        condiciones.append("date(h.fecha_hora) >= date(?)")
        parametros.append(desde)

    if hasta:
        condiciones.append("date(h.fecha_hora) <= date(?)")
        parametros.append(hasta)

    if matricula:
        condiciones.append("h.estudiante_matricula = ?")
        parametros.append(matricula)

    clausula_where = ""

    if condiciones:
        clausula_where = "WHERE " + " AND ".join(condiciones)

    consulta_sql = f"""
        SELECT
            h.id,
            h.fecha_hora,
            h.estudiante_matricula,
            e.nombre AS estudiante,
            e.semestre,
            e.grupo,
            h.consulta,
            h.respuesta,
            h.tipo,
            h.categoria,
            h.confianza,
            r.fue_util
        FROM historial_consultas AS h
        INNER JOIN estudiantes AS e
            ON e.matricula = h.estudiante_matricula
        LEFT JOIN retroalimentaciones AS r
            ON r.historial_id = h.id
        {clausula_where}
        ORDER BY h.fecha_hora, h.id
    """

    with sqlite3.connect(RUTA_BASE_DATOS) as conexion:
        conexion.row_factory = sqlite3.Row
        filas = conexion.execute(
            consulta_sql,
            parametros,
        ).fetchall()

    consultas = [dict(fila) for fila in filas]

    if ultimas is not None:
        consultas = consultas[-ultimas:]

    return consultas


def texto_valoracion(valor):
    if valor == 1:
        return "Sí"

    if valor == 0:
        return "No"

    return "Sin evaluar"


def exportar_csv(consultas, ruta_csv):
    encabezados = [
        "ID",
        "Fecha y hora",
        "Matrícula",
        "Estudiante",
        "Semestre",
        "Grupo",
        "Pregunta",
        "Respuesta",
        "Tipo",
        "Categoría obtenida",
        "Confianza",
        "¿Fue útil?",
        "Categoría esperada",
        "Observaciones",
    ]

    with ruta_csv.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(encabezados)

        for consulta in consultas:
            escritor.writerow(
                [
                    consulta["id"],
                    consulta["fecha_hora"],
                    consulta["estudiante_matricula"],
                    consulta["estudiante"],
                    consulta["semestre"],
                    consulta["grupo"],
                    consulta["consulta"],
                    consulta["respuesta"],
                    consulta["tipo"],
                    consulta["categoria"],
                    f'{consulta["confianza"]:.2%}',
                    texto_valoracion(consulta["fue_util"]),
                    "",
                    "",
                ]
            )


def construir_resumen(consultas, filtros):
    total = len(consultas)
    utiles = sum(c["fue_util"] == 1 for c in consultas)
    no_utiles = sum(c["fue_util"] == 0 for c in consultas)
    sin_evaluar = sum(c["fue_util"] is None for c in consultas)
    evaluadas = utiles + no_utiles
    desconocidas = sum(
        c["categoria"] == "desconocida"
        for c in consultas
    )

    confianza_promedio = (
        sum(c["confianza"] for c in consultas) / total
        if total
        else 0.0
    )

    utilidad = utiles / evaluadas if evaluadas else 0.0
    categorias = Counter(c["categoria"] for c in consultas)
    estudiantes = Counter(c["estudiante"] for c in consultas)

    lineas = [
        "REPORTE DE PRUEBA CONTROLADA DE EDUIA",
        "=" * 70,
        f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        f"Filtros: {filtros}",
        "",
        "RESUMEN GENERAL",
        "-" * 70,
        f"Consultas registradas: {total}",
        f"Valoradas como útiles: {utiles}",
        f"Valoradas como no útiles: {no_utiles}",
        f"Consultas sin evaluar: {sin_evaluar}",
        f"Utilidad entre consultas evaluadas: {utilidad:.2%}",
        f"Consultas desconocidas: {desconocidas}",
        f"Confianza promedio: {confianza_promedio:.2%}",
        "",
        "CONSULTAS POR ESTUDIANTE",
        "-" * 70,
    ]

    if estudiantes:
        for estudiante, cantidad in sorted(estudiantes.items()):
            lineas.append(f"{estudiante}: {cantidad}")
    else:
        lineas.append("No hay consultas para los filtros seleccionados.")

    lineas.extend(
        [
            "",
            "DISTRIBUCIÓN POR CATEGORÍA",
            "-" * 70,
        ]
    )

    if categorias:
        for categoria, cantidad in sorted(categorias.items()):
            lineas.append(f"{categoria}: {cantidad}")
    else:
        lineas.append("No hay categorías registradas.")

    consultas_revision = [
        consulta
        for consulta in consultas
        if (
            consulta["fue_util"] == 0
            or consulta["categoria"] == "desconocida"
            or consulta["confianza"] < 0.60
        )
    ]

    lineas.extend(
        [
            "",
            "CONSULTAS QUE REQUIEREN REVISIÓN",
            "-" * 70,
        ]
    )

    if consultas_revision:
        for consulta in consultas_revision:
            lineas.extend(
                [
                    f'ID {consulta["id"]} | '
                    f'{consulta["estudiante"]}',
                    f'Pregunta: {consulta["consulta"]}',
                    f'Categoría: {consulta["categoria"]} | '
                    f'Confianza: {consulta["confianza"]:.2%} | '
                    f'Útil: {texto_valoracion(consulta["fue_util"])}',
                    "",
                ]
            )
    else:
        lineas.append("No se detectaron consultas para revisión.")

    return "\n".join(lineas)


def main():
    argumentos = leer_argumentos()

    if not RUTA_BASE_DATOS.exists():
        raise FileNotFoundError(
            f"No se encontró la base de datos: {RUTA_BASE_DATOS}"
        )

    consultas = obtener_consultas(
        desde=argumentos.desde,
        hasta=argumentos.hasta,
        matricula=argumentos.matricula,
        ultimas=argumentos.ultimas,
    )

    CARPETA_REPORTES.mkdir(exist_ok=True)
    marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")

    ruta_csv = (
        CARPETA_REPORTES
        / f"prueba_controlada_{marca_tiempo}.csv"
    )
    ruta_txt = (
        CARPETA_REPORTES
        / f"resumen_controlado_{marca_tiempo}.txt"
    )

    filtros = (
        f"desde={argumentos.desde or 'sin límite'}, "
        f"hasta={argumentos.hasta or 'sin límite'}, "
        f"matrícula={argumentos.matricula or 'todas'}, "
        f"últimas={argumentos.ultimas or 'sin límite'}"
    )

    exportar_csv(consultas, ruta_csv)
    resumen = construir_resumen(consultas, filtros)
    ruta_txt.write_text(resumen, encoding="utf-8")

    print(resumen)
    print("\nArchivos generados:")
    print(f"- {ruta_csv}")
    print(f"- {ruta_txt}")


if __name__ == "__main__":
    main()
