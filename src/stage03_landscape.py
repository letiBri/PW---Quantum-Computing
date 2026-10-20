"""Step 1 — general description of the sector

Conducts the analysis of the sector.
Provides helper functions for the data analysis and result storing (cached function)
Contains code from the sections 6-9 from the Step 1 notebook.

"""
from src.stage00_config import load_config
from src.stage02_clean import family_scope, application_scope, Scope
from src.stage01_extract import symbol_prefix_condition
from pathlib import Path
import pandas as pd
from epo.tipdata.patstat import PatstatClient
from sqlalchemy import and_, case, distinct, func, literal, or_
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from epo.tipdata.patstat.database.models import (
    TLS201_APPLN,               # import the needed tables for the extractions
    TLS202_APPLN_TITLE,
    TLS203_APPLN_ABSTR,
    TLS206_PERSON,
    TLS207_PERS_APPLN,
    TLS224_APPLN_CPC,
    TLS230_APPLN_TECHN_FIELD,
    TLS901_TECHN_FIELD_IPC,
)
from matplotlib.ticker import MaxNLocator
import numpy as np
import seaborn as sns

# --------------------------------------------------------------------------- #
# config and global variables
# --------------------------------------------------------------------------- #

cfg = load_config()
patstat = PatstatClient(env=cfg.env)
db = patstat.orm()

TOP_N = cfg.top_n
SECTOR_NAME = cfg.sector_name
LAST_COMPLETE_YEAR = cfg.last_complete_year
YEAR_MIN = cfg.year_min
YEAR_MAX = cfg.year_max
FAMILY_TIME_COLUMN = cfg.family_time_column
APPLN_TIME_COLUMN = cfg.appln_time_column
IPR_TYPE = cfg.ipr_type
IP5_OFFICES = cfg.ip5_offices

OUTPUT_DIR = Path(cfg.output)
LEVELS = ("family", "application")
UNIT_LABEL = {"family": "families", "application": "applications"}
ALT_BASE_YEAR = 2010        # later base, for a sector whose early counts are thin
BLOCKS = {
    "G06N10 (core)":        ("G06N10",),
    "B82Y10/00 (nanotech)": ("B82Y10/00",),
    "H10N60/12 (Josephson)":("H10N60/12",),
    "H04L9/0852 + H04B10/70 (comms)": ("H04L9/0852", "H04B10/70"),
}
CPC_DEFINITIONS = {
    "G06N": "COMPUTING ARRANGEMENTS BASED ON SPECIFIC COMPUTATIONAL MODELS",
    "H04L": "TRANSMISSION OF DIGITAL INFORMATION, e.g. TELEGRAPHIC COMMUNICATION",
    "H04B": "TRANSMISSION",
    "G06F": "ELECTRIC DIGITAL DATA PROCESSING",
    "H10N": "ELECTRIC SOLID-STATE DEVICES NOT OTHERWISE PROVIDED FOR",
    "B82Y": "SPECIFIC USES OR APPLICATIONS OF NANOSTRUCTURES; MEASUREMENT OR ANALYSIS OF NANOSTRUCTURES; MANUFACTURE OR TREATMENT OF NANOSTRUCTURES",
    "Y02D": "CLIMATE CHANGE MITIGATION TECHNOLOGIES IN INFORMATION AND COMMUNICATION TECHNOLOGIES [ICT]",
    "G06Q": "INFORMATION AND COMMUNICATION TECHNOLOGY [ICT] SPECIALLY ADAPTED FOR ADMINISTRATIVE, COMMERCIAL, FINANCIAL, MANAGERIAL OR SUPERVISORY PURPOSES",
    "H03K": "PULSE TECHNIQUE",
    "H10D": "INORGANIC ELECTRIC SEMICONDUCTOR DEVICES",
    "Other": "other fields",
    "Total": ""
}


# --------------------------------------------------------------------------- #
# data counting functions
# --------------------------------------------------------------------------- #


def _join_applications(q, scope):
    """Join each unit to its applications: all members of a family, or the application itself."""
    key = TLS201_APPLN.docdb_family_id if scope.level == "family" else TLS201_APPLN.appln_id
    return q.join(TLS201_APPLN, key == scope.sq.c.unit_id).filter(TLS201_APPLN.ipr_type == IPR_TYPE)


