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

from config import load_config  # noqa: E402


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
