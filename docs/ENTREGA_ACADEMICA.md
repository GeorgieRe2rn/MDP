# Nexo - documentación completa de entrega

Corte: 25 de octubre de 2026. Repositorio: https://github.com/GeorgieRe2rn/MDP

## Documentacióncompleta

Arquitectura, datos, predicción, aprendizaje, evaluación, seguridad y operación.

Datos reales -> Modelos estadísticos -> Validación temporal

| Poisson + regresión lineal OLS + CatBoost |
| --- |

Proyecto académico para Extracción de Conocimiento en Bases de Datos. Guía técnica y funcional de la aplicación existente.

Versión documentada: specialists-v2.0 + linear-ols-v1. Estado de modelos consultado en la base local el 25 de octubre de 2026.

Documento basado en la implementación actual. No reproduce credenciales, claves de API ni datos privados. Las cifras del estado de aprendizaje corresponden a una instantánea; pueden cambiar con nuevas ingestas.

## Índice de contenidos

| Planteamiento del proyecto | 3 |
| --- | --- |
| Requisitos y criterios de aceptación | 4 |
| ETL: extracción, transformación y carga | 5 |
| Modelo de datos y relaciones | 6 |
| Manual del dashboard | 7 |
| Entrega, reproducción y pruebas | 8 |
| Propósito y alcance | 9 |
| Arquitectura del sistema | 10 |
| Fuentes y calidad de datos | 11 |
| Persistencia y trazabilidad | 12 |
| Proceso KDD y variables | 13 |
| Poisson: cantidades y probabilidades | 14 |
| Regresión lineal OLS | 15 |
| CatBoost: árboles que se combinan | 16 |
| Combinación y análisis en vivo | 17 |
| Aprendizaje y validación temporal | 18 |
| Métricas y estado consultado | 19 |
| Momios como referencia adicional | 20 |
| Selecciones automáticas y evaluación | 21 |
| Interfaz y seguimiento de partidos | 22 |
| Seguridad, cuentas y API | 23 |
| Instalación, ejecución y PWA | 24 |
| Verificación, límites y referencias | 25 |

## Planteamiento del proyecto

Problema: consultar datos deportivos aislados no permite evaluar si un pronóstico se emitió con información válida ni si un cambio de modelo realmente mejora. Se necesita reunir datos, conservar decisiones y contrastarlas con resultados posteriores.

### Justificación académica

Nexo conecta bases de datos, web services y aprendizaje supervisado en un caso verificable. Las estadísticas alimentan un proceso ETL; las variables permiten entrenar y comparar modelos; el dashboard presenta evidencia y limitaciones, no solamente una selección final.

### Objetivo general

| Construir una aplicación web de análisis de fútbol que transforme datos reales en pronósticos trazables y evalúe especialistas con validación temporal. |
| --- |

### Objetivos específicos

1. Integrar fuentes externas e identificar equipos y encuentros.2. Conservar datos, fechas de consulta y estados de calidad.3. Construir variables históricas sin usar resultados futuros.4. Implementar Poisson, regresión lineal OLS y CatBoost.5. Evaluar y versionar modelos por mercado y fase.6. Presentar calendario, estadísticas, aprendizaje y resultados en un dashboard.

### Usuarios y alcance

El visitante consulta información deportiva. La cuenta autenticada accede a selecciones simuladas; la administración consulta métricas y sincronización. La aplicación no coloca apuestas reales, no transmite dinero y no garantiza resultados. El proyecto se entrega como código y documentación; no como servicio público hospedado con disponibilidad garantizada.

## Requisitos y criterios de aceptación

| Requisito | Implementación verificable | Criterio |
| --- | --- | --- |
| ETL | live_feed.py, count_history.py y roster_feed.py. | Extrae datos, transforma identidades/fechas y persiste sin duplicar eventos. |
| Regresión lineal | linear_models.py; LinearRegression OLS. | Entrena con ejemplos previos y solo se adopta tras comparación temporal. |
| Árboles de decisión | market_pipeline.py; CatBoost. | Ensamble de árboles para resultado y cantidades; no árbol individual dibujado. |
| Dashboard | AdminHome.jsx y LearningPanel.jsx. | Muestra modelos, datos, métricas y fuentes. |
| API externa | ESPN y The Odds API opcional. | Identifica fuente y trata respuestas faltantes. |
| Persistencia | SQLAlchemy y esquema relacional. | Conserva resultados, capturas y versiones. |
| Seguridad | auth.py y security.py. | Login, hash, sesión, roles, CSRF y control de intentos. |
| Entrega | Código, README y PDF en MDP. | Clonable, con comandos y limitaciones explícitas. |

### Requisitos no funcionales

Responsividad; temas claro/oscuro; trazabilidad de versiones; tratamiento de datos faltantes; separación de credenciales; consultas compartidas para limitar carga; instalabilidad PWA compatible. La latencia depende también del proveedor externo.

| Estado pendiente que no se oculta: no hay autorregistro público; no existe descubrimiento automático general de canchas; un único árbol individual visualizado no forma parte del dashboard. Si la rúbrica exige esas funciones por separado, requieren trabajo adicional. |
| --- |

