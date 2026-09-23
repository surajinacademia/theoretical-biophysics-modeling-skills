# Spectral Formulations

Use this reference when the ordinary Fourier eigenproblem \(A(k)\mathbf{q}=s\mathbf{q}\) is insufficient, or when boundary conditions, constraints, inertia, anisotropy, higher derivatives, or geometry determine the spectrum.

## Contents

- [Common linear form](#common-linear-form)
- [Boundary conditions and admissible modes](#boundary-conditions-and-admissible-modes)
- [Constraints and generalized pencils](#constraints-and-generalized-pencils)
- [Inertial mechanics](#inertial-mechanics)
- [Curvature and higher spatial derivatives](#curvature-and-higher-spatial-derivatives)
- [Classification and thresholds](#classification-and-thresholds)
- [Numerical branches and residuals](#numerical-branches-and-residuals)
- [Sources for specialized methods](#sources-for-specialized-methods)

## Common Linear Form

After verifying a stationary state \(\mathbf{u}_0\), write the perturbation as

\[
\mathbf{u}(\mathbf{x},t)=\mathbf{u}_0(\mathbf{x})+
\epsilon\boldsymbol{\eta}(\mathbf{x},t),\qquad 0<\epsilon\ll1.
\]

For a valid spatial mode with amplitude \(\mathbf{q}\), a first-order system commonly reduces to

\[
B(\mathbf{k})\,\dot{\mathbf{q}}=A(\mathbf{k})\mathbf{q},
\qquad
\bigl[A(\mathbf{k})-sB(\mathbf{k})\bigr]\mathbf{q}=0.
\]

This is an ordinary eigenproblem only when \(B=I\), or after a justified nonsingular transformation. Use \(\det[A-sB]=0\) only for a square regular pencil: the determinant must not vanish identically as a function of \(s\).

For a homogeneous reaction--diffusion system

\[
\partial_t\mathbf{u}=\mathbf{f}(\mathbf{u})+
\sum_{a,b=1}^{d}D^{ab}\partial_a\partial_b\mathbf{u}
+\sum_{a=1}^{d}V^a\partial_a\mathbf{u},
\]

the stated \(\exp(s t+i\mathbf{k}\cdot\mathbf{x})\) convention gives

\[
A(\mathbf{k})=J_f-
\sum_{a,b=1}^{d}D^{ab}k_a k_b
+i\sum_{a=1}^{d}V^a k_a,
\qquad
J_f=\left.\frac{\partial\mathbf{f}}{\partial\mathbf{u}}\right|_{\mathbf{u}_0}.
\]

This display is a pattern, not a replacement for deriving the supplied operator. Cross diffusion, coefficient gradients, field-dependent mobility, nonlocal kernels, and mixed derivatives can change its structure.

## Boundary Conditions And Admissible Modes

Derive the eigenfunctions of the spatial operator with its boundary conditions. The following are scalar Laplacian eigenfunctions for standard second-order problems:

| Domain and boundary condition | Modes | Wavenumbers |
| --- | --- | --- |
| Infinite line or plane | \(e^{i\mathbf{k}\cdot\mathbf{x}}\) | continuous real \(\mathbf{k}\) |
| Periodic interval of length \(L\) | \(e^{i2\pi n x/L}\) | \(k_n=2\pi n/L\), \(n\in\mathbb{Z}\) |
| Neumann interval \([0,L]\) | \(\cos(n\pi x/L)\) | \(k_n=n\pi/L\), \(n=0,1,\ldots\) |
| Dirichlet interval \([0,L]\) | \(\sin(n\pi x/L)\) | \(k_n=n\pi/L\), \(n=1,2,\ldots\) |

For rectangular 2D domains, form the allowed pairs from the boundary condition in each coordinate. Fourth-order operators require their full additional boundary conditions and need not share these second-order modes. For irregular domains, use eigenpairs of the appropriate spatial operator. Coupled or mixed boundary conditions may not preserve a common scalar modal space; discretize the complete coupled operator rather than assigning a convenient \(k\) to each field independently.

Separate the continuous dispersion relation, useful for mechanism and thresholds, from the discrete spectrum of the stated finite domain. Track mode multiplicity and symmetry-related wavevectors.

## Constraints And Generalized Pencils

A singular \(B\) often signals algebraic constraints, Lagrange multipliers, incompressibility, or variables without time derivatives. Do not invert \(B\), add an arbitrary regularization, or treat every returned value as a physical growth rate.

1. Linearize the dynamical equations and constraints together.
2. Identify physical variables, algebraic variables, gauge freedoms, and boundary constraints.
3. Eliminate constrained variables analytically or project onto a constraint-compatible subspace when that operation is justified and documented.
4. Otherwise retain a regular descriptor pencil and use homogeneous generalized eigenvalues \((\alpha,\beta)\), with finite \(s=\alpha/\beta\) only when \(\beta\ne0\).
5. A pair with \(\beta=0\) and \(\alpha\ne0\) is an infinite generalized eigenvalue associated with the descriptor structure; do not label it an infinitely fast instability. A pair with \(\alpha=\beta=0\) is indeterminate and signals a singular or ill-posed formulation, not a physical or infinite mode.

Check the rank and regularity over the parameter regime. A pencil that is singular for every \(s\) needs a reformulation before its spectrum supports a stability claim.

## Inertial Mechanics

For second-order perturbation dynamics,

\[
M\ddot{\mathbf{q}}+C\dot{\mathbf{q}}+K(\mathbf{k})\mathbf{q}=0,
\]

preserve the quadratic eigenvalue problem

\[
P(s)\mathbf{q}
=\bigl[s^2M+sC+K(\mathbf{k})\bigr]\mathbf{q}=0
\]

in the derivation and analytical result. A first-order companion form is a numerical representation, not a change to the mechanical model. State its construction, check dimensions and signs, and verify every computed pair with \(\|P(s)\mathbf{q}\|\) as well as any companion residual. Singular mass matrices require constraint treatment rather than blind companion linearization.

Rigid translations, rotations, or gauge motions can create exact zero modes. Identify their origin and analyze stability on the physical quotient or state explicitly that the conclusion is conditional on those neutral symmetries.

## Curvature And Higher Spatial Derivatives

Declare the normal orientation, signed-curvature definition, mean-curvature normalization, and displacement direction before varying a geometric law. Derive the first variation for the stated reference geometry. A flat Monge-gauge relation cannot be transferred unchanged to a curved base surface.

Flat, constant-coefficient bending problems often produce \(k^4\) terms. Their sign follows from the supplied force, energy, mobility, and curvature conventions; do not assign it by pattern matching. On curved surfaces, use the relevant covariant operator and its admissible eigenfunctions. Include curvature-induced lower-order terms and coupling to tangential or constrained motions when the derivation produces them.

If the base state is nonuniform, Fourier modes generally couple. Linearize in physical space and use an available, validated spectral, finite-element, or finite-difference discretization of the full operator. Demonstrate refinement convergence, distinguish matrix eigenvalues from the continuum spectrum, and describe the result as a numerical linear spectrum rather than a scalar dispersion relation unless a valid mode parameter exists. Plot converged eigenvalues by mode index or in the complex plane; do not invent a wavevector axis.

## Classification And Thresholds

For each finite-dimensional modal problem, classify the finite physical eigenvalues using \(\exp(st)\):

- unstable when at least one physical eigenvalue has \(\operatorname{Re}s>0\);
- asymptotically decaying when all physical eigenvalues have \(\operatorname{Re}s<0\);
- marginal or neutral only after explaining every eigenvalue with zero real part and excluding positive-real-part modes;
- algebraically growing when a zero-real-part eigenvalue is defective or a Jordan chain produces polynomial growth.

Conservation can enforce a \(k=0\) zero mode without making nonzero modes neutral. Symmetry can do the same. State whether stability is considered modulo conserved quantities or symmetries.

For a continuum or infinite-domain operator, mode-wise negative real parts do not by themselves prove uniform asymptotic or semigroup decay. State the spectral conclusion actually established and identify any missing spectral-gap, resolvent, or semigroup control. A non-normal finite matrix or operator can also produce transient amplification even when every eigenvalue has negative real part; do not call all perturbations monotonically decaying without an appropriate transient-growth analysis.

A spectrum evaluated at real \(\mathbf{k}\) establishes temporal growth or decay of those Fourier modes. In an open advective system, this alone does not establish absolute instability or growth at a fixed spatial location. Require separate spatiotemporal evidence for such a claim, without adding absolute-instability analysis to the default deliverable.

Locate a stationary onset through \(s=0\) only when the critical branch is real. For oscillatory onset, impose \(s=i\omega\), \(\omega\ne0\), and solve the real and imaginary conditions. Check transversality or report a degenerate onset. When the dominant branch switches identity, bracket thresholds using the maximum real part while retaining the branch information; a coarse sampled sign change is not an exact threshold.

## Numerical Branches And Residuals

Generate numerical functions from the exact SymPy expressions with `lambdify`. For each evaluated \(\mathbf{k}\), retain complex eigenvalues and right eigenvectors. Scale matrices or variables when conditioning requires it, while recording the transformation and converting reported eigenvectors back to physical variables.

Match branches across neighboring points using a cost that combines normalized eigenvalue distance and eigenvector overlap. Around exact degeneracies, track the invariant subspace rather than forcing an arbitrary eigenvector label. Verify symmetry-related directions separately in 2D.

For an ordinary problem use, for example,

\[
r=\frac{\|A\mathbf{q}-s\mathbf{q}\|_2}
{\|A\|_2\|\mathbf{q}\|_2+|s|\|\mathbf{q}\|_2+\delta},
\]

with a declared small scale \(\delta\). Replace the numerator and denominator consistently for \(A\mathbf{q}=sB\mathbf{q}\) or \(P(s)\mathbf{q}=0\). Choose and report an acceptance tolerance based on precision, conditioning, and matrix scale; do not present a universal tolerance as proof. A small residual is a backward-error check and can coexist with a poorly determined eigenvalue.

For a non-normal or nearly defective problem, use left and right eigenvectors to assess eigenvalue conditioning, or apply a suitable invariant-subspace, higher-precision, or controlled perturbation check. Near degeneracy, report a stable subspace when individual branches are not identifiable. If numerical or conditioning uncertainty reaches across \(\operatorname{Re}s=0\), leave the stability sign and threshold unresolved. Ordinary residual and analytical comparisons are sufficient for well-separated normal or simple eigenvalues.

Compare analytical and numerical values at representative interior points, both sides of every threshold, extrema, branch crossings, \(k=0\), and justified large-\(k\) limits. If the model is a continuum approximation with a finite physical validity range, do not extrapolate the dispersion relation beyond that range. Growth that is still increasing at the sampled edge remains unresolved unless an asymptotic or analytical result establishes its limit. If growth is proven unbounded as \(|\mathbf{k}|\to\infty\), flag possible continuum ill-posedness. A source-supported physical cutoff changes the model's applicable spectrum; a numerical grid truncation merely limits the calculation and cannot supply physical wavelength selection.

## Sources For Specialized Methods

Consult and cite only the sources whose methods are actually used in the report:

- [SymPy mechanics linearization documentation](https://docs.sympy.org/latest/explanation/modules/physics/mechanics/linearize.html) for the official symbolic-linearization interface and conventions.
- [SciPy generalized eigensolver documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.eig.html) for ordinary and generalized eigenproblems and homogeneous eigenvalue output.
- [Tisseur and Meerbergen, “The Quadratic Eigenvalue Problem”](https://eprints.maths.manchester.ac.uk/466/1/38198.pdf) for quadratic pencils and linearizations.
- [Manning, Bamieh, and Carlson, “Descriptor Approach for Eliminating Spurious Eigenvalues in Hydrodynamic Equations”](https://arxiv.org/abs/0705.1542) for constraint-aware descriptor formulations.
- [Capovilla, Guven, and Santiago, “Deformations of the Geometry of Lipid Vesicles”](https://arxiv.org/abs/cond-mat/0212118) for geometric variations on curved interfaces.
