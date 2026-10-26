# NEXO | Análisis de fútbol y aprendizaje supervisado

Entrega académica para **Extracción de Conocimiento en Bases de Datos**.

Nexo integra **ETL**, **regresión lineal OLS**, **árboles de decisión con CatBoost**, una base probabilística **Poisson** y un **dashboard** para analizar y evaluar pronósticos.

## Documentos para la maestra

- [Documentación completa PDF](output/pdf/NEXO_Documentacion_Completa.pdf).
- [Resumen para exposición PDF](output/pdf/NEXO_Resumen_Exposicion.pdf).
- [Informe completo en Markdown](docs/ENTREGA_ACADEMICA.md).
- [Índice y evidencias](docs/INDEX.md).

## Funciones

Calendario con filtros de liga, fecha y estado; resultados, estadísticas, plantillas y posiciones según cobertura; pronósticos de ganador/empate, goles, córners y amarillas por separado en previo y en vivo; selecciones automáticas **simuladas sin dinero**, auditoría, métricas y aprendizaje periódico. Interfaz responsiva, modo claro/oscuro y PWA.

**ESPN público** aporta información deportiva; **The Odds API** aporta cuotas previas cuando hay clave y cobertura. **SportScore** es una visualización externa y solo aparece si se verifica el mismo partido. No existe todavía descubrimiento automático general de canchas. Sin cancha se muestran eventos y estadísticas reales.

## Modelos y reproducibilidad

Poisson transforma tasas en probabilidades; `LinearRegression` aprende cantidades mediante OLS; CatBoost combina árboles para clasificación y regresión. Se evalúan por mercado y fase con divisiones cronológicas 60/20/20, separaciones temporales y mínimos de evidencia.

La instantánea del 25/10/2026 registra OLS activa para goles y córners previos, CatBoost para resultado y amarillas previos y Poisson en vivo. **Clonar el código no restaura la base privada ni esos modelos entrenados**: una instalación nueva recopila datos y aprende con su propia evidencia. El estado documentado no garantiza precisión futura.

## Instalación en Windows

Requisitos: Python 3 disponible como `py -3` (3.11/3.12 recomendado por compatibilidad), Node.js 20.19+ o 22.12+, npm, PowerShell e Internet. PostgreSQL es opcional; se admite SQLite local.

```powershell
git clone https://github.com/GeorgieRe2rn/MDP.git
cd MDP
Copy-Item .env.example .env
```

Configura un `APP_SECRET` aleatorio en `.env`. `ODDS_API_KEY` es opcional: sin ella no se incorpora mercado de cuotas. ESPN no necesita esa clave.

```powershell
.\run.ps1
```

El script crea el entorno e instala dependencias si faltan; sirve la PWA compilada y la API. Conserva procesos que ya ocupen los puertos: comprueba que sean del proyecto y estén actualizados. Si PowerShell bloquea scripts, consulta la política de tu equipo; no es necesario desactivar protecciones globales.

- Sitio: <http://127.0.0.1:5173/>
- Administración: <http://127.0.0.1:5173/admin>
- OpenAPI en desarrollo: <http://127.0.0.1:8000/api/docs>

Las credenciales administrativas se generan al crear la primera cuenta y se guardan en `backend/data/admin_credentials.txt`, excluido de Git. No se comparten contraseñas en el repositorio. **El autorregistro público no está implementado**; el login existente no lo sustituye.

Modo desarrollo: `.\run.ps1 -Dev`.

Arranque manual en dos terminales:

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```powershell
cd frontend
npm ci
npm run dev
```

## Pruebas

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
cd ../frontend
npm test
npm run build
```

Revisión de entrega del 25/10/2026: **108 pruebas backend y 17 frontend aprobadas**, compilación PWA correcta. Una advertencia de deprecación de dependencia en pruebas. [Evidencia](docs/evidence/VERIFICACION_ENTREGA.md).

## Estructura

| Carpeta | Contenido |
| --- | --- |
| backend/app/api | API y autenticación |
| backend/app/services | ETL, modelos, selecciones y evaluación |
| backend/app/ml | Distribuciones y proyecciones |
| backend/app/infrastructure | Persistencia y proveedores |
| backend/tests | Pruebas backend |
| frontend/src | Interfaz y dashboard |
| frontend/tests | Pruebas frontend |
| docs | Informe, diagramas y evidencia |
| output/pdf | Entregables PDF |
| tools | Generación de documentación |

## Seguridad y límites

No se publican claves, `.env`, sesiones, credenciales, bases locales, entornos virtuales ni dependencias instaladas. Se utilizan bcrypt, cookies de sesión, roles, CSRF y límites de acceso. Un despliegue público requiere configuración de seguridad y HTTPS. La programación local está diseñada para un único proceso de API; varios workers necesitan coordinación compartida.

Las fuentes pueden retrasarse o carecer de estadísticas. No se inventan resultados. Los segundos aproximados se identifican. Las predicciones son experimentales: **no garantizan aciertos ni rentabilidad**. La PWA no ofrece resultados en vivo sin conexión.

Los documentos antiguos FORMA/VELAR se conservan como antecedentes. El informe de entrega y el código actual tienen prioridad. Algunos nombres de tablas y cookies conservan esos identificadores por compatibilidad.
