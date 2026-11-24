"""
PATH: data/founder_ceo_exits/analysis/figures.py
PURPOSE: The paper's figures from paper/figdata/figure_series.json, one function per figure named after its image
         file, written to outputs/figures and backend/static/reports/founder-ceo/figures.
WHY: MedTwin redraws these on the server (backend/services/finance_figures/packs.py, FOUNDER_CEO) and the figure
     editor shows each function, so a figure is built in the product from the same series the statistics use.
     Every figure states its horizon on the axis and its N on the plot: a reader never has to guess how long
     after the firing a number is measured, or on how many firms.
LOOK: the shared working-paper style (wp_figstyle.py, beside this file; ~/Desktop/ssrn-design/COLOUR_ROLES.md):
      drawn at print size (6.6 in across both columns), Source Sans 3, hairline grid, the unit above the plot.
      Colour belongs to data: firings red (the focal series), retirements grey (the comparison), founders amber,
      personal scandals violet, other reasons teal. Direct labels are ink beside a short colour key.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import wp_figstyle as S  # noqa: E402

SERIES = HERE.parent / "paper" / "figdata" / "figure_series.json"
OUT = Path(os.environ.get("FCE_OUTPUT_DIR") or HERE.parent / "outputs")
# The served figures folder: DRE_STATIC_REPORT_ROOT in the MedTwin image, backend/static/reports in a MedTwin checkout,
# and nothing in the standalone replication package (figures then go to outputs/figures only).
_STATIC_ROOT = os.environ.get("DRE_STATIC_REPORT_ROOT") or (
    HERE.parents[2] / "backend" / "static" / "reports" if (HERE.parents[2] / "backend").is_dir() else None
)
STATIC = Path(_STATIC_ROOT) / "founder-ceo/figures" if _STATIC_ROOT else None


def _font_dir() -> Path | None:
    candidates = [HERE.parents[2] / "backend" / "services" / "paper_export" / "fonts"]
    try:
        from backend.services.paper_export.engine import FONT_DIR

        candidates.append(Path(FONT_DIR))
    except Exception:  # nosec B110 - a checkout without the backend on the path falls back below
        pass
    candidates.append(Path("/app/backend/services/paper_export/fonts"))
    return next((c for c in candidates if any(c.glob("SourceSans3-*.otf"))), None)


FONTS = _font_dir()
S.use(FONTS)

FORCED, RETIRED, FOUNDER, CONDUCT, PERF = S.FOCAL, S.COMPARE, S.SERIES4, S.SERIES2, S.SERIES3
INK, MUTED, MINUS = S.INK, S.MUTED, S.MINUS
SZ = S.SIZES


def load() -> dict:
    """The aggregated series (figure_series.py)."""
    return json.loads(SERIES.read_text(encoding="utf-8"))


def save(fig, name: str) -> Path:
    """Write the PNG at its print size (no tight box) to outputs/figures and the served static folder. The server
    replaces this when it redraws."""
    paths = []
    for folder in (OUT / "figures", STATIC) if STATIC else (OUT / "figures",):
        folder.mkdir(parents=True, exist_ok=True)
        paths.append(folder / f"{name}.png")
        fig.savefig(paths[-1], dpi=S.DPI, facecolor="white")
    plt.close(fig)
    try:  # RGB: an alpha channel becomes a soft mask in the PDF
        from PIL import Image

        for path in paths:
            Image.open(path).convert("RGB").save(path, optimize=True)
    except ImportError:
        pass
    return paths[0]


def _spread(values: list[float], gap: float) -> list[float]:
    """Pure: label positions at least ``gap`` apart, each as close to its value as the order allows."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    pos = [0.0] * len(values)
    last = None
    for i in order:
        y = values[i] if last is None else max(values[i], last + gap)
        pos[i] = last = y
    shift = (sum(pos) - sum(values)) / len(values)
    return [p - shift for p in pos]


