"""Executable Matplotlib profile for the learning-dynamics-2406 grammar."""

from __future__ import annotations

import logging

import matplotlib
from matplotlib import font_manager


COLORS = {
    "canvas": "#FFFFFF",
    "ink": "#1A1A1A",
    "warm_ink": "#231F20",
    "muted": "#4D4D4D",
    "faint": "#999999",
    "neutral_bar": "#E1E1E1",
    "training": "#2CA05A",
    "training_bar": "#C0E3CE",
    "retrieval": "#A9745C",
    "retrieval_bar": "#EACFC3",
    "purple": "#8B5EB9",
    "purple_edge": "#52386E",
    "orange": "#E8901A",
    "orange_edge": "#8E4D08",
    "blue": "#3B8BC3",
    "blue_dark": "#124984",
    "red": "#F24432",
    "red_dark": "#A52C22",
    "yellow": "#FFD42A",
    "field_core": "#FAD432",
    "field_pale": "#FBECAE",
    "fixed_section": "#D9E9F3",
    "cycle_section": "#F6DFDB",
}

FONT_SIZES = {
    "major_heading": 13.0,
    "panel_label": 11.5,
    "section_label": 10.5,
    "panel_title": 10.0,
    "axis_label": 8.5,
    "annotation": 7.8,
    "tick_label": 7.5,
}


def resolve_cmu_face(target_weight: int):
    """Resolve a concrete CMU Sans face; return a documented fallback if absent."""
    candidates = [
        face
        for face in font_manager.fontManager.ttflist
        if face.name == "CMU Sans Serif" and face.style == "normal"
    ]
    if candidates:
        face = min(candidates, key=lambda item: abs(item.weight - target_weight))
        return font_manager.FontProperties(fname=face.fname), None
    fallback = font_manager.FontProperties(
        family="DejaVu Sans", weight=target_weight
    )
    return fallback, "CMU Sans Serif unavailable; using DejaVu Sans"


def apply_style() -> None:
    """Apply the reusable typography, palette-independent axes, and vector export rules."""
    logging.getLogger("fontTools").setLevel(logging.ERROR)
    matplotlib.rcParams.update(
        {
            "text.usetex": False,
            "font.family": "sans-serif",
            "font.sans-serif": [
                "CMU Sans Serif",
                "Latin Modern Sans",
                "DejaVu Sans",
            ],
            "font.weight": 500,
            "font.size": FONT_SIZES["axis_label"],
            "mathtext.fontset": "cm",
            "axes.unicode_minus": False,
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
