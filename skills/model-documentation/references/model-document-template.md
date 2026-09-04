# Physics-Focused Model Document Template

Read before proposing a model-document plan. Explicit approval of that plan is
required before any document is written or changed. Use one document for the
model, mathematical solution method, and short implementation record.

## Contents

- [Fixed skeleton](#fixed-skeleton)
- [Title and source](#title-and-source)
- [Section guidance](#section-guidance)
- [Writing and verification](#writing-and-verification)
- [Writing-format resources](#writing-format-resources)

## Fixed Skeleton

Copy these headings literally, including numbering, capitalization, and order.
Do not add headings, including model-specific subsections. Use concise paragraphs
or bold run-in labels within the assigned section. Keep inapplicable sections
with a reason; mark proposed or unknown details explicitly.

```markdown
# <Model Name>

Implementation: [<primary source filename>](<relative source path>)

## 1. Model Purpose And Questions

## 2. Physical Picture And Assumptions

## 3. Entities, Domain, And Notation

## 4. Parameters And Scales

## 5. Governing Equations

## 6. Initial And Boundary Conditions

## 7. Observables And Model Tests

## 8. Solution Method

### 8.1. Methodology And Rationale

### 8.2. Numerical Formulation

### 8.3. Algorithm And Flowchart

### 8.4. Accuracy And Verification

## 9. Model Record And Implementation

### 9.1. Implementation Mapping

### 9.2. Method Decisions And Changes

### 9.3. References
```

Departures require an explicit governing repository requirement or an explicit
user instruction overriding this template. Record and approve the exact alternate
skeleton during planning. Ordinary approval of a document plan is not a template
override, and an override must not be used to bypass a format defect.

## Title And Source

Use only the scientific model name, such as `Active Gel Contact Formation Model`
or `Chemotactic Model`. Do not prefix it with `Canonical Model Documentation`,
`Model Documentation`, or another administrative label.

Place the implementation link directly below the title. Preserve the actual
filename and relative destination, even if they contain a repository-forbidden
prose term. Link the primary Python file for Python models; otherwise the actual
primary source. It must be a regular file with no symlink components inside the
selected repository boundary after path and symlink resolution. Do not substitute
an unrelated file for a missing implementation.

For an unimplemented model with a source plan, use:

```markdown
Implementation: Not implemented; plan: [<plan filename>](<relative plan path>)
```

If the approved plan exists only in the conversation, use this literal line:

```markdown
Implementation: Not implemented; source: user-approved plan in this conversation.
```

Do not create a second file just to supply a header link. Describe inaccessible
implemented sources during planning and resolve the header with the user; do not
mislabel existing but inaccessible code as unimplemented.

## Section Guidance

### 1. Model Purpose And Questions

Open with the phenomenon and physical abstraction in words, before introducing
symbols. State the model variant and whether it is implemented or proposed. Give
the question, testable hypothesis, and observable comparison or intervention that
could support or weaken it. Predictions are conditional consequences, not results.

Scientific validation requires an independent observation, benchmark, or
experimental target appropriate to the physical claim. A mathematical benchmark
can verify a calculation but cannot validate biological assumptions. When
independent physical evidence is absent, say so.

### 2. Physical Picture And Assumptions

Explain how the entities interact, what drives the dynamics, and what is included
and excluded. Then use this compact table:

| Assumption | Rationale | Source or evidence | Limitation |
| --- | --- | --- | --- |
| Explicit idealization | Why suitable here | Citation, derivation, inspected evidence, or labeled choice | What cannot be established |

Distinguish evidence for a phenomenon from evidence for its constitutive law.
Do not present unsupported biology as fact. Explain connections the table cannot
carry; do not repeat every row in prose.

### 3. Entities, Domain, And Notation

Define entities and global notation in dependency order: indices, space and time,
particles or other entities, fields, graphs, and geometric conventions. Use a
table with symbol, physical meaning, and units or domain. Distinguish physical
radius, effective diameter, and interaction scale.

Define the domain and dimension, coordinates, continuous time, fields and their
domains, graph directionality and edge meaning, and dimensional or nondimensional
status as relevant. Describe boundary geometry here; prescribe the actual initial
and boundary conditions in Section 6 without repeating them.

Every symbol must be defined before first use, here or immediately before first
local use later, including indices and symbols in tables. Do not hide a state
variable in the parameter table.

Do not infer that every quantity is dimensional merely because physical variables
use SI units. Identify dimensionless groups, normalized observables, and indices
explicitly, and check that later definitions agree with this section.

### 4. Parameters And Scales

Use a table recording symbol, code name when one exists, physical meaning, units,
default, admissible range, and source or value rationale. Compact combined columns
are acceptable only when they retain those distinctions. Label literature
estimates, derived values, calibration, illustrative choices, and unresolved values
accurately. Use `not specified` for an unestablished range. A range is not a sweep.

Distinguish mathematically admissible regimes, code-enforced input bounds, and
experimentally supported physical applicability in the range or rationale cells.
One is not evidence for another. Keep numerical stability limits in Section 8.4.

Define scales and dimensionless groups before using them and explain their
physical interpretation. Keep timesteps, tolerances, iteration limits, and other
numerical controls in Section 8.2 unless they also have an explicit physical role.
Proposed models have proposed values, not implemented defaults.

### 5. Governing Equations

Organize equations by physical dependence, not source-file order. Introduce each
mechanism in words, define new quantities, give its simplest faithful standard
equation, then explain every term and sign. State conditions, coupling,
deterministic or stochastic character, relevant limits, and source-backed rationale.

Use ordinary derivatives, gradients, sums, and piecewise laws when sufficient.
Define vector conventions and noise correlations before using them. Do not invent
formal operators for code calls. Preserve inherently discrete rules; label an
unsupported continuous interpretation as an inference.

Distinguish implemented, optional, proposed, legacy, and unresolved relations.
An approximation is not an identity. Include derivation that clarifies a choice,
not algebra that adds no understanding. Numerical safeguards belong in 8.2 unless
they change effective physics; state that consequence here and cross-reference it.

### 6. Initial And Boundary Conditions

Prescribe the initial state and mathematical boundary conditions. Include relevant
placement distributions, polarity or velocity, graph and field state, random-seed
role, periodic distance convention, and fixed, reflecting, absorbing, or flux
conditions. Explain why no spatial boundary condition is needed for an unbounded
ordinary differential equation.

Describe preliminary relaxation when it changes the scientifically interpreted
initial state. Distinguish its temporary dynamics and stopping rule from the
governing model, and state whether its final state is recorded at time zero.

### 7. Observables And Model Tests

Define each measured or derived quantity mathematically, with physical meaning,
units, normalization, sampling interval, averaging or ensemble, and uncertainty
where relevant. Connect it to Section 1 without repeating the hypothesis. Explain
which comparison would discriminate the mechanism from relevant alternatives.

Label a recurrence residual or source-agreement check as numerical consistency,
not a scientific observable supporting the mechanism. Link existing analyses for
measured values, fitted results, sweep figures, or conclusions; do not include
those results or create another document to hold them.

### 8.1. Methodology And Rationale

Write one compact paragraph explaining the overall solution approach and why it
suits the equations, scales, and question. Distinguish analytic solution, numerical
integration, relaxation, or event-driven treatment as appropriate. Put discrete
formulas in 8.2, execution sequence in 8.3, and evidence-backed method history in
9.2. Do not repeat these explanations.

### 8.2. Numerical Formulation

Define numerical indices, timestep, discretization, and old, intermediate, and
updated states before use. Derive the discrete evolution far enough to reconstruct
each update. State explicit, implicit, split, or event-driven treatment; spatial
interpolation or interaction search; noise distribution, independence, and timestep
scaling; solver residuals, tolerances, and stopping or failure criteria as relevant.
For stochastic code, identify the random-number generator and version-sensitive
dependencies, stream and seed assignment, independence or shared draws, and draw
order where they affect reproducibility. Do not imply a seed alone reproduces a
trajectory across different generators or execution orders.

Use a numerical-controls table when needed: control, code name, numerical role,
value, and accuracy or stability rationale. Explain truncation, caps, cutoffs,
regularization, and singular-case handling, including changes to effective physics.
Say when a numerical feature is absent rather than inventing one.

### 8.3. Algorithm And Flowchart

Start with a short paragraph describing a complete timestep or solve cycle.
Provide mathematical pseudocode using the symbols and equation references from
8.2. State inputs, outputs, initialization, state timing, dependencies, conditions,
random draws, loop bounds, termination, and failure behavior as applicable.
Define assignment notation before use. Do not substitute function-call lists for
a reproducible mathematical procedure.

Embed a compact Mermaid flowchart for a coupled or branching algorithm, or when
requested. Each branch and arrow must agree with the pseudocode and implementation
or approved proposed method. A simple nonbranching calculation may briefly explain
why no flowchart is needed. Do not create a separate diagram file or add operations
absent from the model. Distinguish advancement from measurement and serialization.

### 8.4. Accuracy And Verification

State accuracy order, stability conditions, and convergence or sensitivity checks,
separating known analysis, inspected evidence, and unperformed tests. Define errors
and independent analytic references where available. Check dimensions, limits,
conservation or dissipation, and stochastic statistics as applicable. Stability
does not guarantee accuracy; agreement with the same recurrence does not verify
the physical assumptions.

Disclose numerical limitations. Keep run-specific error tables and transcripts out
of the document; link existing records. Describing a test is not evidence it was
run. Do not launch a simulation solely to complete this section.

### 9.1. Implementation Mapping

Provide a short map: model element or equation, source file, key function or type,
and stored field or generated output. Include the entry point, parameter source,
minimum runtime requirements, and data layout needed to interpret saved quantities.
Do not write a function inventory or call graph.

Except for the required primary-source header link, this section is the only
location for an exact source identifier that contains a repository-forbidden
prose term. Use code formatting and map it to its scientific meaning.

Record the inspected source revision and dirty state when version control exists;
also record the repository-relative path and SHA-256 content hash of each inspected
model-relevant source file that is dirty or untracked. Without version control,
record paths and hashes and label the mapping unversioned. For plan-only work,
identify the originating plan or approved conversation and mark code mappings and
generated outputs not implemented. Never invent source files or outputs.

### 9.2. Method Decisions And Changes

Keep a short record of consequential choices, rationale, and supporting code, test,
run, commit, or explicit user account. A decision, rationale, and evidence/status
table is sufficient. Mention a failed alternative only with evidence for both the
attempt and its observed limitation. Label undocumented history unknown. This is
not a routine edit chronology, results section, or separate lab notebook.

### 9.3. References

List only sources used, with stable links or identifiers. Cite them near the
assumptions, equations, and values they support as well. Prefer primary papers,
original textbook exposition, and official numerical-method documentation.
Presentation examples such as VisualPDE and HyperPhysics are not automatically
evidence for the documented model's assumptions or parameter values.

## Writing And Verification

Write a compact pedagogical methods record, not a book or results paper. Use
connected explanatory prose, limited tables, familiar notation, and explicit
rationale without repetition. A definition after an equation is too late for a
new symbol; the following explanation describes already-defined terms.

After drafting, apply the skill's format checker and separate verification and
scientific critical-review subagents. A checker cannot judge first-use meaning,
scientific validity, source support, or equation-code fidelity. Correct in-scope
findings, recheck the final document, and report limitations in the conversation.
Keep the plan, review findings, and completion report out of separate files.

## Writing-Format Resources

The user selected these examples as references for explanatory structure,
physical narration, and equation presentation. Consult them for presentation,
not as automatic evidence for a model's assumptions or parameter values. Retain
the fixed document headings above rather than copying a source's organization.

- [VisualPDE: Explore](https://visualpde.com/explore#)
- [Wikipedia: Lotka-Volterra equations](https://en.wikipedia.org/wiki/Lotka%E2%80%93Volterra_equations)
- [Emergent Mind: Active Brownian Particles](https://www.emergentmind.com/topics/active-brownian-particles-abps)
- [Demian Levis: Lecture PDF](https://demianlevis.wordpress.com/wp-content/uploads/2018/02/edinburgo_marzo2017.pdf)
- [HyperPhysics: Broadcast example](http://hyperphysics.phy-astr.gsu.edu/hbase/Audio/bcast.html#c3.)

These are linked resources, not bundled copies. Read and assess a source before
describing or citing its scientific content in a model document.