def _tag(df, scope):
    return df.assign(scope=scope.name, level=scope.level)


def count_per_year(scope, only_pct=False):
    """Units per year; only_pct keeps those filed through the PCT."""
    sq = scope.sq
    q = db.query(sq.c.year, func.count().label("n")).group_by(sq.c.year).order_by(sq.c.year)
    if only_pct:
        q = q.filter(sq.c.is_pct == 1)
    return _tag(patstat.df(q), scope)


def _split_equally(scope, unit_category, category):
    """Fractional counting: each unit is split equally across its distinct categories."""
    pairs = unit_category.distinct().subquery()
    k = db.query(pairs.c.unit_id, func.count().label("k")).group_by(pairs.c.unit_id).subquery()
    q = (
        db.query(getattr(pairs.c, category), pairs.c.year, func.sum(1.0 / k.c.k).label("n_frac"))
        .join(k, k.c.unit_id == pairs.c.unit_id)
        .group_by(getattr(pairs.c, category), pairs.c.year)
    )
    return _tag(patstat.df(q), scope)


def fractional_by_country(scope, role="applicant", count_unknown=False):
    """Fractional counts by person country and year (role: 'applicant' or 'inventor')."""
    sq = scope.sq
    seq_nr = TLS207_PERS_APPLN.applt_seq_nr if role == "applicant" else TLS207_PERS_APPLN.invt_seq_nr
    raw_ctry = func.trim(TLS206_PERSON.person_ctry_code)   # unknown countries are NULL, '' or blanks

    if count_unknown:
        ctry = func.coalesce(
            func.nullif(raw_ctry, ""),
            "Unknown" # counting unknown countries 
        )
        country_filter = seq_nr > 0
    else:
        ctry = raw_ctry
        country_filter = (
            (seq_nr > 0)
            & raw_ctry.isnot(None)
            & (raw_ctry != "") # deleting unkonown countries
        )
        
    persons = (
        _join_applications(
            db.query(sq.c.unit_id, sq.c.year, TLS207_PERS_APPLN.person_id, ctry.label("ctry")).distinct(), scope
        )
        .join(TLS207_PERS_APPLN, TLS207_PERS_APPLN.appln_id == TLS201_APPLN.appln_id)
        .join(TLS206_PERSON, TLS206_PERSON.person_id == TLS207_PERS_APPLN.person_id)
        .filter(country_filter)
        .subquery()
    )
    k = db.query(persons.c.unit_id, func.count().label("k")).group_by(persons.c.unit_id).subquery()
    q = (
        db.query(persons.c.ctry, persons.c.year, func.sum(1.0 / k.c.k).label("n_frac"))
        .join(k, k.c.unit_id == persons.c.unit_id)
        .group_by(persons.c.ctry, persons.c.year)
    )
    
    return _tag(patstat.df(q), scope).assign(role=role)


def fractional_by_cpc_subclass(scope):
    """Fractional counts by CPC subclass (the first 4 characters) and year."""
    sq = scope.sq
    subclass = func.substr(func.replace(TLS224_APPLN_CPC.cpc_class_symbol, " ", ""), 1, 4)
    q = (
        _join_applications(db.query(sq.c.unit_id, sq.c.year, subclass.label("subclass")), scope)
        .join(TLS224_APPLN_CPC, TLS224_APPLN_CPC.appln_id == TLS201_APPLN.appln_id)
    )
    return _split_equally(scope, q, "subclass")


def fractional_by_techn_field(scope):
    """Fractional counts by WIPO technology field (1-35) and year.

    tls230 weights sum to 1 per application; at family level they are rescaled
    so that every family also sums to 1.
    """
    sq = scope.sq
    unit_field = (
        _join_applications(
            db.query(sq.c.unit_id, sq.c.year, TLS230_APPLN_TECHN_FIELD.techn_field_nr,
                     func.sum(TLS230_APPLN_TECHN_FIELD.weight).label("w")),
            scope,
        )
        .join(TLS230_APPLN_TECHN_FIELD, TLS230_APPLN_TECHN_FIELD.appln_id == TLS201_APPLN.appln_id)
        .group_by(sq.c.unit_id, sq.c.year, TLS230_APPLN_TECHN_FIELD.techn_field_nr)
        .subquery()
    )
    unit_total = (
        db.query(unit_field.c.unit_id, func.sum(unit_field.c.w).label("w_total"))
        .group_by(unit_field.c.unit_id)
        .subquery()
    )
    q = (
        db.query(unit_field.c.techn_field_nr, unit_field.c.year,
                 func.sum(unit_field.c.w / unit_total.c.w_total).label("n_frac"))
        .join(unit_total, unit_total.c.unit_id == unit_field.c.unit_id)
        .group_by(unit_field.c.techn_field_nr, unit_field.c.year)
    )
    return _tag(patstat.df(q), scope)


