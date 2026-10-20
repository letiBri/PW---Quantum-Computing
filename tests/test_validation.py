"""Tests for the validation arithmetic in src/validation.py.

No TIP account or PATSTAT connection needed:

    pytest tests/
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from validation import (  # noqa: E402
    normalise_labels,
    rater_agreement,
    resolve_final,
    stratum_precision,
    weighted_precision,
    wilson_interval,
)


def test_spreadsheet_labels_are_normalised():
    raw = pd.Series([1, 0.0, " ? ", "1.0", None, float("nan")])
    assert normalise_labels(raw).tolist() == ["1", "0", "?", "1", "", ""]


def test_unknown_label_is_rejected():
    with pytest.raises(ValueError):
        normalise_labels(pd.Series(["yes"]))


def test_final_is_filled_only_where_raters_agree():
    labels = pd.DataFrame({
        "rater_1": [1, 1, 0, ""],
        "rater_2": [1, 0, 0, 1],
        "final":   ["", "", "", ""],
    })
    resolved, unresolved = resolve_final(labels)
    assert resolved["final"].tolist() == ["1", "", "0", ""]
    assert len(unresolved) == 2


def test_an_explicit_final_overrides_the_raters():
    labels = pd.DataFrame({"rater_1": [1], "rater_2": [0], "final": [0]})
    resolved, unresolved = resolve_final(labels)
    assert resolved["final"].tolist() == ["0"] and unresolved.empty


def test_wilson_interval_stays_inside_unit_range_at_perfect_precision():
    low, high = wilson_interval(20, 20)
    assert 0.8 < low < 1.0 and high == 1.0


def test_wilson_interval_known_value():
    # 8 of 10: the Wilson 95% interval is about 0.490 to 0.943
    low, high = wilson_interval(8, 10)
    assert low == pytest.approx(0.490, abs=1e-3)
    assert high == pytest.approx(0.943, abs=1e-3)


def test_unsure_labels_are_counted_but_left_out_of_precision():
    labelled = pd.DataFrame({"stratum": ["C"] * 5, "final": ["1", "1", "1", "0", "?"]})
    row = stratum_precision(labelled).loc["C"]
    assert (row["yes"], row["no"], row["unsure"]) == (3, 1, 1)
    assert row["precision"] == pytest.approx(0.75)


def test_weighted_precision_uses_population_not_sample_weights():
    labelled = pd.DataFrame({
        "stratum": ["A"] * 10 + ["C"] * 10,
        "final": ["1"] * 10 + ["1"] * 5 + ["0"] * 5,
    })
    per_stratum = stratum_precision(labelled)
    # A is nine times larger than C in the population, so the total leans to A.
    estimate, low, high = weighted_precision(per_stratum, pd.Series({"A": 900, "C": 100}))
    assert estimate == pytest.approx(0.9 * 1.0 + 0.1 * 0.5)
    assert low < estimate < high


def test_weighted_precision_needs_every_stratum_size():
    per_stratum = stratum_precision(pd.DataFrame({"stratum": ["A", "B"], "final": ["1", "1"]}))
    with pytest.raises(ValueError):
        weighted_precision(per_stratum, pd.Series({"A": 10}))


def test_kappa_is_one_for_perfect_agreement_and_zero_for_chance():
    same = pd.DataFrame({"rater_1": ["1", "0", "1", "0"], "rater_2": ["1", "0", "1", "0"]})
    assert rater_agreement(same)["kappa"] == pytest.approx(1.0)

    chance = pd.DataFrame({"rater_1": ["1", "1", "0", "0"], "rater_2": ["1", "0", "1", "0"]})
    result = rater_agreement(chance)
    assert result["agreement"] == pytest.approx(0.5)
    assert result["kappa"] == pytest.approx(0.0)
    assert result["disagreements"] == 2


def test_agreement_ignores_rows_one_rater_skipped():
    labels = pd.DataFrame({"rater_1": ["1", "1", ""], "rater_2": ["1", "", "0"]})
    assert rater_agreement(labels)["n"] == 1
    assert math.isclose(rater_agreement(labels)["agreement"], 1.0)
