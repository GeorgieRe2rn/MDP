# Regresión lineal OLS

Se incorpora un especialista independiente para goles, córners y amarillas, en previo y en vivo. Para 1X2 se mantiene la clasificación; no se aplica OLS a probabilidades.

Utiliza exactamente los ejemplos elegibles y cortes temporales del motor existente: mínimo 200 encuentros, división 60/20/20, separaciones de tres horas y tamaños mínimos de los bloques. Variables numéricas: se excluyen columnas sin observaciones; medianas y escalas se calculan únicamente en entrenamiento. Liga: codificación categórica. El JSON conserva coeficientes, intercepto y transformación; no se deserializan objetos ejecutables.

Predicción OLS = intercepto + suma de coeficientes por variables transformadas. Se limita a 0.01 por ser una tasa de conteo; es una regla de modelado, no un dato observado. Esa tasa alimenta la misma proyección probabilística Poisson. Se prueban pesos 0, 0.25, 0.5, 0.75 y 1 frente a la base en validación. Solo se adopta si mejora el log loss de prueba frente a Poisson y al especialista activo por más de 0.002; también se informa MAE.

La primera evaluación usa un benchmark histórico cronológico compartido con los otros especialistas, no una prueba prospectiva inédita del proyecto. Los siguientes candidatos de la misma familia necesitan una prueba posterior a la ya utilizada. No se evalúa contra un incumbente entrenado con datos posteriores al inicio de esa prueba. La comparación histórica interna no garantiza mejora futura.

Los modelos se guardan en MarketLearner con esquema linear-ols-v1. Se añaden versiones sin borrar historiales ni apuestas iniciadas. El selector de producción puede cargar CatBoost o regresión lineal, informando la familia correcta. El trabajo periódico de seis horas incorpora ambas familias. Los candidatos en vivo esperan muestras suficientes.

Panel: Administración → Aprendizaje → Regresión lineal OLS, con estado, número de ejemplos y MAE frente a la base. La explicación metodológica también se actualizó.
