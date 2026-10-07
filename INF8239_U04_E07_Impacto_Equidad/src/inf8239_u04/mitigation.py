"""Evaluación de estrategias de mitigación con el mismo corte temporal y las mismas métricas.

Ninguna estrategia se ajusta mirando la prueba: los umbrales se eligen en una validación
temporal dentro del entrenamiento (último 25 % del periodo de entrenamiento).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from fairlearn.postprocessing import ThresholdOptimizer
from fairlearn.reductions import EqualizedOdds, ExponentiatedGradient, TruePositiveRateParity
from sklearn.metrics import precision_score, recall_score

from .data import features, temporal_split
from .fairness import audit, gap, intersectional
from .model import build_model

NO_ZONE = ["age_band", "previous_incidents", "infrastructure_score", "exposure"]


def group_metrics(y_true, y_pred, groups) -> dict:
    _, by_group, _ = audit(y_true, y_pred, groups)
    out = {f"{m}_{g}": float(by_group.loc[g, m]) for g in by_group.index for m in ("recall", "fpr", "selection_rate")}
    out["recall_gap"], out["fpr_gap"] = gap(by_group, "recall"), gap(by_group, "fpr")
    return out


def summarize(name: str, test: pd.DataFrame, pred: np.ndarray, uses_group_at_decision: bool, note: str) -> dict:
    y = test.target.to_numpy()
    _, inter, _ = audit(test.target, pred, intersectional(test))
    big = inter[inter["count"] >= 10]
    return {
        "strategy": name, "accuracy": float((pred == y).mean()), "recall": float(recall_score(y, pred)),
        "precision": float(precision_score(y, pred, zero_division=0)), "fpr": float(pred[y == 0].mean()),
        "selection_rate": float(pred.mean()), "reviews_per_100": float(pred.mean() * 100),
        **group_metrics(test.target, pred, test.protected_group),
        "worst_intersection_recall": float(big["recall"].min()),
        "worst_intersection": str(big["recall"].idxmin()),
        "uses_group_at_decision": uses_group_at_decision, "note": note,
    }


def threshold_for_recall(model, valid: pd.DataFrame, target_recall: float) -> float:
    """Mayor umbral global cuyo recall en validación alcanza `target_recall` en TODOS los grupos."""
    scores = model.predict_proba(features(valid))[:, 1]
    for t in np.round(np.arange(0.70, 0.19, -0.01), 2):
        pred = (scores >= t).astype(int)
        recalls = [recall_score(valid.target[valid.protected_group == g], pred[valid.protected_group == g])
                   for g in sorted(valid.protected_group.unique())]
        if min(recalls) >= target_recall:
            return float(t)
    return 0.2


def compare(df: pd.DataFrame, min_recall: float) -> tuple[pd.DataFrame, dict]:
    train, test = temporal_split(df)
    inner_train, valid = temporal_split(train)
    rows, info = [], {}

    base = build_model("logistic").fit(features(train), train.target)
    rows.append(summarize("M0 Logística base (umbral 0.50)", test, base.predict(features(test)), False,
                          "Modelo del laboratorio"))
    tree = build_model("tree").fit(features(train), train.target)
    rows.append(summarize("M1 Árbol (profundidad 5)", test, tree.predict(features(test)), False,
                          "Alternativa del laboratorio"))

    no_zone = build_model("logistic")
    no_zone.steps[0][1].transformers = [("cat", no_zone.steps[0][1].transformers[0][1], ["age_band"]),
                                        no_zone.steps[0][1].transformers[1]]
    no_zone.fit(train[NO_ZONE], train.target)
    rows.append(summarize("M2 Logística sin zona", test, no_zone.predict(test[NO_ZONE]), False,
                          "Prueba de minimización de variables"))

    tuner = build_model("logistic").fit(features(inner_train), inner_train.target)
    threshold = threshold_for_recall(tuner, valid, min_recall)
    info["global_threshold"] = threshold
    pred = (base.predict_proba(features(test))[:, 1] >= threshold).astype(int)
    rows.append(summarize(f"M3 Logística, umbral global {threshold:.2f}", test, pred, False,
                          "Umbral elegido en validación para que cada grupo alcance el recall mínimo"))

    for label, constraint in (("M4 Reducción: paridad de recall", TruePositiveRateParity(difference_bound=0.05)),
                              ("M5 Reducción: igualdad de oportunidades y FPR", EqualizedOdds(difference_bound=0.05))):
        mitigator = ExponentiatedGradient(build_model("logistic"), constraints=constraint,
                                         sample_weight_name="logisticregression__sample_weight")
        mitigator.fit(features(train), train.target, sensitive_features=train.protected_group)
        rng_pred = mitigator.predict(features(test), random_state=42)
        rows.append(summarize(label, test, np.asarray(rng_pred).astype(int), False,
                              "Usa el grupo solo al entrenar; predicción aleatorizada"))
        if label.startswith("M4"):
            det = (mitigator._pmf_predict(features(test))[:, 1] >= 0.5).astype(int)
            rows.append(summarize("M4d Reducción: paridad de recall (determinista)", test, det, False,
                                  "M4 con decisión determinista: probabilidad de la mezcla >= 0.5"))
            seeds = np.array([np.asarray(mitigator.predict(features(test), random_state=s)) for s in range(20)])
            info["m4_unstable_share"] = float((seeds.min(0) != seeds.max(0)).mean())

    post = ThresholdOptimizer(estimator=build_model("logistic"), constraints="true_positive_rate_parity",
                              objective="balanced_accuracy_score", prefit=False, predict_method="predict_proba")
    post.fit(features(train), train.target, sensitive_features=train.protected_group)
    pred = post.predict(features(test), sensitive_features=test.protected_group, random_state=42)
    rows.append(summarize("M6 Umbrales por grupo (post-proceso)", test, np.asarray(pred).astype(int), True,
                          "Usa el grupo protegido al decidir: trato diferenciado explícito"))
    return pd.DataFrame(rows), info


def predictions(df: pd.DataFrame, min_recall: float) -> dict[str, np.ndarray]:
    """Predicciones de prueba de cada estrategia (para intervalos bootstrap)."""
    train, test = temporal_split(df)
    inner_train, valid = temporal_split(train)
    base = build_model("logistic").fit(features(train), train.target)
    out = {"M0": base.predict(features(test))}
    out["M1"] = build_model("tree").fit(features(train), train.target).predict(features(test))
    nz = build_model("logistic")
    nz.steps[0][1].transformers = [("cat", nz.steps[0][1].transformers[0][1], ["age_band"]), nz.steps[0][1].transformers[1]]
    out["M2"] = nz.fit(train[NO_ZONE], train.target).predict(test[NO_ZONE])
    t = threshold_for_recall(build_model("logistic").fit(features(inner_train), inner_train.target), valid, min_recall)
    out["M3"] = (base.predict_proba(features(test))[:, 1] >= t).astype(int)
    for key, constraint in (("M4", TruePositiveRateParity(difference_bound=0.05)), ("M5", EqualizedOdds(difference_bound=0.05))):
        eg = ExponentiatedGradient(build_model("logistic"), constraints=constraint,
                                   sample_weight_name="logisticregression__sample_weight")
        eg.fit(features(train), train.target, sensitive_features=train.protected_group)
        out[key] = np.asarray(eg.predict(features(test), random_state=42)).astype(int)
        if key == "M4":
            out["M4d"] = (eg._pmf_predict(features(test))[:, 1] >= 0.5).astype(int)
    post = ThresholdOptimizer(estimator=build_model("logistic"), constraints="true_positive_rate_parity",
                              objective="balanced_accuracy_score", prefit=False, predict_method="predict_proba")
    post.fit(features(train), train.target, sensitive_features=train.protected_group)
    out["M6"] = np.asarray(post.predict(features(test), sensitive_features=test.protected_group, random_state=42)).astype(int)
    return out


def evaluate_criteria(row: dict, ci: dict, gates: dict) -> dict:
    """Tres criterios de equidad, de menos a más exigente (todos sobre la misma prueba)."""
    c1 = (row["recall"] >= gates["min_recall"] and row["recall_gap"] <= gates["max_recall_gap"]
          and row["fpr_gap"] <= gates["max_fpr_gap"])
    c2 = c1 and min(row["recall_G1"], row["recall_G2"]) >= gates["min_recall"]
    c3 = c2 and max(abs(ci["recall_low"]), abs(ci["recall_high"])) <= gates["max_recall_gap"] \
        and max(abs(ci["fpr_low"]), abs(ci["fpr_high"])) <= gates["max_fpr_gap"]
    return {"C1_puertas_oficiales": c1, "C2_recall_por_grupo": c2, "C3_intervalo_dentro_tolerancia": c3}


def propose_decision(matrix: pd.DataFrame) -> dict:
    """Regla propuesta (a ratificar por la persona responsable):
    1. Solo estrategias deterministas y que no usan el grupo protegido al decidir.
    2. Si alguna cumple C3 -> DESPLEGAR (con monitoreo).
    3. Si alguna cumple C2 pero ninguna C3 -> LIMITAR (piloto con revisión humana) usando esa estrategia;
       si no es el modelo base, la decisión es MODIFICAR + LIMITAR.
    4. Si alguna cumple solo C1 -> LIMITAR con la de menores brechas (MODIFICAR + LIMITAR si no es el base)
       y vigilancia reforzada del grupo con menor recall.
    5. Si ninguna cumple C1 -> NO UTILIZAR."""
    eligible = matrix[matrix["determinista"] & ~matrix["uses_group_at_decision"]]
    for criterion, decision in (("C3_intervalo_dentro_tolerancia", "DESPLEGAR"),
                                ("C2_recall_por_grupo", "LIMITAR"), ("C1_puertas_oficiales", "LIMITAR")):
        ok = eligible[eligible[criterion]]
        if not ok.empty:
            best = ok.sort_values(["recall_gap", "fpr_gap"]).iloc[0]
            modified = not str(best["strategy"]).startswith("M0")
            label = decision if not modified or decision == "DESPLEGAR" else "MODIFICAR + LIMITAR"
            return {"decision": label, "strategy": str(best["strategy"]), "criterion_met": criterion}
    return {"decision": "NO UTILIZAR", "strategy": None, "criterion_met": None}


def bootstrap_gap(test: pd.DataFrame, pred: np.ndarray, metric: str = "recall", n: int = 2000, seed: int = 42):
    """Intervalo bootstrap (95 %) de la brecha entre grupos, remuestreando casos de prueba."""
    rng = np.random.default_rng(seed)
    y, g = test.target.to_numpy(), test.protected_group.to_numpy()
    values = []
    for _ in range(n):
        idx = rng.integers(0, len(y), len(y))
        yy, pp, gg = y[idx], pred[idx], g[idx]
        rates = []
        for grp in ("G1", "G2"):
            mask = (gg == grp) & ((yy == 1) if metric == "recall" else (yy == 0))
            rates.append(pp[mask].mean() if mask.any() else np.nan)
        values.append(rates[1] - rates[0])
    values = np.asarray(values)
    return float(np.nanquantile(values, 0.025)), float(np.nanquantile(values, 0.975))
