# Dataset Card

Synthetic territorial-risk dataset generated with a fixed educational seed. It contains no real persons, locations, rates or official Dominican Republic statistics. Intended only to practice contracts, temporal evaluation, subgroup auditing and governance. Prohibited: operational profiling or inference about real populations.

## Resumen verificado (E07)
- 640 casos del 01-01-2026 al 27-12-2026 (fechas repetidas permitidas), 9 columnas, sin nulos ni identificadores directos.
- Objetivo binario `target`: 55.2 % de positivos (G1 49.7 %, G2 63.9 %).
- Grupos: G1 396, G2 244; franjas de edad 18-29, 30-44, 45-59 y 60+; zonas Norte, Sur, Este y Oeste.
- Partición temporal: 480 casos de entrenamiento (hasta el 24-09-2026) y 160 de prueba (desde el 25-09-2026).
- Excluidas del modelo: `case_id`, `received_date`, `protected_group` y `target`.
- `zone` tiene distribución casi igual por grupo; `infrastructure_score` y `exposure` permiten inferir parcialmente el grupo (AUC 0.70).
- Deriva: la proporción de positivos en G2 sube de 0.61 en entrenamiento a 0.73 en prueba.
