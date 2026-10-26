# Verificación de entrega

Fecha: **25/10/2026**. Entorno local Windows; zona de presentación America/Hermosillo.

| Comprobación ejecutada | Resultado |
| --- | --- |
| `backend/.venv/Scripts/python.exe -m pytest -q` desde backend | 108 aprobadas; 1 advertencia; 20.54 s |
| `npm test` desde frontend | 17 aprobadas; 0 fallidas |
| `npm run build` desde frontend | Correcto; manifiesto y service worker generados |
| Renderizado de PDF | Documentación completa y resumen exportados y revisados |

La advertencia es una deprecación de `anyio.abc.BlockingPortal` usada por una dependencia del cliente de pruebas. No produjo un fallo de prueba.

Las pruebas cubren lógica de calendario, filtros, estadísticas, identidad, eventos, métricas, historial, momios, pronósticos, modelos y validación temporal. No certifican disponibilidad permanente de APIs ni exactitud futura. La instantánea `model_snapshot_2026-10-25.json` corresponde a la consulta local documentada; no sustituye pruebas prospectivas y no es una base de producción.

La publicación incluye código y evidencias, no `.env`, claves, contraseñas, sesiones, SQLite ni dependencias instaladas. Un clon nuevo inicia su propio estado de aprendizaje.
