"""Compatibility names for existing examples, backed by the Minimalist profile.

The historical module name is retained for source compatibility; it no longer
selects a second palette or a fallback font. New examples can use the shared
profile directly and assign scientific roles in their own source.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from minimalist_profile import apply_style, palette, FONT_PT, OPACITY, INK, MUTED, PAPER, tint, neutral_colors

_c = palette()
_n = neutral_colors()
def _pale(color):
    return tint(color, OPACITY['fill'])

COLORS = {
    'canvas': PAPER, 'ink': INK, 'warm_ink': INK, 'muted': MUTED, 'faint':_n['faint'],
    'neutral_bar':_n['panel'], 'training':_c[4], 'training_bar':_pale(_c[4]),
    'retrieval':_c[0], 'retrieval_bar':_pale(_c[0]),
    'purple':_c[5], 'purple_edge':_c[5], 'orange':_c[1], 'orange_edge':_c[1],
    'blue':_c[4], 'blue_dark':_c[4], 'red':_c[0], 'red_dark':_c[0],
    'yellow':_c[2], 'field_core':_c[2], 'field_pale':_pale(_c[2]),
    'fixed_section':_pale(_c[4]), 'cycle_section':_pale(_c[0]),
}
FONT_SIZES = {'major_heading':FONT_PT['panel'],'panel_label':FONT_PT['panel'],
              'section_label':FONT_PT['title'],'panel_title':FONT_PT['title'],
              'axis_label':FONT_PT['body'],'annotation':FONT_PT['body'],
              'tick_label':FONT_PT['small']}

def resolve_cmu_face(target_weight):
    """Retained caller signature; require the actual CMU face, never substitute."""
    from matplotlib.font_manager import FontProperties, findfont
    prop = FontProperties(family='CMU Sans Serif', weight=target_weight)
    findfont(prop, fallback_to_default=False)
    return FontProperties(family='sans-serif', weight=target_weight), None
