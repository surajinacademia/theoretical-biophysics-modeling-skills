"""Complementary modeling choices for collective cells.

All geometry and analytically specified fields are illustrative, not simulation
results. The five columns are not a taxonomy or a ranking of model resolution.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

SKILL_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(SKILL_ROOT / 'scripts'))
sys.path.insert(0, str(SKILL_ROOT / 'assets' / 'styles'))
sys.path.insert(0, str(SKILL_ROOT / 'assets' / 'styles' / 'matplotlib'))
from minimalist_profile import apply_style, FONT_PT, LINE_PT, MARKER_PT, tint
apply_style()
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, Rectangle
from scientific_neutral import COLORS
from native_tikz import arrow as tikz_arrow
from vector_output import save_vector_pair

OUTPUT_BASENAME = 'collective-cell-model-classes'
PAPER_SIZE_IN = (11.2, 7.2)
INK, MUTED = COLORS['ink'], COLORS['muted']
ACCENTS = [COLORS[k] for k in ('purple', 'blue', 'green', 'orange', 'red')]


def text(ax, x, y, label, *, role='body', color=INK, weight='normal', ha='center'):
    return ax.text(x, y, label, fontsize=FONT_PT[role], color=color,
                   weight=weight, ha=ha, va='center', linespacing=1.25)


def arrow(ax, start, end, *, color=INK, dashed=False):
    return tikz_arrow(ax, start, end, color=color,
                      linewidth=LINE_PT['structure'],
                      linestyle='--' if dashed else '-', zorder=10)


def cell(ax, xy, radius=.09, *, color, label=None):
    ax.add_patch(Circle(xy, radius, facecolor=tint(color, .12),
                        edgecolor=color, linewidth=LINE_PT['emphasis'], zorder=3))
    if label:
        text(ax, *xy, label, role='small')


def subheading(ax, y, label):
    text(ax, .5, y, label, role='title', weight='bold')


def central_force(xi, xj, *, k=1., rest=.4):
    """Force on i for U(r)=k(r-rest)^2/2, with e_ij pointing i to j."""
    delta = np.asarray(xj) - np.asarray(xi)
    distance = np.linalg.norm(delta)
    if distance == 0:
        raise ValueError('The pair direction requires distinct centers')
    return k * (distance - rest) * delta / distance


def particle_panel(ax, color):
    subheading(ax, 2.39, 'Illustrative spring law')
    # Same k and rest length, and same force-to-arrow scale in both examples.
    for y, distance, label in [(2.10, .58, r'Attraction: $r>r_0$'),
                               (1.60, .22, r'Repulsion: $r<r_0$')]:
        xi, xj = np.array([.5-distance/2, y]), np.array([.5+distance/2, y])
        force = central_force(xi, xj)
        ax.plot([xi[0], xj[0]], [y, y], color=COLORS['grid'], lw=LINE_PT['context'])
        cell(ax, xi, color=color)
        cell(ax, xj, color=color)
        arrow(ax, xi, xi+force, color=color)
        arrow(ax, xj, xj-force, color=color)
        text(ax, .5, y-.20, label)
        if distance > .4:
            text(ax, xi[0], y+.15, r'$i$', role='small')
            text(ax, xj[0], y+.15, r'$j$', role='small')
    text(ax, .5, 1.21, r'$\mathbf F_i=k(r-r_0)\hat{\mathbf e}_{ij}$')
    text(ax, .5, 1.05, r'$\mathbf F_j=-\mathbf F_i$; $k>0$')
    text(ax, .5, .92, r'$\hat{\mathbf e}_{ij}$: unit direction from $i$ to $j$', role='small')
    subheading(ax, .78, 'Optional propulsion velocity')
    cell(ax, (.30, .51), color=color)
    arrow(ax, (.30, .51), (.65, .51), color=color)
    text(ax, .71, .51, r'$v_0\mathbf p_i$', ha='left')
    text(ax, .5, .29, r'$v_0$: speed; $\mathbf p_i$: unit polarity', role='small')
    text(ax, .5, .12, r'$r$: center separation'+'\n'+r'$r_0$: equilibrium separation')


def rule_panel(ax, color):
    subheading(ax, 2.39, 'Sense local inputs')
    text(ax, .5, 2.19, 'Signals, neighbors, environment')
    arrow(ax, (.5, 2.06), (.5, 1.90), color=color)
    cell(ax, (.5, 1.71), radius=.15, color=color)
    ax.add_patch(Rectangle((.467, 1.677), .066, .066,
                           facecolor=color, edgecolor='none', zorder=4))
    text(ax, .5, 1.45, 'Internal marker = state')
    text(ax, .5, 1.27, 'State-dependent rules', weight='bold')
    # A branching dependency graph: these are possible outcomes, not a sequence.
    arrow(ax, (.5, 1.14), (.5, .99), color=color, dashed=True)
    ax.plot([.18, .82], [.99, .99], color=color, lw=LINE_PT['structure'])
    for x, label in [(.18, 'Move'), (.5, 'Divide'), (.82, 'Secrete')]:
        arrow(ax, (x, .99), (x, .78), color=color, dashed=True)
        text(ax, x, .64, label)
    text(ax, .5, .40, 'Also: change internal state')
    text(ax, .5, .17, 'Possible behaviors')


def lattice(ax, origin, labels, color):
    nrow, ncol = labels.shape
    size = .115
    for row in range(nrow):
        for col in range(ncol):
            value = labels[row, col]
            xy = (origin[0] + col*size, origin[1] + row*size)
            face = '#ffffff' if value == 0 else tint(color, .16 if value == 1 else .40)
            ax.add_patch(Rectangle(xy, size, size, facecolor=face,
                                  edgecolor=COLORS['grid'], lw=LINE_PT['context']))
            if value:
                text(ax, xy[0]+size/2, xy[1]+size/2, str(value), role='small')


def lattice_panel(ax, color):
    subheading(ax, 2.39, 'Cellular automaton')
    ca = np.zeros((4, 6), dtype=int)
    ca[1, 1] = ca[2, 3] = ca[1, 4] = 1
    lattice(ax, (.155, 1.73), ca, color)
    text(ax, .5, 1.55, 'One occupied site per cell')
    text(ax, .5, 1.38, '1 = occupied; blank = empty', role='small')
    subheading(ax, 1.10, 'Cellular Potts model')
    cpm = np.array([[0,1,1,0,0,0], [1,1,1,0,2,0],
                    [0,1,0,2,2,2], [0,0,0,0,2,0]])
    lattice(ax, (.155, .44), cpm, color)
    text(ax, .5, .27, 'Many lattice sites per cell')
    text(ax, .5, .09, '1 and 2 = distinct cell identities', role='small')


def shape_field(x, y):
    """Illustrative diffuse cell: the ellipse is exactly the phi=0.5 contour."""
    distance = np.sqrt((x/.31)**2 + (y/.21)**2)
    return .5*(1-np.tanh((distance-1)/.15))


SAMPLE_POSITIONS = np.array([[-.23,-.06], [-.08,.08], [.10,-.08], [.24,.08]])
DENSITY_SIGMA = .115


def density_field(x, y):
    """Sum of normalized 2D kernels; integral over the plane equals cell count."""
    result = np.zeros(np.broadcast_shapes(np.shape(x), np.shape(y)))
    for px, py in SAMPLE_POSITIONS:
        result += np.exp(-((x-px)**2+(y-py)**2)/(2*DENSITY_SIGMA**2))
    return result/(2*np.pi*DENSITY_SIGMA**2)


def field_panel(ax, color):
    cmap = LinearSegmentedColormap.from_list('cell_fields', ['#ffffff', tint(color,.3),color])
    x, y = np.meshgrid(np.linspace(-.44,.44,90), np.linspace(-.30,.30,65))
    subheading(ax, 2.39, 'Cell-shape field')
    phi = shape_field(x, y)
    ax.contourf(x+.5, y+1.96, phi, levels=np.linspace(0,1,15), cmap=cmap)
    ax.contour(x+.5, y+1.96, phi, levels=[.5], colors=INK, linewidths=LINE_PT['structure'])
    text(ax, .5, 1.96, r'$\phi_i\approx 1$', color='#ffffff')
    text(ax, .5, 1.55, r'Diffuse edge: $\phi_i=0.5$')
    text(ax, .5, 1.39, r'Outside: $\phi_i\approx 0$')
    subheading(ax, 1.10, 'Tissue-density field')
    density = density_field(x, y)
    ax.contourf(x+.5, y+.70, density, levels=np.linspace(0,density.max(),15), cmap=cmap)
    ax.scatter(SAMPLE_POSITIONS[:,0]+.5, SAMPLE_POSITIONS[:,1]+.70,
               s=MARKER_PT['point']**2, c=INK, zorder=8)
    text(ax, .5, .27, r'$\rho(\mathbf x)=\sum_i K_h(\mathbf x-\mathbf x_i)$')
    text(ax, .5, .08, r'Dots: cells; $\int K_h\,\mathrm d^2x=1$', role='small')


def chemical_field(x, y):
    """Dimensionless analytic concentration, increasing toward the upper right."""
    return np.exp(.9*x + .6*y)


def chemical_gradient(x, y):
    return chemical_field(x, y)*np.array([.9,.6])


def coupled_panel(ax, color):
    subheading(ax, 2.39, 'Cells + chemical field')
    x,y = np.meshgrid(np.linspace(.06,.94,80),np.linspace(1.57,2.18,60))
    c = chemical_field(x,y)
    cmap = LinearSegmentedColormap.from_list('chemical', ['#ffffff',tint(color,.12),tint(color,.50)])
    ax.contourf(x,y,c,levels=16,cmap=cmap)
    ax.contour(x,y,c,levels=7,colors=[tint(color,.6)],linewidths=LINE_PT['context'])
    point = np.array([.32,1.79])
    cell(ax, point, color=color)
    grad = chemical_gradient(*point)
    arrow(ax, point, point+.30*grad/np.linalg.norm(grad), color=color)
    text(ax, .76, 1.95, r'$\nabla c$')
    text(ax, .5, 1.42, 'Cell senses local gradient')
    text(ax, .5, 1.26, 'Arrow: gradient direction\n'+r'Contours: constant $c$', role='small')
    subheading(ax, 1.00, 'Cells + fiber network')
    fibers = [((.08,.40),(.89,.77)), ((.11,.81),(.84,.31)),
              ((.08,.59),(.91,.60)), ((.40,.31),(.65,.84))]
    for start,end in fibers:
        ax.plot([start[0],end[0]],[start[1],end[1]],color=MUTED,lw=LINE_PT['structure'])
    cell(ax, (.32,.63), radius=.11,color=color)
    # Dashed link denotes a model dependency, deliberately not a mechanical force.
    arrow(ax, (.44,.66),(.78,.60),color=color,dashed=True)
    text(ax, .5, .13, 'Possible coupling\nDashed link: dependency, not force')


def build_figure(figure_size=PAPER_SIZE_IN):
    fig=plt.figure(figsize=figure_size)
    titles=['Particle\ndynamics', 'Cell states\nand rules', 'Lattice\nrepresentations',
            'Continuous\nfields', 'Cell--environment\ncoupling']
    functions=[particle_panel,rule_panel,lattice_panel,field_panel,coupled_panel]
    for i,(title,color,draw) in enumerate(zip(titles,ACCENTS,functions)):
        ax=fig.add_axes([.026+i*.194,.195,.18,.69])
        ax.set(xlim=(0,1),ylim=(0,2.85),aspect='equal')
        ax.axis('off')
        text(ax,.02,2.72,chr(65+i),role='panel',weight='bold',ha='left')
        text(ax,.20,2.72,title,role='title',weight='bold',ha='left')
        ax.plot([.02,.98],[2.51,2.51],color=color,lw=LINE_PT['emphasis'])
        draw(ax,color)
    fig.text(.035,.959,'Modeling choices for collective cell dynamics',
             fontsize=14,weight='bold',va='top')
    fig.text(.035,.919,'Complementary choices of variables, representation and coupling; not mutually exclusive model classes.',
             fontsize=FONT_PT['title'],color=MUTED,va='top')
    fig.text(.035,.155,'Define for the scientific question',fontsize=FONT_PT['title'],weight='bold')
    for x,heading,detail in [(.035,'Retained variables','Positions, shapes, internal states, fields'),
                             (.366,'Spatial detail','Subcellular, cell or tissue description'),
                             (.697,'Coarse-graining','Which degrees of freedom are averaged out?')]:
        fig.text(x,.114,heading,fontsize=FONT_PT['body'],weight='bold')
        fig.text(x,.085,detail,fontsize=FONT_PT['body'],color=MUTED)
    fig.text(.035,.029,'Illustrative geometry and prescribed analytic fields; not to scale, not simulation results. No panel ordering by resolution.',
             fontsize=FONT_PT['small'],color=MUTED)
    return fig


def export_figure(figure, output_directory, basename):
    artifacts=save_vector_pair(figure,output_directory,basename,
                              common_options={'bbox_inches':'tight','pad_inches':.08})
    plt.close(figure)
    return artifacts


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=Path('outputs'))
    args=parser.parse_args()
    export_figure(build_figure(),args.output_dir,OUTPUT_BASENAME)


if __name__=='__main__':
    main()
