from base_datos import buscar_estudiante, crear_base_datos
from eduia import crear_contexto_conversacional, procesar_consulta


def consultar(pregunta, estudiante, contexto):
    respuesta, tipo, categoria, confianza, _ = procesar_consulta(
        pregunta,
        estudiante,
        contexto,
    )

    return respuesta, tipo, categoria, confianza


def main():
    crear_base_datos()
    estudiante = buscar_estudiante("2026001")

    if estudiante is None:
        raise RuntimeError("No se encontró al estudiante de prueba.")

    resultados = []

    def verificar(nombre, condicion):
        resultados.append((nombre, bool(condicion)))
        estado = "CORRECTA" if condicion else "ERROR"
        print(f"[{estado}] {nombre}")

    contexto = crear_contexto_conversacional()
    consultar("¿Dónde está la biblioteca?", estudiante, contexto)
    respuesta = consultar("¿A qué hora abre?", estudiante, contexto)
    verificar(
        "Hereda Biblioteca en una pregunta de horario",
        respuesta[2] == "biblioteca"
        and "Horario de Biblioteca" in respuesta[0],
    )

    contexto = crear_contexto_conversacional()
    consultar("¿Cuánto cuesta un taco?", estudiante, contexto)
    respuesta = consultar("¿Y una quesadilla?", estudiante, contexto)
    verificar(
        "Conserva la intención de consultar un precio",
        respuesta[2] == "cafeteria"
        and "$20" in respuesta[0],
    )

    contexto = crear_contexto_conversacional()
    consultar(
        "¿Cómo puedo reservar el laboratorio?",
        estudiante,
        contexto,
    )
    respuesta = consultar("¿Quién lo autoriza?", estudiante, contexto)
    verificar(
        "Resuelve una referencia al laboratorio",
        respuesta[2] == "laboratorio"
        and "Adrián Morales Vega" in respuesta[0],
    )

    contexto = crear_contexto_conversacional()
    consultar("¿Qué exámenes tengo?", estudiante, contexto)
    respuesta = consultar(
        "¿Y el de Inteligencia Artificial?",
        estudiante,
        contexto,
    )
    verificar(
        "Conserva la categoría Examen y cambia de materia",
        respuesta[2] == "examen"
        and "Inteligencia Artificial" in respuesta[0],
    )

    contexto = crear_contexto_conversacional()
    consultar(
        "¿Cuándo es el avance de Seminario de Titulación?",
        estudiante,
        contexto,
    )
    respuesta = consultar("¿Y cuándo es?", estudiante, contexto)
    verificar(
        "Recuerda el aviso de Seminario",
        respuesta[2] == "aviso"
        and "21/09/2026" in respuesta[0],
    )

    contexto = crear_contexto_conversacional()
    consultar("¿Dónde está la biblioteca?", estudiante, contexto)
    respuesta = consultar(
        "¿A qué hora abre la cafetería?",
        estudiante,
        contexto,
    )
    verificar(
        "Permite cambiar explícitamente de tema",
        respuesta[2] == "cafeteria"
        and "Horario de las cafeterías" in respuesta[0],
    )

    contexto = crear_contexto_conversacional()
    consultar("¿Dónde está la biblioteca?", estudiante, contexto)
    respuesta = consultar(
        "¿Cuál es la mejor computadora?",
        estudiante,
        contexto,
    )
    verificar(
        "No fuerza contexto sobre una consulta externa",
        respuesta[2] == "desconocida",
    )

    contexto = crear_contexto_conversacional()
    respuesta = consultar("¿A qué hora abre?", estudiante, contexto)
    verificar(
        "Sin contexto solicita una pregunta más específica",
        respuesta[2] == "desconocida",
    )

    correctas = sum(resultado for _, resultado in resultados)
    total = len(resultados)

    print("\n" + "=" * 70)
    print("RESUMEN DE MEMORIA CONVERSACIONAL")
    print("=" * 70)
    print(f"Total de pruebas: {total}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {total - correctas}")
    print(f"Precisión: {(correctas / total) * 100:.2f}%")

    if correctas != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
