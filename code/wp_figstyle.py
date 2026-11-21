"""
PATH: wp_figstyle.py (beside figures.py; matplotlib only)
PURPOSE: The figure style of the two-column working paper (design "Exhibit", the two-column working-paper 
         wp2col_template.tex): one palette shared with the page, Source Sans 3 at print size, a hairline grid,
         direct labels, the two print widths, and the cover's headline chart ("at a glance"), so every figure reads
         as one system with the tables and boxes around it.
WHY: Figures drawn at 17 cm and scaled into a 6.6 in or 3.4 in slot print their text at random sizes. Drawn at the
     slot's own width, 8 pt in matplotlib is 8 pt on the page.

COLOUR ROLES (21 Nov 2026): colour belongs to data, the frame is
    neutral. The paper's focal series is red (firings, in the founder-CEO paper); comparison and benchmark groups
    (retirements, the market, "other") are a light-mid grey; further series take violet, teal and amber in that order;
    no blue or navy in data (navy is the page's frame and links).
    Validated with the dataviz validate_palette.js (light, white surface): red, violet, teal, amber pass lightness,
    chroma, adjacent CVD (worst 12.7) and normal vision (worst 21.3); all pairs including the grey pass CVD (worst
    10.9) and normal vision (worst 17.0). The grey is 2.2:1 on white, so a comparison line always carries a direct
    label (end_label). A darker mid-grey failed against teal under protanopia (2.6), hence the lighter grey.

ADOPTING IT IN A PACK (figures.py):
    import wp_figstyle as S
    S.use(FONTS)                             # FONTS: the folder with SourceSans3-*.otf
    fig, ax = S.figure("full", "standard")   # 6.6 x 2.7 in; "column" for 3.425 in
    ax.plot(x, y, color=S.FOCAL, linewidth=S.LINE["main"])
    S.frame(ax, "Return minus the market")   # hairline grid, unit label above the plot
    S.end_label(ax, x[-1], y[-1], "Firings  -7.3%", S.FOCAL)
    S.save(fig, OUT / "fig1_event_time.png")  # exact print size, RGB
  Replace the pack's own colour constants with S.FOCAL (S.FORCED), S.COMPARE (S.RETIRED), S.SERIES2 (S.CONDUCT),
  S.SERIES3 (S.PERF), S.SERIES4 (S.FOUNDER), S.INK, S.MUTED, S.HAIR, S.ZERO, S.SHADE; keep panel titles in the image
  only for multi-panel figures (the LaTeX caption carries the label and the message title).

THE COVER'S HEADLINE CHART (optional, per paper):
    S.hero(days, {"Firings": (mean, S.FOCAL, lo, hi), "Retirements": (mean, S.COMPARE, None, None)},
           OUT / "fig0_hero.png", xlabel="Trading days from the announcement", window_span=(-1, 1))
  Serve it like the other figures (/static/reports/<pack>/figures/fig0_hero.png) and set in jf_export:
  hero_figure, hero_title (the message, one line), hero_unit (what and on how many), hero_note (one line, may
  name the full figure). Without hero_figure the cover sets the abstract beside the keywords.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

# Data colours. Colour follows the entity, never the rank.
FOCAL = "#D42A3C"  # the paper's subject (red): firings, forced exits
COMPARE = "#A9AEB6"  # comparison and benchmark groups (grey): retirements, the market, "other"
SERIES2 = "#7A4FC0"  # violet: a further series (personal conduct)
SERIES3 = "#12968A"  # teal: a further series (performance, other reasons; acquisitions)
SERIES4 = "#C98612"  # amber: a further series (founders)
SERIES = [FOCAL, SERIES2, SERIES3, SERIES4]
# The founder-CEO pack's names for the same roles.
FORCED, RETIRED, CONDUCT, PERF, FOUNDER = FOCAL, COMPARE, SERIES2, SERIES3, SERIES4
# Text and chrome (the frame): neutral. Text never wears a series colour; a short colour key beside it carries the
# identity.
INK = "#14161B"  # values and direct labels (the page's ink)
MUTED = "#5A5E66"  # axis text, unit labels
HAIR = "#E4E6EA"  # grid
ZERO = "#5A5E66"  # the zero line: dark and thin, never read as the grey comparison line
BASE = ZERO
SHADE = "#F1F2F4"  # an event window
NAVY = "#13294B"  # the page's frame colour; never a series colour
MINUS = "\u2212"

# Print sizes (inches) on the two-column page: the figure width across both columns (wp2col_meta's figuresetup,
# 6.6 in) and one column (page_spec: 3.425 in); heights from a short list; the cover's headline chart.
FULL_W = 6.6
COL_W = 3.425
HEIGHTS = {"short": 2.2, "standard": 2.7, "tall": 3.4}
HERO = (2.45, 1.8)
DPI = 600

SIZES = {"tick": 7.5, "label": 8.0, "direct": 8.0, "panel": 8.5, "unit": 7.5, "small": 7.0}
LINE = {"main": 1.8, "comparison": 1.2, "ci_alpha": 0.10}


def use(font_dir: Optional[Path] = None) -> None:
    """Register Source Sans 3 (the page's label face) and set the rcParams."""
    for face in sorted(Path(font_dir).glob("SourceSans3-*.otf")) if font_dir else ():
        font_manager.fontManager.addfont(str(face))
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Source Sans 3", "Helvetica Neue", "Arial", "DejaVu Sans"],
            "font.size": SIZES["label"],
            "text.color": INK,
            "axes.edgecolor": "#9AA0A8",
            "axes.linewidth": 0.6,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.left": False,
            "axes.labelcolor": MUTED,
            "axes.labelsize": SIZES["label"],
            "axes.titlesize": SIZES["panel"],
            "axes.titleweight": "semibold",
            "axes.titlecolor": INK,
            "axes.titlelocation": "left",
            "axes.titlepad": 12,
            "axes.grid": False,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelsize": SIZES["tick"],
            "ytick.labelsize": SIZES["tick"],
            "xtick.major.size": 0,
            "ytick.major.size": 0,
            "xtick.major.pad": 4,
            "ytick.major.pad": 3,
            "lines.linewidth": LINE["main"],
            "lines.solid_capstyle": "round",
            "lines.solid_joinstyle": "round",
            "legend.frameon": False,
            "legend.fontsize": SIZES["label"],
            "axes.unicode_minus": True,
            "savefig.dpi": DPI,
            "savefig.facecolor": "white",
            "figure.dpi": 100,
        }
    )