## ETL: extracción, transformación y carga

E Extraer -> T Transformar -> L Cargar -> Verificar y consultar

### Extracción

El scheduler invoca sync_feed, que consulta calendarios de las competiciones configuradas y resúmenes necesarios. Se reutilizan respuestas mediante caché y se registra el estado de cada fuente. Los directorios y plantillas tienen su trabajo periódico; las cuotas se solicitan por separado cuando hay clave y cobertura.

### Transformación

Se valida que el evento tenga identificador, competidores y fecha. Se resuelven equipos por su identidad; se convierten fechas a instantes con zona horaria; se normalizan estados como programado, en vivo y finalizado; se interpretan los contadores publicados. Un mismo proveedor/evento debe referirse al mismo encuentro.

### Carga

persist_event busca el registro por provider y provider_id. Si existe, actualiza información confirmada; si no, crea el encuentro. Se guardan consulta, estado y detalles. La ingesta de un refresco no debe producir un partido nuevo por cada minuto. Las capturas de pronóstico y cuotas mantienen su propia trazabilidad.

### Ejemplo de recorrido

| Evento externo con fecha UTC y dos equipos -> identidad interna y estado normalizado -> Match y datos asociados -> variables anteriores al inicio -> pronóstico versionado -> comparación con resultado final. |
| --- |

### Errores y recuperación

Si el proveedor no responde o falta un campo, la interfaz conserva el último estado recibido o indica indisponibilidad. Un campo vacío no se interpreta como cero. El trabajo debe liberar bloqueos y cerrar sesiones aun si falla. Los errores se registran localmente; los logs y cachés privados no se publican en GitHub.

La transformación de variables para entrenamiento es una etapa posterior a la ingesta: agrega antecedentes y no modifica los hechos deportivos originales.

## Modelo de datos y relaciones

League competición -> Team equipo -> Match encuentro -> Snapshot pronóstico

| Relación principal | Cardinalidad y finalidad |
| --- | --- |
| League - Team / Match | Una liga agrupa varios equipos y encuentros. |
| Team - Player | Un equipo puede registrar varios jugadores disponibles. |
| Match - equipos | Cada encuentro referencia un equipo local y uno visitante. |
| Match - ForecastSnapshot | Un encuentro conserva varias capturas por fase y momento. |
| ForecastRevision - ForecastSnapshot | Una revisión versiona múltiples capturas. |
| ForecastSnapshot - ForecastSelection | Una captura puede originar varias selecciones. |
| User - ForecastSelection | Cada selección pertenece a una cuenta. |
| Match - CountObservation / OddsObservation | Evidencias y cuotas se relacionan con el encuentro. |
| MarketLearner - ShadowForecast | Candidatos CatBoost registran pruebas en sombra. |

### Claves y restricciones

Los IDs internos son claves de la aplicación; provider_id identifica eventos externos. ForecastSnapshot usa una huella única. Las selecciones tienen restricciones de unicidad por usuario, captura, mercado y línea. Los vínculos automáticos evitan duplicaciones por usuario, encuentro y mercado. El archivo models.py contiene los nombres y claves foráneas exactos.

### Separación entre dato, estimación y decisión

Match registra el hecho deportivo; MarketLearner conserva parámetros aprendidos; ForecastSnapshot contiene una estimación fechada; ForecastSelection contiene la decisión simulada. Separar estas entidades evita que una nueva predicción sobrescriba lo que se había decidido antes.

En GitHub, docs/DIAGRAMAS.md incluye diagramas Mermaid navegables y el modelo conceptual. No se entrega una copia de la base con usuarios o sesiones.

## Manual del dashboard

| Tarea | Pasos y resultado esperado |
| --- | --- |
| Consultar jornada | Abrir Inicio; seleccionar liga, fecha y estado; buscar un equipo. Los resultados respetan esos filtros. |
| Revisar un partido | Abrir Ver partido; consultar marcador, resumen, estadísticas y plantillas según cobertura. |
| Ver cancha | Si el mismo encuentro tiene vínculo verificado, se carga SportScore y estadísticas al costado. Si no, solo eventos y estadísticas. |
| Revisar pronósticos | Iniciar sesión y consultar previo y en vivo por separado; los mercados sin evidencia se indican como no disponibles. |
| Evaluar selecciones | Abrir Mis apuestas o Apuestas automáticas del panel; consultar pendiente, acertada, fallida o anulada. |
| Examinar aprendizaje | Administración > Modelos y aprendizaje: familia activa, candidatos, muestras y métricas. |
| Auditar datos | Abrir Datos de entrenamiento y Resultados y métricas; revisar cobertura y exclusiones. |
| Cambiar apariencia | Usar el botón de sol/luna; la preferencia se conserva localmente. |

### Interpretación responsable

Un porcentaje es una estimación del modelo, no una estadística observada del partido. Un total esperado admite decimales. La simulación no afecta la estadística en vivo. Una selección pendiente no es un fallo ni un acierto. La hora de captura permite detectar información atrasada.