def _end_labels(ax, x, items, gap) -> None:
    """Direct labels at the line ends, spread so none overlaps: items are (y, text, colour). A short colour key,
    then the text in ink."""
    for (_y, text, color), yl in zip(items, _spread([it[0] for it in items], gap)):
        ax.annotate(
            "—",
            (x, yl),
            xytext=(3, 0),
            textcoords="offset points",
            color=color,
            fontsize=SZ["direct"],
            fontweight="bold",
            va="center",
            annotation_clip=False,
        )
        ax.annotate(
            text,
            (x, yl),
            xytext=(13, 0),
            textcoords="offset points",
            color=INK,
            fontsize=SZ["direct"],
            va="center",
            linespacing=1.15,
            annotation_clip=False,
        )


def _pct_axis(ax, digits: int = 0) -> None:
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: (MINUS if v < 0 else "") + f"{abs(v) * 100:.{digits}f}%")
    )


def fig1_event_time(data: dict):
    """Cumulative market-adjusted return, trading days -30 to +60: firings against retirements (a), and by who was
    fired and why (b). The announcement window [-1,+1] is the grey band."""
    et = data["event_time"]
    days = et["days"]
    fig, axes = plt.subplots(1, 2, figsize=(S.FULL_W, 2.9), sharey=True)
    fig.subplots_adjust(left=0.076, right=0.84, top=0.83, bottom=0.17, wspace=0.6)
    panels = [
        (
            axes[0],
            "(a) Firings and retirements, means",
            [("forced", "Firings", FORCED, "main"), ("retired", "Retirements", RETIRED, "comparison")],
            "mean",
        ),
        (
            axes[1],
            "(b) Founders, personal scandals and other firings, medians",
            [
                ("forced_founder", "Founder fired", FOUNDER, "main"),
                ("performance", "Other firings", FORCED, "comparison"),  # firings stay red (review r1, item 33)
                ("conduct", "Personal scandal", CONDUCT, "comparison"),
            ],
            "median",  # small groups: one firm can move a mean (a +210% day at one founder firm), so medians
        ),
    ]
    for ax, title, lines, stat in panels:
        S.window(ax, -1, 1)
        S.zero(ax)
        items = []
        for key, label, color, weight in lines:
            s = et[key]
            ax.plot(days, s[stat], color=color, linewidth=S.LINE[weight], zorder=3)
            if key == "forced":  # the subgroups are too small for a band to say much
                ax.fill_between(days, s["lo"], s["hi"], color=color, alpha=S.LINE["ci_alpha"], linewidth=0, zorder=2)
            items.append((s[stat][-1], f"{label}\n{S.pct(s[stat][-1])}, n = {s['n']:,}", color))
        _end_labels(ax, days[-1], items, 0.042)
        ax.set_xlim(-30, 60)
        ax.set_xticks([-30, -15, 0, 15, 30, 45, 60])
        ax.set_xlabel("Trading days from the announcement (day 0)")
        ax.set_title(title, pad=16)
        S.frame(ax, "Cumulative return minus the market, from day " + MINUS + "30")
    axes[0].set_ylim(-0.21, 0.03)
    axes[0].set_yticks([0, -0.05, -0.10, -0.15, -0.20])
    axes[1].tick_params(labelleft=True)
    return save(fig, "fig1_event_time")


