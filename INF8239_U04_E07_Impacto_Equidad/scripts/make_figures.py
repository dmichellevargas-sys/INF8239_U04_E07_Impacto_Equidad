"""Figuras de apoyo del expediente (se regeneran; los datos fuente están en reports/)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

out = Path("reports/figures")
out.mkdir(parents=True, exist_ok=True)
gates = {"min_recall": 0.68, "gap": 0.16}

g = pd.read_csv("reports/lab12/logistic/fairness_by_group.csv", index_col=0)
fig, ax = plt.subplots(figsize=(7, 3.6))
g[["recall", "fpr", "selection_rate", "precision"]].T.plot.bar(ax=ax, rot=0, color=["#1f77b4", "#e67e22"])
ax.axhline(gates["min_recall"], ls="--", c="gray", lw=1)
ax.text(-0.45, gates["min_recall"] + 0.02, "recall mínimo 0.68", fontsize=8, color="gray")
ax.set(title="Modelo base (M0): métricas por grupo en prueba", ylim=(0, 1))
ax.legend(title="Grupo")
fig.tight_layout()
fig.savefig(out / "fig_groups.png", dpi=170)
plt.close(fig)

inter = pd.read_csv("reports/lab12/logistic/fairness_intersectional.csv", index_col=0)
inter[["grupo", "edad"]] = inter.index.to_series().str.split(" \\| ", expand=True).values
fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
for ax, metric, cmap in ((axes[0], "recall", "RdYlGn"), (axes[1], "fpr", "RdYlGn_r")):
    pivot = inter.pivot(index="grupo", columns="edad", values=metric)
    counts = inter.pivot(index="grupo", columns="edad", values="count")
    im = ax.imshow(pivot.values, cmap=cmap, vmin=0, vmax=1)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, f"{pivot.values[i, j]:.2f}\nn={int(counts.values[i, j])}", ha="center", va="center", fontsize=8)
    ax.set_xticks(range(pivot.shape[1]), pivot.columns)
    ax.set_yticks(range(pivot.shape[0]), pivot.index)
    ax.set_title(f"{metric.upper()} interseccional (M0)")
    fig.colorbar(im, ax=ax, fraction=0.04)
fig.tight_layout()
fig.savefig(out / "fig_intersectional.png", dpi=170)
plt.close(fig)

m = pd.read_csv("reports/lab12/mitigation_comparison.csv")
m["key"] = m["strategy"].str.split().str[0]
fig, ax = plt.subplots(figsize=(7.5, 4.5))
for _, r in m.iterrows():
    color = "#c0392b" if r["uses_group_at_decision"] else ("#94a3b8" if not r["determinista"] else "#0f7c7b")
    ax.errorbar(r["recall_gap"], r["fpr_gap"], xerr=[[r["recall_gap"] - max(r["ci95_recall_low"], 0)],
                [r["ci95_recall_high"] - r["recall_gap"]]], fmt="o", color=color, capsize=3, alpha=0.8)
    ax.annotate(f"{r['key']} (recall {r['recall']:.2f})", (r["recall_gap"], r["fpr_gap"]), fontsize=8,
                xytext=(4, -11 if r["key"] == "M0" else 4), textcoords="offset points")
ax.axvline(gates["gap"], ls="--", c="gray", lw=1)
ax.axhline(gates["gap"], ls="--", c="gray", lw=1)
ax.set(xlabel="Brecha de recall (barra: IC 95 % de G2 − G1, recortado en 0)", ylabel="Brecha de FPR",
       title="Trade-offs de mitigación (verde: elegible; gris: aleatorizada; rojo: usa el grupo)")
fig.tight_layout()
fig.savefig(out / "fig_tradeoffs.png", dpi=170)
plt.close(fig)

r = pd.read_csv("reports/lab11/risk_register_scored.csv")
fig, ax = plt.subplots(figsize=(5.5, 4.5))
for _, row in r.iterrows():
    ax.scatter(row["likelihood_1_4"], row["impact_1_4"], s=400, alpha=0.35,
               color={"high": "#c0392b", "medium": "#e67e22", "low": "#27ae60"}[row["residual"]])
offsets = {}
for _, row in r.iterrows():
    key = (row["likelihood_1_4"], row["impact_1_4"])
    k = offsets.get(key, 0)
    offsets[key] = k + 1
    ax.annotate(row["id"], key, xytext=(-8, 10 - 12 * k), textcoords="offset points", fontsize=8)
ax.set(xlim=(0.5, 4.5), ylim=(0.5, 4.5), xticks=range(1, 5), yticks=range(1, 5), xlabel="Probabilidad (1-4)",
       ylabel="Impacto (1-4)", title="Registro de riesgos (color = riesgo residual)")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(out / "fig_risk_matrix.png", dpi=170)
plt.close(fig)
print("Figuras en", out)
