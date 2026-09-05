# Guía de demostración de EduIA

Duración sugerida: 6 a 8 minutos.

## Preparación

1. Activa el entorno virtual y ejecuta `python ejecutar_todas_las_pruebas.py`.
2. Confirma que el resumen muestre cero errores y cero archivos no encontrados.
3. Ejecuta `python main.py`.
4. Verifica el micrófono, el volumen y la conexión a Internet.
5. Inicia sesión con una matrícula de demostración conocida.

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
- Si una respuesta es extensa, utiliza primero la pregunta contextual breve «¿Cuánto tiempo tardaría?».

## Lista de comprobación final

- [ ] Batería completa sin errores.
- [ ] Matrícula de demostración lista.
- [ ] Micrófono y altavoces funcionando.
- [ ] Respuestas por voz configuradas según el entorno.
- [ ] Internet disponible.
- [ ] Ventanas del navegador cerradas antes de comenzar.