def fig2_long_run(data: dict):
    """Median buy-and-hold return minus the market, month 1 to 60 after the announcement, with the median against a
    matched firm at 12, 36 and 60 months and the number of firings measured there."""
    lr = data["long_run"]
    months = lr["months"]
    fig, ax = plt.subplots(figsize=(S.FULL_W, 2.7))
    fig.subplots_adjust(left=0.075, right=0.80, top=0.86, bottom=0.17)
    S.zero(ax)
    items = []
    for key, label, color, weight in (
        ("forced", "Firings", FORCED, "main"),
        ("retired", "Retirements", RETIRED, "comparison"),
        ("forced_founder", "Founder fired", FOUNDER, "comparison"),
    ):
        s = lr[key]
        ax.plot(months, s["median"], color=color, linewidth=S.LINE[weight], zorder=3)
        items.append((s["median"][-1], f"{label} {S.pct(s['median'][-1])}", color))
        mt = data.get("matched", {}).get(key, {})
        off = {"forced": -1.1, "retired": 0.0, "forced_founder": 1.1}[key]
        for h in (1, 3, 5):
            v = (mt.get(str(h)) or {}).get("value")
            if v is not None:
                ax.scatter(
                    [12 * h + off], [v], color="white", edgecolor=color, linewidth=1.3, s=24, zorder=5, marker="D"
                )
    _end_labels(ax, months[-1] + 0.5, items, 0.075)
    fn = lr["forced"]["n"]
    for h in (1, 3, 5):
        ax.axvline(12 * h, color=S.HAIR, linewidth=0.6, zorder=0)
        ax.text(12 * h, -0.985, f"n = {fn[12 * h - 1]:,} firings", ha="center", color=MUTED, fontsize=SZ["small"])
    ax.scatter([1.4], [0.075], color="white", edgecolor=MUTED, linewidth=1.1, s=18, marker="D")
    ax.text(
        2.4,
        0.075,
        "median return against a matched firm at 12, 36 and 60 months",
        color=MUTED,
        fontsize=SZ["small"],
        va="center",
    )
    ax.set_ylim(-1.0, 0.12)
    ax.set_xlim(0, 62)  # room for the 60-month diamonds, offset either side of month 60
    ax.set_xticks([0, 12, 24, 36, 48, 60])
    ax.set_xlabel("Months after the announcement (21 trading days each, from day +2)")
    S.frame(ax, "Median buy-and-hold return minus the market")
    return save(fig, "fig2_long_run")


def fig3_exits(data: dict):
    """Cumulative share of firms delisted, by month after the announcement: for any reason (a) and in bankruptcy (b),
    firings against retirements on one axis. Firms with a complete five-year horizon, so the denominator does not
    change across months; takeovers are most of the gap between the panels (Table 4)."""
    ex = data["exits"]
    months = ex["months"]
    fig, axes = plt.subplots(1, 2, figsize=(S.FULL_W, 2.6), sharey=True)
    fig.subplots_adjust(left=0.076, right=0.84, top=0.82, bottom=0.17, wspace=0.62)
    for ax, title, part in (
        (axes[0], "(a) Delisted for any reason", ("acquired", "bankruptcy", "other")),
        (axes[1], "(b) Delisted in bankruptcy", ("bankruptcy",)),
    ):
        items = []
        for key, label, color, weight in (
            ("forced", "Firings", FORCED, "main"),
            ("retired", "Retirements", RETIRED, "comparison"),
        ):
            s = ex[key]
            y = [sum(s[p][i] for p in part) for i in range(len(months))]
            ax.plot(months, y, color=color, linewidth=S.LINE[weight], zorder=3)
            items.append((y[-1], f"{label}\n{S.pct(y[-1], sign=False)}, n = {s['n']:,}", color))
        _end_labels(ax, months[-1], items, 0.055)
        ax.set_xlim(0, 60)
        ax.set_xticks([0, 12, 24, 36, 48, 60])
        ax.set_xlabel("Months after the announcement")
        ax.set_title(title, pad=16)
        S.frame(ax, "Share of firms delisted")
    axes[0].set_ylim(0, 0.36)
    axes[0].set_yticks([0, 0.1, 0.2, 0.3])
    return save(fig, "fig3_exits")


NICE = {
    "financial_misconduct": "Financial misconduct",
    "legal_or_regulatory": "Legal or regulatory",
    "merger_or_restructuring": "Merger or restructuring",
    "retirement_or_health": "Pushed out, described as retirement or health",
    "relationship_with_employee": "Relationship with an employee",
    "activist_or_shareholder_pressure": "Activist or shareholder pressure",
    "strategy_or_power_dispute": "Strategy or power dispute",
    "other_personal_conduct": "Other personal conduct",
    "unclear": "Reason unclear",
    "performance": "Performance",
    "new_opportunity": "Left for a new job",
    "other_sexual_misconduct": "Sexual misconduct",
}


