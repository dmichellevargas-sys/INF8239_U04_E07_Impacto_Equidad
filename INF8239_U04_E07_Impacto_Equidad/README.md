# INF-8239 · Ejercicio 07 · Evaluación de impacto y auditoría de equidad

Expediente de LAB11-LAB12 sobre el DSS territorial **sintético** de la Unidad 04: finalidad, partes interesadas,
proporcionalidad, registro de riesgos con NIST AI RMF, auditoría global, por grupo e interseccional, mitigación,
trade-offs y decisión. Proyecto base del curso: Edwin Ramón José Nolasco.

> Los datos son sintéticos y didácticos. El sistema no autoriza decisiones automáticas sobre personas.

## Inicio
```bash
uv sync --frozen
uv run pytest -q                                 # 18 pruebas
uv run python scripts/check_environment.py
```

## Ruta del ejercicio
```bash
uv run python scripts/describe_dataset.py
uv run python scripts/lab12_audit.py --model logistic
uv run python scripts/lab12_audit.py --model tree
uv run python scripts/lab12_mitigation.py        # mitigaciones, criterios C1-C3 y propuesta de decisión
uv run python scripts/validate_lab12_decision.py
uv run python scripts/lab11_impact.py            # riesgos priorizados, resumen RMF y registro de decisión
uv run python scripts/make_figures.py
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/E07_impacto_equidad.ipynb
uv run streamlit run app.py
```
`lab11_impact.py` va después de LAB12 porque su registro de decisión usa `lab12_decision.yml`.

## Artefactos editables
| Archivo | Contenido |
|---|---|
| `student_inputs/lab11_impact.yml` | Finalidad, decisión asistida, usuarios, población, responsable, alternativa, usos fuera de alcance, retiro y apelación |
| `student_inputs/stakeholders.csv` | Partes interesadas: beneficio, daño, poder y participación |
| `student_inputs/risk_register.csv` | 8 riesgos con control, responsable, evidencia, residual y función NIST AI RMF |
| `student_inputs/raci.csv` | Responsabilidades (R y A obligatorios) |
| `student_inputs/lab12_decision.yml` | Daño prioritario, métrica, tolerancia, evidencia, limitación y recomendación |
| `docs/EXPEDIENTE_E07.md` | Síntesis del expediente y marco normativo (legal, voluntario y ético) |
| `docs/AI_USE_DECLARATION.md` | Declaración de uso de IA |

## Evidencias generadas
`reports/lab11/` (riesgos priorizados, RMF, registro de decisión), `reports/lab12/<modelo>/` (métricas globales, por grupo e interseccionales), `reports/lab12/mitigation_comparison.csv`, `reports/lab12/decision_proposal.json` y `reports/figures/` (se regeneran; los PNG están en `.gitignore` como en el proyecto base).

## Resultado principal
| Estrategia | Recall | Recall G1 | Brecha recall | Brecha FPR | C1 | C2 | C3 |
|---|---|---|---|---|---|---|---|
| M0 Logística base | 0.717 | 0.653 | 0.138 | 0.125 | ✓ | ✗ | ✗ |
| M4 Reducción (aleatorizada) | 0.739 | 0.694 | 0.097 | 0.106 | ✓ | ✓ | ✗ |
| **M4d Reducción determinista** | 0.728 | 0.673 | 0.117 | 0.125 | ✓ | ✗ | ✗ |
| M6 Umbrales por grupo (usa el grupo) | 0.793 | 0.816 | 0.049 | 0.154 | ✓ | ✓ | ✗ |

Decisión propuesta (a ratificar): **MODIFICAR + LIMITAR**. Detalle en `docs/EXPEDIENTE_E07.md`.

`docs/MODEL_CARD.md` y `docs/RUNBOOK.md` se completan en LAB13 (Ejercicio 08).

## Git
```bash
git init && git add . && git commit -m "chore: base project U04"
git add student_inputs docs/EXPEDIENTE_E07.md && git commit -m "docs: impact assessment, stakeholders and risk register"
git add src scripts tests && git commit -m "feat: mitigation comparison, fairness criteria and decision rule"
git add reports notebooks README.md docs && git commit -m "docs: audit evidence, notebook and AI use statement"
git tag u04-ejercicio07
```
