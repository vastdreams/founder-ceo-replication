"""
PATH: data/founder_ceo_exits/analysis/figures.py
PURPOSE: The paper's six figures from paper/figdata/figure_series.json, one function per figure named after its
         image file, written to outputs/figures and backend/static/reports/founder-ceo/figures.
WHY: MedTwin redraws these on the server (backend/services/finance_figures/packs.py, FOUNDER_CEO) and the figure
     editor shows each function, so a figure is built in the product from the same series the statistics use.
     Every figure states its horizon on the axis and its N on the plot: a reader never has to guess how long
     after the firing a number is measured, or on how many firms.
LOOK: one colour per group (crimson forced exits, slate retirements, amber founders, violet conduct, teal
      performance), the result line heaviest, values labelled at line ends, hairline grids, the unit as a small
      label above the plot, Source Sans 3, drawn at 600 dpi.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

HERE = Path(__file__).resolve().parent
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
for _face in sorted(FONTS.glob("SourceSans3-*.otf")) if FONTS else ():
    font_manager.fontManager.addfont(str(_face))

FORCED = "#c62f45"
RETIRED = "#5b6b7f"
FOUNDER = "#e08a1e"
CONDUCT = "#7b4fb3"
PERF = "#1f8f86"
INK = "#1a1a19"
MUTED = "#6b6a65"
HAIR = "#ecebe7"
BASE = "#bdbcb6"
SHADE = "#f6f5f2"
MINUS = "−"
CM = 1 / 2.54
WIDE = 17.0 * CM
DPI = 600

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Source Sans 3", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 9.5,
        "axes.edgecolor": BASE,
        "axes.linewidth": 0.7,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "xtick.major.pad": 5,
        "ytick.major.pad": 4,
        "lines.solid_capstyle": "round",
        "axes.unicode_minus": True,
        "axes.titlesize": 10,
        "axes.titleweight": "semibold",
        "axes.titlecolor": INK,
        "axes.titlelocation": "left",
        "axes.titlepad": 14,
    }
)


def load() -> dict:
    """The aggregated series (figure_series.py)."""
    return json.loads(SERIES.read_text(encoding="utf-8"))


def save(fig, name: str) -> Path:
    """Write the PNG to outputs/figures and the served static folder. The server replaces this when it redraws."""
    paths = []
    for folder in (OUT / "figures", STATIC) if STATIC else (OUT / "figures",):
        folder.mkdir(parents=True, exist_ok=True)
        paths.append(folder / f"{name}.png")
        fig.savefig(paths[-1], dpi=DPI, bbox_inches="tight", pad_inches=0.06, facecolor="white")
    plt.close(fig)
    return paths[0]


def _pct(v: float, digits: int = 1, sign: bool = True) -> str:
    text = f"{abs(v) * 100:.{digits}f}%"
    if v < 0:
        return MINUS + text
    return ("+" if sign else "") + text


def _frame(ax, unit: str) -> None:
    """Hairline grid behind the data, no y-axis line, the unit as a small label above the plot."""
    ax.grid(axis="y", color=HAIR, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.text(0, 1.02, unit, transform=ax.transAxes, color=MUTED, fontsize=8, va="bottom")
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: (MINUS if v < 0 else "") + f"{abs(v) * 100:.0f}%")
    )


def _zero(ax) -> None:
    ax.axhline(0, color=BASE, linewidth=0.8, zorder=1)


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
    """Labels at the line ends, spread so none overlaps: items are (y, text, color)."""
    ys = _spread([it[0] for it in items], gap)
    for (y, text, color), yl in zip(items, ys):
        ax.annotate(
            text,
            (x, y),
            xytext=(x, yl),
            textcoords="data",
            color=color,
            fontsize=8.5,
            fontweight="semibold",
            va="center",
            ha="left",
            annotation_clip=False,
        )


def _end_label(ax, x, y, text, color, dy=0.0, bold=True) -> None:
    ax.annotate(
        text,
        (x, y),
        xytext=(5, dy),
        textcoords="offset points",
        color=color,
        fontsize=8.5,
        fontweight="semibold" if bold else "normal",
        va="center",
    )


def fig1_event_time(data: dict):
    """Cumulative market-adjusted return, trading days -30 to +60: forced exits against retirements (a), and by
    who was fired and why (b). The announcement window [-1,+1] is shaded."""
    et = data["event_time"]
    days = et["days"]
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, 7.4 * CM), sharey=True)
    panels = [
        (
            axes[0],
            "(a) Forced exits and retirements",
            [("forced", "Forced exits", FORCED, 2.2), ("retired", "Retirements", RETIRED, 1.4)],
        ),
        (
            axes[1],
            "(b) Founders, conduct and performance",
            [
                ("forced_founder", "Founder fired", FOUNDER, 1.8),
                ("performance", "Performance", PERF, 1.4),
                ("conduct", "Conduct", CONDUCT, 1.4),
            ],
        ),
    ]
    for ax, title, lines in panels:
        ax.axvspan(-1, 1, color=SHADE, zorder=0)
        _zero(ax)
        items = []
        for key, label, color, lw in lines:
            s = et[key]
            ax.plot(days, s["mean"], color=color, linewidth=lw, zorder=3)
            if key in ("forced", "retired"):
                ax.fill_between(days, s["lo"], s["hi"], color=color, alpha=0.12, linewidth=0, zorder=2)
            items.append((s["mean"][-1], f"{label}  {_pct(s['mean'][-1])}\nn = {s['n']:,}", color))
        _end_labels(ax, 62, items, 0.03)
        ax.set_xlim(-30, 60)
        ax.set_xticks([-30, -20, -10, 0, 10, 20, 30, 40, 50, 60])
        ax.set_xlabel("Trading days from the announcement (day 0)", color=MUTED, fontsize=8.5)
        ax.set_title(title)
        _frame(ax, "Cumulative return minus the market, from day " + MINUS + "30")
    for ax in axes:
        ax.set_ylim(-0.21, 0.025)
        ax.text(0, -0.205, "days " + MINUS + "1 to +1", ha="center", color=MUTED, fontsize=7)
    axes[0].text(-29, -0.19, "shaded bands: 95% confidence interval", color=MUTED, fontsize=7)
    fig.subplots_adjust(wspace=0.55)
    return save(fig, "fig1_event_time")


def fig2_long_run(data: dict):
    """Median buy-and-hold return minus the market, month 1 to 60 after the announcement, with the number of firms
    measured at 12, 36 and 60 months."""
    lr = data["long_run"]
    months = lr["months"]
    fig, ax = plt.subplots(figsize=(WIDE, 7.0 * CM))
    _zero(ax)
    for key, label, color, lw in (
        ("forced", "Forced exits", FORCED, 2.2),
        ("retired", "Retirements", RETIRED, 1.4),
        ("forced_founder", "Founder fired", FOUNDER, 1.4),
    ):
        s = lr[key]
        ax.plot(months, s["median"], color=color, linewidth=lw, zorder=3)
        _end_label(ax, months[-1], s["median"][-1], f"{label}  {_pct(s['median'][-1])}", color)
        mt = data.get("matched", {}).get(key, {})
        off = {"forced": -1.1, "retired": 0.0, "forced_founder": 1.1}[key]
        for h in (1, 3, 5):
            v = (mt.get(str(h)) or {}).get("value")
            if v is not None:
                ax.scatter(
                    [12 * h + off], [v], color="white", edgecolor=color, linewidth=1.4, s=30, zorder=5, marker="D"
                )
    fn = data["long_run"]["forced"]["n"]
    for h in (1, 3, 5):
        ax.axvline(12 * h, color=HAIR, linewidth=0.8, zorder=0)
        ax.text(12 * h, -0.88, f"{h} yr: n = {fn[12 * h - 1]:,} forced", ha="center", color=MUTED, fontsize=7)
    ax.scatter([1.6], [0.105], color="white", edgecolor=MUTED, linewidth=1.2, s=22, marker="D")
    ax.text(
        2.6, 0.105, "median return against a matched firm at 1, 3 and 5 years", color=MUTED, fontsize=7.5, va="center"
    )
    ax.set_ylim(-0.9, 0.14)
    ax.set_xlim(0, 62)
    ax.set_xticks([0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60])
    ax.set_xlabel("Months after the announcement (21 trading days each, from day +2)", color=MUTED, fontsize=8.5)
    _frame(ax, "Median buy-and-hold return minus the market")
    return save(fig, "fig2_long_run")


def fig3_exits(data: dict):
    """Cumulative share of firms that stopped trading, by month and by how: forced exits (a), retirements (b).
    Firms with a complete five-year horizon, so the denominator does not change across months."""
    ex = data["exits"]
    months = ex["months"]
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, 6.8 * CM), sharey=True)
    for ax, key, title in (
        (axes[0], "forced", "(a) After a forced exit"),
        (axes[1], "retired", "(b) After a retirement"),
    ):
        s = ex[key]
        acq, bk = s["acquired"], s["bankruptcy"]
        oth = s["other"]
        lay1 = acq
        lay2 = [a + b for a, b in zip(acq, bk)]
        lay3 = [a + o for a, o in zip(lay2, oth)]
        ax.fill_between(months, 0, lay1, color=PERF, alpha=0.85, linewidth=0)
        ax.fill_between(months, lay1, lay2, color=FORCED, alpha=0.85, linewidth=0)
        ax.fill_between(months, lay2, lay3, color=BASE, alpha=0.9, linewidth=0)
        ax.set_xlim(0, 60)
        ax.set_xticks([0, 12, 24, 36, 48, 60])
        ax.set_xlabel("Months after the announcement", color=MUTED, fontsize=8.5)
        ax.set_title(title)
        _frame(ax, f"Share of firms no longer trading (n = {s['n']:,})")
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v * 100:.0f}%"))
        _end_labels(
            ax,
            61.5,
            [
                (lay3[-1] + 0.025, f"{lay3[-1] * 100:.1f}% gone", INK),
                (lay1[-1] / 2, f"acquired {acq[-1] * 100:.1f}%", PERF),
                ((lay1[-1] + lay2[-1]) / 2, f"bankrupt {bk[-1] * 100:.1f}%", FORCED),
            ],
            0.035,
        )
    axes[0].set_ylim(0, 0.42)
    fig.subplots_adjust(wspace=0.45)
    return save(fig, "fig3_exits")


NICE = {
    "financial_misconduct": "Financial misconduct",
    "legal_or_regulatory": "Legal or regulatory",
    "merger_or_restructuring": "Merger or restructuring",
    "retirement_or_health": "Pushed out, described as retirement",
    "relationship_with_employee": "Relationship with an employee",
    "activist_or_shareholder_pressure": "Activist or shareholder pressure",
    "strategy_or_power_dispute": "Strategy or power dispute",
    "other_personal_conduct": "Other personal conduct",
    "unclear": "Reason unclear",
    "performance": "Performance",
    "new_opportunity": "Left for a new job",
    "other_sexual_misconduct": "Sexual misconduct",
}
SEX = {"relationship_with_employee", "other_sexual_misconduct", "other_personal_conduct"}
MONEY = {"financial_misconduct", "legal_or_regulatory"}


def fig4_reasons(data: dict):
    """Mean CAR[-1,+1] with its 95% interval for each coded reason a forced exit happened (at least 10 cases),
    sorted from the most costly. Money and legal cases in crimson, personal-conduct cases in violet."""
    rs = sorted(data["reasons"], key=lambda r: r["mean"])
    fig, ax = plt.subplots(figsize=(WIDE, 8.6 * CM))
    for i, r in enumerate(rs):
        color = FORCED if r["reason"] in MONEY else CONDUCT if r["reason"] in SEX else RETIRED
        ax.plot([r["lo"], r["hi"]], [i, i], color=color, linewidth=1.6, alpha=0.55, solid_capstyle="butt")
        ax.scatter([r["mean"]], [i], color=color, s=34, zorder=3)
        ax.text(
            0.162, i, f"{_pct(r['mean'])}   n = {r['n']}", va="center", color=color, fontsize=8, fontweight="semibold"
        )
    ax.set_yticks(range(len(rs)))
    ax.set_yticklabels([NICE.get(r["reason"], r["reason"]) for r in rs], color=INK, fontsize=8.5)
    ax.axvline(0, color=BASE, linewidth=0.8)
    ax.set_xlim(-0.16, 0.16)
    ax.grid(axis="x", color=HAIR, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines["bottom"].set_visible(False)
    ax.xaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: (MINUS if v < 0 else "") + f"{abs(v) * 100:.0f}%")
    )
    ax.text(
        0,
        1.02,
        "Mean abnormal return, trading days " + MINUS + "1 to +1, with 95% interval",
        transform=ax.transAxes,
        color=MUTED,
        fontsize=8,
    )
    return save(fig, "fig4_reasons")


def fig5_per_year(data: dict):
    """Forced exits per year by the database's dismissal type, with founder removals marked; 1998 to 2023."""
    py = data["per_year"]
    yrs = py["years"]
    fig, ax = plt.subplots(figsize=(WIDE, 6.2 * CM))
    ax.bar(yrs, py["performance"], color=PERF, width=0.72, label="Fired for performance")
    ax.bar(
        yrs,
        py["conduct"],
        bottom=py["performance"],
        color=CONDUCT,
        width=0.72,
        label="Fired for legal or personal conduct",
    )
    tops = [a + b for a, b in zip(py["performance"], py["conduct"])]
    for y, t, fo in zip(yrs, tops, py["founder"]):
        if fo:
            ax.text(y, t + 1.5, str(fo), ha="center", color=FOUNDER, fontsize=7, fontweight="semibold")
    ax.grid(axis="y", color=HAIR, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.set_xlim(1997.3, 2023.7)
    ax.set_xticks(list(range(1998, 2024, 2)))
    ax.text(
        1,
        1.02,
        "Forced CEO exits per year; amber numbers: founders among them",
        transform=ax.transAxes,
        color=MUTED,
        fontsize=8,
        ha="right",
    )
    ax.set_ylim(0, 112)
    leg = ax.legend(frameon=False, fontsize=8, loc="lower left", ncol=2, bbox_to_anchor=(0.0, 1.06))
    for t in leg.get_texts():
        t.set_color(INK)
    return save(fig, "fig5_per_year")


def fig6_roa_board(data: dict):
    """(a) Median change in return on assets against the matched firm, fiscal years 0 to 3 against year -1.
    (b) The board about two years later: directors gone, chair and CEO roles split, the former CEO still a director."""
    roa, board = data["roa"], data["board"]
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, 6.8 * CM), gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axes[0]
    _zero(ax)
    items = []
    for key, label, color, lw in (("forced", "Forced exits", FORCED, 2.0), ("retired", "Retirements", RETIRED, 1.4)):
        s = roa[key]
        ax.plot(roa["years"], s["median"], color=color, linewidth=lw, marker="o", markersize=3.5)
        items.append((s["median"][-1], f"{label}\nn = {s['n'][-1]:,} in year 3", color))
    _end_labels(ax, 3.12, items, 0.0045)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(["Year 0", "Year 1", "Year 2", "Year 3"])
    ax.set_title("(a) Profitability against a matched firm")
    _frame(ax, "Median change in ROA since year " + MINUS + "1 minus the match, pp")
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: (MINUS if v < 0 else "") + f"{abs(v) * 100:.1f}")
    )
    ax.set_xlim(-0.2, 3.9)
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
    xs = range(len(bars))
    for i, (_label, kf, kr) in enumerate(bars):
        vf, vr = board.get(kf, {}).get("value"), board.get(kr, {}).get("value")
        if vf is not None:
            ax.bar(i - 0.19, vf, width=0.36, color=FORCED)
            if i != 2:
                ax.text(
                    i - 0.19,
                    vf + 0.015,
                    f"{vf * 100:.0f}%",
                    ha="center",
                    color=FORCED,
                    fontsize=7.5,
                    fontweight="semibold",
                )
        if vr is not None:
            ax.bar(i + 0.19, vr, width=0.36, color=RETIRED)
            ax.text(
                i + 0.19,
                vr + 0.015,
                f"{vr * 100:.0f}%",
                ha="center",
                color=RETIRED,
                fontsize=7.5,
                fontweight="semibold",
            )
    fs = board.get("board.forced_founder.founder_stays.mean", {})
    if fs.get("value") is not None:
        ax.scatter([2 - 0.19], [fs["value"]], color=FOUNDER, s=30, zorder=4, marker="D")
        ax.annotate(
            f"fired founders\n{fs['value'] * 100:.0f}%",
            (2 - 0.19, fs["value"]),
            xytext=(0, 22),
            textcoords="offset points",
            color=FOUNDER,
            fontsize=7.5,
            fontweight="semibold",
            ha="center",
        )
    ax.set_xticks(list(xs))
    ax.set_xticklabels([b[0] for b in bars], fontsize=8)
    ax.set_title("(b) The board about two years later")
    _frame(ax, "Share of firms (crimson forced, slate retired)")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v * 100:.0f}%"))
    ax.set_ylim(0, 0.8)
    fig.subplots_adjust(wspace=0.45)
    return save(fig, "fig6_roa_board")


FIGURES = (fig1_event_time, fig2_long_run, fig3_exits, fig4_reasons, fig5_per_year, fig6_roa_board)


def main():
    data = load()
    for fn in FIGURES:
        print(fn(data))


if __name__ == "__main__":
    main()