def fig4_reasons(data: dict):
    """Mean CAR[-1,+1] with its 95% interval for each coded reason a firing happened (at least 10 cases), sorted from
    the largest fall. Every row is a firing, so every row is the focal red."""
    rs = sorted(data["reasons"], key=lambda r: r["mean"], reverse=True)
    fig, ax = plt.subplots(figsize=(S.FULL_W, 2.9))
    fig.subplots_adjust(left=0.36, right=0.83, top=0.88, bottom=0.12)  # room for the longest reason label
    for i, r in enumerate(rs):
        ax.plot([r["lo"], r["hi"]], [i, i], color=FORCED, linewidth=1.4, alpha=0.45, solid_capstyle="butt")
        ax.scatter([r["mean"]], [i], color=FORCED, s=26, zorder=3)
        ax.annotate(
            f"{S.pct(r['mean'])}   n = {r['n']}",
            (1.0, i),
            xycoords=("axes fraction", "data"),
            xytext=(8, 0),
            textcoords="offset points",
            va="center",
            color=INK,
            fontsize=SZ["direct"],
            annotation_clip=False,
        )
    ax.set_yticks(range(len(rs)))
    ax.set_yticklabels([NICE.get(r["reason"], r["reason"]) for r in rs], color=INK, fontsize=SZ["label"])
    ax.axvline(0, color=S.ZERO, linewidth=0.5)
    ax.set_xlim(-0.18, 0.06)
    ax.set_ylim(-0.6, len(rs) - 0.4)
    ax.grid(axis="x", color=S.HAIR, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.spines["bottom"].set_visible(False)
    ax.xaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: (MINUS if v < 0 else "") + f"{abs(v) * 100:.0f}%")
    )
    ax.text(
        0,
        1.03,
        "Mean abnormal return, trading days " + MINUS + "1 to +1, with 95% interval",
        transform=ax.transAxes,
        color=MUTED,
        fontsize=SZ["unit"],
        va="bottom",
    )
    return save(fig, "fig4_reasons")