### Presentación para evaluación

Demostrar filtros y dashboard; mostrar un registro de pronóstico y su versión; explicar la elegibilidad de datos; abrir la sección de regresión lineal; presentar métricas con su muestra y fase. No hace falta esperar un partido en vivo para explicar la arquitectura o las pruebas automatizadas.

## Entrega, reproducción y pruebas

| Repositorio de entrega:https://github.com/GeorgieRe2rn/MDP |
| --- |

### Reproducción desde GitHub

Clonar MDP, copiar .env.example a .env, configurar un APP_SECRET propio e iniciar con .\run.ps1. Consultar README para Python, Node, comandos manuales y puertos. La cuenta administrativa inicial se genera localmente; sus credenciales nunca forman parte del repositorio.

La entrega contiene código, pruebas, archivos de ejemplo, informe Markdown, PDF, diagramas y evidencia de evaluación. Excluye .env real, claves, contraseñas, sesiones, SQLite, entornos virtuales, node_modules, logs y temporales. Una instalación limpia no hereda los modelos aprendidos de la base local: debe recopilar y entrenar con evidencia propia.

### Verificación ejecutada el 25/10/2026

| Comprobación | Resultado |
| --- | --- |
| Backend: python -m pytest -q | 108 pruebas aprobadas. |
| Frontend: npm test | 17 pruebas aprobadas. |
| Frontend: npm run build | Compilación PWA correcta. |
| Advertencias | Deprecación de una dependencia de pruebas; sin fallos. |
| Documentación | PDF renderizados y revisados visualmente; enlaces y contenido comprobados. |

### Qué cubren las pruebas

Fechas y zonas horarias; filtros; eventos y relojes; identidad de encuentros; historial de conteos; métricas; momios; separación temporal; exclusión de información futura; serialización y adopción de OLS; preservación de modelos vigentes. Las pruebas no equivalen a disponibilidad permanente de APIs externas ni a precisión garantizada.

### Criterio de entrega

El lector debe poder localizar los cuatro requisitos centrales, instalar el proyecto, ejecutar las pruebas y distinguir funciones existentes de pendientes. El informe describe el estado revisado y conserva las limitaciones, no simula un producto terminado sin restricciones.

## Propósito y alcance

Nexo centraliza información de fútbol, calcula probabilidades y registra selecciones simuladas para contrastarlas con resultados confirmados. Su valor académico es hacer trazable el recorrido desde los datos hasta la evaluación.

### Objetivos

Consultar encuentros y estadísticas reales; transformar historiales en variables; comparar especialistas por mercado y fase; medir sus errores; conservar versiones y presentar la información de manera accesible.

### Lectura del documento

| Bloque | Contenido |
| --- | --- |
| Sistema | Arquitectura, proveedores y persistencia. |
| Conocimiento | KDD, variables y calidad de datos. |
| Predicción | Poisson, OLS, CatBoost, combinación y fase en vivo. |
| Evaluación | Validación temporal, métricas y estado consultado. |
| Operación | Momios, selecciones, interfaz, seguridad, PWA, API y ejecución. |

### Lo que significa un pronóstico

Es una estimación condicionada por datos y supuestos. Un porcentaje alto no convierte el resultado en seguro. Las apuestas del proyecto son simulaciones sin dinero, independientes del marcador real y de la animación de la cancha.

| Alcance verificado: existen especialistas entrenados de regresión lineal y CatBoost. No todos están activos para todos los mercados. La cobertura de estadísticas y canchas depende del proveedor. |
| --- |

## Arquitectura del sistema

React Interfaz -> FastAPI Servicios -> SQLAlchemy Persistencia -> APIs Proveedores

El frontend es una SPA con React, Vite y Tailwind CSS. FastAPI expone servicios HTTP y Python ejecuta ingesta, análisis y entrenamiento. SQLAlchemy conecta las entidades con PostgreSQL o SQLite; el arranque local admite SQLite cuando no hay PostgreSQL disponible.

| Capa | Responsabilidad | Ubicación |
| --- | --- | --- |
| Presentación | Rutas, filtros, formularios y gráficos. | frontend/src |
| API | Validación de entradas y acceso a servicios. | backend/app/api/v1 |
| Servicios | Ingesta, modelos, selecciones y evaluación. | backend/app/services |
| Modelo y dominio | Proyecciones estadísticas e identidad. | backend/app/ml y domain |
| Infraestructura | Tablas, sesiones, caché y adaptadores. | backend/app/infrastructure |

### Flujo de consulta

El navegador solicita datos a /api/v1. El backend devuelve información persistida y su estado de actualización. Los procesos programados consultan proveedores para reducir duplicación de solicitudes. Excepción visual: SportScore se incrusta como iframe externo, por lo que el navegador sí se conecta a ese proveedor para la cancha.

### Trabajos periódicos