def figure(width: str = "full", height: str | float = "standard", **kw):
    """A figure at its print size: width "full" (FULL_W) or "column" (COL_W); height a HEIGHTS key or inches."""
    w = FULL_W if width == "full" else COL_W
    h = HEIGHTS[height] if isinstance(height, str) else float(height)
    return plt.subplots(figsize=(w, h), **kw)


def pct(v: float, digits: int = 1, sign: bool = True) -> str:
    """-0.073 -> "−7.3%" (a true minus), +0.05 -> "+5.0%"."""
    text = f"{abs(v) * 100:.{digits}f}%"
    return MINUS + text if v < 0 else ("+" if sign and v > 0 else "") + text


def frame(ax, unit: str = "", percent: bool = True, digits: int = 0) -> None:
    """A hairline y grid behind the data, no y spine, the unit as a small label above the plot."""
    ax.grid(axis="y", color=HAIR, linewidth=0.6)
    ax.set_axisbelow(True)
    if unit:
        ax.text(0, 1.03, unit, transform=ax.transAxes, color=MUTED, fontsize=SIZES["unit"], va="bottom")
    if percent:
        ax.yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda v, _: (MINUS if v < 0 else "") + f"{abs(v) * 100:.{digits}f}%")
        )


def zero(ax) -> None:
    ax.axhline(0, color=ZERO, linewidth=0.5, zorder=1)


def window(ax, lo: float, hi: float) -> None:
    """An event window as a quiet band."""
    ax.axvspan(lo, hi, color=SHADE, zorder=0, linewidth=0)


def end_label(ax, x, y, text: str, color: str, dy: float = 0.0) -> None:
    """A direct label at a line's end: a short colour key, then the text in ink."""
    ax.annotate(
        "—",
        (x, y),
        xytext=(3, dy),
        textcoords="offset points",
        color=color,
        fontsize=SIZES["direct"],
        fontweight="bold",
        va="center",
        annotation_clip=False,
    )
    ax.annotate(
        text,
        (x, y),
        xytext=(13, dy),
        textcoords="offset points",
        color=INK,
        fontsize=SIZES["direct"],
        va="center",
        annotation_clip=False,
    )


def save(fig, path: Path) -> Path:
    """At the print size (no tight bbox, so the image is exactly the slot's width), as RGB: an alpha channel becomes
    a soft mask in the PDF and shows as a faint box in some viewers."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, facecolor="white")
    plt.close(fig)
    try:
        from PIL import Image

        Image.open(path).convert("RGB").save(path, optimize=True)
    except ImportError:  # matplotlib's PNG still prints; only the soft mask remains
        pass
    return path


def hero(
    x,
    series: dict,
    path: Path,
    xlabel: str = "",
    window_span: Optional[tuple] = None,
    ylim: Optional[tuple] = None,
    yticks: Optional[list] = None,
) -> Path:
    """The cover's headline chart at HERO size: one panel, at most three series given as
    {label: (y, colour, lo or None, hi or None)}, the first the focal series (FOCAL, heaviest, with its band), the
    others comparisons (COMPARE) or further series, labelled at the line ends with their last values; the window
    band and the zero line. The unit and N go in jf_export.hero_unit."""
    fig, ax = plt.subplots(figsize=HERO)
    fig.subplots_adjust(left=0.17, right=0.66, top=0.97, bottom=0.17)
    if window_span:
        window(ax, *window_span)
    zero(ax)
    items = list(series.items())
    for n, (_label, (y, color, lo, hi)) in enumerate(reversed(items)):
        main = n == len(items) - 1
        if lo is not None and hi is not None:
            ax.fill_between(x, lo, hi, color=color, alpha=LINE["ci_alpha"], linewidth=0, zorder=2)
        ax.plot(x, y, color=color, linewidth=LINE["main"] if main else LINE["comparison"], zorder=3)
    ends = sorted(((y[-1], label, color) for label, (y, color, _lo, _hi) in items), reverse=True)
    for k, (yv, label, color) in enumerate(ends):
        end_label(ax, x[-1], yv, f"{label}\n{pct(yv, sign=False)}", color, dy=4 if k == 0 else -4)
    ax.set_xlim(min(x), max(x))
    if ylim:
        ax.set_ylim(*ylim)
    if yticks is not None:
        ax.set_yticks(yticks)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=SIZES["small"], labelpad=3)
    frame(ax)
    return save(fig, path)