def fig5_per_year(data: dict):
    """Firings per year by the database's dismissal type, with the founders among them; 1998 to 2023."""
    py = data["per_year"]
    yrs = py["years"]
    fig, ax = plt.subplots(figsize=(S.FULL_W, 2.4))
    fig.subplots_adjust(left=0.06, right=0.99, top=0.88, bottom=0.12)
    ax.bar(yrs, py["performance"], color=PERF, width=0.72, label="Database: job performance")
    ax.bar(
        yrs,
        py["conduct"],
        bottom=py["performance"],
        color=CONDUCT,
        width=0.72,
        label="Database: legal or personal conduct",
    )
    tops = [a + b for a, b in zip(py["performance"], py["conduct"])]
    for y, t, fo in zip(yrs, tops, py["founder"]):
        if fo:
            ax.text(y, t + 1.5, str(fo), ha="center", color=INK, fontsize=SZ["small"])
    ax.grid(axis="y", color=S.HAIR, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.set_xlim(1997.3, 2023.7)
    ax.set_xticks(list(range(1998, 2024, 2)))
    ax.set_ylim(0, 128)
    ax.set_yticks(range(0, 101, 20))
    ax.text(
        0,
        1.03,
        "Firings per year; the number above a bar counts the founders",
        transform=ax.transAxes,
        color=MUTED,
        fontsize=SZ["unit"],
        va="bottom",
    )
    leg = ax.legend(
        frameon=False,
        fontsize=SZ["label"],
        loc="upper left",
        ncol=2,
        handlelength=1.0,
        handleheight=0.8,
        columnspacing=1.4,
        borderaxespad=0.1,
    )
    for t in leg.get_texts():
        t.set_color(INK)
    return save(fig, "fig5_per_year")


def fig6_roa_board(data: dict):
    """(a) Median change in return on assets against the matched firm, fiscal years 0 to 3 against year -1.
    (b) The board about two years later: directors gone, chair and CEO roles split, the former CEO still a director."""
    roa, board = data["roa"], data["board"]
    fig, axes = plt.subplots(1, 2, figsize=(S.FULL_W, 2.7), gridspec_kw={"width_ratios": [1, 1.15]})
    fig.subplots_adjust(left=0.07, right=0.985, top=0.80, bottom=0.17, wspace=0.62)
    ax = axes[0]
    S.zero(ax)
    items = []
    for key, label, color, weight in (
        ("forced", "Firings", FORCED, "main"),
        ("retired", "Retirements", RETIRED, "comparison"),
    ):
        s = roa[key]
        ax.plot(roa["years"], s["median"], color=color, linewidth=S.LINE[weight], marker="o", markersize=3)
        items.append((s["median"][-1], f"{label}\nn = {s['n'][-1]:,} in year 3", color))
    _end_labels(ax, 3.05, items, 0.0055)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(["Year 0", "Year 1", "Year 2", "Year 3"])
    ax.set_xlim(-0.2, 3.1)
    ax.set_title("(a) Profitability against a matched firm", pad=16)
    S.frame(ax, "Change in return on assets, pp", percent=False)
    ax.set_ylim(-0.022, 0.012)
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: (MINUS if v < 0 else "") + f"{abs(v) * 100:.1f}")
    )
    ax = axes[1]
    bars = [
        ("Directors\ngone", "board.forced.director_turnover.mean", "board.retired.director_turnover.mean"),
        ("Chair and CEO\nsplit", "board.forced.split_after.mean", "board.retired.split_after.mean"),
        (
            "Former CEO\nstill a director",
            "board.forced_nonfounder.ceo_stays_director.mean",
            "board.retired.ceo_stays_director.mean",
        ),
    ]
    for i, (_label, kf, kr) in enumerate(bars):
        for dx, key, color in ((-0.19, kf, FORCED), (0.19, kr, RETIRED)):
            v = board.get(key, {}).get("value")
            if v is not None:
                ax.bar(i + dx, v, width=0.36, color=color)
                if not (i == 2 and color == FORCED):  # the founders' diamond sits there; the text gives the share
                    ax.text(i + dx, v + 0.015, f"{v * 100:.0f}%", ha="center", color=INK, fontsize=SZ["small"])
    fs = board.get("board.forced_founder.founder_stays.mean", {})
    if fs.get("value") is not None:
        ax.scatter([2 - 0.19], [fs["value"]], color=FOUNDER, s=26, zorder=4, marker="D")
        ax.annotate(
            f"fired founders {fs['value'] * 100:.0f}%",
            (2 - 0.19, fs["value"]),
            xytext=(0, 54),
            textcoords="offset points",
            color=INK,
            fontsize=SZ["small"],
            ha="center",
            arrowprops={"arrowstyle": "-", "color": MUTED, "linewidth": 0.5, "shrinkA": 0, "shrinkB": 3},
        )
    ax.set_xticks(range(len(bars)))
    ax.set_xticklabels([b[0] for b in bars])
    ax.set_ylim(0, 0.8)
    ax.set_title("(b) The board about two years later", pad=16)
    S.frame(ax, "Share of firms; red: firings, grey: retirements")
    return save(fig, "fig6_roa_board")


def fig0_hero(data: dict):
    """The two-column working paper's cover chart ("at a glance"): mean cumulative return minus the market, trading
    days -30 to +60, firings against retirements, drawn by the shared style's hero() at its print size (2.45 x 1.8 in).
    The export settings name it (jf_export.hero_figure) and carry its title, unit and note."""
    et = data["event_time"]
    f, r = et["forced"], et["retired"]
    paths = []
    for folder in (OUT / "figures", STATIC) if STATIC else (OUT / "figures",):
        paths.append(
            S.hero(
                et["days"],
                {"Firings": (f["mean"], FORCED, f["lo"], f["hi"]), "Retirements": (r["mean"], RETIRED, None, None)},
                folder / "fig0_hero.png",
                xlabel="Trading days from the announcement",
                window_span=(-1, 1),
                ylim=(-0.135, 0.012),
                yticks=[0, -0.04, -0.08, -0.12],
            )
        )
    return paths[0]


FIGURES = (fig1_event_time, fig2_long_run, fig3_exits, fig4_reasons, fig5_per_year, fig6_roa_board, fig0_hero)


def main():
    data = load()
    for fn in FIGURES:
        print(fn(data))


if __name__ == "__main__":
    main()
