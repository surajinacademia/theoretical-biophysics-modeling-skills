# Report And Verification Contract

Read this reference before drafting or revising a linear-stability report. The report follows the model-documentation narrative discipline but is self-contained: do not invoke another skill at runtime. Results, plots, calculation code, and data are authorized parts of this specialized analysis.

## Contents

- [Fixed LaTeX structure](#fixed-latex-structure)
- [Section content](#section-content)
- [Artifact and figure contract](#artifact-and-figure-contract)
- [Writing discipline](#writing-discipline)
- [Verification and review](#verification-and-review)

## Fixed LaTeX Structure

Use normal, unstarred LaTeX section commands so numbering is generated automatically. Preserve these title arguments and their order:

```latex
\section{Model Purpose And Questions}
\section{Physical Picture And Assumptions}
\section{Entities, Domain, And Notation}
\section{Parameters And Scales}
\section{Governing Equations}
\section{Initial And Boundary Conditions}
\section{Observables And Model Tests}
\section{Solution Method}
\subsection{Methodology And Rationale}
\subsection{Numerical Formulation}
\subsection{Algorithm And Flowchart}
\subsection{Accuracy And Verification}
\section{Model Record And Implementation}
\subsection{Implementation Mapping}
\subsection{Method Decisions And Changes}
\subsection{References}
```

Do not rename, reorder, merge, omit, or add section or subsection headings. Use concise paragraphs, equations, tables, and bold run-in labels for model-specific organization. Keep an inapplicable section and explain why it is inapplicable.

Place the scientific model name and “Linear Stability Analysis” in the title. Directly below the title, identify the governing-equation source, analysis code, parameter-data file, and spectrum-data file. Use contained relative paths when the artifacts are local; never invent a file or claim an uninspected source.

## Section Content

**1. Model Purpose And Questions.** State the phenomenon, reference state, stability question, model status, and observable criterion. State what an instability would predict and what linear analysis cannot establish.

**2. Physical Picture And Assumptions.** Explain the competing stabilizing and destabilizing mechanisms in words before equations. Give the small-perturbation, stationary-state, geometry, constitutive, and scale-separation assumptions with evidence or labeled modeling rationale and a limitation for each.

**3. Entities, Domain, And Notation.** Define every field, index, coordinate, domain, vector orientation, geometric convention, and dimensional status before use. Distinguish two spatial dimensions from two dependent fields. Define \(s\), \(\mathbf{k}\), and branch labels here or immediately before their first local use.

**4. Parameters And Scales.** Record symbol, numerical code name, meaning, units, value, admissible range, and provenance. Separate physical parameters from wavenumber sampling, solver tolerances, and other numerical controls. Define nondimensional groups and validity ranges before interpreting them. Missing numerical values permit a symbolic partial result, but the numerical analysis and full report remain incomplete until they are supplied; never fabricate values, data, or plots.

**5. Governing Equations.** Present the original governing equations and verify the reference-state residual. Show the perturbation substitution, collect first-order terms, and display the complete linearized equations before the modal reduction. Then derive the spectral matrix or polynomial, its analytical dispersion relation when a valid wavevector basis exists, or the full-operator eigenproblem otherwise. Mark exact, asymptotic, and numerical results distinctly.

**6. Initial And Boundary Conditions.** State the boundary conditions used by the original and perturbed fields. Derive the admissible spatial eigenfunctions and continuous or discrete wavenumbers. Explain how constraints, gauge conditions, and excluded modes are handled. The initial perturbation amplitude affects the validity of the linear approximation but not the eigenvalues.

**7. Observables And Model Tests.** With a valid wavevector basis, present analytical and numerical dispersion results, instability thresholds, unstable bands or allowed unstable modes, and a 2D growth map when anisotropy requires it. Without one, present a refinement-supported indexed or complex-plane eigenspectrum and do not invent a dispersion relation. Include the appropriate spectral figure, compare like quantities, and interpret only supported early-time consequences. State whether the fastest admissible mode is finite and nonzero before reporting a wavelength. Qualify uncertain signs or thresholds in non-normal or nearly defective cases. Treat unresolved edge growth as unresolved; proven unbounded high-wavenumber growth can indicate continuum ill-posedness, and a numerical grid cutoff is not a physical cutoff.

**8. Solution Method.** Keep the four required subsections distinct.

- **Methodology And Rationale:** explain why the chosen symbolic linearization, spatial basis, and eigensolver match the equations and question.
- **Numerical Formulation:** define the evaluated matrix or pencil, either the valid wavenumber grid and finite modes or the full-operator discretization and refinements, branch or subspace matching, tolerances, scaling, and data schema. Explain any constraint projection or companion linearization.
- **Algorithm And Flowchart:** give mathematical pseudocode for input validation, base-state check, symbolic construction, lambdification, the applicable modal sweep or refined eigensolution, matching, residual tests, storage, and plotting. A compact in-report TikZ flowchart is optional only when it adds information; do not create a separate narrative diagram.
- **Accuracy And Verification:** report performed residual, analytical-comparison, limiting-case, resolution or refinement, conditioning, and threshold checks. A small backward residual does not establish eigenvalue accuracy; use proportionate conditioning or subspace checks for non-normal or nearly defective cases and leave classifications unresolved when uncertainty crosses zero. Distinguish performed evidence from proposed checks.

**9. Model Record And Implementation.** Keep the three required subsections distinct.

- **Implementation Mapping:** map equations and report quantities to the governing source, SymPy expressions, SciPy calculation, parameter input, spectrum columns, and figure files. Record runtime and package versions. When version control is available, record revision and dirty state; hash each dirty or untracked inspected source relevant to the analysis. Identify the SHA-256 artifact manifest described below.
- **Method Decisions And Changes:** record consequential analytical or numerical choices, their rationale, and evidence or status. Do not turn this into an edit log.
- **References:** list only sources actually used, with stable identifiers, and cite them where they support assumptions, equations, parameter values, or numerical methods.

## Artifact And Figure Contract

The analysis output root should contain the report, calculation, inputs, computed spectrum, and figures it references. A typical layout is:

```text
analysis-output/
|-- stability-report.tex
|-- stability-report.pdf
|-- linear_stability.py
|-- parameters.json
|-- spectrum.csv
|-- artifact-manifest.sha256
`-- figures/
    |-- dispersion_relation.pdf
    `-- dispersion_relation.png
```

Use different names when the model already has a convention, and record the actual paths in Section 9.1. Keep all local report dependencies inside the analysis-output root as regular files without symlink components. Include the required Section 7 spectral figure through a direct `\includegraphics` path. The bundled template's conditional missing-figure block is an authoring aid only. A completed report must replace that entire conditional block with one unconditional direct `\includegraphics` command referencing the contained generated dispersion or eigenspectrum figure.

The computation must serialize enough information to reproduce each plotted point: parameter set, spatial mode or wavevector when defined, branch or refinement identity, real and imaginary parts of \(s\), admissibility, and any eigenpair-residual or analytical-comparison metric used in the report. Prefer a tidy CSV for the spectrum and JSON or another explicit text format for parameters and metadata. Do not embed unverifiable hand-entered plot values in the LaTeX source.

Every figure must have readable axis labels with symbols and units or explicit nondimensional status, a legend or direct labels, and a caption that states the parameter set, spectral representation, analytical versus numerical encodings when both exist, and stability convention. Avoid decorative interpolation in 2D maps that implies resolution the calculation did not provide.

After the report and PDF are final, create a SHA-256 manifest for the `.tex` report, calculation, parameters, spectrum, every figure, compiled PDF, and checker source or version. Do not include the manifest itself among the hashed inputs. Compute the manifest's own SHA-256 separately; completion and review records outside the manifest reference that hash so the record is bound without a self-reference.

## Writing Discipline

Write a compact scientific argument in the order needed to assess it: physical question, assumptions, defined quantities, original model, linearization, modal basis, analytical prediction, numerical calculation, verification, interpretation, and limitations. Explain why each mathematical operation is valid for the stated model. Keep symbols, signs, units, and branch names consistent across equations, code, data, figures, and prose.

Distinguish:

- inspected equations and parameter values from author assumptions;
- exact results for the linearized problem from asymptotic or numerical approximations;
- the first-order approximation to nonlinear dynamics from numerical error in solving the linearized problem;
- calculation verification from physical or experimental validation;
- continuous dispersion curves from finite-domain admissible modes;
- wavevector-resolved dispersion relations from full-operator eigenspectra without a valid wavevector label;
- early-time mode selection from nonlinear saturation or final morphology.

Real-wavevector growth is a temporal spectral conclusion. For open advective systems, do not call it absolute or fixed-location instability without separate supporting analysis, and do not add that analysis by default.

Do not invent evidence, citations, parameter provenance, convergence results, or thresholds. A sampled spectrum supports statements only over its documented parameter and wavenumber range.

## Verification And Review

Run the static checker on the final `.tex` file and analysis root. It checks the fixed heading order and local figure-path structure; it does not verify mathematics or scientific claims.

Inspect the report source before compilation and compile locally from a clean output directory with shell escape disabled. Do not execute imported TeX or analysis code merely because it was supplied. Treat missing references, overfull content that obscures meaning, absent figures, and compile errors as defects. Render and inspect every page at readable resolution. Confirm equations, tables, legends, colors, captions, and mathematical glyphs are visible and consistent with the data.

The calculation review must trace at least one plotted spectral point from the displayed symbolic matrix through `lambdify`, the SciPy eigenpair, the stored spectrum row, the plotted mark, and the prose conclusion. It must also inspect the reference-state residual, admissible-mode derivation or full-operator discretization, pencil regularity or constraint reduction, analytical comparison when available, branch or subspace matching, conditioning where material, and declared limits.

Use a distinct scientific review to challenge physical assumptions, geometry and curvature conventions, boundary compatibility, neutral-mode interpretation, instability classification, short-wave behavior, and claim strength. Reviewers should inspect the final artifacts independently. Bind the checker, compilation, visual inspection, data trace, and reviews to the external hash of the final artifact manifest, and record any incomplete capability honestly in the completion message rather than declaring a pass.