Resultados: aproximadamente cada 60 segundos. Calendario amplio: cada tres horas. Plantillas y momios: trabajos de 24 horas. Entrenamiento de especialistas: cada seis horas. También hay tareas iniciales al arrancar. Un trabajo puede no ejecutarse si otro mantiene el bloqueo de ingesta.

El scheduler y los bloqueos actuales están pensados para un único proceso local. Escalar a varios workers requiere coordinación compartida y separar los trabajos de la API.

## Fuentes y calidad de datos

| Fuente | Uso actual | Límite relevante |
| --- | --- | --- |
| ESPN público | Calendarios, marcadores, equipos, plantillas y estadísticas disponibles. | Sin contrato de latencia ni disponibilidad; cobertura variable. |
| The Odds API | Momios previos de referencia cuando hay coincidencia y cuota válida. | Clave privada, cuota de solicitudes y caché; no es un feed de momios en vivo. |
| SportScore | Cancha de un encuentro explícitamente vinculado. | Solo visualización; no alimenta el entrenamiento. |

### Reglas de integridad

Los identificadores de cada proveedor no se intercambian. Se revisan identidad de equipos, competición, fecha y hora. Los resultados deben ser finalizados y verificados para incorporarse como etiquetas. Se descartan duplicados del mismo evento y ejemplos incompatibles con el alcance a 90 minutos.

Un dato ausente se conserva como ausente; no se considera cero. Para córners y amarillas el motor exige historial observado suficiente de ambos equipos y, en vivo, contadores recientes. Cuando no se cumplen las condiciones, el mercado se omite o se informa como no disponible.

### Imputación técnica, distinta de inventar estadísticas

OLS puede reemplazar una entrada numérica faltante por la mediana calculada solo en entrenamiento; excluye columnas sin observaciones. Es un tratamiento interno explícito del modelo, no una estadística real mostrada del equipo. No reemplaza la elegibilidad del historial ni crea resultados finales.

### Competiciones configuradas

Liga MX (MX), Premier League (PL), La Liga (PD), Serie A (SA), MLS, Champions League (CL), Bundesliga (BL1) y Saudi Pro League (SPL). La configuración permite consultarlas; no garantiza cobertura idéntica en cada proveedor.

## Persistencia y trazabilidad

La base conserva hechos deportivos, agregados y decisiones del sistema. Esto permite reconstruir qué información estaba disponible al emitir un pronóstico y qué versión se utilizó.

| Entidad o grupo | Función |
| --- | --- |
| League, Team y Player | Competiciones, equipos, identidad y plantillas. |
| Match | Encuentro, proveedor, fecha, estado, marcador y detalles recibidos. |
| CountObservation | Contadores observados de córners y amarillas. |
| TeamFormSnapshot y Prediction | Forma agregada y predicción deportiva serializada. |
| ForecastSnapshot | Captura de un pronóstico previo o en vivo con sus parámetros. |
| ForecastSelection y vínculos automáticos | Selección simulada, estado, revisiones y liquidación. |
| MarketLearner y ForecastRevision | Modelos entrenados, informes y revisiones de calibración. |
| ShadowForecast | Capturas experimentales de candidatos CatBoost. |
| OddsObservation, caché y FeedState | Capturas de cuotas, reutilización de respuestas y estado de fuentes. |
| User y LoginAttempt | Acceso a cuentas y control de intentos. |

### Separación de responsabilidades

Un resultado real no se modifica para coincidir con un pronóstico. Una captura de cuotas conserva la hora de captura. La selección guarda el modelo y la política usados. Las revisiones futuras no borran el registro de decisiones ya iniciadas.

Existen tablas y rutas heredadas de versiones anteriores. La arquitectura descrita aquí se basa en specialists-v2.0 y linear-ols-v1, no en las fórmulas históricas que aún aparecen en algunos documentos antiguos.

## Proceso KDD y variables

Seleccionar datos -> Limpiar y validar -> Transformar variables -> Modelar y evaluar

| Etapa KDD | Aplicación |
| --- | --- |
| Selección | Encuentros de proveedores admitidos y resultados verificables. |
| Limpieza | Identidad, fechas, valores válidos, duplicados y cobertura. |
| Transformación | Ventanas históricas y vector numérico/categórico. |
| Minería | Poisson como base, regresión lineal OLS y CatBoost. |
| Interpretación | Métricas, estados, informes y comparación con resultados. |

### Entradas de los especialistas

La liga es una categoría. Las variables numéricas incluyen goles a favor y en contra, puntos, descanso y proporción de antecedentes como local para cada equipo. Córners y amarillas agregan promedios de conteos a favor y en contra. En vivo se añaden minuto, goles de ambos equipos y contador observado.

### Ventana histórica

El motor reconstruye los últimos cinco antecedentes elegibles por equipo dentro del intervalo histórico admitido. Excluye el propio evento, partidos posteriores y antecedentes demasiado cercanos. Algunos antecedentes publicados en resúmenes pueden pertenecer a otras competiciones; eso amplía cobertura, pero no ajusta automáticamente la fuerza entre ligas.

