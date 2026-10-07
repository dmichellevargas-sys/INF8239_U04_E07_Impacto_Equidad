import json
from pathlib import Path
import pandas as pd, yaml
from inf8239_u04.impact import validate_impact, score_risks
out=Path("reports/lab11"); out.mkdir(parents=True,exist_ok=True)
impact=yaml.safe_load(Path("student_inputs/lab11_impact.yml").read_text(encoding="utf-8")); validate_impact(impact)
stake=pd.read_csv("student_inputs/stakeholders.csv")
if stake.astype(str).apply(lambda s:s.str.contains("REPLACE")).any().any(): raise ValueError("Complete stakeholders.csv")
risks=score_risks(pd.read_csv("student_inputs/risk_register.csv")); risks.to_csv(out/"risk_register_scored.csv",index=False); stake.to_csv(out/"stakeholders.csv",index=False)
rmf = {"GOVERN": "Responsable, RACI y usos prohibidos (student_inputs/raci.csv, configs/governance.yml)",
       "MAP": f"Finalidad, partes interesadas y {len(risks)} riesgos documentados",
       "MEASURE": "Auditoría global, por grupo e interseccional con intervalos (reports/lab12)",
       "MANAGE": "Mitigación, condiciones de retiro y apelación (lab11_impact.yml, decision_proposal.json)",
       "risks_by_function": risks.groupby("rmf_function")["id"].apply(list).to_dict() if "rmf_function" in risks else {}}
(out/"rmf_summary.json").write_text(json.dumps(rmf, indent=2, ensure_ascii=False), encoding="utf-8")
decision = yaml.safe_load(Path("student_inputs/lab12_decision.yml").read_text(encoding="utf-8"))
lines = ["# Decision record", "", f"- Responsable: {impact['owner']}", f"- Finalidad: {impact['purpose']}"]
lines += [f"- {k}: {v}" for k, v in decision.items()]
lines += ["", "Estado: REVIEW hasta ratificación humana (ver reports/lab12/decision_proposal.json)."]
(out/"DECISION_RECORD.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(risks[["id","priority","owner"]].head(3).to_string(index=False))
