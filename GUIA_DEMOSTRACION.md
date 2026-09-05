# Guía de demostración de EduIA

Duración sugerida: 6 a 8 minutos.

## Preparación

1. Activa la zona Wi-Fi móvil de la computadora servidor.
2. Conecta los equipos cliente a esa red.
3. Inicia `ServidorEduIA` y confirma que muestre «listo para recibir conexiones».
4. Ejecuta la batería completa y confirma cero errores.
5. Inicia EduIA en uno o más equipos cliente.
6. Verifica el micrófono, el volumen y la conexión a Internet.
7. Inicia sesión con una matrícula de demostración conocida.

## Demostración del servidor compartido

Mantén visible la ventana del servidor y realiza una consulta desde un cliente. Señala la solicitud HTTP con código `200` que aparece en el servidor. Después abre el historial desde otro cliente con la misma matrícula para demostrar que ambos utilizan una sola base de datos.

Explica brevemente que los clientes no abren el archivo SQLite: solamente el servidor central lo hace, reduciendo el riesgo de bloqueos y manteniendo la información sincronizada.

La validación presencial se realizó satisfactoriamente con computadoras independientes: los estudiantes accedieron a la información académica y las consultas efectuadas desde un equipo aparecieron en el historial consultado desde otro.

## Recorrido recomendado

### 1. Presentación académica

Di: **«¿Cuál es mi horario?»**

Explica que EduIA identifica al estudiante mediante su matrícula y responde con información personalizada almacenada localmente.

### 2. Conversación escolar

Di: **«¿Dónde está la biblioteca?»** y después **«¿A qué hora abre?»**

Destaca que la segunda pregunta hereda el tema sin obligar al usuario a repetir «biblioteca».

### 3. Búsqueda externa encadenada

Di: **«Busca hospitales cerca del Instituto Irapuato»**.

Después continúa con:

1. **«¿Dónde está el segundo?»**
2. **«¿Cómo llego al segundo?»**
3. **«¿Cuánto tiempo tardaría?»**
4. **«¿Cómo está el clima ahí?»**

Señala que EduIA conserva los resultados, resuelve ordinales y comparte coordenadas entre OpenStreetMap, OSRM y Open-Meteo. Aclara que la lista de cercanos usa distancia en línea recta y la ruta usa calles y carreteras.

### 4. Botones interactivos

Pulsa **Abrir ruta** en la respuesta de OSRM. En otra respuesta, muestra **Abrir en OpenStreetMap**, **Abrir Wikipedia** o **Abrir Open-Meteo**.

Explica que el enlace visible conserva la fuente y el botón facilita abrirla sin copiarla.

### 5. Consulta general controlada

Di: **«Busca en Wikipedia qué es inteligencia artificial»**.

Destaca que Wikipedia se activa de manera explícita, evitando confundir búsquedas generales con consultas académicas locales.

### 6. Cierre

Muestra brevemente:

- la clasificación y confianza de una respuesta;
- los botones **Sí** y **No** para retroalimentación;
- el historial;
- **Nuevo chat**, que reinicia el contexto.

## Mensaje de cierre sugerido

> EduIA combina información académica personalizada, interacción por voz y servicios abiertos de Internet en una conversación continua. Su diseño conserva las fuentes, controla los errores externos y se valida con una batería automatizada completa.

## Plan de contingencia

- Si el micrófono no entiende una frase, repítela o escríbela en el campo de consulta.
- Si Overpass está ocupado, vuelve a intentar o muestra una búsqueda realizada previamente en el historial.
- Si un lugar no aparece, explica que OpenStreetMap depende de datos comunitarios y etiquetas disponibles.
- Si Internet falla, demuestra las consultas académicas locales y menciona que permanecen funcionales.
- Si el cliente no inicia sesión, confirma que el servidor siga abierto y que ambos equipos estén conectados a la misma zona Wi-Fi móvil.
- Si una respuesta es extensa, utiliza primero la pregunta contextual breve «¿Cuánto tiempo tardaría?».

## Lista de comprobación final

- [ ] Batería completa sin errores.
- [ ] Matrícula de demostración lista.
- [ ] Micrófono y altavoces funcionando.
- [ ] Respuestas por voz configuradas según el entorno.
- [ ] Internet disponible.
- [ ] Servidor central encendido y accesible.
- [ ] Equipos conectados a la misma red local.
- [ ] Instalador del cliente disponible para los participantes.
- [ ] Ventanas del navegador cerradas antes de comenzar.