| Etiqueta supervisada: resultado 0/1/2 para local/empate/visitante; total final para conteos previos; conteo restante desde la captura para modelos en vivo. El resultado futuro no forma parte de las entradas previas. |
| --- |

## Poisson: cantidades y probabilidades

Poisson es una distribución discreta para representar cantidades de eventos. El parámetro lambda es la cantidad esperada, que se estima a partir del historial o de un especialista entrenado. No es un conteo observado.

| P(X = k) = exp(-lambda) * lambda^k / k! |
| --- |

k es una cantidad entera no negativa. En la base de goles, la tasa del local combina su promedio ofensivo con los goles recibidos del visitante, y viceversa. La suma de las tasas aproxima el total esperado.

### Ganador o empate

La base construye probabilidades de marcadores combinando las distribuciones de ambos equipos. Se suman las celdas donde el local anota más, ambos anotan igual o el visitante anota más. CatBoost puede producir el vector 1X2 directamente y combinarlo con esta base.

### Más / menos

| Más de 2.5 goles = P(X >= 3) = 1 - P(0) - P(1) - P(2) |
| --- |

Ejemplo didáctico: con lambda = 2.8, la probabilidad Poisson de tres goles o más es aproximadamente 53.1%. No es un pronóstico de un partido real.

### Supuestos y límites

Una Poisson simple vincula media y varianza. El fútbol puede presentar dependencia entre eventos, cambios de ritmo y dispersión distinta, especialmente en córners y tarjetas. Por eso se mide el error de la distribución y no se supone que una tasa histórica sea una ley del partido.

Implementación principal: backend/app/ml/markets.py y market_pipeline.py. La proyección de mercados puede incorporar parámetros de calibración; la fórmula anterior explica la distribución base.

## Regresión lineal OLS

Está implementada y entrenada mediante sklearn.linear_model.LinearRegression. OLS ajusta coeficientes para reducir la suma de errores cuadrados. Se aplica a goles, córners y amarillas, con modelos independientes en previo y en vivo; no se aplica directamente al vector de probabilidades 1X2.

| y_estimado = b0 + b1*z1 + b2*z2 + ... + bn*zn |
| --- |

Las z son variables transformadas. Las ligas se codifican como categorías indicadoras. Para columnas numéricas observadas se guardan mediana y escala aprendidas en entrenamiento. Las columnas sin datos de entrenamiento se excluyen. Esas transformaciones se reutilizan en validación, prueba e inferencia.

### Qué predice y cómo se utiliza

El valor estimado representa una tasa de conteo: total en previo o cantidad restante en vivo. Como una recta puede producir negativos, se aplica un límite inferior de 0.01. Después la tasa pasa a la proyección Poisson para convertirla en probabilidades de más/menos.

| Ejemplo inventado solo para explicar la fórmula:goles estimados = 0.8 + 0.6 x promedio ofensivo + 0.4 x promedio recibido rival.Con 2.0 y 1.5: 0.8 + 1.2 + 0.6 = 2.6. Estos coeficientes no son los del modelo guardado. |
| --- |

### Ventajas y precauciones

Es una referencia interpretable y económica. Supone una relación aditiva lineal; no descubre por sí sola interacciones complejas. La codificación completa de ligas junto con intercepto puede hacer que los coeficientes no sean únicos, aunque la solución por mínimos cuadrados produzca predicciones utilizables. Los coeficientes no prueban causalidad.

Los modelos se guardan como JSON con coeficientes, intercepto y transformaciones bajo linear-ols-v1. Archivo: backend/app/services/linear_models.py.

## CatBoost: árboles que se combinan

CatBoost es aprendizaje supervisado mediante gradient boosting de árboles de decisión. Construye árboles sucesivos para reducir una función de pérdida. No es un solo árbol ni una regresión lineal.

Variables del partido -> Árbol 1 aporte -> Árbol 2 corrección -> Conjunto predicción

### Clasificación y regresión

| Uso | Implementación | Salida |
| --- | --- | --- |
| Ganador / empate | CatBoostClassifier; pérdida MultiClass. | Probabilidades local, empate y visitante. |
| Goles, córners y amarillas | CatBoostRegressor; pérdida Poisson. | Tasa positiva estimada de conteo. |

### Configuración del proyecto

Cada mercado y fase usa su propio modelo. Configuración registrada: 160 iteraciones, profundidad 4, learning_rate 0.04, regularización L2 de 8, semilla 42 y dos hilos. La liga se declara variable categórica. El orden temporal se conserva con has_time=True.

### Cómo interpretar los árboles

Un árbol puede separar ejemplos por promedios ofensivos o descanso; las preguntas y umbrales se aprenden, no se escriben manualmente. La suma de aportes representa relaciones no lineales. El informe guarda importancia de variables, que describe el modelo pero no demuestra causalidad.

| Distinción fundamental: CatBoostRegressor es regresión basada en árboles. LinearRegression es regresión lineal OLS. El proyecto contiene ambas técnicas y las compara, sin confundir sus nombres. |
| --- |

## Combinación y análisis en vivo

