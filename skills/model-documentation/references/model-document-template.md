# Physics-Focused Model Document Template

Read before proposing a model-document plan. Explicit approval of that plan is required before any document is written or changed. Use one document for the model, mathematical solution method, and short implementation record. This is the authoritative standard for document structure and section content; the skill governs approval, evidence handling, scientific writing, and independent review.

## Contents

- [Fixed skeleton](#fixed-skeleton)
- [Title and source](#title-and-source)
- [Section guidance](#section-guidance)
- [Writing and verification](#writing-and-verification)
- [Writing-format resources](#writing-format-resources)

## Fixed Skeleton

Copy these headings literally, including numbering, capitalization, and order. Do not add headings, including model-specific subsections. Use short bullets with optional bold labels within the assigned section. Keep inapplicable sections with a reason; mark proposed or unknown details explicitly.

```markdown
# <Model Name>

Implementation: [<primary source filename>](<relative source path>)

Model version control name:

## 1. Purpose, Questions, and Hypothesis

## 2. Mechanism and Assumptions

## 3. Notation, Parameters, Values, and Evidence

## 4. Governing Model

### 4.1. Model Equations

### 4.2. Mechanistic Steps

### 4.3. Initial and Boundary Conditions

## 5. Observables and Outputs

## 6. Method

### 6.1. Methodology and Rationale

### 6.2. Numerical Formulation

### 6.3. Algorithm and Flowchart

### 6.4. Verification, Validation, and Required Scientific Tests

## 7. Model Record and Implementation History

### 7.1. Scripts and Version History

### 7.2. Method Decisions and Changes

### 7.3. References
```

## Title And Source

Use only the scientific model name, such as `Active Gel Contact Formation Model` or `Chemotactic Model`. Do not prefix it with `Canonical Model Documentation`, `Model Documentation`, or another administrative label.

Place the implementation link directly below the title. Preserve the actual filename and relative destination, even if they contain a repository-forbidden prose term. Link the primary Python file for Python models; otherwise the actual primary source. It must be a regular file with no symlink components inside the selected repository boundary after path and symlink resolution. Do not substitute an unrelated file for a missing implementation.

For an unimplemented model with a source plan, use:

```markdown
Implementation: Not implemented; plan: [<plan filename>](<relative plan path>)
```

If the approved plan exists only in the conversation, use this literal line:

```markdown
Implementation: Not implemented; source: user-approved plan in this conversation.
```

Do not create a second file just to supply a header link. Describe inaccessible implemented sources during planning and resolve the header with the user; do not mislabel existing but inaccessible code as unimplemented.

Every model document, including an unimplemented model, must include the literal field `Model version control name:` after the implementation line and before Section 1. Keep `Implementation:` as the first nonblank line after the title. Populate the new field only by copying an explicitly recorded model version or release name exactly, after confirming that it applies to the documented model. Identify its supporting source in Section 7.1. Do not invent a name or version or substitute a Git branch, commit identifier, or plugin version. When no applicable name is recorded, leave the value literally blank, as in the skeleton; do not use `unknown`, `N/A`, or another placeholder. This field does not replace the separate revision, dirty-state, and content-hash source record required in Section 7.1.

## Section Guidance

### 1. Purpose, Questions, and Hypothesis

Open with the phenomenon and physical abstraction in words, before introducing symbols. State the model variant and whether it is implemented or proposed. Give the question, testable hypothesis, and observable comparison or intervention that could support or weaken it. Predictions are conditional consequences, not results.

Scientific validation requires independent physical observations or experimental targets appropriate to the claim. A mathematical benchmark can verify a calculation but cannot validate biological assumptions. When independent physical evidence is absent, say so; specify the relevant tests in Section 6.4.

### 2. Mechanism and Assumptions

Explain the entities, domain and spatial dimension, boundary geometry, interactions, and driving processes in short bullet points. State what the model includes and excludes. For each consequential assumption, connect its rationale, supporting source or evidence, and limitation in a short bullet with an optional bold label. Distinguish evidence for a phenomenon from evidence for its constitutive law; do not present unsupported biology as fact.

Describe fields, graph directionality and edge meaning, geometry, and dimensional or nondimensional formulation as relevant. Distinguish physical radius, effective diameter, and interaction scale. Put global mathematical notation in Section 3; define any symbol needed earlier immediately before its first use. Prescribe the actual initial and boundary conditions in Section 4.3 without repeating them here.

### 3. Notation, Parameters, Values, and Evidence

Include exactly one consolidated quantity table in this section. It is the only table in the authored model document; use short bullet lists elsewhere. This restriction does not prohibit tabular data files or CSV outputs produced by the model. Cover global notation, state variables, physical parameters, relevant derived scales and dimensionless groups, and numerical controls. Use exactly the five columns below. Put the mathematical notation in brackets after the quantity name, for example `Mass [$m$]`. Explain the quantity’s role in the meaning or rationale column; do not add category, code-name, or separate range columns. Put a supported citation in the last column when available; otherwise leave that cell literally blank. Do not invent a citation or fill a missing citation with a placeholder.

| Quantity [notation] | Units | Values or range | Meaning or rationale for inclusion | Citation source |
| --- | --- | --- | --- | --- |
| Quantity name [symbol] | Units or dimensionless | Supported value, definition, or range | Physical meaning and why it is included | |

Introduce entries in dependency order: indices and coordinate/time conventions, state variables, parameters, derived quantities, and numerical controls. Define a symbol before using it in another row's expression. A state variable has a domain and evolution or initialization definition, not a fixed parameter default; refer to Section 4.3 for its prescribed initial state. Label dimensionless groups, normalized quantities, and indices explicitly rather than inferring units from nearby dimensional variables.

Label literature estimates, derived values, calibrated parameters, illustrative choices, proposed values, and unresolved values accurately. Proposed models have proposed values, not implemented defaults. Do not invent values or ranges: use `not specified` for an unestablished range and `not applicable` where a range has no role. Distinguish mathematical admissibility, code-enforced input bounds, and experimentally supported physical applicability. A range is not a sweep; a code default is not evidence of physical applicability.

Explain the physical interpretation of scales and dimensionless groups in short bullets. A derived quantity used only locally may instead be defined immediately before its first use; do not add another table or repeat the consolidated entries. List timestep, tolerance, iteration-limit, and other numerical-control values here; explain their treatment and rationale in Section 6.2 and accuracy or stability requirements in Section 6.4. Keep mathematical symbols, meanings, values, and units consistent wherever referenced.

### 4. Governing Model

Present the governing relations, causal mechanism, and prescribed conditions in the following subsections.

### 4.1. Model Equations

Organize equations by physical dependence, not source-file order. Introduce each mechanism in words, define new quantities, give its simplest faithful standard equation, then explain every term and sign. State conditions, coupling, deterministic or stochastic character, relevant limits, and source-backed rationale.

Use ordinary derivatives, gradients, sums, and piecewise laws when sufficient. Define vector conventions and noise correlations before using them. Do not invent formal operators for code calls. Preserve inherently discrete rules; label an unsupported continuous interpretation as an inference.

Distinguish implemented, optional, proposed, legacy, and unresolved relations. An approximation is not an identity. Include derivation that clarifies a choice, not algebra that adds no understanding. Numerical safeguards belong in Section 6.2 unless they change effective physics; state that consequence here and cross-reference it.

### 4.2. Mechanistic Steps

Describe the causal physical interactions in short bullets (numbered only for genuinely ordered events), referring to the governing rules in Section 4.1. Explain how one process affects the next and identify simultaneous or coupled processes without inventing a physical ordering. Include intrinsically discrete model events or transition rules where they are part of the mechanism. Distinguish that modeled sequence from numerical operator splitting or timestep order, which belongs in Section 6.3. Do not duplicate the solver algorithm or reinterpret a numerical operation as a physical mechanism.

### 4.3. Initial and Boundary Conditions

Prescribe the initial state and mathematical boundary conditions. Include relevant placement distributions, polarity or velocity, graph and field state, random-seed role, periodic distance convention, and fixed, reflecting, absorbing, or flux conditions. Explain why no spatial boundary condition is needed for an unbounded ordinary differential equation.

Describe preliminary relaxation when it changes the scientifically interpreted initial state. Distinguish its temporary dynamics and stopping rule from the governing model, and state whether its final state is recorded at time zero.

### 5. Observables and Outputs

Define each measured or derived quantity mathematically, with physical meaning, units, normalization, sampling interval, averaging or ensemble, and uncertainty where relevant. Connect it to Section 1 without repeating the hypothesis. Explain which comparison would discriminate the mechanism from relevant alternatives. Describe stored states, derived outputs, sampling or save cadence, and conventions needed to interpret them in short bullet lists; connect exact source fields to their scientific meaning in Section 7.1.

Label a recurrence residual or source-agreement check as numerical consistency, not a scientific observable supporting the mechanism. Link existing analyses for measured values, fitted results, sweep figures, or conclusions; do not include those results or create another document to hold them.

### 6. Method

Explain how the governing model is solved and how its numerical and scientific adequacy will be assessed.

### 6.1. Methodology and Rationale

Write a few short bullets explaining the overall solution approach and why it suits the equations, scales, and question. Distinguish analytic solution, numerical integration, relaxation, or event-driven treatment as appropriate. Put discrete formulas in Section 6.2, execution sequence in Section 6.3, and evidence-backed method history in Section 7.2. Do not repeat these explanations.

### 6.2. Numerical Formulation

Define numerical indices, timestep, discretization, and old, intermediate, and updated states before use. Derive the discrete evolution far enough to reconstruct each update. State explicit, implicit, split, or event-driven treatment; spatial interpolation or interaction search; noise distribution, independence, and timestep scaling; solver residuals, tolerances, and stopping or failure criteria as relevant. For stochastic code, identify the random-number generator and version-sensitive dependencies, stream and seed assignment, independence or shared draws, and draw order where they affect reproducibility. Do not imply a seed alone reproduces a trajectory across different generators or execution orders.

Reference the numerical-control values in the Section 3 table and explain their roles and rationale here in short bullets and equations. Define locally needed numerical indices or intermediate quantities immediately before use; do not add a controls table. Explain truncation, caps, cutoffs, regularization, and singular-case handling, including changes to effective physics. Say when a numerical feature is absent rather than inventing one.

### 6.3. Algorithm and Flowchart

Start with a short bullet describing a complete timestep or solve cycle. Provide mathematical pseudocode using the symbols and equation references from Section 6.2. State inputs, outputs, initialization, state timing, dependencies, conditions, random draws, loop bounds, termination, and failure behavior as applicable. Define assignment notation before use. Do not substitute function-call lists for a reproducible mathematical procedure.

Embed a compact Mermaid flowchart for a coupled or branching algorithm, or when requested. Each branch and arrow must agree with the pseudocode and implementation or approved proposed method. A simple nonbranching calculation may briefly explain why no flowchart is needed. Do not create a separate diagram file or add operations absent from the model. Distinguish advancement from measurement and serialization.

### 6.4. Verification, Validation, and Required Scientific Tests

Agree on the relevant scientific tests and their acceptance criteria during planning. Connect each test to the model question or a necessary condition for a credible calculation; ordinary software tests alone do not establish scientific adequacy. Distinguish the following in short bullet lists:

- **Numerical verification:** assess whether the equations are solved correctly. Define errors and independent analytic references where available; check dimensions, limiting cases, conservation or dissipation, stability, convergence under discretization refinement, and stochastic statistics as applicable. Stability alone does not guarantee accuracy.
- **Sensitivity:** assess dependence on uncertain physical parameters, assumptions, or numerical choices. Explain which uncertainties matter for the observables and how robust conclusions would be distinguished from numerical artifacts.
- **Physical validation and hypothesis tests:** identify independent physical evidence and comparisons or interventions that could support, weaken, or discriminate the hypothesis from relevant alternatives and confounders. Source agreement, recurrence residuals, and convergence cannot establish physical validity.

For each applicable test, state its purpose, observable or error measure, reference or comparison, and evidence-based acceptance criterion or expected discriminating outcome. If a criterion or necessary evidence is unresolved, identify what must be agreed or obtained. Do not impose universal numerical thresholds or invent targets. Distinguish proposed tests from tests supported by inspected execution records.

Some tests may require multiple simulations or experiments. Approval of this test plan or model document does not authorize those runs; obtain explicit execution authorization before performing them. Disclose missing evidence and numerical or physical limitations. Keep run-specific error tables, results, and transcripts out of the document and link existing records; never imply that describing a test means it was executed or passed.

### 7. Model Record and Implementation History

Keep a concise, evidence-backed implementation and methods record in the following subsections, using short bullet lists.

### 7.1. Scripts and Version History

Provide a short map in short bullet lists: model element or equation, source file, key function or type, and stored field or generated output. Include the entry point, parameter source, minimum runtime requirements, and data layout needed to interpret saved quantities. Do not write a function inventory or call graph.

Except for the required primary-source header link, this section is the only location for an exact source identifier that contains a repository-forbidden prose term. Use code formatting and map it to its scientific meaning.

Record the inspected source revision and dirty state when version control exists; also record the repository-relative path and SHA-256 content hash of each inspected model-relevant source file that is dirty or untracked. Without version control, record paths and hashes and label the mapping unversioned. For plan-only work, identify the originating plan or approved conversation and mark code mappings and generated outputs not implemented. Never invent source files or outputs.

### 7.2. Method Decisions and Changes

Keep a short record of consequential choices, rationale, and supporting code, test, run, commit, or explicit user account. Use short bullets connecting each decision to its rationale, evidence, and status. Mention a failed alternative only with evidence for both the attempt and its observed limitation. Label undocumented history unknown. This is not a routine edit chronology, results section, or separate lab notebook.

### 7.3. References

List only sources used, with stable links or identifiers. Cite them near the assumptions, equations, and values they support as well. Prefer primary papers, original textbook exposition, and official numerical-method documentation. Presentation examples such as VisualPDE and HyperPhysics are not automatically evidence for the documented model's assumptions or parameter values.

## Writing And Verification

Write short bullet points with one idea per item. Keep necessary definitions, assumptions, rationale, and limitations; remove repetition and heavy prose. Use numbered lists only when order matters, such as algorithm steps. Keep the title/source header, table, display equations, and fenced diagrams in their own Markdown structures. Write each list item on one source line; do not hard-wrap text to a fixed column width or add artificial line breaks. Let the Markdown viewer wrap list text. Preserve structural newlines for headings, separate list items, tables, fenced code, and display equations. Use `$...$` for inline LaTeX math and `$$...$$` for standalone equations, with each `$$` delimiter on its own line and a blank line before and after the block. Do not use code fences or backticks around equations intended to render as mathematics. Preserve LaTeX commands, mathematical line breaks inside aligned equations, and equation numbering.

Write a compact pedagogical methods record, not a book or results paper. Use short explanatory bullets, the single Section 3 table, familiar notation, and explicit rationale without repetition. Every symbol must be defined before first use, including in the table, equations, and algorithms. A definition after an equation is too late for a new symbol; the following explanation describes already-defined terms.

After drafting, use separate verification and scientific critical-review subagents. The verification reviewer directly compares the literal headings, order, title/source header, section presence, and content against this template, including exactly one authored table located in Section 3 and short bullet lists in other sections. Check that quantity categories and values are consistent, that physical mechanism steps do not duplicate the numerical algorithm, and that no old section references or conflicting placement instructions remain. Then check definitions, dimensions, source support, and equation-code fidelity. Confirm that `Model version control name:` follows the implementation line and that its value exactly matches an applicable recorded model identity supported in Section 7.1, or is literally blank when no such name is recorded. The scientific critic assesses the physical reasoning and strength of evidence. Correct in-scope findings and have both reviewers assess the same final document version. Report remaining limitations in the conversation; keep the plan, review findings, and completion report out of separate files.

## Writing-Format Resources

The user selected these examples as references for explanatory structure, physical narration, and equation presentation. Consult them for presentation, not as automatic evidence for a model's assumptions or parameter values. Retain the fixed document headings above rather than copying a source's organization.

- [VisualPDE: Explore](https://visualpde.com/explore#)
- [Wikipedia: Lotka-Volterra equations](https://en.wikipedia.org/wiki/Lotka%E2%80%93Volterra_equations)
- [Emergent Mind: Active Brownian Particles](https://www.emergentmind.com/topics/active-brownian-particles-abps)
- [HyperPhysics: Broadcast example](http://hyperphysics.phy-astr.gsu.edu/hbase/Audio/bcast.html#c3.)

Read and assess a source before describing or citing its scientific content in a model document.
