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
    'canvas': PAPER, 'ink': INK, 'muted': MUTED, 'faint': _n['faint'],
    'grid': _n['grid'], 'panel_fill': PAPER,
    'purple': _c[5], 'purple_light': _pale(_c[5]), 'purple_text': _c[5],
    'blue': _c[4], 'blue_light': _pale(_c[4]),
    'green': _c[3], 'green_light': _pale(_c[3]), 'green_text': _c[5],
    'orange': _c[1], 'orange_light': _pale(_c[1]), 'orange_text': INK,
    'red': _c[0], 'red_light': _pale(_c[0]), 'red_text': _c[0],
    'teal': _c[4], 'teal_text': _c[4], 'yellow': _c[2], 'ecm': MUTED,
}
SEMANTIC_COLORS = {
    'cell_fill': COLORS['blue_light'], 'cell_edge': COLORS['blue'],
    'source_fill': COLORS['orange_light'], 'source_edge': COLORS['orange'],
    'field': COLORS['yellow'], 'signal': COLORS['purple'],
    'update': COLORS['green'], 'noise': COLORS['red'], 'context': MUTED,
}
SIZE_TOKENS = {'cell_width':1.20,'cell_height':.82,'process_box_width':1.42,'process_box_height':.50}
FONT_SIZES = {'panel_label':FONT_PT['panel'],'title':FONT_PT['title'],
              'body':FONT_PT['body'],'small':FONT_PT['small'],'tiny':FONT_PT['small'],
              'equation':FONT_PT['equation']}