| Momento | Información permitida | Objetivo |
| --- | --- | --- |
| Previo | Historial anterior al inicio y cuotas previas válidas. | Distribución del resultado final. |
| En vivo | Historial, minuto, marcador y contadores recientes. | Resultado final o cantidad que falta por ocurrir. |

### Combinación deportiva

| salida = (1 - w) * base_Poisson + w * especialista |
| --- |

El peso w se elige entre 0, 0.25, 0.5, 0.75 y 1 mediante validación. Puede combinarse un vector de probabilidades 1X2 o una tasa de conteo. El motor no suma OLS, CatBoost y Poisson con pesos arbitrarios: un especialista candidato debe superar al modelo activo.

### Partido en curso

Para goles se reduce la tasa base al tiempo restante usando un horizonte de 95 minutos. Un especialista en vivo puede estimar esa cantidad restante con variables del minuto y marcador. Los eventos ya ocurridos se conservan como contador actual, no se vuelven a pronosticar como si aún no hubieran sucedido.

Si el marcador está pendiente de confirmación, no hay minuto utilizable, falta contador reciente o la información envejece más allá del límite, el sistema puede suspender el pronóstico en vivo. Los especialistas en vivo no heredan automáticamente el entrenamiento de los previos.

### Coherencia y límites

Ganador y goles tienen objetivos independientes: sus salidas no garantizan una única distribución conjunta perfectamente coherente. No se incluyen prórroga ni penales en el alcance declarado. El horizonte de 95 minutos es una aproximación, no una duración observada del encuentro.

## Aprendizaje y validación temporal

El aprendizaje se realiza por lotes con resultados confirmados. Recibir una actualización no equivale a reentrenar ni a adoptar un modelo. El scheduler revisa especialistas cada seis horas; un mismo conjunto de datos se identifica con una huella para evitar repetirlo sin necesidad.

60% Entrenar -> 20% Validar peso -> 20% Probar -> Comparar y decidir

Se exigen al menos 200 ejemplos; además, los bloques deben contener al menos 100 ejemplos de entrenamiento y 30 por cada bloque posterior. Los cortes respetan fechas y separaciones de tres horas. Un evento no debe aparecer simultáneamente en entrenamiento y prueba; las capturas en vivo se reducen a un ejemplo por encuentro elegible.

### Condiciones de adopción

El candidato debe tener peso mayor que cero y reducir el log loss de prueba en más de 0.002 frente a la base y al modelo vigente. CatBoost exige datos para las tres clases en entrenamiento. Si no hay mejora o falta evidencia, se conserva el modelo anterior.

### Qué tan independiente es la prueba

La primera comparación de OLS es un benchmark histórico cronológico compartido con otros especialistas. No constituye evidencia prospectiva completamente inédita de todo el sistema. Las siguientes revisiones de una familia necesitan un bloque posterior al ya usado; aun así, la selección reiterada entre familias debe vigilarse para no sobreajustar el benchmark.

| Activo y aprendiendo: el modelo vigente sigue atendiendo consultas mientras se evalúan candidatos. Solo una adopción cambia el despliegue; los resultados previos y las selecciones ya iniciadas se conservan. |
| --- |

## Métricas y estado consultado

| Mercado | Fase | Modelo activo | Ejemplos |
| --- | --- | --- | --- |
| Ganador / empate | Previo | CatBoost + Poisson | 1673 |
| Goles | Previo | Regresión lineal + Poisson | 1673 |
| Córners | Previo | Regresión lineal + Poisson | 303 |
| Amarillas | Previo | CatBoost + Poisson | 303 |
| Ganador / empate | En vivo | Poisson observado | 71 |
| Goles | En vivo | Poisson observado | 71 |
| Córners | En vivo | Poisson observado | 39 |
| Amarillas | En vivo | Poisson observado | 39 |

| OLS previo | Decisión | MAE candidato | MAE base |
| --- | --- | --- | --- |
| Goles | Adoptada | 1.397 | 1.421 |
| Córners | Adoptada | 3.121 | 3.316 |
| Amarillas | No mejoró | 1.624 | 1.617 |

Instantánea local del 25/10/2026. Los ejemplos indican disponibilidad de datos elegibles, no partidos nuevos evaluados prospectivamente ni garantía de precisión. La fila de modelo activo y el último intento de entrenamiento pueden corresponder a revisiones diferentes.

### Cómo leer las métricas

Accuracy: porcentaje de clase más probable acertada. Log loss: penaliza probabilidades incorrectas, especialmente cuando son muy confiadas. Brier: distancia cuadrática entre probabilidades y resultado (rango multiclase usado: 0 a 2). MAE: promedio de |real - estimado| para cantidades.

El sistema selecciona por log loss, no por el porcentaje de apuestas acertadas. En conteos usa la pérdida de la distribución Poisson completa; también reporta MAE. La matriz de confusión, precisión, recall y F1 ayudan a revisar errores por clase. No deben mezclarse métricas de previo y en vivo como si fueran una sola prueba.

## Momios como referencia adicional

