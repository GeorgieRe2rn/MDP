# Nexo - resumen para exposición

Corte: 25 de octubre de 2026. Repositorio: https://github.com/GeorgieRe2rn/MDP

## Lo esencialpara exponer

Qué hace Nexo y cómo utiliza Poisson, regresión lineal y CatBoost.

Datos reales -> Modelos estadísticos -> Validación temporal

| Poisson + regresión lineal OLS + CatBoost |
| --- |

Guía breve para explicar el proyecto a la maestra. Incluye conceptos, funcionamiento real, evaluación y respuestas a preguntas frecuentes.

Versión documentada: specialists-v2.0 + linear-ols-v1. Estado de modelos consultado en la base local el 25 de octubre de 2026.

Documento basado en la implementación actual. No reproduce credenciales, claves de API ni datos privados. Las cifras del estado de aprendizaje corresponden a una instantánea; pueden cambiar con nuevas ingestas.

## El proyecto en un minuto

| Nexo convierte datos reales de fútbol en pronósticos evaluables. Recopila información, la limpia, construye variables, calcula probabilidades y compara sus decisiones con resultados confirmados. |
| --- |

Datos reales -> Historial y variables -> Modelos por mercado -> Evaluación de resultados

### Qué analiza

Ganador o empate, goles, córners y amarillas. Separa el pronóstico previo del análisis en vivo. Las apuestas son simulaciones sin dinero; sirven para llevar un registro verificable de aciertos, fallos y datos pendientes.

### Tecnologías y fuentes

React: interfaz. FastAPI/Python: servicios y modelos. SQLAlchemy con PostgreSQL o SQLite: persistencia. ESPN: datos deportivos. The Odds API: referencia de cuotas. SportScore: cancha externa cuando existe una vinculación segura.

### Relación con KDD

Selección de datos, limpieza, transformación, minería y evaluación. Por ejemplo, resultados anteriores se transforman en promedios ofensivos/defensivos, puntos y descanso; después se relacionan con resultados finales para aprender y medir errores.

| Frase clave: los datos del partido son observaciones; las probabilidades son estimaciones. Si falta una estadística real, no se presenta un valor inventado como dato del equipo. |
| --- |

## Los tres métodos principales

| Método | Qué hace en Nexo | Idea para explicarlo |
| --- | --- | --- |
| Poisson | Convierte una tasa esperada en probabilidades de cantidades y marcadores. | ¿Qué probabilidades tienen 0, 1, 2 o más eventos? |
| Regresión lineal OLS | Aprende una suma ponderada de variables para estimar goles, córners y amarillas. | Cada variable aporta un efecto lineal a la cantidad estimada. |
| CatBoost | Combina árboles para clasificación 1X2 y regresión de conteos. | Muchos árboles sucesivos intentan reducir el error del conjunto. |

### Poisson

| P(X = k) = exp(-lambda) * lambda^k / k! |
| --- |

Lambda es la cantidad esperada. Con lambda = 2.8, P(tres goles o más) es aproximadamente 53.1%. Ejemplo didáctico, no un partido real.

### Regresión lineal

| y_estimado = b0 + b1*x1 + b2*x2 + ... |
| --- |

OLS aprende coeficientes usando resultados conocidos. En Nexo se ajusta por mercado y fase; su tasa se combina con la base y se proyecta con Poisson. Se limitan los conteos negativos como regla explícita del modelo.

### CatBoost

Un árbol divide ejemplos mediante condiciones aprendidas, como promedios de goles o descanso. CatBoost combina muchos árboles para capturar relaciones no lineales. CatBoostRegressor no significa regresión lineal: ambas técnicas están implementadas por separado.

## Cómo aprende y cómo se comprueba

Es aprendizaje supervisado por lotes: cada ejemplo contiene variables anteriores y una etiqueta real confirmada. Las revisiones se programan cada seis horas, mientras el modelo activo sigue funcionando.

60% Entrenamiento -> 20% Validación -> 20% Prueba -> Mejora real o conservar

Se requieren al menos 200 ejemplos utilizables y tamaños mínimos por bloque. Se respetan fechas y separaciones de tres horas. Para en vivo, muchos minutos del mismo partido no cuentan como muchos partidos independientes.

### Decisión de adopción

El peso entre base y especialista se elige en validación. Después, el candidato debe mejorar la pérdida de prueba frente a la base y al modelo vigente por más de 0.002. Si no lo logra, el sistema conserva el modelo anterior.

| Métrica | Interpretación |
| --- | --- |
| Accuracy | Porcentaje de resultado 1X2 elegido correctamente. |
| Log loss | Calidad de probabilidades; castiga la confianza equivocada. |
| Brier | Distancia entre probabilidades y resultado real. |
| MAE | Error promedio en la cantidad estimada. |

| Cuidado al exponer: la primera prueba de OLS es un benchmark histórico interno, no una garantía prospectiva ni una prueba externa. Tener un modelo entrenado no significa que esté activo o que sea mejor para todos los mercados. |
| --- |

## Qué está activo y qué decir

| Mercado | Previo activo | En vivo activo |
| --- | --- | --- |
| Ganador / empate | CatBoost + Poisson | Poisson observado |
| Goles | Regresión lineal + Poisson | Poisson observado |
| Córners | Regresión lineal + Poisson | Poisson observado |
| Amarillas | CatBoost + Poisson | Poisson observado |

Estado local consultado el 25/10/2026. OLS mejoró el benchmark de goles y córners previos; en amarillas se conserva CatBoost. Los candidatos en vivo esperan evidencia suficiente. Los modelos pueden cambiar tras evaluaciones posteriores.

### Preguntas que puede hacer la maestra

¿Aprende solo? Sí: recopila resultados y revisa candidatos por lotes. No cambia automáticamente solo porque pase el tiempo.

¿Por qué varios métodos? Porque un clasificador de ganador no resuelve igual una cantidad de córners. Se compara cada mercado y fase con su base.

¿Usa momios? Sí, cuando hay datos válidos. El aporte inicial de 10%/20% es experimental; no demuestra por sí solo mayor precisión.

¿La cancha entrena el modelo? No. SportScore es visualización y aún requiere vínculos verificados; sin cancha se muestran estadísticas reales.

¿Garantiza acertar? No. La aportación es analizar, medir y conservar trazabilidad. Un acierto aislado no valida el sistema.

### Cierre listo para decir

“Mi proyecto aplica KDD para transformar datos reales en pronósticos medibles. Compara Poisson, regresión lineal y CatBoost por mercado y fase; evalúa con partidos posteriores y solo adopta mejoras comprobadas internamente.”

Apoyo técnico: LinearRegression de scikit-learn, documentación de entrenamiento CatBoost y distribución Poisson de SciPy. Las referencias completas y los límites de implementación están en el documento técnico complementario.