def count_by_office(scope):
    """Units per office and year.

    Family level: families with at least one application at the office.
    Application level: applications filed at the office.
    """
    sq = scope.sq
    q = (
        _join_applications(
            db.query(TLS201_APPLN.appln_auth.label("office"), sq.c.year,
                     func.count(distinct(sq.c.unit_id)).label("n")),
            scope,
        )
        .group_by(TLS201_APPLN.appln_auth, sq.c.year)
    )
    return _tag(patstat.df(q), scope)


def scope_profile(scope):
    """Units, units via PCT, granted units and mean family size."""
    sq = scope.sq
    q = db.query(
        func.count().label("n"),
        func.sum(sq.c.is_pct).label("n_pct"),
        func.sum(sq.c.is_granted).label("n_granted"),
        func.avg(sq.c.family_size * 1.0).label("mean_family_size"),
    ).filter(sq.c.year <= LAST_COMPLETE_YEAR)
    return _tag(patstat.df(q), scope)


# --------------------------------------------------------------------------- #
# helper functions
# --------------------------------------------------------------------------- #


def cached(name, build, force=False):
    """Compute build() once, then serve it from disk. Pass force=True to recompute."""
    path = OUTPUT_DIR / "cache" / f"{name}.pkl"
    if path.exists() and not force:
        df = pd.read_pickle(path)
        print(f"[cache] {name:<22} {len(df):>8,} rows")
        return df
    df = build()
    df.to_pickle(path)
    print(f"[query] {name:<22} {len(df):>8,} rows")
    return df


def shade_truncated(ax):
    """Shade incomplete years; a no-op while the window ends at the last complete year."""
    if LAST_COMPLETE_YEAR >= YEAR_MAX:
        return
    ax.axvspan(LAST_COMPLETE_YEAR + 0.5, YEAR_MAX + 0.5, color="grey", alpha=0.15, lw=0,
               label="incomplete years")


def complete_years(df):
    return df[df["year"] <= LAST_COMPLETE_YEAR]


def pool_other(df, category, n=TOP_N, value="n_frac", other_label="Other"):
    """Keep the n largest categories and pool the rest into 'Other'."""
    top = complete_years(df).groupby(category)[value].sum().nlargest(n).index
    out = df.copy()
    out[category] = out[category].where(out[category].isin(top), other_label)
    return out.groupby([category, "year"], as_index=False)[value].sum()


def share_table(counts):
    """Counts -> percentages summing to 100 per column, 'Other' last, with a Total row."""
    shares = counts / counts.sum() * 100
    order = [c for c in shares.sort_values(shares.columns[0], ascending=False).index if c != "Other"]
    order += ["Other"] if "Other" in shares.index else []
    shares = shares.loc[order]
    shares.loc["Total"] = shares.sum()
    return shares


def share_over_time(df, category, value="n_frac"):
    """Year x category table of percentages (each year sums to 100)."""
    wide = df.pivot_table(index="year", columns=category, values=value, aggfunc="sum", fill_value=0)
    wide = wide.div(wide.sum(axis=1), axis=0) * 100
    order = [c for c in complete_years(wide.reset_index()).set_index("year").sum().sort_values(ascending=False).index
             if c != "Other"]
    return wide[order + (["Other"] if "Other" in wide.columns else [])]


