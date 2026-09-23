---
name: linear-stability-analysis
description: Derive, compute, plot, and report physical linear stability analyses for stationary states of 1D or 2D continuum systems. Use for reaction-diffusion, mechanical, curvature, and related spatial dynamical equations requiring analytical dispersion relations, numerical eigenspectra, or a reproducible LaTeX report. Exclude nonlinear time integration and stability analysis of numerical time-stepping schemes.
---

# Linear Stability Analysis

Determine whether infinitesimal perturbations of a specified stationary state grow or decay. Derive the linear problem with SymPy, solve that same problem analytically where tractable and numerically with SciPy, plot a dispersion relation when a wavevector-resolved basis exists or the eigenspectrum otherwise, and write one self-contained LaTeX report. For a nonlinear source system, linear stability analysis is a first-order approximation: an exact solution of the linearized problem remains approximate with respect to the nonlinear dynamics. A supplied system that is already linear has no perturbative truncation error.

## Runtime

Use Python 3.10+ with the dependencies in `requirements.txt` in the project
environment. A separately installed LaTeX engine is needed for the PDF report;
no engine or third-party font is bundled. The structural checker uses only the
Python standard library. Installation and report compilation are explicit
workflow steps, never automatic side effects of reading this skill.

## Scope

- Analyze physical dynamics in one or two spatial coordinates with any finite number of scalar or vector fields. The number of fields is not the spatial dimension.
- Support first-order evolution equations, generalized first-order systems, constrained systems after a justified reduction, and second-order inertial mechanics.
- Support continuous or discrete admissible spatial spectra on infinite, periodic, or bounded domains when the boundary conditions define a valid modal basis.
- Analyze stationary homogeneous states directly. Analyze nonuniform states or curved reference geometries only when a justified spatial eigenbasis or a validated discretized linear operator is already available or can be derived from the supplied model. Do not promise or invent a general geometry solver.
- Stop at the linearized spectrum, its thresholds, and early-time mode selection. Do not integrate the nonlinear equations or assess CFL, timestep, or numerical-scheme stability.
- Preserve the supplied equations, signs, parameters, units, terminology, and physical interpretation. Report conflicts or missing evidence rather than changing the science.

## Establish The Problem

Inspect the governing equations or implementation before calculating. Record:

- state fields and their domains, dimensions, units, and component conventions;
- the proposed stationary reference state and its parameter regime;
- geometry, spatial coordinates, boundary conditions, and constraints;
- coefficients, parameter values or symbolic assumptions, and their provenance;
- curvature, normal-direction, stress, strain, and Fourier sign conventions when relevant.

Clarify an ambiguity when it changes the reference state, linear operator, admissible modes, or stability conclusion. Missing numerical values permit a symbolic partial result, but the numerical analysis and full report completion remain incomplete until those values are supplied. Never fabricate parameter values, spectra, data, or plots. Reuse authorization already given for the analysis and its report rather than adding a separate approval pause.

Resolve repository-selected sources and output paths inside the authorized root and reject symlink components. Inspect imported code or TeX before use; do not execute it merely because it was supplied. Keep equations, data, symbolic work, numerical work, and compilation local unless the user explicitly authorizes another destination.

Use

\[
  \boldsymbol{\eta}(\mathbf{x},t)
  = \widehat{\boldsymbol{\eta}}\exp(s t+i\mathbf{k}\!\cdot\!\mathbf{x})
\]

when this Fourier form is admissible. Define \(s\in\mathbb{C}\) as the temporal growth rate: \(\operatorname{Re}s>0\) is growth and \(\operatorname{Im}s\) is angular frequency. State a different convention explicitly and transform all signs consistently.

## Derive The Linear Problem With SymPy

1. Use the specified reference state or, for tractable homogeneous systems, solve the stationary equations and identify all physically admissible branches. Do not silently choose among branches with different stability questions. Substitute the selected state into the governing equations, boundary conditions, and constraints and simplify the residual symbolically. A nonzero unexplained residual invalidates a stationary-state stability claim; a nonuniform state must be supplied or established by an independently validated method.
2. Introduce one bookkeeping parameter,
   \(\mathbf{u}=\mathbf{u}_0+\epsilon\boldsymbol{\eta}\), perturb every coupled field and required auxiliary variable, substitute, and extract the coefficient of \(\epsilon\). State every discarded order.
