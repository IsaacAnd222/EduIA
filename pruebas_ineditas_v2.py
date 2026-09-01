from collections import defaultdict

from eduia import buscar_respuesta


PRUEBAS = [
    # Naturales: cuatro preguntas nuevas por intención.
    ("Natural", "Hola, vengo a realizar una consulta", "saludo"),
    ("Natural", "Muy buen día, EduIA", "saludo"),
    ("Natural", "Buenas, ¿me escuchas?", "saludo"),
    ("Natural", "Qué tal va tu día, asistente", "saludo"),

    ("Natural", "Indícame las áreas en las que brindas orientación", "capacidades"),
    ("Natural", "¿Qué clase de información universitaria manejas?", "capacidades"),
    ("Natural", "¿Cuáles son tus funciones dentro del sistema?", "capacidades"),
    ("Natural", "Antes de empezar, dime en qué puedes apoyarme", "capacidades"),

    ("Natural", "¿Dónde y a qué hora curso Inteligencia Artificial?", "horario"),
    ("Natural", "Ordena las clases que tengo durante mi jornada", "horario"),
    ("Natural", "¿Cuál es la última clase que aparece en mi día?", "horario"),
    ("Natural", "Necesito localizar Redes II dentro de mi horario", "horario"),

    ("Natural", "Muéstrame la composición de mi semestre", "materia"),
    ("Natural", "¿Qué unidades de aprendizaje tengo registradas?", "materia"),
    ("Natural", "Haz una relación de las asignaturas que estoy cursando", "materia"),
    ("Natural", "Quiero revisar mi carga escolar actual", "materia"),

    ("Natural", "¿Qué parcial tengo más cercano?", "examen"),
    ("Natural", "Consulta cuándo y dónde será mi siguiente evaluación", "examen"),
    ("Natural", "¿Existe algún examen programado para Redes II?", "examen"),
    ("Natural", "Dime qué prueba académica presentaré después", "examen"),

    ("Natural", "¿Quién es la persona docente responsable de Sistemas Embebidos?", "profesor"),
    ("Natural", "Localiza el contacto del maestro de Seminario de Titulación", "profesor"),
    ("Natural", "¿A quién le corresponde impartir Inteligencia Artificial?", "profesor"),
    ("Natural", "Necesito los datos del profesor que enseña Redes II", "profesor"),

    ("Natural", "¿Qué resultado conseguí en Inteligencia Artificial?", "calificacion"),
    ("Natural", "Revisa si acredité todas mis asignaturas", "calificacion"),
    ("Natural", "Enséñame las notas registradas en mi boleta", "calificacion"),
    ("Natural", "¿Cuál es mi desempeño académico hasta ahora?", "calificacion"),

    ("Natural", "¿Se publicó algún mensaje importante para estudiantes?", "aviso"),
    ("Natural", "Consulta los comunicados que todavía están activos", "aviso"),
    ("Natural", "¿Tengo notificaciones escolares recientes?", "aviso"),
    ("Natural", "Muéstrame las novedades oficiales de la universidad", "aviso"),

    ("Natural", "Enséñame el funcionamiento de una red neuronal", "academica"),
    ("Natural", "¿Puedes darme un ejemplo de planificación de procesos?", "academica"),
    ("Natural", "Ayúdame a estudiar interrupciones en sistemas embebidos", "academica"),
    ("Natural", "Plantea un ejercicio sobre estructuras de datos", "academica"),

    ("Natural", "¿Cómo formalizo mi registro para el próximo periodo?", "inscripcion"),
    ("Natural", "¿Qué debo hacer para renovar mi carga escolar?", "inscripcion"),
    ("Natural", "Consulta cuándo abre el proceso de reinscripción", "inscripcion"),
    ("Natural", "¿Dónde confirmo que quedé inscrito?", "inscripcion"),

    ("Natural", "¿Cuál es el plazo para regresar un libro?", "biblioteca"),
    ("Natural", "¿Puedo consultar recursos digitales en la biblioteca?", "biblioteca"),
    ("Natural", "Necesito renovar un préstamo bibliográfico", "biblioteca"),
    ("Natural", "¿Qué necesito para llevarme material de lectura a casa?", "biblioteca"),

    ("Natural", "¿Existe financiamiento para continuar mis estudios?", "beca"),
    ("Natural", "¿Cómo verifico si fui beneficiado con el apoyo?", "beca"),
    ("Natural", "¿Cuándo publican la próxima convocatoria de ayudas económicas?", "beca"),
    ("Natural", "¿Qué requisitos mantienen vigente una beca?", "beca"),

    ("Natural", "¿Qué vía puedo escoger para conseguir el título?", "titulacion"),
    ("Natural", "Quiero conocer el procedimiento para obtener mi grado", "titulacion"),
    ("Natural", "¿Dónde registro la modalidad con la que terminaré la carrera?", "titulacion"),
    ("Natural", "¿El proyecto profesional puede servir para titularme?", "titulacion"),

    ("Natural", "¿Con quién tramito la entrada al laboratorio?", "laboratorio"),
    ("Natural", "¿Qué horario está disponible para usar el laboratorio de cómputo?", "laboratorio"),
    ("Natural", "Quiero apartar un espacio para realizar una práctica", "laboratorio"),
    ("Natural", "¿Cuáles son las normas para trabajar dentro del laboratorio?", "laboratorio"),

    ("Natural", "¿A qué hora dejan de vender comida?", "cafeteria"),
    ("Natural", "¿Qué formas de pago acepta la cafetería?", "cafeteria"),
    ("Natural", "Consulta si todavía hay servicio de alimentos", "cafeteria"),
    ("Natural", "¿Cuánto vale una bebida en el comedor universitario?", "cafeteria"),

    # Ortográficas: una pregunta inédita por intención.
    ("Ortográfica", "Wenas tardes EduIA", "saludo"),
    ("Ortográfica", "Dime ke tipo de konsltas resuelves", "capacidades"),
    ("Ortográfica", "Kiero saver la ora y salon de redes 2", "horario"),
    ("Ortográfica", "Muestrame mi karga eskolar", "materia"),
    ("Ortográfica", "¿Ai algun ecsamen progamado?", "examen"),
    ("Ortográfica", "¿Kien inparte sistemas emvevidos?", "profesor"),
    ("Ortográfica", "Kiero saver mi rezultado akademiko", "calificacion"),
    ("Ortográfica", "Revisa los komunicados reientes", "aviso"),
    ("Ortográfica", "Alludame a konprender un algoritimo", "academica"),
    ("Ortográfica", "Kiero renobar mi rejistro semestral", "inscripcion"),
    ("Ortográfica", "¿Puedo renobar un prestammo de livro?", "biblioteca"),
    ("Ortográfica", "¿Onde beo la konbocatoria de vekas?", "beca"),
    ("Ortográfica", "Kiero saver komo optener mi titullo", "titulacion"),
    ("Ortográfica", "¿Ke reglas ai en el lavoratorio de komputo?", "laboratorio"),
    ("Ortográfica", "¿Asta ke ora benden komida?", "cafeteria"),

    # Ambiguas: no contienen el objeto o servicio necesario.
    ("Ambigua", "¿Dónde se realiza?", "desconocida"),
    ("Ambigua", "¿Qué sigue después?", "desconocida"),
    ("Ambigua", "¿A quién le pregunto?", "desconocida"),
    ("Ambigua", "¿Todavía puedo hacerlo?", "desconocida"),
    ("Ambigua", "¿Cuál es la fecha límite?", "desconocida"),
    ("Ambigua", "¿Qué costo tiene?", "desconocida"),
    ("Ambigua", "¿Necesito registrarme?", "desconocida"),
    ("Ambigua", "¿Me corresponde alguno?", "desconocida"),
    ("Ambigua", "¿Dónde reviso el resultado?", "desconocida"),
    ("Ambigua", "¿Qué debo completar?", "desconocida"),

    # Desconocidas: solicitudes ajenas al alcance universitario de EduIA.
    ("Desconocida", "¿Cuánto vale Bitcoin en este momento?", "desconocida"),
    ("Desconocida", "Busca vuelos económicos a Ciudad de México", "desconocida"),
    ("Desconocida", "Dame una receta para preparar enchiladas", "desconocida"),
    ("Desconocida", "¿Va a llover durante la tarde?", "desconocida"),
    ("Desconocida", "¿Cómo terminó el juego de anoche?", "desconocida"),
    ("Desconocida", "Necesito encontrar un dentista cercano", "desconocida"),
    ("Desconocida", "Pon una canción tranquila para dormir", "desconocida"),
    ("Desconocida", "¿Dónde venden teléfonos baratos?", "desconocida"),
    ("Desconocida", "Explícame las próximas elecciones nacionales", "desconocida"),
    ("Desconocida", "¿A qué hora abre el banco?", "desconocida"),
    ("Desconocida", "Solicita un taxi para mi ubicación", "desconocida"),
    ("Desconocida", "Recomiéndame un videojuego de estrategia", "desconocida"),
    ("Desconocida", "Dime mi horóscopo del día", "desconocida"),
    ("Desconocida", "Encuentra un hotel disponible para mañana", "desconocida"),
    ("Desconocida", "¿Hay mucho tráfico rumbo al centro?", "desconocida"),
]


def ejecutar_pruebas():
    resultados_tipo = defaultdict(
        lambda: {"total": 0, "correctas": 0}
    )
    errores = []

    print("=" * 110)
    print("SEGUNDA EVALUACIÓN INÉDITA DE EDUIA")
    print("=" * 110)

    for numero, (tipo_prueba, pregunta, esperado) in enumerate(
        PRUEBAS,
        start=1,
    ):
        _, _, obtenido, confianza = buscar_respuesta(pregunta)
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
        print("Evaluación: " + ("CORRECTO" if correcto else "ERROR"))

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
    print("RESUMEN DE LA SEGUNDA EVALUACIÓN INÉDITA")
    print("=" * 110)
    print(f"Total de pruebas: {total}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {len(errores)}")
    print(f"Precisión inédita: {precision:.2f}%")

    if errores:
        print("\nERRORES DE LA SEGUNDA EVALUACIÓN")
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