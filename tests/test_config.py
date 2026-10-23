"""Tests for the sector configuration.

These run anywhere — no TIP account and no PATSTAT connection needed:

    pytest tests/

They guard the things that have actually bitten us: a CPC prefix silently
failing to select the subgroups it looks like it should, and a keyword broad
enough to drag in a neighbouring technology.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from stage00_config import load_config  # noqa: E402


@pytest.fixture(scope="module")
def cfg():
    return load_config()


def test_config_loads(cfg):
    assert cfg.sector_name == "Quantum computing"
    assert cfg.client == "Dell"
    assert cfg.team == 30


def test_window_is_closed_at_a_complete_year(cfg):
    """No incomplete year may be plotted: the window ends where completeness does."""
    assert cfg.year_min < cfg.year_max
    assert cfg.last_complete_year == cfg.year_max


def test_core_cpc_lists_every_subgroup_explicitly(cfg):
    """Prefix matching is a string operation, not a hierarchy walk.

    'G06N10/00' does not match 'G06N10/20', because that string does not begin
    with 'G06N10/00'. Listing the parent alone would silently drop five of the
    six core groups, so every subgroup must appear.
    """
    expected = {"G06N10/00", "G06N10/20", "G06N10/40",
                "G06N10/60", "G06N10/70", "G06N10/80"}
    assert expected <= set(cfg.cpc_core)


def test_legacy_codes_are_not_in_the_active_definition(cfg):
    """G06N99/002 belongs to the pre-2019 scheme and is held back deliberately."""
    assert cfg.cpc_legacy, "the legacy code should still be recorded"
    assert not set(cfg.cpc_legacy) & set(cfg.cpc_prefixes)


def test_excluded_codes_are_not_in_the_active_definition(cfg):
    """B82Y10/00 was removed on evidence; it must not creep back in.

    Counted on its own it held 96% of the year-2000 families, fell 89% from its
    2004 peak to its 2014 trough and compounded at zero across the window — all
    of the distortion in the volume curve and none of the trend. The code stays
    recorded under `excluded` so the decision is visible rather than invisible.
    """
    assert "B82Y10/00" in cfg.cpc_excluded
    assert not set(cfg.cpc_excluded) & set(cfg.cpc_prefixes)


def test_josephson_code_is_out_after_validation(cfg):
    """H10N60/12 was dropped on evidence: 1 of 20 families entering only through
    it was quantum computing (docs/validation.md). It stays recorded as excluded."""
    assert "H10N60/12" in cfg.cpc_excluded
    assert "H10N60/12" not in cfg.cpc_prefixes


def test_generic_quantum_computing_stem_is_not_a_keyword(cfg):
    """'quantum comput' matched 27 of 39 keyword-only false positives: passing
    mentions and post-quantum cryptography. Only specific terms select a family."""
    assert "quantum comput" not in cfg.keywords


def test_keyword_exclusions_cannot_cancel_a_keyword(cfg):
    """An exclusion phrase contained in a keyword would drop every match of that
    keyword; one contained in an exclusion of its own is merely redundant."""
    assert cfg.keyword_exclusions, "the post-quantum exclusions should be configured"
    for phrase in cfg.keyword_exclusions:
        assert phrase == phrase.strip().lower(), f"{phrase!r} is not lower-case and stripped"
        for term in cfg.keywords:
            assert phrase not in term, f"exclusion {phrase!r} would cancel keyword {term!r}"


def test_communication_codes_are_separable(cfg):
    """The scope boundary must be testable without editing the pipeline."""
    assert set(cfg.cpc_communication) <= set(cfg.cpc_prefixes)
    assert not set(cfg.cpc_communication) & set(cfg.cpc_computing_only)


def test_no_dangerously_broad_keyword(cfg):
    """Guard against terms that match neighbouring technologies.

    'quantum' alone matches quantum dot, quantum well and quantum efficiency —
    optoelectronics and photovoltaics, not computing. 'squid' matches the animal
    and, more awkwardly, SQUID magnetometers used in MRI and geophysics.
    """
    banned = {"quantum", "squid", "superconduct", "photonic", "laser"}
    lowered = {k.lower().strip() for k in cfg.keywords}
    assert not (banned & lowered)


def test_keywords_are_lowercase_and_stripped(cfg):
    """Matching lower-cases both sides; stray case or whitespace signals a typo."""
    for term in cfg.keywords:
        assert term == term.strip(), f"{term!r} has surrounding whitespace"
        assert term == term.lower(), f"{term!r} is not lower-case"


def test_time_columns_are_real_patstat_columns(cfg):
    valid = {"appln_filing_year", "earliest_publn_year", "earliest_filing_year"}
    assert cfg.family_time_column in valid
    assert cfg.appln_time_column in valid


def test_ipr_type_excludes_utility_models(cfg):
    """'PI' keeps patents of invention; 'UM' would add utility models."""
    assert cfg.ipr_type == "PI"