def stack_100(ax, shares, title):
    """Stacked area of percentages, y axis from 0% to 100%."""
    palette = [c for i, c in enumerate(plt.get_cmap("tab10").colors) if i != 7]   # grey reserved for "Other"
    colors = ["lightgrey" if c == "Other" else palette[i % len(palette)] for i, c in enumerate(shares.columns)]
    ax.stackplot(shares.index, shares.T.values, labels=shares.columns, colors=colors, alpha=0.85)
    shade_truncated(ax)
    ax.set(title=title, xlabel="year", xlim=(YEAR_MIN, YEAR_MAX), ylim=(0, 100))
    ax.yaxis.set_major_formatter(PercentFormatter(100))


def pct_format(df):
    return df.style.format("{:.1f}%")


def side_by_side(title, **kw):
    """Two axes: families (left) and applications (right)."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.5), **kw)
    fig.suptitle(title)
    return fig, axes


def _dating_series(sector_ids, volume):
    by_col = [
        count_per_year(Scope(SECTOR_NAME, "application", application_scope(sector_ids, col)))
        .assign(series=f"applications by {col}")
        for col in ("appln_filing_year", "earliest_publn_year", "earliest_filing_year")
    ]
    fam = volume[(volume["scope"] == SECTOR_NAME)
                 & (volume["level"] == "family")
                 & (volume["series"] == "all")].assign(series=f"families by {FAMILY_TIME_COLUMN}")
    return pd.concat(by_col + [fam], ignore_index=True)


def growth_block(start, end, volume, totals):
    rows = [(lvl, s) for lvl in LEVELS for s in ("all patents", SECTOR_NAME)]
    return pd.DataFrame({
        f"count {start}": totals.loc[start],
        f"count {end}": totals.loc[end],
        f"growth {start}-{end} (%)": (totals.loc[end] / totals.loc[start] - 1) * 100,
        f"CAGR {start}-{end} (%)": ((totals.loc[end] / totals.loc[start]) ** (1 / (end - start)) - 1) * 100,
    }).loc[rows]


def block_series(prefixes):
    ids = (db.query(TLS201_APPLN.docdb_family_id.label("docdb_family_id"))
           .join(TLS224_APPLN_CPC, TLS201_APPLN.appln_id == TLS224_APPLN_CPC.appln_id)
           .filter(symbol_prefix_condition(TLS224_APPLN_CPC.cpc_class_symbol, prefixes))
           .distinct())
    return count_per_year(Scope(SECTOR_NAME, "family", family_scope(ids)))


# --------------------------------------------------------------------------- #
# plotting and calculating functions
# --------------------------------------------------------------------------- #


def plot_volume_per_year(volume, sector_scopes):
    fig, axes = side_by_side(f"{SECTOR_NAME}: volume per year", sharex=True)
    for ax, scope in zip(axes, sector_scopes):
        data = volume.query("scope == @scope.name and level == @scope.level")
        for series, grp in data.groupby("series"):
            ax.plot(grp["year"], grp["n"], marker="o", ms=3, label=f"{UNIT_LABEL[scope.level]}, {series}")
        shade_truncated(ax)
        year_col = FAMILY_TIME_COLUMN if scope.level == "family" else APPLN_TIME_COLUMN
        ax.set(title=f"{UNIT_LABEL[scope.level]} per {year_col}", xlabel="year", ylabel=UNIT_LABEL[scope.level])
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "figures" / "fig_volume.png", dpi=200, bbox_inches="tight")
    # plt.show()

def plot_patents_dated_in_different_ways(dating):
    fig, ax = plt.subplots(figsize=(10, 5))
    for series, grp in dating.groupby("series"):
        ax.plot(grp["year"], grp["n"], marker="o", ms=3, label=series)
    shade_truncated(ax)
    ax.set(title=f"{SECTOR_NAME}: the same patents dated in different ways", xlabel="year", ylabel="count")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend()
    plt.savefig(OUTPUT_DIR / "figures" / "fig_dating.png", dpi=200, bbox_inches="tight")
    # plt.show()


def calculate_growth(volume, totals):
    growth = growth_block(YEAR_MIN, LAST_COMPLETE_YEAR, volume, totals).join(
        growth_block(ALT_BASE_YEAR, LAST_COMPLETE_YEAR, volume, totals)[
            [f"growth {ALT_BASE_YEAR}-{LAST_COMPLETE_YEAR} (%)",
             f"CAGR {ALT_BASE_YEAR}-{LAST_COMPLETE_YEAR} (%)"]
        ]
    )
    growth.to_csv(OUTPUT_DIR / "tables" / "tab_growth.csv")
    # display(growth.style.format({c: ("{:,.0f}" if c.startswith("count") else "{:+.1f}%") for c in growth.columns}))
                  

def plot_sector_growth_percentage(growth_path):
    fig, axes = side_by_side(f"{SECTOR_NAME} vs all patents: growth (%) since {YEAR_MIN}", sharey=True)
    for ax, level in zip(axes, LEVELS):
        for scope_name in ("all patents", SECTOR_NAME):
            ax.plot(growth_path.index, growth_path[(level, scope_name)], marker="o", ms=3, label=scope_name)
        ax.axhline(0, color="grey", lw=0.8)
        ax.set(title=UNIT_LABEL[level], xlabel="year", ylabel=f"growth since {YEAR_MIN}")
        ax.yaxis.set_major_formatter(PercentFormatter(100))
        ax.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "figures" / "fig_growth.png", dpi=200, bbox_inches="tight")
    # plt.show()


def plot_volume_by_code_block(blocks):
    fig, ax = plt.subplots(figsize=(11, 5))
    for name, g in blocks.groupby("block"):
        ax.plot(g["year"], g["n"], marker="o", ms=3, label=name)
    ax.set(title=f"{SECTOR_NAME}: volume by code block", xlabel="year", ylabel="families")
    ax.legend()
    plt.savefig(OUTPUT_DIR / "figures" / "fig_blocks.png", dpi=200, bbox_inches="tight")
    # plt.show()


def plot_and_calculate_cpc_subclasses(sector_scopes):
    cpc_mix = pd.concat([fractional_by_cpc_subclass(s) for s in sector_scopes], ignore_index=True)
    cpc_pooled = pd.concat([pool_other(cpc_mix[cpc_mix["level"] == lvl], "subclass").assign(level=lvl)
                            for lvl in LEVELS], ignore_index=True)

    # table
    cpc_counts = complete_years(cpc_pooled).pivot_table(index="subclass", columns="level", values="n_frac",
                                                        aggfunc="sum", fill_value=0)[list(LEVELS)]
    cpc_shares = share_table(cpc_counts)
    cpc_shares["definition (fill in from the CPC scheme)"] = (cpc_shares.index.map(CPC_DEFINITIONS))
    cpc_shares.to_csv(OUTPUT_DIR / "tables" / "tab_cpc_subclasses.csv")
    # display(cpc_shares.style.format("{:.1f}%", subset=list(LEVELS)))

    # plot
    fig, axes = side_by_side(f"{SECTOR_NAME}: CPC subclass mix over time", sharey=True)
    for ax, level in zip(axes, LEVELS):
        stack_100(ax, share_over_time(cpc_pooled[cpc_pooled["level"] == level], "subclass"),
                  f"share of {UNIT_LABEL[level]}")
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    axes[-1].legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "figures" / "fig_cpc_subclasses.png", dpi=200, bbox_inches="tight")
    # plt.show()


def plot_and_calculate_wipo_technology_mix(sector_scopes):

    # table wipo sector
    field_names = patstat.df(
        db.query(TLS901_TECHN_FIELD_IPC.techn_field_nr, TLS901_TECHN_FIELD_IPC.techn_field,
                 TLS901_TECHN_FIELD_IPC.techn_sector).distinct()
    ).drop_duplicates("techn_field_nr")
    
    fields = (
        pd.concat([fractional_by_techn_field(s) for s in sector_scopes], ignore_index=True)
        .merge(field_names, on="techn_field_nr", how="left")
    )
    
    techn_sector_counts = complete_years(fields).pivot_table(index="techn_sector", columns="level", values="n_frac",
                                                             aggfunc="sum", fill_value=0)[list(LEVELS)]
    techn_sector_shares = share_table(techn_sector_counts)
    techn_sector_shares.to_csv(OUTPUT_DIR / "tables" / "tab_wipo_sectors.csv")
    # display(pct_format(techn_sector_shares))

    # plot wipo sectors
    bars = techn_sector_shares.drop("Total").T
    fig, ax = plt.subplots(figsize=(11, 3))
    left = np.zeros(len(bars))
    for techn_sector in bars.columns:
        values = bars[techn_sector].values
        ax.barh([UNIT_LABEL[l] for l in bars.index], values, left=left, label=techn_sector)
        for y, (x0, v) in enumerate(zip(left, values)):
            if v >= 5:
                ax.text(x0 + v / 2, y, f"{v:.0f}%", ha="center", va="center", color="white", fontsize=9)
        left += values
    ax.set(title=f"{SECTOR_NAME}: split across the 5 WIPO technology sectors", xlim=(0, 100))
    ax.xaxis.set_major_formatter(PercentFormatter(100))
    ax.invert_yaxis()
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    plt.savefig(OUTPUT_DIR / "figures" / "fig_wipo_sectors.png", dpi=200, bbox_inches="tight")
    # plt.show()

    # table wipo fields
    field_counts = complete_years(fields).pivot_table(index="techn_field", columns="level", values="n_frac",aggfunc="sum", fill_value=0)[list(LEVELS)]
    top_fields = field_counts["family"].nlargest(TOP_N).index
    field_counts = field_counts.groupby(field_counts.index.where(field_counts.index.isin(top_fields), "Other")).sum()
    pct_format(share_table(field_counts))
    share_table(field_counts).to_csv(OUTPUT_DIR / "tables" / "tab_wipo_fields.csv")
    # display(pct_format(share_table(field_counts)))


def calculate_shares_of_sector_applications(offices):
    office_counts = complete_years(offices.query("level == 'application'")).groupby("office")["n"].sum().to_frame("applications")
    office_shares = share_table(office_counts)
    pct_format(office_shares)
    office_shares.to_csv(OUTPUT_DIR / "tables" / "tab_sector_geo_shares.csv")
    # display(pct_format(office_shares))


def plot_fillings_at_the_ip5_offices(offices):
    fig, axes = side_by_side(f"{SECTOR_NAME}: filings at the IP5 offices", sharex=True)
    for ax, level in zip(axes, LEVELS):
        data = offices.query("level == @level and office in @IP5_OFFICES")
        for office, g in data.groupby("office"):
            ax.plot(g["year"], g["n"], marker="o", ms=3, label=office)
        shade_truncated(ax)
        title = ("families with an application at the office" if level == "family"
                 else "applications filed at the office")
        ax.set(title=title, xlabel="year", ylabel=UNIT_LABEL[level])
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    axes[-1].legend(loc="center left", bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "figures" / "fig_fillings_at_the_ip5_offices.png", dpi=200, bbox_inches="tight")
    # plt.show()


def heatmap_fillings_at_the_ip5_offices(offices):
    fig, axes = side_by_side(
        f"{SECTOR_NAME}: filings at the IP5 offices",
        sharex=True
    )
    
    for ax, level in zip(axes, LEVELS):
        data = offices.query("level == @level and office in @IP5_OFFICES")
        heatmap_data = data.pivot_table(
            index="office",
            columns="year",
            values="n",
            aggfunc="sum",
            fill_value=0
        )
        sns.heatmap(
            heatmap_data,
            ax=ax,
            cmap="YlOrRd",
            cbar=True,
            linewidths=0.2,
            linecolor="white"
        )
        title = (
            "Families with an application at the office"
            if level == "family"
            else "Applications filed at the office"
        )
        ax.set(
            title=title,
            xlabel="Year",
            ylabel="Patent office"
        )
        plt.setp(ax.get_xticklabels(), rotation=60, ha="right")
        plt.setp(ax.get_yticklabels(), rotation=0, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "figures" / "heatmap_fillings_at_the_ip5_offices.png", dpi=200, bbox_inches="tight")
    # plt.show()


def calculate_investor_and_applicants_countries(sector_scopes, countries, count_unknown):
    if count_unknown:
        name = "_with_unknown"
    else:
        name = "_without_unknown"
    country_counts = complete_years(countries).pivot_table(index="ctry", columns=["level", "role"], values="n_frac",
                                                           aggfunc="sum", fill_value=0)
    country_counts = country_counts[[(lvl, role) for lvl in LEVELS for role in ("applicant", "inventor")]]
    top_countries = country_counts[("family", "applicant")].nlargest(TOP_N).index
    country_counts = country_counts.groupby(country_counts.index.where(country_counts.index.isin(top_countries), "Other")).sum()
    share_table(country_counts).to_csv(OUTPUT_DIR / "tables" / f"tab_sector_geo_shares{name}.csv")
    # display(pct_format(share_table(country_counts)))


def plot_applicant_countries_over_time(countries):
    fig, axes = side_by_side(f"{SECTOR_NAME}: applicant countries over time", sharey=True)
    for ax, level in zip(axes, LEVELS):
        data = countries.query("role == 'applicant' and level == @level")
        stack_100(ax, share_over_time(pool_other(data, "ctry"), "ctry"), f"share of {UNIT_LABEL[level]}")
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    axes[-1].legend(loc="center left", bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "figures" / "fig_applicants_countries_over_time.png", dpi=200, bbox_inches="tight")
    # plt.show()


# --------------------------------------------------------------------------- #
# analysis functions
# --------------------------------------------------------------------------- #


def analyse_volume(scopes, sector_ids):
    """Conducts an analysis of the volume. 
    1. volume per year
    2. same patents dated in different ways
    3. growth table
    4. sector growth percentage in comparison to all patents
    5. volume by code block"""
    sector_scopes = [s for s in scopes if s.name == SECTOR_NAME]  # family first, then application
    start, end = YEAR_MIN, LAST_COMPLETE_YEAR

    # 1
    volume = cached(
        "volume",
        lambda: pd.concat(
            [count_per_year(s).assign(series="all") for s in scopes]
            + [count_per_year(s, only_pct=True).assign(series="via PCT") for s in scopes],
            ignore_index=True,
        ),
    )
    plot_volume_per_year(volume, sector_scopes)

    # 2
    dating = cached("dating", lambda: _dating_series(sector_ids, volume))
    plot_patents_dated_in_different_ways(dating)

    # 3
    totals = volume.query("series == 'all'").pivot_table(index="year", columns=["level", "scope"], values="n")
    calculate_growth(volume, totals)

    # 4
    growth_path = (totals.loc[start:end] / totals.loc[start] - 1) * 100
    plot_sector_growth_percentage(growth_path)

    # 5
    blocks = cached("blocks", lambda: pd.concat([block_series(p).assign(block=name) for name, p in BLOCKS.items()], ignore_index=True))
    plot_volume_by_code_block(blocks)


def analyse_technology_mix(scopes):
    """Conducts the analysis of  technology mix. 
    1. CPC subclasses
    2. WIPO technology fields and split across sectors"""
    sector_scopes = [s for s in scopes if s.name == SECTOR_NAME]

    # 1
    plot_and_calculate_cpc_subclasses(sector_scopes)

    # 2
    plot_and_calculate_wipo_technology_mix(sector_scopes)


def analyse_geography(scopes):
    """Conducts the analysis of geography.
    1. shares of the sector's applications
    2. fillings at the IP5 offices per year
    3. fillings at the IP5 offices per year heatmap
    4. applicant and inventor countries without unknown
    5. applicant and inventor countries with unknown
    6. applicant countries over time
    """
    sector_scopes = [s for s in scopes if s.name == SECTOR_NAME]
    
    offices = pd.concat([count_by_office(s) for s in sector_scopes], ignore_index=True)
    offices["office"] = offices["office"].where(offices["office"].isin(IP5_OFFICES + ("WO",)), "Other")
    offices = offices.groupby(["level", "office", "year"], as_index=False)["n"].sum()

    countries_without_unknown = pd.concat(
        [fractional_by_country(s, role, count_unknown=False) for s in sector_scopes for role in ("applicant", "inventor")],
        ignore_index=True,
    )
    countries_with_unknown = pd.concat(
        [fractional_by_country(s, role, count_unknown=True) for s in sector_scopes for role in ("applicant", "inventor")],
        ignore_index=True,
    )

    # 1
    calculate_shares_of_sector_applications(offices)

    # 2
    plot_fillings_at_the_ip5_offices(offices)

    # 3
    heatmap_fillings_at_the_ip5_offices(offices)

    # 4
    calculate_investor_and_applicants_countries(sector_scopes, countries_without_unknown, count_unknown=False)

    # 5
    calculate_investor_and_applicants_countries(sector_scopes, countries_with_unknown, count_unknown=True)

    # 6
    plot_applicant_countries_over_time(countries_without_unknown)
    



    