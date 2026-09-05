# EduIA

EduIA es un asistente virtual universitario de escritorio desarrollado en Python. Permite que cada estudiante inicie sesión con su matrícula y consulte información académica o servicios externos mediante texto y voz desde una interfaz conversacional.

La información escolar simulada se almacena localmente en SQLite. Para las consultas externas, EduIA integra Wikipedia, Open-Meteo y los servicios abiertos de OpenStreetMap sin requerir tarjetas ni claves privadas.

## Funciones principales

- Inicio y cierre de sesión mediante matrícula.
- Consultas personalizadas de materias, horarios, profesores, calificaciones y exámenes.
- Información sobre inscripción, becas, titulación, biblioteca, cafetería y laboratorios.
- Avisos generales y correspondientes al semestre del estudiante.
- Tolerancia a variaciones naturales y errores ortográficos.
- Memoria conversacional para preguntas de seguimiento.
- Historial de consultas y registro de retroalimentación.
- Consultas mediante micrófono y respuestas habladas opcionales.
- Búsquedas explícitas de información general en Wikipedia.
- Clima actual y pronóstico mediante Open-Meteo.
- Ubicaciones y coordenadas mediante OpenStreetMap.
- Distancias, duración e indicaciones por carretera mediante OSRM.
- Hospitales, farmacias, cafeterías, restaurantes, bancos y otros lugares cercanos mediante Overpass.
- Botones para abrir fuentes, lugares y rutas en el navegador.
- Modo cliente-servidor para compartir una sola base de datos en la red local.

## Contexto entre servicios

EduIA conserva temporalmente los resultados externos para resolver referencias naturales:

```text
Estudiante: Busca hospitales cerca del Instituto Irapuato.
EduIA: 1. ISSSTE... 2. IMSS...

Estudiante: ¿Cómo llego al primero?
EduIA: Ruta del Instituto Irapuato al ISSSTE...

Estudiante: ¿Cuánto tiempo tardaría?
EduIA: De Instituto Irapuato a ISSSTE tardarías aproximadamente 6 min...

Estudiante: ¿Cómo está el clima ahí?
EduIA: Clima en ISSSTE...
```

Las referencias como `primero`, `segundo`, `último`, `ahí` y `ese lugar` utilizan las coordenadas exactas del resultado seleccionado. El contexto se reinicia al elegir **Nuevo chat** o **Cerrar sesión**, y no se impone cuando el estudiante cambia claramente de tema.

## Servicios externos

| Función | Servicio | Resultado |
|---|---|---|
| Información general | Wikipedia | Resumen y fuente |
| Clima | Open-Meteo | Condiciones actuales y pronóstico |
| Ubicaciones | Nominatim / OpenStreetMap | Nombre, dirección y coordenadas |
| Rutas | OSRM / OpenStreetMap | Distancia vial, duración e indicaciones |
| Lugares cercanos | Overpass / OpenStreetMap | Lugares ordenados por distancia lineal |

Las distancias mostradas en una búsqueda de lugares cercanos son aproximaciones en línea recta. Cuando se solicita cómo llegar, OSRM calcula la distancia por calles y carreteras; por eso ambas cifras pueden ser diferentes.

## Servidor compartido

EduIA puede trabajar en modo local o conectarse a un servidor central mediante HTTP. En el modo compartido, únicamente `ServidorEduIA` abre el archivo SQLite; los clientes solicitan la información mediante una API autenticada. De esta manera, estudiantes, horarios, calificaciones, avisos, historial y retroalimentación provienen de una sola base de datos.

La dirección se define en `configuracion_cliente.json`, por lo que puede cambiarse al trasladar el servidor a otra red sin volver a compilar EduIA. El servidor escucha de forma predeterminada en el puerto `8765`.

## Funciones de voz

El botón **Hablar** presenta cuatro estados:

```text
Hablar → Preparando... → Escuchando... → Reconociendo...
```

Al terminar el reconocimiento, la consulta se envía automáticamente. Si no se entiende audio —por ejemplo, debido a una pausa larga o silencio— EduIA lo informa sin bloquear la conversación.

