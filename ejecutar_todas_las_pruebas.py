from pathlib import Path
import subprocess
import sys
import time


PRUEBAS = (
    "pruebas_actividad4.py",
    "pruebas_validacion.py",
    "pruebas_finales.py",
    "pruebas_independientes_nuevas.py",
    "pruebas_ineditas_v2.py",
    "pruebas_contexto_v1.py",
    "pruebas_internet.py",
    "pruebas_integracion_wikipedia.py",
    "pruebas_clima.py",
    "pruebas_integracion_clima.py",
    "pruebas_ubicaciones.py",
    "pruebas_integracion_ubicaciones.py",
    "pruebas_rutas.py",
    "pruebas_integracion_rutas.py",
    "pruebas_cercanos.py",
    "pruebas_integracion_cercanos.py",
    "pruebas_contexto_externo_v1.py",
    "pruebas_voz.py",
)


def ejecutar_prueba(ruta):
    inicio = time.monotonic()
    proceso = subprocess.run(
        [sys.executable, str(ruta)],
        cwd=ruta.parent,
        check=False,
    )
    duracion = time.monotonic() - inicio
    return proceso.returncode, duracion


def main():
    raiz = Path(__file__).resolve().parent
    resultados = []

    print("=" * 70)
    print("BATERÍA COMPLETA DE EDUIA")
    print("=" * 70)
    print(f"Intérprete: {sys.executable}")
    print(f"Total de archivos: {len(PRUEBAS)}")

    for numero, nombre in enumerate(PRUEBAS, start=1):
        ruta = raiz / nombre
        print("\n" + "-" * 70)
        print(f"[{numero}/{len(PRUEBAS)}] {nombre}")
        print("-" * 70, flush=True)

        if not ruta.is_file():
            print(f"[NO ENCONTRADA] {nombre}")
            resultados.append((nombre, "no_encontrada", 0.0))
            continue

        codigo, duracion = ejecutar_prueba(ruta)
        estado = "correcta" if codigo == 0 else "error"
        resultados.append((nombre, estado, duracion))

        if codigo == 0:
            print(f"[ARCHIVO CORRECTO] {nombre} ({duracion:.2f} s)")
        else:
            print(
                f"[ARCHIVO CON ERROR] {nombre} "
                f"(código {codigo}, {duracion:.2f} s)"
            )

    correctas = sum(
        estado == "correcta"
        for _, estado, _ in resultados
    )
    errores = sum(
        estado == "error"
        for _, estado, _ in resultados
    )
    no_encontradas = sum(
        estado == "no_encontrada"
        for _, estado, _ in resultados
    )
    duracion_total = sum(
        duracion for _, _, duracion in resultados
    )

    print("\n" + "=" * 70)
    print("RESUMEN GENERAL DE PRUEBAS DE EDUIA")
    print("=" * 70)

    for nombre, estado, duracion in resultados:
        etiquetas = {
            "correcta": "CORRECTA",
            "error": "ERROR",
            "no_encontrada": "NO ENCONTRADA",
        }
        print(
            f"[{etiquetas[estado]}] {nombre} "
            f"({duracion:.2f} s)"
        )

    print("-" * 70)
    print(f"Archivos ejecutados correctamente: {correctas}")
    print(f"Archivos con errores: {errores}")
    print(f"Archivos no encontrados: {no_encontradas}")
    print(f"Duración acumulada: {duracion_total:.2f} s")
    print(
        "Resultado general: "
        + (
            "100.00%"
            if correctas == len(PRUEBAS)
            else f"{correctas / len(PRUEBAS):.2%}"
        )
    )

    if errores or no_encontradas:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
