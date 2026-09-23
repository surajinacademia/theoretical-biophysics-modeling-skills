"""Numerical geometry adapted from Chen Liu's figures4papers VIGIL concept.

Source: https://github.com/ChenLiu-1996/figures4papers/blob/
3c181f85e82c6f24948fcaaf3be6696102b41d8d/figure_VIGIL/plot_concept.py
License: Creative Commons Attribution-NonCommercial 4.0 International
https://creativecommons.org/licenses/by-nc/4.0/ (see accompanying LICENSE).
Adaptation: plotting and filesystem operations removed; original constants,
seeded random draw order, and numerical calculations retained in a pure
geometry function for a local restyling demonstration. No endorsement implied.
"""

import numpy as np
from scipy.stats import gaussian_kde
from scipy.interpolate import CubicSpline


def _gauss(x, mu, sig):
    y = np.exp(-0.5 * ((x - mu) / sig) ** 2)
    return y / (y.max() + 1e-12)


def _sample_tube(center_curve, t_samples, rng, sigma_u=0.08, sigma_v=0.18):
    pts = center_curve(t_samples)
    eps = 1e-3
    pts_f = center_curve(np.clip(t_samples + eps, 0, 1))
    tan = pts_f - pts
    tan_norm = np.linalg.norm(tan, axis=1, keepdims=True) + 1e-9
    t_hat = tan / tan_norm
    n_hat = np.stack([-t_hat[:, 1], t_hat[:, 0]], axis=1)
    u = rng.normal(0, sigma_u, size=(len(t_samples), 1))
    v = rng.normal(0, sigma_v, size=(len(t_samples), 1))
    return pts + u * n_hat + v * t_hat


def _mixture_t(n, centers, scales, weights, rng):
    weights = np.array(weights, dtype=float)
    weights /= weights.sum()
    comp = rng.choice(len(centers), size=n, p=weights)
    t = rng.normal(np.array(centers)[comp], np.array(scales)[comp])
    return np.clip(t, 0, 1)


def _kde_prepare(P, grid=280, pad_x=1.8, pad_y=1.3):
    Xv, Yv = P[:, 0], P[:, 1]
    kde = gaussian_kde(np.vstack([Xv, Yv]))
    xmin, xmax = Xv.min() - pad_x, Xv.max() + pad_x
    ymin, ymax = Yv.min() - pad_y, Yv.max() + pad_y
    xx, yy = np.mgrid[xmin:xmax:complex(grid), ymin:ymax:complex(grid)]
    zz = kde(np.vstack([xx.ravel(), yy.ravel()])).reshape(xx.shape)
    return xx, yy, zz, xmin, xmax, ymin, ymax