- Reconocimiento: SpeechRecognition, configurado en español de México (`es-MX`).
- Voz principal: `es-MX-JorgeNeural`, mediante Edge TTS.
- Respaldo sin conexión: primera voz local disponible mediante pyttsx3.
- Reproducción: pygame.
- Los MP3 temporales se eliminan después de reproducirse.

## Tecnologías

- Python 3.13
- CustomTkinter y Pillow
- SQLite
- scikit-learn
- SpeechRecognition y PyAudio
- Edge TTS, pyttsx3 y pygame
- Wikipedia, Open-Meteo, Nominatim, OSRM y Overpass API

## Estructura principal

```text
EduIA/
├── assets/                         Recursos gráficos
├── data/                           Base de datos SQLite
├── reportes/                       Reportes generados
├── academico.py                    Operaciones académicas
├── base_datos.py                   Creación y acceso a SQLite
├── internet.py                     Consultas en Wikipedia
├── clima.py                        Clima y pronóstico
├── ubicaciones.py                  Geocodificación de lugares
├── rutas.py                        Rutas y distancias por carretera
├── cercanos.py                     Lugares cercanos
├── enlaces.py                      Acciones para fuentes y rutas
├── configuracion_red.py             Configuración local y remota
├── repositorio_datos.py             Acceso unificado a los datos
├── servidor_eduia.py                API del servidor central
├── eduia.py                        Clasificación, contexto y procesamiento
├── interfaz.py                     Interfaz gráfica y conversación
├── ejecutar_todas_las_pruebas.py   Ejecutor de la validación completa
├── main.py                         Punto de entrada
├── microfono.py                    Reconocimiento de voz
├── voz.py                          Síntesis y reproducción de voz
└── requirements.txt                Dependencias
```

## Instalación en Windows

Para usuarios finales se generan dos instaladores:

- `EduIA_Cliente_Setup_v1.8.0.exe`: instala la aplicación utilizada por los estudiantes.
- `EduIA_Servidor_Setup_v1.8.0.exe`: instala el servidor central, crea la regla privada del Firewall para el puerto `8765` y conserva SQLite en `%LOCALAPPDATA%\EduIA\Servidor\data`.

Los compañeros instalan únicamente el cliente. La computadora anfitriona ejecuta el servidor y comparte su red local; todos los clientes consultan y actualizan una sola base de datos central.

Para ejecutar el proyecto desde el código fuente:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Ejecución

Con el entorno virtual activado:

```powershell
python main.py
```

## Pruebas

La validación completa se ejecuta con un solo comando:

```powershell
python ejecutar_todas_las_pruebas.py
```

El ejecutor recorre 20 baterías, muestra el resultado de cada una y calcula tanto los archivos correctos como los casos individuales comprobados. Incluye pruebas históricas, clasificación, contexto local, voz, Wikipedia, clima, ubicaciones, rutas, lugares cercanos, contexto entre servicios, experiencia de enlaces y comunicación con el servidor compartido.

Las pruebas de servicios y voz utilizan simulaciones cuando corresponde, por lo que no abren el navegador, reproducen audio ni dependen de una respuesta real de Internet.

## Consideraciones

- Los datos académicos y contactos son simulados y se usan exclusivamente para demostración.
- La precisión del reconocimiento depende del micrófono, el ruido ambiental y la conexión.
- Nominatim, OSRM, Overpass, Wikipedia y Open-Meteo son servicios externos; pueden responder lentamente o estar ocupados temporalmente.
- OpenStreetMap contiene datos aportados por su comunidad. Un negocio ausente o sin etiquetas adecuadas podría no aparecer.
- Las funciones académicas escritas continúan disponibles si un servicio externo o de voz falla.

## Estado del proyecto

La versión estable más reciente es **v1.8.0**. Incluye aplicación de escritorio, servicios externos, memoria contextual, distribución para Windows y funcionamiento cliente-servidor con una base de datos central compartida. La validación comprende 20 baterías y 511 casos individuales.
