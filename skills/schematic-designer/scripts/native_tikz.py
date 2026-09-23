"""Native TikZ arrow artists for Matplotlib's PGF renderer.

Only numeric geometry and fixed, allowlisted TikZ options enter the TeX source.
Paths are transformed at draw time, so layout, clipping and artist z-order stay
with Matplotlib while arrows.meta owns the actual arrowhead geometry.
"""
from __future__ import annotations

import math
from pathlib import Path
import sys
import numpy as np
from matplotlib.artist import Artist
from matplotlib.colors import to_rgba
from matplotlib.font_manager import FontProperties
from matplotlib.transforms import Bbox

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets" / "styles"))
from minimalist_profile import ARROW_PT, DASH_PT, FONT_PT, _validate_roles


class TikzArrow(Artist):
    def __init__(self, start, end, *, color, linewidth=.75, rad=0,
                 linestyle='-', shrink_a=0, shrink_b=0, zorder=6,
                 alpha=1, clip_on=False, ends='end', head='Latex'):
        super().__init__()
        self.start = np.asarray(start, dtype=float)
        self.end = np.asarray(end, dtype=float)
        if self.start.shape != (2,) or self.end.shape != (2,):
            raise ValueError('Arrow endpoints must be 2D coordinates')
        values = [*self.start, *self.end, linewidth, rad, shrink_a, shrink_b, alpha]
        if not all(math.isfinite(float(v)) for v in values):
            raise ValueError('Arrow geometry and styling must be finite')
        if linewidth <= 0 or min(shrink_a, shrink_b) < 0 or not 0 <= alpha <= 1:
            raise ValueError('Invalid arrow width, shortening, or opacity')
        if ends not in {'end', 'start', 'both'} or head not in {'Latex', 'Bar', 'Circle', 'Diamond'}:
            raise ValueError('Unsupported arrow terminal')
        if linestyle not in {'-', '--', ':'}:
            raise ValueError('Use solid, dashed, or dotted arrow strokes')
        self.color = to_rgba(color)
        self.linewidth, self.rad = linewidth, rad
        self.linestyle, self.ends, self.head = linestyle, ends, head
        self.shrink_a, self.shrink_b = shrink_a, shrink_b
        self.set_alpha(alpha)
        self.set_zorder(zorder)
        self.set_clip_on(clip_on)

    def _geometry(self):
        p0, p1 = self.get_transform().transform([self.start, self.end])
        delta = p1 - p0
        control = (p0 + p1) / 2 + self.rad * np.array([delta[1], -delta[0]])
        return p0, p1, control

    def get_window_extent(self, renderer=None):
        p0, p1, q = self._geometry()
        points = np.array([p0,p1,q])
        # Include customized tips at any tangent angle. The second term also
        # bounds the library's stroke-dependent non-Latex terminal defaults.
        tip_extent = max(ARROW_PT['length'] + ARROW_PT['width'], 4 + 6*self.linewidth)
        pad = (tip_extent + self.linewidth) * self.figure.dpi / 72
        return Bbox.from_extents(*(points.min(axis=0)-pad), *(points.max(axis=0)+pad))

    def draw(self, renderer):
        if not self.get_visible():
            return
        # Deliberately no backend fallback: ordinary raster/SVG renderers cannot
        # produce the requested native TikZ arrowheads.
        if 'backend_pgf' not in type(self.figure.canvas).__module__:
            raise RuntimeError('Native TikZ arrows require the PGF canvas and minimalist profile')
        _validate_roles()
        p0, p1, q = self._geometry()
        scale = 72 / self.figure.dpi
        end, control = (p1-p0)*scale, (q-p0)*scale
        def pair(p): return f'({p[0]:.8f},{p[1]:.8f})'
        c1 = 2/3*control
        c2 = end + 2/3*(control-end)
        tip = self.head
        if tip == 'Latex':
            tip += f"[length={ARROW_PT['length']:g}bp,width={ARROW_PT['width']:g}bp]"
        terminal = {'end': '-{'+tip+'}', 'start': '{'+tip+'}-',
                    'both': '{'+tip+'}-{'+tip+'}'}[self.ends]
        dash = 'solid'
        if self.linestyle != '-':
            on, off = DASH_PT['dashed' if self.linestyle == '--' else 'dotted']
            dash = f'dash pattern=on {on:g}bp off {off:g}bp'
        body = ('(0,0) -- '+pair(end) if self.rad == 0 else
                '(0,0) .. controls '+pair(c1)+' and '+pair(c2)+' .. '+pair(end))
        tex = (r'\tikz[overlay,baseline=0bp,x=1bp,y=1bp]{\draw['+terminal+','+dash+
               f',line width={self.linewidth:g}bp,line cap=butt,line join=round,'+
               f'shorten <={self.shrink_a:g}bp,shorten >={self.shrink_b:g}bp] '+body+';}')
        gc = renderer.new_gc()
        try:
            self._set_gc_clip(gc)
            gc.set_foreground(self.color)
            gc.set_alpha(self.get_alpha() * self.color[3])
            renderer.draw_tex(gc, *p0, tex, FontProperties(family='sans-serif',size=FONT_PT['body']), 0)
        finally:
            gc.restore()
        self.stale = False


def arrow(ax, start, end, **kwargs):
    """Attach one native TikZ arrow using the axes' data transform."""
    artist = TikzArrow(start, end, **kwargs)
    ax.add_artist(artist)
    return artist