The Odds API aporta cuotas previas cuando hay cobertura y coincidencia de equipos y hora. No hay integración confirmada de momios de Draftea. Los mercados consultados son resultado 1X2 y total de goles; no se presupone cobertura de córners y tarjetas.

| probabilidad implícita = 1 / cuota_decimalp_sin_margen(i) = (1 / cuota_i) / suma(1 / cuota_j) |
| --- |

La política stable-market-v1 construye una referencia robusta por mercado. Exige al menos tres grupos de fuentes válidas, filtra discrepancias y compara la misma línea para goles. Agrupar marcas relacionadas evita contarlas como confirmaciones totalmente separadas; no prueba independencia entre casas.

| Situación | Aporte inicial experimental |
| --- | --- |
| Una captura y concordancia transversal suficiente | 10% de referencia de mercado. |
| Capturas comparables con estabilidad temporal | Hasta 20%. |
| Datos antiguos, insuficientes o mercado con movimiento excesivo | 0%; se conserva la salida deportiva. |

### Calidad frente a certeza

Se admiten cuotas con antigüedad limitada; el filtro usa dispersión máxima de ocho puntos porcentuales. La estabilidad temporal requiere capturas separadas al menos 30 minutos, comparables dentro de 48 horas, con movimiento máximo de cuatro puntos. El refresco diario no equivale a estabilidad minuto a minuto.

Los pesos 10%/20% son reglas experimentales, no una mejora ya aprendida. Un combinador puede reemplazarlos después de evaluación temporal con suficientes ejemplos prospectivos, incluso con peso cero. No se trasladan cuotas previas al motor en vivo como si fueran cuotas actuales.

## Selecciones automáticas y evaluación

Las apuestas automáticas son registros de simulación sin dinero. Se generan a partir de pronósticos elegibles de resultado, goles, córners y amarillas. Cada registro conserva probabilidad, selección, fase, política, revisión y fecha.

Pronóstico elegible -> Selección registrada -> Resultado confirmado -> Acierto o fallo

### Ejemplo

Una selección de menos de 3.5 goles acierta con un total final de tres y falla con cuatro. La evaluación de córners necesita el contador final de córners; no basta con que el partido tenga marcador final. Si falta el dato, no se inventa una liquidación.

### Estados

| Estado | Significado |
| --- | --- |
| Pendiente | Todavía falta resultado o estadística final utilizable. |
| Acertada / fallida | La selección se comparó con el dato final correspondiente. |
| Anulada / retirada | La selección no debe evaluarse normalmente por una condición de invalidez o falta de respaldo. |

### Revisiones y doble oportunidad

Antes del inicio pueden revisarse selecciones automáticas futuras al cambiar el modelo o el aporte de mercado, conservando auditoría. Las selecciones empezadas no se reescriben para mejorar el historial. Una política puede proponer doble oportunidad si ciertas probabilidades son cercanas; es una regla de selección y no un modelo de aprendizaje adicional.

| El modelo aprende de resultados confirmados. Elegir una apuesta no la vuelve una etiqueta verdadera. Acertar una simulación tampoco demuestra rentabilidad: sin cuotas y costes evaluados no puede inferirse rendimiento económico. |
| --- |

## Interfaz y seguimiento de partidos

| Ruta | Contenido |
| --- | --- |
| / y /en-vivo | Jornada, filtros y encuentro destacado. |
| /match/:id | Marcador, cancha vinculada o eventos, estadísticas y análisis. |
| /plantillas y /equipo/:id | Equipos, jugadores y detalles disponibles. |
| /posiciones | Clasificación por competición. |
| /cartelera | Calendario de encuentros compatibles. |
| /mis-pronosticos | Selecciones simuladas y resultados de la cuenta. |
| /admin y /admin/login | Acceso y módulos de administración. |

### Cancha real del mismo encuentro

LiveCoverage solo muestra el iframe de SportScore si existe una vinculación verificada para el partido. Si no existe, muestra eventos y estadísticas ESPN, sin cancha ilustrativa ni partido ajeno. Las estadísticas van al costado en escritorio y se apilan en móvil.

La vinculación general automática todavía no está implementada. El registro actual contiene dos pilotos fechados del 23/10/2026: Al Faisaly-Al Nassr e Ipswich-Nottingham. Se comprueban equipos, liga, hora, estado LIVE y una ventana de cuatro horas. No son una cobertura permanente para todos los partidos. La animación del proveedor no garantiza coordenadas físicas continuas del balón.

### Fecha, reloj y accesibilidad

Las horas se presentan en America/Hermosillo, UTC-7. Los segundos pueden interpolarse entre minutos publicados y se identifican como aproximados. Eso no crea eventos deportivos. El diseño incorpora modo claro/oscuro, preferencia local, navegación móvil y estados de datos faltantes.

## Seguridad, cuentas y API

La autenticación disponible es inicio y cierre de sesión. Las contraseñas se verifican con bcrypt; no se guardan en texto plano en la tabla de usuarios. Las sesiones usan cookies, con HttpOnly y controles SameSite; Secure depende de la configuración de despliegue. Se verifican permisos y CSRF en operaciones protegidas.

