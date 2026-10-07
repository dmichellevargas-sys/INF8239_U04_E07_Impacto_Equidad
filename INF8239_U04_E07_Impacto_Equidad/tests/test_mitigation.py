import warnings

import numpy as np
import pandas as pd
import pytest

from inf8239_u04.data import load_data, temporal_split
from inf8239_u04.mitigation import bootstrap_gap, evaluate_criteria, propose_decision

GATES = {"min_recall": 0.68, "max_recall_gap": 0.16, "max_fpr_gap": 0.16}
ROW = {"recall": 0.72, "recall_gap": 0.10, "fpr_gap": 0.10, "recall_G1": 0.70, "recall_G2": 0.80}
NARROW = {"recall_low": -0.05, "recall_high": 0.12, "fpr_low": -0.1, "fpr_high": 0.1}


def test_temporal_split_has_no_overlap_in_dates():
    train, test = temporal_split(load_data())
    assert train.received_date.max() < test.received_date.min()


def test_criteria_are_nested_from_lenient_to_strict():
    wide = {**NARROW, "recall_high": 0.30}
    assert evaluate_criteria(ROW, NARROW, GATES) == {
        "C1_puertas_oficiales": True, "C2_recall_por_grupo": True, "C3_intervalo_dentro_tolerancia": True}
    assert not evaluate_criteria(ROW, wide, GATES)["C3_intervalo_dentro_tolerancia"]
    low_group = {**ROW, "recall_G1": 0.60}
    result = evaluate_criteria(low_group, NARROW, GATES)
    assert result["C1_puertas_oficiales"] and not result["C2_recall_por_grupo"]


def _matrix(**overrides):
    base = {"strategy": "M0 base", "recall_gap": 0.13, "fpr_gap": 0.12, "determinista": True,
            "uses_group_at_decision": False, "C1_puertas_oficiales": True, "C2_recall_por_grupo": False,
            "C3_intervalo_dentro_tolerancia": False}
    return pd.DataFrame([{**base, **overrides}])


def test_decision_rule_limits_when_only_global_gates_pass():
    assert propose_decision(_matrix())["decision"] == "LIMITAR"


def test_decision_rule_never_uses_group_or_random_strategies():
    m = _matrix(strategy="M6 grupos", uses_group_at_decision=True, C2_recall_por_grupo=True,
                C3_intervalo_dentro_tolerancia=True)
    assert propose_decision(m)["decision"] == "NO UTILIZAR"


def test_decision_rule_deploys_only_with_strict_evidence():
    m = _matrix(C2_recall_por_grupo=True, C3_intervalo_dentro_tolerancia=True)
    assert propose_decision(m)["decision"] == "DESPLEGAR"
    assert propose_decision(_matrix(C1_puertas_oficiales=False))["decision"] == "NO UTILIZAR"


def test_bootstrap_interval_contains_zero_for_identical_groups():
    test = pd.DataFrame({"target": [1, 0] * 100, "protected_group": ["G1"] * 100 + ["G2"] * 100})
    pred = np.array([1, 0] * 100)
    low, high = bootstrap_gap(test, pred, "recall", n=200)
    assert low == pytest.approx(0.0) and high == pytest.approx(0.0)


def test_comparison_runs_on_real_dataset():
    from inf8239_u04.mitigation import compare
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        table, info = compare(load_data(), 0.68)
    assert {"recall_gap", "fpr_gap", "worst_intersection_recall"} <= set(table.columns)
    assert 0 <= info["m4_unstable_share"] <= 1 and len(table) == 8
