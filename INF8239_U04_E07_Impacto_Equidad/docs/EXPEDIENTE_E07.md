# Expediente E07 · Evaluación de impacto y auditoría de equidad

Sistema: **Territorial Review DSS – Synthetic** (datos sintéticos, uso educativo). Fuente de cada cifra: `reports/`.

## 1. Finalidad, interesados y proporcionalidad
- **Finalidad:** ordenar casos para revisión humana; el modelo no decide intervenciones (`student_inputs/lab11_impact.yml`).
- **Interesados:** persona afectada, operador, responsable institucional y equipo de datos (`student_inputs/stakeholders.csv`), con beneficios, daños, poder y participación.
- **Proporcionalidad:** la decisión asistida es de bajo nivel (orden de una cola), existe una alternativa no predictiva (criterios fijos por orden de llegada) y los usos de alto impacto (elegibilidad, intervención automática, emergencia) están prohibidos. Se usa el mínimo de variables: el grupo protegido no entra al modelo; `zone` se conserva porque no funciona como proxy del grupo (distribución casi igual por zona), mientras que `infrastructure_score` y `exposure` sí lo predicen parcialmente (AUC 0.70), riesgo R03.

## 2. Marco normativo: obligación, marco voluntario y recomendación ética
| Tipo | Instrumento | Aplicación al caso | Estado en este proyecto |
|---|---|---|---|
| Obligación legal (RD) | Constitución de la República Dominicana, art. 39 (derecho a la igualdad) | Prohíbe la discriminación; aplicaría a cualquier uso con personas reales | No se activa con datos sintéticos; fundamenta la auditoría por grupo |
| Obligación legal (RD) | Ley 172-13 de protección integral de datos de carácter personal | Tratamiento de datos personales y sensibles con datos reales | Sin datos personales; el esquema rechaza identificadores directos (`validate_schema`) |
| Obligación legal (RD, sector público) | Ley 200-04 General de Libre Acceso a la Información Pública | Transparencia si una institución pública usara el sistema | Se documentan finalidad, métricas y límites de forma pública |
| Marco voluntario | NIST AI RMF 1.0 (NIST AI 100-1, 2023) | Estructura GOVERN, MAP, MEASURE y MANAGE y características de confiabilidad | Aplicado en el registro de riesgos y en `rmf_summary.json` |
| Marco voluntario | ISO/IEC 42001:2023 (sistemas de gestión de IA) | Gobierno organizacional de la IA | Referencia para la matriz RACI; no se certifica |
| Recomendación ética | UNESCO, Recomendación sobre la ética de la inteligencia artificial (2021) | Supervisión humana, equidad, proporcionalidad, rendición de cuentas | Revisión humana de todos los casos, apelación y condiciones de retiro |
| Recomendación ética (propia) | Criterios de este expediente | Recall mínimo por grupo, intervalos y no usar el grupo al decidir | Criterios C2 y C3 y regla de decisión |

> La interpretación normativa es de la estudiante y debe verificarse con asesoría jurídica antes de cualquier uso real. El EU AI Act no es vinculante en la República Dominicana; solo se cita como referencia comparada si se discute en clase.

## 3. Registro de riesgos y NIST AI RMF
Ocho riesgos con probabilidad, impacto, prioridad (probabilidad × impacto), control, responsable, evidencia, riesgo residual, función del RMF y característica de confiabilidad: `student_inputs/risk_register.csv` y `reports/lab11/risk_register_scored.csv`. Prioridades más altas: R02 deriva temporal (9), R01 menor recall en G1 (8) y R07 subgrupos interseccionales ocultos (8).

| Función | Evidencia |
|---|---|
| GOVERN | Responsable (Product Owner), RACI completo, usos prohibidos y puertas en `configs/governance.yml` |
| MAP | Finalidad, contexto, partes interesadas, alternativa no predictiva y riesgos R03–R04 |
| MEASURE | Auditoría global, por grupo e interseccional con intervalos bootstrap (`reports/lab12`) |
| MANAGE | Mitigaciones comparadas, decisión, condiciones de retiro, apelación y monitoreo |

## 4. Auditoría (modelo base M0, prueba temporal de 160 casos)
- Global: exactitud 0.719, recall 0.717, precisión 0.776, FPR 0.279. Cumple las puertas oficiales (decisión automática de LAB13: GO).
- Por grupo: recall G1 0.653 frente a G2 0.791 (brecha 0.138, IC 95 % −0.04 a 0.32); FPR G1 0.250 frente a G2 0.375 (brecha 0.125). G1 queda por debajo del recall mínimo de 0.68.
- Interseccional: peor recall en G1 | 30-44 (0.56, n = 24) y G1 | 45-59 (0.59, n = 35); peor FPR en G2 | 60+ (0.56, n = 26) y G2 | 30-44 (0.50, n = 14). Las celdas tienen entre 8 y 35 casos.
- Deriva: la proporción de positivos en G2 pasa de 0.61 (entrenamiento) a 0.73 (prueba).

## 5. Mitigación, trade-offs y decisión
Ocho estrategias en `reports/lab12/mitigation_comparison.csv`, evaluadas con tres criterios cada vez más exigentes: C1 puertas oficiales; C2 C1 + recall ≥ 0.68 en cada grupo; C3 C2 + IC 95 % de las brechas dentro de la tolerancia.

- Solo M0, M4, M4d y M6 cumplen C1; solo M4 y M6 cumplen C2; ninguna cumple C3 (los intervalos son demasiado anchos con 160 casos).
- M4 (reducción por paridad de recall) es aleatorizada: el 20 % de los casos cambia de decisión según la semilla, lo que vuelve inconsistentes las decisiones. M6 usa el grupo protegido para decidir (trato diferenciado explícito). Ambas se excluyen.
- La versión determinista M4d reduce las brechas (recall 0.117, FPR 0.125) y sube el recall de G1 a 0.673, sin alcanzar 0.68.

**Daño prioritario (decisión de la estudiante):** falsos negativos y falsos positivos pesan igual; por eso se vigilan juntas las brechas de recall y de FPR.

**Decisión propuesta por regla explícita** (`propose_decision`, a ratificar): **MODIFICAR + LIMITAR**. Adoptar M4d solo en un piloto que ordena la cola, con revisión humana de todos los casos, monitoreo mensual por grupo e intersección, condiciones de retiro y canal de apelación. No desplegar de forma general mientras no se cumpla C3 con más datos. Se descartan: DESPLEGAR (no hay evidencia suficiente de equidad, aunque las puertas globales digan GO) y NO UTILIZAR (el piloto con revisión humana mantiene los daños acotados y genera la evidencia que falta).