def make_geometry():
    """Return upstream distribution/manifold arrays and annotation anchors."""
    x = np.linspace(0.0, 1, 1000)
    p_prior = _gauss(x, 0.30, 0.07)
    p_see = _gauss(x, 0.72, 0.07)
    p_blind = 0.30 * _gauss(x, 0.30, 0.12) + 0.22
    y_star = 0.72
    see_star = np.interp(y_star, x, p_see)
    blind_star = np.interp(y_star, x, p_blind)

    rng = np.random.default_rng(42)
    xp = np.array([0.0, 0.18, 0.45, 0.72, 1.0])
    yt = np.array([0.15, 0.28, 0.18, 0.05, 0.10])
    ym = np.array([0.78, 0.70, 0.60, 0.68, 0.80])
    cs_t = CubicSpline(xp, yt, bc_type="natural")
    cs_m = CubicSpline(xp, ym, bc_type="natural")

    def curve_text(t):
        x = t
        y = cs_t(x) + 0.03 * np.sin(6 * np.pi * t)
        return np.stack([x, y], axis=1)

    def curve_mm(t):
        x = t
        y = cs_m(x) + 0.02 * np.sin(4 * np.pi * t + 0.6)
        return np.stack([x, y], axis=1)

    N = 2600
    t_text = _mixture_t(N, [0.20, 0.55, 0.82], [0.07, 0.09, 0.06], [0.35, 0.40, 0.25], rng)
    t_mm = _mixture_t(N, [0.18, 0.52, 0.80], [0.06, 0.10, 0.07], [0.30, 0.45, 0.25], rng)
    pts_text = _sample_tube(curve_text, t_text, rng, sigma_u=0.09, sigma_v=0.14)
    pts_mm = _sample_tube(curve_mm, t_mm, rng, sigma_u=0.08, sigma_v=0.13)
    A = np.array([[10.0, 0.0], [0.0, 3.5]])
    b_text = np.array([0.6, 0.9])
    b_mm = np.array([0.6, 2.4])
    P_t = pts_text @ A.T + b_text
    P_m = pts_mm @ A.T + b_mm
    tt = np.linspace(0.08, 0.95, 450)
    ridge_t = curve_text(tt) @ A.T + b_text
    ridge_m = curve_mm(tt) @ A.T + b_mm
    t_mid = 0.42
    idx_mid = np.searchsorted(tt, t_mid)
    u = np.linspace(0, 1, idx_mid)
    smooth = 3 * u**2 - 2 * u**3
    x_mix = (1 - smooth) * ridge_t[:idx_mid, 0] + smooth * ridge_m[:idx_mid, 0]
    y_mix = (1 - smooth) * ridge_t[:idx_mid, 1] + smooth * ridge_m[:idx_mid, 1] + 0.10 * np.sin(np.pi * u)
    x_ours = np.concatenate([x_mix, ridge_m[idx_mid:, 0]])
    y_ours = np.concatenate([y_mix, ridge_m[idx_mid:, 1]])
    star_inds = np.linspace(0, len(tt) - 1, 10, dtype=int)
    S_t = ridge_t[star_inds]
    star_inds_ours = np.linspace(0, len(x_ours) - 1, 10, dtype=int)
    S_m = np.column_stack([x_ours[star_inds_ours], y_ours[star_inds_ours]])
    xx_m, yy_m, zz_m, xmin_m, xmax_m, ymin_m, ymax_m = _kde_prepare(P_m)
    xx_t, yy_t, zz_t, xmin_t, xmax_t, ymin_t, ymax_t = _kde_prepare(P_t)
    xmin = min(xmin_m, xmin_t) - 0.6
    xmax = max(xmax_m, xmax_t) + 0.6
    ymin = min(ymin_m, ymin_t) - 0.4
    ymax = max(ymax_m, ymax_t) + 0.8
    levels_m = np.quantile(zz_m, np.linspace(0.72, 0.99, 10))
    levels_t = np.quantile(zz_t, np.linspace(0.72, 0.99, 10))
    x0, y0 = xmin + 2.1, (ymin + ymax) / 2 - 0.2
    t0 = 0.12
    z_t0 = (curve_text(np.array([t0])) @ A.T + b_text)[0]
    z_m0 = (curve_mm(np.array([t0])) @ A.T + b_mm)[0]
    idx_dpo = np.argmin(np.abs(ridge_t[:, 0]))
    xy_dpo = ridge_t[idx_dpo] + np.array([2, -0.2])
    idx_ours = np.argmin(np.abs(x_ours - 4))
    xy_ours = np.array([x_ours[idx_ours], y_ours[idx_ours]]) + np.array([0.8, 0.5])
    names = (
        "x p_prior p_blind p_see y_star see_star blind_star "
        "P_t P_m ridge_t ridge_m x_ours y_ours S_t S_m "
        "xx_m yy_m zz_m levels_m xx_t yy_t zz_t levels_t "
        "xmin xmax ymin ymax x0 y0 z_t0 z_m0 xy_dpo xy_ours"
    ).split()
    values = locals()
    return {name: values[name] for name in names}
