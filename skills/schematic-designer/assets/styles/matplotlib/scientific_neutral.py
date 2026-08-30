"""Executable Matplotlib profile for the portable scientific-neutral grammar."""

from __future__ import annotations

import logging

import matplotlib
from cycler import cycler


COLORS = {
    "canvas": "#FFFFFF",
    "ink": "#202124",
    "muted": "#5F6368",
    "faint": "#98A2AE",
    "grid": "#C7CED8",
    "panel_fill": "#FBFCFD",
    "purple": "#7656A5",
    "purple_light": "#E4DAEF",
    "purple_text": "#5F3B8D",
    "blue": "#3F78A8",
    "blue_light": "#D8E7F3",
    "green": "#2C8C68",
    "green_light": "#D8EEE5",
    "green_text": "#176447",
    "orange": "#D88A24",
    "orange_light": "#F7E2C4",
    "orange_text": "#8A5500",
    "red": "#B84B52",
    "red_light": "#F3D7D9",
    "red_text": "#8F2F36",
    "teal": "#278C8A",
    "teal_text": "#166866",
    "yellow": "#E9B949",
    "ecm": "#7C8795",
}

SEMANTIC_COLORS = {
    "cell_fill": COLORS["blue_light"],
    "cell_edge": COLORS["blue"],
    "source_fill": COLORS["orange_light"],
    "source_edge": COLORS["orange"],
    "field": COLORS["yellow"],
    "signal": COLORS["purple"],
    "update": COLORS["green"],
    "noise": COLORS["red"],
    "context": COLORS["muted"],
}

SIZE_TOKENS = {
    "cell_width": 1.20,
    "cell_height": 0.82,
    "process_box_width": 1.42,
    "process_box_height": 0.50,
}

FONT_SIZES = {
    "panel_label": 11.5,
    "title": 10.0,
    "body": 8.5,
    "small": 7.5,
    "tiny": 7.0,
    "equation": 9.0,
}


def apply_style() -> None:
    """Apply neutral typography, color cycle, axes, and outlined SVG export."""
    logging.getLogger("fontTools").setLevel(logging.ERROR)
    matplotlib.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["CMU Sans Serif", "DejaVu Sans", "Arial"],
            "font.size": FONT_SIZES["body"],
            "axes.titlesize": FONT_SIZES["title"],
            "axes.labelsize": FONT_SIZES["body"],
            "xtick.labelsize": FONT_SIZES["small"],
            "ytick.labelsize": FONT_SIZES["small"],
            "legend.fontsize": FONT_SIZES["small"],
            "mathtext.fontset": "cm",
            "axes.unicode_minus": False,
            "axes.edgecolor": COLORS["ink"],
            "axes.labelcolor": COLORS["ink"],
            "axes.titlecolor": COLORS["ink"],
            "xtick.color": COLORS["ink"],
            "ytick.color": COLORS["ink"],
            "grid.color": COLORS["grid"],
            "axes.prop_cycle": cycler(
                color=[
                    COLORS["blue"],
                    COLORS["orange"],
                    COLORS["green"],
                    COLORS["red"],
                    COLORS["purple"],
                    COLORS["teal"],
                ]
            ),
            "figure.facecolor": COLORS["canvas"],
            "axes.facecolor": COLORS["canvas"],
            "savefig.facecolor": COLORS["canvas"],
            "savefig.transparent": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "path",
            "svg.image_inline": True,
        }
    )