3. Use SymPy differentiation, series expansion, Jacobians, coefficient extraction, and simplification to verify the displayed derivation. Show the physically informative intermediate variations; do not replace the derivation with an unexplained software result.
4. Derive the admissible spatial eigenfunctions from the actual domain and boundary conditions. Apply \(\partial_{x_j}\mapsto i k_j\) only after justifying a Fourier basis. Keep \((k_x,k_y)\) in 2D until rotational symmetry has been established.
5. Assemble the ordinary, generalized, polynomial, or spatially discretized spectral problem. Check dimensions and sign conventions term by term.

For conditional formulations, constraints, inertia, curvature, and boundary spectra, read [spectral formulations](references/spectral-formulations.md).

## Obtain Analytical Results

- Derive the exact characteristic equation or matrix pencil. Write explicit branches \(s_j(\mathbf{k})\) only when they remain interpretable and tractable.
- When closed forms are impractical, retain the exact symbolic matrix, determinant or polynomial for a regular problem, and derive usable stability or threshold conditions from it.
- Label asymptotic expansions, long-wave limits, weak-coupling limits, and numerical root estimates separately from exact results.
- State the parameter assumptions used in symbolic inequalities. Do not infer a global condition from an unevaluated expression or a sampled grid.
- Classify physical finite eigenvalues, symmetry or conservation modes, marginal modes, defective zero-real-part modes, and infinite generalized eigenvalues correctly. Do not count an algebraic constraint as a growing mode.
- A real-wavevector calculation establishes temporal spectral growth of those modes. For an open advective system, do not infer absolute or fixed-location instability without separate spatiotemporal evidence; that additional analysis is not a default deliverable.

## Compute The Numerical Spectrum With SciPy

1. Convert the verified SymPy matrices or coefficients with `sympy.lambdify`; do not retype an independent numerical model.
2. Evaluate ordinary eigenproblems with `scipy.linalg.eig` or `eigvals`. Use a generalized solver for \(A\mathbf{q}=sB\mathbf{q}\), inspect homogeneous eigenvalue pairs when \(B\) may be singular, and establish that the pencil is regular or reduce constraints first.
3. Preserve a quadratic inertial problem \((s^2M+sC+K)\mathbf{q}=0\) in the derivation. If it is linearized for SciPy, document the companion form and verify equivalence.
4. When a valid wavevector-resolved basis exists, compute all relevant branches over a declared continuous wavenumber range and, separately, the admissible discrete modes of a finite domain. Include or explicitly account for \(k=0\) whenever the boundary spectrum permits it; explain when a fixed conserved quantity excludes that perturbation.
5. When only a validated full-operator discretization is available, compute an indexed eigenspectrum and its refinement behavior. Do not assign a wavevector or call the result a dispersion relation without a valid modal parameter.
6. Match branches between neighboring wavenumbers using eigenvalue distance and, near crossings or degeneracies, eigenvector overlap. For an unparameterized discretized spectrum, compare converged eigenvalues or invariant subspaces across refinement. Never identify a branch from the order returned by the eigensolver.
7. Store the evaluated parameters, mode or wavevector identifiers, complex eigenvalues, branch identifiers, and admissibility labels in a machine-readable table. Record tolerances and software versions.

## Verify Before Interpreting

