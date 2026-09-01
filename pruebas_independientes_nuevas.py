from collections import defaultdict

from eduia import buscar_respuesta


PRUEBAS = [
    # Preguntas naturales: tres ejemplos nuevos por intención.
    ("Natural", "Hola de nuevo, ¿cómo va todo?", "saludo"),
    ("Natural", "Buenas noches, asistente", "saludo"),
    ("Natural", "Qué gusto saludarte, EduIA", "saludo"),
    (
        "Natural",
        "Enumera los asuntos en los que puedes orientarme",
        "capacidades",
    ),
    (
        "Natural",
        "¿Hasta dónde llega tu ayuda universitaria?",
        "capacidades",
    ),
    (
        "Natural",
        "¿Qué servicios puedes consultar por mí?",
        "capacidades",
    ),
    (
        "Natural",
        "¿En qué bloque del día aparece mi clase de Redes de Computadoras II?",
        "horario",
    ),
    (
        "Natural",
        "Localiza el salón y la hora de Sistemas Embebidos",
        "horario",
    ),
    (
        "Natural",
        "¿Qué clase tengo después del receso?",
        "horario",
    ),
    (
        "Natural",
        "¿Cómo está integrada mi carga académica?",
        "materia",
    ),
    (
        "Natural",
        "Enumera las asignaturas que pertenecen a mi semestre",
        "materia",
    ),
    (
        "Natural",
        "¿Cuántas materias curso actualmente?",
        "materia",
    ),
    (
        "Natural",
        "¿Qué evaluación presentaré primero?",
        "examen",
    ),
    (
        "Natural",
        "Consulta el día y el salón de mi siguiente parcial",
        "examen",
    ),
    (
        "Natural",
        "¿Tengo algún examen pendiente este mes?",
        "examen",
    ),
    (
        "Natural",
        "¿Cuál es el nombre del docente de Inteligencia Artificial?",
        "profesor",
    ),
    (
        "Natural",
        "Necesito contactar al profesor responsable de Seminario de Titulación",
        "profesor",
    ),
    (
        "Natural",
        "Dame el correo del maestro de Redes de Computadoras II",
        "profesor",
    ),
    (
        "Natural",
        "¿Cuál fue mi resultado en Sistemas Embebidos?",
        "calificacion",
    ),
    (
        "Natural",
        "Quiero saber si tengo alguna materia reprobada",
        "calificacion",
    ),
    (
        "Natural",
        "Consulta mis notas del semestre",
        "calificacion",
    ),
    (
        "Natural",
        "¿Publicaron algún comunicado para séptimo semestre?",
        "aviso",
    ),
    (
        "Natural",
        "Revisa si hay avisos recientes",
        "aviso",
    ),
    (
        "Natural",
        "¿Qué anuncios escolares siguen vigentes?",
        "aviso",
    ),
    (
        "Natural",
        "Explícame qué es un semáforo en un RTOS",
        "academica",
    ),
    (
        "Natural",
        "Ayúdame a resolver un ejercicio de pseudocódigo",
        "academica",
    ),
    (
        "Natural",
        "Propón una práctica para entender redes neuronales",
        "academica",
    ),
    (
        "Natural",
        "¿Cuándo puedo confirmar mi carga para el nuevo ciclo?",
        "inscripcion",
    ),
    (
        "Natural",
        "¿Qué pasos debo completar para quedar reinscrito?",
        "inscripcion",
    ),
    (
        "Natural",
        "¿En qué área valido mi registro semestral?",
        "inscripcion",
    ),
    (
        "Natural",
        "¿Cuánto tiempo puedo conservar un libro prestado?",
        "biblioteca",
    ),
    (
        "Natural",
        "¿La biblioteca cuenta con material digital?",
        "biblioteca",
    ),
    (
        "Natural",
        "¿Dónde renuevo el préstamo de un libro?",
        "biblioteca",
    ),
    (
        "Natural",
        "¿Qué apoyos económicos puedo solicitar este ciclo?",
        "beca",
    ),
    (
        "Natural",
        "¿Dónde reviso el estado de mi solicitud de beca?",
        "beca",
    ),
    (
        "Natural",
        "¿Qué condiciones debo cumplir para mantener el apoyo?",
        "beca",
    ),
    (
        "Natural",
        "¿Qué alternativas de titulación reconoce la universidad?",
        "titulacion",
    ),
    (
        "Natural",
        "¿Dónde inicio el expediente para obtener mi título?",
        "titulacion",
    ),
    (
        "Natural",
        "¿Puedo obtener el grado mediante promedio?",
        "titulacion",
    ),
    (
        "Natural",
        "¿Qué debo presentar para ingresar al laboratorio?",
        "laboratorio",
    ),
    (
        "Natural",
        "¿Con cuánta anticipación reservo una práctica de cómputo?",
        "laboratorio",
    ),
    (
        "Natural",
        "¿Dónde consulto la disponibilidad del laboratorio?",
        "laboratorio",
    ),
    (
        "Natural",
        "¿Qué bebidas ofrecen hoy en la cafetería?",
        "cafeteria",
    ),
    (
        "Natural",
        "¿Puedo pagar el almuerzo con tarjeta?",
        "cafeteria",
    ),
    (
        "Natural",
        "¿En qué horario venden alimentos?",
        "cafeteria",
    ),

    # Errores ortográficos nuevos: uno por intención.
    ("Ortográfica", "Ola de nuebo, EduIA", "saludo"),
    (
        "Ortográfica",
        "¿Ke puedes aser por mi como asistente?",
        "capacidades",
    ),
    (
        "Ortográfica",
        "¿En ke salon esta mi clace de redes dos?",
        "horario",
    ),
    (
        "Ortográfica",
        "¿Ke asignaturras yebo este semestre?",
        "materia",
    ),
    (
        "Ortográfica",
        "¿Kuando tengo mi procsima evaluasion?",
        "examen",
    ),
    (
        "Ortográfica",
        "Dame el correo del dozente de intelijencia artificial",
        "profesor",
    ),
    (
        "Ortográfica",
        "¿Ke nota obtube en sistemas emvevidos?",
        "calificacion",
    ),
    (
        "Ortográfica",
        "¿Ai algun abiso nuebo para mi grupo?",
        "aviso",
    ),
    (
        "Ortográfica",
        "Explicame un ejersisio de algoritmos",
        "academica",
    ),
    (
        "Ortográfica",
        "¿Komo renuebo mi inscripsion?",
        "inscripcion",
    ),
    (
        "Ortográfica",
        "¿La viblioteca tiene livros dijitales?",
        "biblioteca",
    ),
    (
        "Ortográfica",
        "¿Ke apollo ekonomiko ofrecen a estudiantes?",
        "beca",
    ),
    (
        "Ortográfica",
        "¿Ke modalidades de titulasion existen?",
        "titulacion",
    ),
    (
        "Ortográfica",
        "¿Komo puedo rezervar el lavoratorio?",
        "laboratorio",
    ),
    (
        "Ortográfica",
        "¿Kuanto kuesta el menu de la cafeterya?",
        "cafeteria",
    ),

    # Consultas sin contexto suficiente.
    ("Ambigua", "¿Dónde debo presentarme?", "desconocida"),
    ("Ambigua", "¿Qué tengo pendiente?", "desconocida"),
    ("Ambigua", "¿Quién puede ayudarme con eso?", "desconocida"),
    ("Ambigua", "¿Cuándo termina?", "desconocida"),
    ("Ambigua", "¿Dónde está ubicado?", "desconocida"),
    ("Ambigua", "¿Qué requisitos solicitan?", "desconocida"),
    ("Ambigua", "¿Puedo renovarlo?", "desconocida"),
    ("Ambigua", "¿Cuál debo escoger?", "desconocida"),
    ("Ambigua", "¿A quién se lo entrego?", "desconocida"),
    ("Ambigua", "¿Hay cupo?", "desconocida"),

    # Temas fuera del alcance actual de EduIA.
    (
        "Desconocida",
        "¿Cuál es el precio del dólar hoy?",
        "desconocida",
    ),
    ("Desconocida", "Busca una receta de pastel", "desconocida"),
    ("Desconocida", "¿Qué equipo ganó la liga?", "desconocida"),
    ("Desconocida", "Reproduce música relajante", "desconocida"),
    (
        "Desconocida",
        "¿Dónde reparan teléfonos celulares?",
        "desconocida",
    ),
    (
        "Desconocida",
        "¿Qué síntomas tiene la gripe?",
        "desconocida",
    ),
    (
        "Desconocida",
        "Muéstrame ofertas de computadoras",
        "desconocida",
    ),
    (
        "Desconocida",
        "¿Cómo llego al aeropuerto?",
        "desconocida",
    ),
    (
        "Desconocida",
        "¿Quién es el presidente del país?",
        "desconocida",
    ),
    (
        "Desconocida",
        "Genera una imagen de un gato",
        "desconocida",
    ),
]