El acceso administrativo comprueba el rol y la cuenta persistida. El sistema registra intentos de acceso y aplica bloqueo temporal. CORS restringe orígenes configurados. Las entradas se validan mediante modelos y parámetros de FastAPI/Pydantic.

### Gestión de secretos

Las claves de proveedores y APP_SECRET deben mantenerse en .env, excluido de Git. No deben ponerse secretos en variables VITE_* porque terminan en el navegador. Los alias públicos de widgets son distintos de las claves REST privadas. Este documento no contiene credenciales.

| Servicio representativo | Acceso / propósito |
| --- | --- |
| GET /api/v1/health, /leagues, /feed | Lecturas públicas de salud, ligas y jornada. |
| GET /api/v1/matches/{id}, /teams/{id} | Detalle público de entidades. |
| GET /api/v1/leagues/{code}/standings | Tabla de posiciones. |
| GET /api/v1/learning | Estado del aprendizaje. |
| GET /api/v1/metrics, /models/audit | Métricas y auditoría administrativa. |
| POST /api/v1/feed/refresh, /odds/sync | Operaciones administrativas protegidas. |
| /api/v1/auth/login, /logout, /me, /csrf | Sesión, usuario actual y protección de solicitudes. |

| Requisito académico por completar: no se encontró una ruta/pantalla de autorregistro de usuarios en la versión revisada. El login existente no debe presentarse como un registro con validación ya implementado. |
| --- |

## Instalación, ejecución y PWA

### Arranque en Windows

| cd C:\Users\Jorge\Desktop\sport-analytics-platform.\run.ps1 |
| --- |

El script prepara dependencias si faltan y arranca backend y frontend. Por defecto utiliza la compilación para PWA. Con .\run.ps1 -Dev se usa Vite de desarrollo. Si un puerto ya está ocupado, conserva el proceso: eso no garantiza que ese proceso tenga la última compilación.

| Dirección local | Uso |
| --- | --- |
| http://127.0.0.1:5173 | Sitio y administración bajo /admin. |
| http://127.0.0.1:8000/api/docs | OpenAPI en entornos donde está habilitado. |
| backend/data/forma.db | Base SQLite local de respaldo cuando corresponde. |

### Actualizar y verificar

| cd frontendnpm run buildnpm testcd ..\backend.\.venv\Scripts\python.exe -m pytest |
| --- |

Para cambios Python, reiniciar el proceso de API de este proyecto. Para cambios del frontend compilado, aceptar la actualización de la PWA o recargar cuando se publique la nueva versión. Antes de migraciones, respaldar la base y los modelos. No ejecutar varios schedulers contra el mismo SQLite.

### Qué aporta la PWA

Manifiesto, iconos, instalación compatible y archivos estáticos precacheados. No guarda sesiones, cuotas o marcadores como una supuesta fuente offline. Un teléfono necesita un despliegue HTTPS accesible para instalación normal; localhost solo apunta al dispositivo que lo abre. La cancha externa requiere conexión.

## Verificación, límites y referencias

### Comprobaciones registradas

La implementación de OLS incluyó pruebas de recuperación de una relación lineal, serialización JSON, exclusión de columnas sin observaciones, límites de conteos negativos, adopción temporal y conservación del incumbente sin prueba nueva. En la verificación final del 25/10/2026 se ejecutaron las suites completas: 108 pruebas backend y 17 frontend aprobadas; compilación PWA correcta. Se registró una advertencia de deprecación de una dependencia de pruebas. No equivale a certificar todo el producto ni una precisión futura.

### Límites principales

Cobertura y disponibilidad externas variables; diferencias de retraso entre ESPN y SportScore; independencia y dispersión imperfectas en Poisson; poco historial en vivo; comparación interna de modelos, sin auditoría externa; posibles fugas por revisiones históricas de proveedores; necesidad de coordinación para escalar; autorregistro pendiente y vínculos de cancha limitados a pilotos.

### Referencias de implementación

market_pipeline.py: evidencia, división temporal, especialistas y selección.linear_models.py: OLS, transformación y persistencia.forecasts.py: capturas, revisiones y resultados.stable_market.py y odds_feed.py: cuotas y combinación.scheduler.py: periodicidad.LiveCoverage.jsx y verifiedTrackers.js: cancha y estadísticas.security.py y auth.py: autenticación.vite.config.js y run.ps1: PWA y arranque.

### Bibliografía técnica oficial

scikit-learn - LinearRegression:scikit-learn.org / LinearRegressionCatBoost - How training is performed:catboost.ai / algorithm-main-stagesSciPy - Distribución Poisson (referencia matemática):docs.scipy.org / scipy.stats.poissonSportScore - Widgets y condiciones:sportscore.com/embed

Referencias consultadas el 25/10/2026. La documentación en línea puede corresponder a versiones distintas de las dependencias fijadas en el repositorio. Algunos documentos antiguos conservan nombres FORMA/VELAR y fórmulas anteriores; no describen por sí solos la versión actual.