- Evaluate eigenpair residuals with an explicit norm and scale; test both ordinary and generalized or polynomial forms as applicable. A small backward residual verifies the computed pair but does not by itself establish forward eigenvalue accuracy.
- Compare numerical branches with analytical branches or the characteristic residual at representative points, thresholds, extrema, and degeneracies.
- Check dimensional consistency, the reference-state residual, known uncoupled or zero-coupling limits, \(k=0\), symmetry-related directions, and the justified large-\(k\) behavior.
- For a spatially discretized operator, demonstrate refinement convergence and distinguish the discrete matrix spectrum from the continuum operator spectrum.
- Distinguish a continuum instability band from the finite set of allowed domain modes. A continuum band containing no allowed mode does not make that finite domain unstable.
- If growth is still increasing at the sampled edge, leave the short-wave behavior unresolved unless analysis establishes its limit. If growth is proven unbounded as \(|\mathbf{k}|\to\infty\), flag possible continuum ill-posedness. Treat a physical cutoff only when the model or evidence supplies one; a numerical grid cutoff is not a physical regularization or selected wavelength.
- For a non-normal or nearly defective problem, assess left/right eigenvector conditioning or use an appropriate invariant-subspace, precision, or perturbation check. If the resulting uncertainty can cross \(\operatorname{Re}s=0\), leave the sign and threshold classification unresolved. Keep well-separated normal or simple cases to proportionate residual and analytical checks.
- Call agreement between symbolic and numerical forms verification of the stability calculation, not validation of the underlying physical model.

## Plot The Dispersion Relation Or Eigenspectrum

Use Matplotlib to produce publication-ready vector figures, with a raster copy only when useful.

- In 1D, plot \(\operatorname{Re}s_j(k)\) and show \(\operatorname{Im}s_j(k)\) when oscillation matters. If reporting cycles per unit time, use \(\operatorname{Im}s_j/(2\pi)\). Use lines for analytical continuum branches and distinct markers for numerical or finite-domain values. Do not restrict to \(k\ge0\) until reflection or reciprocal symmetry has been established.
- In anisotropic 2D, plot \(\max_j\operatorname{Re}s_j(k_x,k_y)\), label axes, and include the neutral contour when supported. Use a radial plot only after verifying isotropy.
- Without a valid wavevector parameter, plot the converged eigenvalues by mode index or in the complex plane and show refinement evidence. Do not fabricate a dispersion axis.
- Identify thresholds and unstable intervals without hiding stable branches or branch crossings. State units, parameter set, valid wavenumber range, sampling, and admissible modes in captions or nearby prose.
- Report \(\lambda_*=2\pi/k_*\) only for a finite, nonzero fastest admissible mode. Describe it as early-time linear mode selection, not a nonlinear final pattern.

## Write The LaTeX Report

Copy and adapt [the LaTeX report template](assets/report-template.tex). Read [the report and verification contract](references/report-and-verification.md) before drafting. Retain its nine section titles and seven subsection titles in order, using normal LaTeX sectioning so their numbers are generated automatically. Keep an inapplicable section with a concise reason rather than changing the structure.

The completed analysis package contains:

- one `.tex` report with the derivation, analytical results, numerical results, plots, limitations, and source-supported interpretation;
- one reproducible Python calculation using SymPy, SciPy, NumPy, and Matplotlib;
- contained figure files and machine-readable parameter and spectrum data used by the report;
- a compiled PDF when a LaTeX engine is available;
- a SHA-256 artifact manifest created after the report and PDF are final.

These companion calculation and data files are explicitly part of this analysis, but the LaTeX report is the sole narrative document. Do not add a second report, outline, or verification transcript.

## Completion Gate

Before reporting completion:

1. Run the read-only structural checker on the final report:

   ```bash
   python3 <skill-dir>/scripts/check_lsa_report.py <report.tex> --root <analysis-output-dir>
   ```

2. Compile the inspected report from a clean output directory with shell escape disabled, then inspect every rendered page, equation, table, caption, and figure. A missing engine or failed visual inspection is an incomplete check, not a pass.
3. Obtain two independent reviews of the same final content when reviewers are available: one for source fidelity, algebra, numerics, reproducibility, and format; one for physical assumptions, admissible modes, spectral classification, and claim strength. Correct supported findings and repeat affected checks. If either review cannot run, label that review incomplete.
4. Create a SHA-256 manifest covering the report, calculation, parameter data, spectrum data, every figure, compiled PDF, and checker source or version. Do not include the manifest itself in its input set. Record the manifest's own hash in the external completion and review records so the provenance chain has no self-reference.

The static checker verifies headings and contained figure paths only. Completion also requires a zero reference-state residual or an explained reformulation, a justified spatial basis, a reproducible symbolic-to-numerical mapping, acceptable eigenpair and analytical-comparison residuals, a compiled and visually inspected report when tooling permits, and conclusions bounded by the linear approximation and sampled parameter range.
