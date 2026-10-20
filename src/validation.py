"""Step 0 — precision of the sector definition, from the hand-labelled sample.

The protocol is in docs/validation.md; the sample is drawn by
notebooks/STEP0_validation.ipynb. This module holds only the arithmetic. It
reads no PATSTAT table, so it runs anywhere and is covered by
tests/test_validation.py.

Labels are strings: "1" (quantum computing), "0" (not) and "?" (cannot tell).
Precision counts "1" against "1" + "0"; "?" is reported but left out, since a
family nobody could judge is evidence about the abstract, not the query.
"""

from __future__ import annotations

import math

import pandas as pd

LABELS = ("1", "0", "?")
RATER_COLUMNS = ("rater_1", "rater_2", "final")
Z95 = 1.959963984540054


def normalise_labels(values: pd.Series) -> pd.Series:
    """Map 1, 1.0, " 1 " to "1" and blanks to "". Anything else is an error."""

    def one(value):
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return ""
        text = str(value).strip()
        if text.endswith(".0"):              # spreadsheets turn 1 into 1.0
            text = text[:-2]
        if text not in LABELS + ("",):
            raise ValueError(f"unexpected label {value!r}; use 1, 0 or ?")
        return text

    return values.map(one)


def resolve_final(labels: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fill a blank `final` where both raters agree.

    Returns the labels with normalised columns, and the rows that still have no
    final label: those the raters disagree on, or that one of them skipped.
    They must be settled by discussion before precision can be computed.
    """
    out = labels.copy()
    for column in RATER_COLUMNS:
        out[column] = normalise_labels(out[column])
    agreed = (out["final"] == "") & (out["rater_1"] == out["rater_2"]) & (out["rater_1"] != "")
    out.loc[agreed, "final"] = out.loc[agreed, "rater_1"]
    return out, out[out["final"] == ""]


def wilson_interval(k: int, n: int, z: float = Z95) -> tuple[float, float]:
    """Wilson score interval for k successes in n trials.

    Preferred to the normal approximation because our strata are small and their
    precision is close to 1, where the normal interval runs past 100%.
    """
    if n == 0:
        return math.nan, math.nan
    p = k / n
    denominator = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return max(0.0, centre - half), min(1.0, centre + half)


def stratum_precision(labelled: pd.DataFrame) -> pd.DataFrame:
    """One row per stratum: counts of each label, precision and its 95% interval.

    `labelled` needs the columns `stratum` and `final`.
    """
    rows = []
    for stratum, group in labelled.groupby("stratum"):
        yes = int((group["final"] == "1").sum())
        no = int((group["final"] == "0").sum())
        unsure = int((group["final"] == "?").sum())
        judged = yes + no
        low, high = wilson_interval(yes, judged)
        rows.append({
            "stratum": stratum, "labelled": len(group), "yes": yes, "no": no, "unsure": unsure,
            "precision": yes / judged if judged else math.nan, "ci_low": low, "ci_high": high,
        })
    return pd.DataFrame(rows).set_index("stratum")


def weighted_precision(per_stratum: pd.DataFrame, population: pd.Series) -> tuple[float, float, float]:
    """Combine stratum precisions by population weight: p = sum(N_s p_s) / sum(N_s).

    `population` maps stratum to its number of families. The interval uses the
    stratified-sampling variance sum(W_s^2 p_s (1 - p_s) / n_s); a stratum with
    perfect precision contributes no variance, so the interval is narrow when
    the large strata are near 1 — read it alongside the per-stratum intervals.
    """
    sizes = population.reindex(per_stratum.index).astype(float)
    if sizes.isna().any():
        raise ValueError(f"no population size for strata {list(sizes[sizes.isna()].index)}")
    weights = sizes / sizes.sum()
    p = per_stratum["precision"]
    n = per_stratum["yes"] + per_stratum["no"]
    estimate = float((weights * p).sum())
    se = math.sqrt(float((weights**2 * p * (1 - p) / n).sum()))
    return estimate, max(0.0, estimate - Z95 * se), min(1.0, estimate + Z95 * se)


def rater_agreement(labels: pd.DataFrame) -> dict:
    """Raw agreement and Cohen's kappa between rater_1 and rater_2.

    Kappa discounts the agreement two raters would reach by chance. With most
    families labelled "1", raw agreement is high almost automatically, which is
    why both are reported.
    """
    both = labels[(labels["rater_1"] != "") & (labels["rater_2"] != "")]
    if both.empty:
        return {"n": 0, "agreement": math.nan, "disagreements": 0, "kappa": math.nan}
    observed = float((both["rater_1"] == both["rater_2"]).mean())
    categories = set(both["rater_1"]) | set(both["rater_2"])
    expected = sum(float((both["rater_1"] == c).mean()) * float((both["rater_2"] == c).mean())
                   for c in categories)
    kappa = (observed - expected) / (1 - expected) if expected < 1 else math.nan
    return {
        "n": len(both),
        "agreement": observed,
        "disagreements": int((both["rater_1"] != both["rater_2"]).sum()),
        "kappa": kappa,
    }
