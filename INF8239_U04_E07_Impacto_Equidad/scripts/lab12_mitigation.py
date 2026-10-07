"""LAB12 ampliado: mitigación, trade-offs, criterios de equidad y propuesta de decisión.

Uso:  uv run python scripts/lab12_mitigation.py
"""
import json
import warnings
from pathlib import Path

import pandas as pd

from inf8239_u04.data import load_data, temporal_split
from inf8239_u04.governance import load_config
from inf8239_u04.mitigation import bootstrap_gap, compare, evaluate_criteria, predictions, propose_decision

warnings.filterwarnings("ignore", category=FutureWarning)
out = Path("reports/lab12")
out.mkdir(parents=True, exist_ok=True)
gates = load_config()["gates"]
df = load_data()
_, test = temporal_split(df)
table, info = compare(df, gates["min_recall"])
preds = predictions(df, gates["min_recall"])
rows = []
for _, row in table.iterrows():
    key = row["strategy"].split()[0]
    r_lo, r_hi = bootstrap_gap(test, preds[key], "recall")
    f_lo, f_hi = bootstrap_gap(test, preds[key], "fpr")
    ci = {"recall_low": r_lo, "recall_high": r_hi, "fpr_low": f_lo, "fpr_high": f_hi}
    rows.append({**row.to_dict(), **{f"ci95_{k}": v for k, v in ci.items()}, **evaluate_criteria(row.to_dict(), ci, gates),
                 "determinista": key not in {"M4", "M5", "M6"}})
matrix = pd.DataFrame(rows)
matrix.to_csv(out / "mitigation_comparison.csv", index=False)
proposal = propose_decision(matrix)
(out / "decision_proposal.json").write_text(json.dumps({"gates": gates, **info, **proposal,
    "nota": "Propuesta generada por regla explícita; requiere ratificación de la persona responsable."},
    indent=2, ensure_ascii=False), encoding="utf-8")
cols = ["strategy", "recall", "recall_G1", "recall_gap", "fpr_gap", "ci95_recall_low", "ci95_recall_high",
        "C1_puertas_oficiales", "C2_recall_por_grupo", "C3_intervalo_dentro_tolerancia", "determinista",
        "uses_group_at_decision"]
print(matrix[cols].round(3).to_string(index=False))
print(proposal, info)
