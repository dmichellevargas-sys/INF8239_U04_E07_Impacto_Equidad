# Declaración de uso de IA · Ejercicio 07

**Herramienta:** Claude (Anthropic), interfaz web claude.ai, en un proyecto de la asignatura. Octubre de 2026.

## Finalidad y fragmentos afectados
- Revisión del proyecto base (LAB11-LAB13) y corrección de errores.
- Código nuevo: `src/inf8239_u04/mitigation.py` (estrategias de mitigación, intervalos bootstrap, criterios C1-C3 y regla de decisión), `scripts/lab12_mitigation.py`, `scripts/make_figures.py`, `tests/test_mitigation.py` y una prueba en `tests/test_impact.py`.
- Cambios en scripts base: `scripts/lab11_impact.py` (registro de decisión y resumen RMF) y `scripts/simulate_incident.py`.
- Borradores de `student_inputs/` (evaluación de impacto, partes interesadas, registro de riesgos, decisión LAB12), `docs/EXPEDIENTE_E07.md`, el notebook y el informe PDF.

## Prompts relevantes y valores del análisis
1. Se entregaron los archivos del proyecto base con el enunciado y la rúbrica; luego: *"listo"*.
2. La IA presentó la evidencia y pidió a la estudiante decidir tres valores. Respuestas:
   - **Daño prioritario:** *"Ambos por igual"* (decisión de la estudiante).
   - **Criterio de equidad:** *"elige la mejor o si es más conveniente evaluar todo para determinar qué es lo mejor"*.
   - **Decisión final:** *"elige lo que sea mejor o hacerlo todo para demostrar que es lo mejor para usar"*.
3. Como el enunciado prohíbe que la IA decida los valores, ante la delegación la IA **no eligió un único criterio**: evaluó los tres criterios (C1, C2, C3) para todas las estrategias y propuso una regla de decisión explícita y comprobable (`propose_decision`). La decisión MODIFICAR + LIMITAR es una **propuesta** que la estudiante debe ratificar o modificar y defender.

## Verificaciones humanas
> Marque solo lo que haya comprobado personalmente.

- [ ] Ejecuté `uv run pytest -q` y los scripts de LAB11 y LAB12 y obtuve las mismas cifras.
- [ ] Leí y ajusté con mi criterio la evaluación de impacto, las partes interesadas y el registro de riesgos.
- [ ] Revisé la regla de decisión y **ratifico / modifico** (tache lo que no corresponda) la decisión MODIFICAR + LIMITAR.
- [ ] Verifiqué en las fuentes oficiales la Constitución (art. 39), la Ley 172-13, la Ley 200-04, NIST AI 100-1, ISO/IEC 42001 y la Recomendación de la UNESCO.
- [ ] Puedo explicar cada archivo modificado o creado.

## Errores detectados y correcciones
| Problema | Corrección |
|---|---|
| `scripts/lab11_impact.py` y `scripts/simulate_incident.py` tenían cadenas con saltos de línea literales y no compilaban. | Se reescribieron con cadenas multilínea válidas; `lab11_impact.py` ahora genera el registro de decisión a partir de `lab12_decision.yml`. |
| `ExponentiatedGradient` fallaba con el pipeline de scikit-learn (no acepta `sample_weight`). | Se indicó `sample_weight_name="logisticregression__sample_weight"`. |
| La mitigación por reducción da predicciones aleatorizadas (20 % de casos inestables). | Se añadió una versión determinista (M4d) y se excluyeron las estrategias aleatorizadas de la decisión. |
| El umbral global elegido en validación (M3) bajó el recall en prueba por deriva temporal. | Se reporta como hallazgo; no se ajustó con la prueba. |
| La figura de trade-offs superponía etiquetas. | Se desplazaron las etiquetas. |

## Responsabilidad
La estudiante responde por las referencias, la interpretación normativa, el código y las conclusiones, y debe poder defender cada elemento.
