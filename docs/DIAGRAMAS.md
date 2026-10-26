# Diagramas del sistema

## Arquitectura

```mermaid
flowchart LR
  ESPN[ESPN público] --> ETL[ETL]
  Odds[The Odds API] --> ETL
  ETL --> DB[(Base de datos)]
  DB --> Features[Variables históricas]
  Features --> Models[Poisson / OLS / CatBoost]
  Models --> Forecasts[Pronósticos y selecciones]
  Results[Resultados confirmados] --> Evaluation[Evaluación temporal]
  Forecasts --> Evaluation
  Evaluation --> Dashboard[Dashboard]
  DB --> API[FastAPI]
  API --> UI[React y PWA]
  SportScore[SportScore: cancha vinculada] --> UI
```

## Relaciones principales

Resumen conceptual; las columnas y relaciones exactas están en `backend/app/infrastructure/db/models.py`.

```mermaid
erDiagram
  LEAGUE ||--o{ TEAM : agrupa
  LEAGUE ||--o{ MATCH : organiza
  TEAM ||--o{ PLAYER : registra
  TEAM ||--o{ MATCH : local_o_visitante
  MATCH ||--o{ COUNT_OBSERVATION : respalda
  MATCH ||--o{ FORECAST_SNAPSHOT : captura
  FORECAST_REVISION ||--o{ FORECAST_SNAPSHOT : versiona
  FORECAST_SNAPSHOT ||--o{ FORECAST_SELECTION : contiene
  USER ||--o{ FORECAST_SELECTION : registra
  MARKET_LEARNER ||--o{ SHADOW_FORECAST : evalua
  MATCH ||--o{ ODDS_OBSERVATION : vincula
```

No se intercambian IDs entre proveedores. Una selección no cambia el resultado real. Se conservan versiones para auditoría.
