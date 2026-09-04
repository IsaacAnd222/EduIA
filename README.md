# EduIA

EduIA es un asistente virtual universitario de escritorio desarrollado en Python. Permite que un estudiante inicie sesión con su matrícula y consulte información académica mediante texto o voz desde una interfaz de conversación.

El proyecto trabaja con información escolar simulada almacenada localmente en SQLite y utiliza clasificación de texto para identificar la intención de cada consulta.

## Funciones principales

- Inicio y cierre de sesión mediante matrícula.
- Consultas personalizadas de materias, horarios, profesores, calificaciones y exámenes.
- Información sobre inscripción, becas, titulación, biblioteca, cafetería y laboratorios.
- Avisos generales y avisos correspondientes al semestre del estudiante.
- Tolerancia a variaciones naturales y errores ortográficos.
- Respuesta segura ante preguntas ambiguas o desconocidas.
- Memoria conversacional durante el chat actual.
- Historial de consultas y registro de retroalimentación.
- Consultas mediante micrófono.
- Respuestas habladas opcionales.

## Memoria conversacional

EduIA conserva temporalmente el tema y la intención de la conversación. Esto permite formular preguntas de seguimiento como:

```text
Estudiante: ¿Dónde está la biblioteca?
EduIA: El Instituto Irapuato cuenta con dos espacios de biblioteca...

Estudiante: ¿A qué hora abre?
EduIA: Horario de Biblioteca...
```

El contexto se reinicia al seleccionar **Nuevo chat** o **Cerrar sesión**. Una pregunta que cambia explícitamente de tema no queda forzada al contexto anterior.

## Funciones de voz

### Reconocimiento de consultas

El botón **Hablar** presenta cuatro estados:

```text
Hablar → Preparando... → Escuchando... → Reconociendo...
```

Cuando el reconocimiento termina correctamente, la consulta se envía automáticamente. La interfaz permanece disponible porque la captura se ejecuta en un hilo secundario.

El reconocimiento utiliza SpeechRecognition con el servicio de Google configurado para español de México (`es-MX`). Esta función necesita conexión a Internet.

### Respuestas habladas

El interruptor **Respuestas por voz** permite activar o desactivar la lectura de las respuestas.

- Voz principal: `es-MX-JorgeNeural`, mediante Edge TTS.
- Respaldo sin conexión: primera voz local disponible mediante pyttsx3.
- Reproducción: pygame.
- Los archivos MP3 se crean en la carpeta temporal de Windows y se eliminan automáticamente después de reproducirse.
- Si la voz falla, la respuesta escrita continúa disponible.

Edge TTS necesita Internet. El respaldo de pyttsx3 utiliza las voces instaladas localmente en Windows.

## Tecnologías

- Python 3.13
- CustomTkinter
- SQLite
- scikit-learn
- Pillow
- SpeechRecognition
- PyAudio
- Edge TTS
- pyttsx3
- pygame

## Estructura principal

```text
EduIA/
├── assets/                 Recursos gráficos
├── data/                   Base de datos SQLite
├── reportes/               Reportes generados
├── academico.py            Operaciones académicas
├── base_datos.py           Creación y acceso a SQLite
├── eduia.py                Clasificación y procesamiento
├── interfaz.py             Interfaz gráfica y conversación
├── main.py                 Punto de entrada
├── microfono.py            Reconocimiento de voz
├── voz.py                  Síntesis y reproducción de voz
└── requirements.txt        Dependencias
```

## Instalación en Windows

### 1. Crear el entorno virtual

```powershell
python -m venv .venv
```

### 2. Permitir temporalmente la activación

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### 3. Activar el entorno

```powershell
& .\.venv\Scripts\Activate.ps1
```

### 4. Instalar las dependencias

```powershell
python -m pip install -r requirements.txt
```

## Ejecución

Con el entorno virtual activado:

```powershell
python main.py
```

La aplicación solicitará una matrícula registrada antes de abrir el asistente académico.

## Pruebas

Las baterías existentes validan consultas naturales, ortográficas, ambiguas, desconocidas y dependientes del contexto:

```powershell
python pruebas_actividad4.py
python pruebas_validacion.py
python pruebas_finales.py
python pruebas_independientes_nuevas.py
python pruebas_ineditas_v2.py
python pruebas_contexto_v1.py
python pruebas_voz.py
```

Resultados de la validación:

| Batería | Correctas | Total |
|---|---:|---:|
| Actividad 4 | 40 | 40 |
| Validación | 50 | 50 |
| Pruebas finales | 60 | 60 |
| Independientes nuevas | 80 | 80 |
| Inéditas v2 | 100 | 100 |
| Memoria conversacional | 8 | 8 |
| Funciones de voz | 8 | 8 |
| **Total** | **346** | **346** |

`pruebas_voz.py` utiliza simulaciones para comprobar Edge TTS, pygame, el respaldo local y la eliminación de archivos temporales sin reproducir audio ni acceder a Internet.

## Consideraciones

- Los datos académicos y contactos incluidos son simulados y se utilizan exclusivamente para la demostración.
- La precisión del reconocimiento depende del micrófono, el ruido ambiental y la conexión.
- Los índices de dispositivos de audio pueden cambiar cuando se conectan dispositivos Bluetooth o USB.
- Las funciones escritas continúan disponibles aunque fallen los servicios de voz.

## Estado del proyecto

Las funciones académicas, la memoria conversacional y la interacción por voz están implementadas. El proyecto se encuentra en su etapa de validación final y documentación.