def ejecutar_pruebas():
    resultados_tipo = defaultdict(
        lambda: {"total": 0, "correctas": 0}
    )
    errores = []

    print("=" * 110)
    print("NUEVA EVALUACIÓN INDEPENDIENTE DE EDUIA")
    print("=" * 110)

    for numero, (tipo_prueba, pregunta, esperado) in enumerate(
        PRUEBAS,
        start=1,
    ):
        _, _, obtenido, confianza = buscar_respuesta(
            pregunta
        )
        correcto = obtenido == esperado

        resultados_tipo[tipo_prueba]["total"] += 1

        if correcto:
            resultados_tipo[tipo_prueba]["correctas"] += 1
        else:
            errores.append(
                (
                    numero,
                    tipo_prueba,
                    pregunta,
                    esperado,
                    obtenido,
                    confianza,
                )
            )

        print(f"\nPrueba {numero} — {tipo_prueba}")
        print(f"Pregunta:   {pregunta}")
        print(f"Esperado:   {esperado}")
        print(f"Resultado:  {obtenido}")
        print(f"Confianza:  {confianza:.0%}")
        print(
            "Evaluación: "
            + ("CORRECTO" if correcto else "ERROR")
        )

    total = len(PRUEBAS)
    correctas = total - len(errores)
    precision = correctas / total * 100

    print("\n" + "=" * 110)
    print("RESULTADOS POR TIPO")
    print("=" * 110)

    for tipo_prueba, valores in resultados_tipo.items():
        total_tipo = valores["total"]
        correctas_tipo = valores["correctas"]
        precision_tipo = correctas_tipo / total_tipo * 100

        print(
            f"{tipo_prueba}: {correctas_tipo}/{total_tipo} "
            f"({precision_tipo:.2f}%)"
        )

    print("\n" + "=" * 110)
    print("RESUMEN DE LA NUEVA EVALUACIÓN")
    print("=" * 110)
    print(f"Total de pruebas: {total}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {len(errores)}")
    print(f"Precisión independiente real: {precision:.2f}%")

    if errores:
        print("\nERRORES NUEVOS")
        print("-" * 110)

        for (
            numero,
            tipo_prueba,
            pregunta,
            esperado,
            obtenido,
            confianza,
        ) in errores:
            print(f"{numero}. [{tipo_prueba}] {pregunta}")
            print(
                f"   Esperado: {esperado} | "
                f"Obtenido: {obtenido} | "
                f"Confianza: {confianza:.0%}"
            )


if __name__ == "__main__":
    ejecutar_pruebas()
