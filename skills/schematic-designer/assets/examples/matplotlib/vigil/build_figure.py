"""Minimalist adaptation of Chen Liu's VIGIL concept figure.

Geometry adapted from figures4papers, commit
3c181f85e82c6f24948fcaaf3be6696102b41d8d, figure_VIGIL/plot_concept.py.
Original and adapted material: CC BY-NC 4.0. See ATTRIBUTION.md and LICENSE.
Changes: palette, typography, physical style roles, layout, native TikZ heads,
non-color line patterns, vector PDF/SVG export. Scientific construction retained.
"""
from pathlib import Path
import argparse
import sys
import json
import tempfile

SKILL_ROOT = Path(__file__).resolve().parents[4]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', type=Path, required=True)
args = parser.parse_args()
sys.path[:0] = [str(SKILL_ROOT/'assets/styles'), str(SKILL_ROOT/'scripts')]
from vector_output import prepare_output_directory, publish_bytes_atomic, save_figure_atomic
OUT = prepare_output_directory(args.output_dir)
# Generated inputs are never read back from the shared output directory.
with tempfile.TemporaryDirectory(prefix='vigil-build-') as private_directory:
    SOURCE = Path(private_directory).resolve()
    import minimalist_profile as style
    style.apply_style()
    from matplotlib import pyplot as plt
    import numpy as np
    from vigil_geometry import make_geometry

    g = make_geometry()
    C = style.palette()
    prior, blind, seen = C[0], C[2], C[4]
    # Dense-cloud detail needs smaller marks than isolated schematic entities.
    # These named figure roles are derived once; numerical point positions and
    # contour levels remain the upstream geometry.
    DETAIL = {'cloud_diameter': style.MARKER_PT['point'] / 3,
              'cloud_opacity': style.OPACITY['fill'],
              'contour_opacity': style.OPACITY['context'],
              'star_outline': style.LINE_PT['context'] / 2}
    BLIND_DASH = (style.DASH_PT['dashed'][0], style.DASH_PT['dotted'][1],
                  *style.DASH_PT['dotted'])
    BLIND_TIKZ_DASH = 'dash pattern=' + ' '.join(
        f'{"on" if i % 2 == 0 else "off"} {length:g}bp'
        for i, length in enumerate(BLIND_DASH))
    W, H = 8.5, 3.15
    fig = plt.figure(figsize=(W,H))
    left = fig.add_axes([.074,.215,.36,.58])
    right = fig.add_axes([.526,.185,.399,.655])

    for arr,color,pattern,role in [
        (g['p_prior'],prior,'--','structure'),
        (g['p_blind'],blind,(0,BLIND_DASH),'structure'),
        (g['p_see'],seen,'-','emphasis')]:
        left.fill_between(g['x'],0,arr,color=color,alpha=style.OPACITY['fill'],linewidth=0)
        left.plot(g['x'],arr,color=color,ls=pattern,lw=style.LINE_PT[role])
    left.plot([g['y_star']]*2,[0,g['see_star']],color=C[5],ls=':',lw=style.LINE_PT['context'],alpha=style.OPACITY['context'])
    left.set(xlim=(0,1.05),ylim=(0,1.10),xticks=[0,.5,1],xticklabels=['$-1$','$0$','$1$'],yticks=np.arange(0,1.01,.2))
    left.set_yticklabels([f'${v:.1f}$' for v in np.arange(0,1.01,.2)])
    left.set_xlabel('Answer space (arbitrary units)',labelpad=6)
    left.set_ylabel('Probability',labelpad=7)
    left.spines[['top','right']].set_visible(False)
    left.tick_params(axis='both',labelsize=style.FONT_PT['small'],width=style.LINE_PT['context'],length=2.5,pad=3)

    # Preserve every sampled cloud point and all original contour thresholds.
    for suffix,color,contour in [('m',C[3],seen),('t',C[1],prior)]:
        P=g['P_'+suffix]
        right.scatter(P[:,0],P[:,1],s=DETAIL['cloud_diameter']**2,alpha=DETAIL['cloud_opacity'],c=color,linewidths=0,zorder=1)
        right.contour(g['xx_'+suffix],g['yy_'+suffix],g['zz_'+suffix],levels=g['levels_'+suffix],colors=contour,linewidths=style.LINE_PT['context'],alpha=DETAIL['contour_opacity'],zorder=2)
    right.plot(g['ridge_t'][:,0],g['ridge_t'][:,1],color=prior,ls='--',lw=style.LINE_PT['structure'],zorder=3)
    right.plot(g['x_ours'],g['y_ours'],color=seen,lw=style.LINE_PT['emphasis'],zorder=3)
    for key in ('S_t','S_m'):
        p=g[key]
        right.scatter(p[:,0],p[:,1],marker='*',s=style.MARKER_PT['emphasis']**2,c=C[2],edgecolors=C[5],linewidths=DETAIL['star_outline'],zorder=5)
    right.plot([g['x0']]*2,[g['z_t0'][1],g['z_m0'][1]],color=C[5],ls='--',lw=style.LINE_PT['context'],alpha=style.OPACITY['context'],zorder=3)
    for y,color in [(g['y0'],style.INK),(g['z_t0'][1],prior),(g['z_m0'][1],seen)]:
        right.plot(g['x0'],y,'o',ms=style.MARKER_PT['point'],color=color,mew=0,zorder=6)
    right.set(xlim=(g['xmin'],g['xmax']),ylim=(g['ymin'],g['ymax']))
    right.axis('off')
    save_figure_atomic(fig, SOURCE, 'panels.pdf')

    # Convert data positions through the actual fixed axes transforms; no manual
    # remapping of the VIG endpoints or scientific trajectories.
    def xy(ax,x,y):
        p=ax.transData.transform((x,y))/fig.dpi*72
        return '('+','.join(f'{v:.5f}' for v in p)+')'
    def pos(x,y): return f'({x:.3f},{y:.3f})'
    lines=[r'\documentclass[tikz,border=0bp]{standalone}',r'\usepackage{graphicx}',r'\usepackage{minimalist-profile}',r'\begin{document}',r'\begin{tikzpicture}[ms base,x=1bp,y=1bp]',f'\\path[use as bounding box] (0,0) rectangle ({W*72},{H*72});',r'\node[anchor=south west,inner sep=0bp,outer sep=0bp] at (0,0) {\includegraphics{panels.pdf}};']
    def text(x,y,label,opts=''):
        lines.append(r'\node[ms body,anchor=west,inner sep=0bp'+(','+opts if opts else '')+'] at '+pos(x,y)+' {'+label+'};')
    def datatext(x,y,label,opts=''):
        p=right.transData.transform((x,y))/fig.dpi*72
        text(*p,label,opts)
    # Sparse hierarchy and a single, aligned legend row.
    text(13,215,r'A',r'ms panel')
    text(28,215,'Answer distributions',r'ms title')
    text(308,215,r'B',r'ms panel')
    text(324,215,'Multimodal grounding',r'ms title')
    for x,color,label,pattern in [
        (44,'msColor1',r'$P(y\mid x_t)$','ms dashed'),
        (119,'msColor3',r'$P(y\mid x_v^{\emptyset},x_t)$',BLIND_TIKZ_DASH),
        (215,'msColor5',r'$P(y\mid x_v,x_t)$','ms solid')]:
        lines.append(r'\draw[ms structure,color='+color+','+pattern+'] '+pos(x,195)+' -- '+pos(x+12,195)+';')
        text(x+16,195,label,r'ms small,text='+(color if color!='msColor3' else 'msInk'))
    lines.append(r'\draw[ms structure,color=msColor6,<->] '+xy(left,g['y_star'],g['blind_star'])+' -- '+xy(left,g['y_star'],g['see_star'])+';')
    p=left.transData.transform((g['y_star']+.11,(g['blind_star']+g['see_star'])/2))/fig.dpi*72
    text(*p,'VIG',r'ms body,text=msColor6')
    # Same scientific labels as the source, with opaque backgrounds on callouts.
    datatext(g['xmin']+.9,g['ymax']+.15,r'Multimodal manifold $\mathcal{M}_{\mathrm{mm}}$',r'ms body,text=msColor5,anchor=south west')
    datatext(g['xmin']+.9,g['ymin']-.2,r'Textual manifold $\mathcal{M}_{\mathrm t}$',r'ms body,text=msColor1,anchor=north west')
    datatext(g['x0']-2,g['z_m0'][1]+1.2,r'$z_{\mathrm{mm}}=f_{\mathrm{mm}}(x_v,x_t)$',r'ms small,anchor=south west,fill=white,inner sep=1bp')
    datatext(g['x0']-2,g['z_t0'][1]-.8,r'$z_{\mathrm t}=f_{\mathrm t}(x_t)$',r'ms small,anchor=north west,fill=white,inner sep=1bp')
    datatext(g['x0']-2,g['y0']+.4,r'sample $x=(x_v,x_t)$',r'ms small,fill=white,inner sep=1bp')
    for node,label,start,end,color in [
        ('ours',r'Ours: enter $\mathcal{M}_{\mathrm{mm}}$',(4,g['ymax']-1.3),g['xy_ours'],'msColor5'),
        ('dpo','Standard DPO shortcut',(4,g['ymin']+.8),g['xy_dpo'],'msColor1')]:
        lines.append(r'\node[ms small,anchor=west,text='+color+r',inner sep=2bp,fill=white] ('+node+') at '+xy(right,*start)+' {'+label+'};')
        lines.append(r'\draw[ms arrow,color='+color+'] ('+node+('.south west)' if node=='ours' else '.north west)')+' -- '+xy(right,*end)+';')
    for curve,offset,label,color in [('ridge_m',4.2,'grounded','msColor5'),('ridge_t',4.2,'prior-dominated','msColor1')]:
        datatext(g[curve][-1,0]+offset,g[curve][-1,1],label,r'ms small,text='+color+r',fill=white,inner sep=1bp')
    text(13,8,'Illustrative probability profiles and synthetic manifolds.',r'ms small,text=msMuted')
    lines += [r'\end{tikzpicture}',r'\end{document}']
    (SOURCE/'vigil-minimalist.tex').write_text('\n'.join(lines)+'\n')
    (SOURCE/'minimalist-profile.sty').write_text(style.tikz_style())
    (SOURCE/'geometry-check.json').write_text(json.dumps({'seed':42,'cloud_points_each':len(g['P_m']),'trajectory_points':len(g['x_ours']),'stars_each':len(g['S_m']),'vig_gap':float(g['see_star']-g['blind_star']),'bounds':[float(g[k]) for k in ('xmin','xmax','ymin','ymax')],'width_inches':W,'height_inches':H},indent=2)+'\n')
    plt.close(fig)
    print(OUT)

    # Compile only this newly generated compositor and its declared inputs.
    import subprocess
    subprocess.run([sys.executable, str(SKILL_ROOT/'scripts/render_tikz.py'),
                    str(SOURCE/'vigil-minimalist.tex'),
                    '--include', str(SOURCE/'minimalist-profile.sty'),
                    '--include', str(SOURCE/'panels.pdf'), '--output-dir', str(OUT),
                    '--basename', 'vigil-minimalist', '--engine', 'lualatex'], check=True)

    # Retain the exact private inputs only after successful compilation.
    retained = prepare_output_directory(OUT/'source')
    for name in ('panels.pdf', 'vigil-minimalist.tex', 'minimalist-profile.sty', 'geometry-check.json'):
        publish_bytes_atomic((SOURCE/name).read_bytes(), retained, name)
