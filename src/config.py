"""Load the sector configuration.

Every parameter that defines the dataset — CPC codes, keywords, the time window,
the counting rules — lives in ``config/sector.yaml``. Nothing in the analysis
hard-codes them. This module is the single place that reads that file.

Usage, from a notebook on TIP or from a script in this folder::

    from config import load_config

    cfg = load_config()
    print(cfg.sector_name, len(cfg.cpc_prefixes), "CPC codes")

Run it directly to check that the file parses and to see what it contains::

    python src/config.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

# config/sector.yaml, found relative to this file so that the working directory
# does not matter.
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "sector.yaml"


@dataclass(frozen=True)
class SectorConfig:
    """The sector definition, as read from sector.yaml."""

    sector_name: str
    client: str
    team: int

    cpc_core: tuple[str, ...]
    cpc_hardware: tuple[str, ...]
    cpc_communication: tuple[str, ...]
    cpc_legacy: tuple[str, ...]
    keywords: tuple[str, ...]

    year_min: int
    year_max: int
    last_complete_year: int
    family_time_column: str
    appln_time_column: str

    ipr_type: str
    ip5_offices: tuple[str, ...]
    top_n: int
    env: str

    raw: dict = field(repr=False, default_factory=dict)

    @property
    def cpc_prefixes(self) -> tuple[str, ...]:
        """The CPC codes actually used to select the sector.

        Legacy codes are excluded: they belong to the pre-2019 scheme and are
        included only if the backfile turns out to be incompletely reclassified.
        See docs/methodology.md, section 7.
        """
        return self.cpc_core + self.cpc_hardware + self.cpc_communication

    @property
    def cpc_computing_only(self) -> tuple[str, ...]:
        """The sector without the quantum-communication classes.

        Used for the sensitivity analysis that settles the scope boundary
        (docs/methodology.md, section 6).
        """
        return self.cpc_core + self.cpc_hardware


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> SectorConfig:
    """Read sector.yaml and return it as a frozen SectorConfig."""
    path = Path(path)
    with path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    cpc = raw["cpc"]
    time = raw["time"]
    counting = raw["counting"]

    return SectorConfig(
        sector_name=raw["sector"]["name"],
        client=raw["sector"]["client"],
        team=int(raw["sector"]["team"]),
        cpc_core=tuple(cpc["core"]),
        cpc_hardware=tuple(cpc["hardware"]),
        cpc_communication=tuple(cpc["communication"]),
        cpc_legacy=tuple(cpc.get("legacy", ())),
        keywords=tuple(raw["keywords"]),
        year_min=int(time["year_min"]),
        year_max=int(time["year_max"]),
        last_complete_year=int(time["last_complete_year"]),
        family_time_column=time["family_time_column"],
        appln_time_column=time["appln_time_column"],
        ipr_type=counting["ipr_type"],
        ip5_offices=tuple(counting["ip5_offices"]),
        top_n=int(counting["top_n"]),
        env=raw["patstat"]["env"],
        raw=raw,
    )


if __name__ == "__main__":
    cfg = load_config()
    print(f"Sector   : {cfg.sector_name}  (client: {cfg.client}, team {cfg.team})")
    print(f"Window   : {cfg.year_min}-{cfg.year_max}, complete to {cfg.last_complete_year}")
    print(f"Family y : {cfg.family_time_column}")
    print(f"Appln y  : {cfg.appln_time_column}")
    print(f"Env      : {cfg.env}")
    print()
    print(f"CPC core         ({len(cfg.cpc_core)}): {', '.join(cfg.cpc_core)}")
    print(f"CPC hardware     ({len(cfg.cpc_hardware)}): {', '.join(cfg.cpc_hardware)}")
    print(f"CPC communication({len(cfg.cpc_communication)}): {', '.join(cfg.cpc_communication)}")
    print(f"CPC legacy       ({len(cfg.cpc_legacy)}, unused): {', '.join(cfg.cpc_legacy)}")
    print(f"Keywords         ({len(cfg.keywords)})")
