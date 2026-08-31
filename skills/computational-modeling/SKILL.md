---
name: computational-modeling 
description: >
  Core workflow for implementing, modifying, debugging, validating, or
  reviewing code for scientific and biophysical models. Trigger this skill
  whenever the user asks to work on code for a scientific model. Trigger only
  when the chat is about both coding and modeling. Do not trigger for data
  analysis, statistics, plotting, or figure generation.
---

# Scientific Computing Core Workflow

## Objective

Answer the exact scientific question with the smallest correct, readable,
reproducible change.

Scientific correctness takes priority over software sophistication.
Do not broaden the task, redesign the project, or add infrastructure that
is not required to support the requested scientific result.

Citation: Wilson G, Aruliah DA, Brown CT, Chue Hong NP, Davis M, Guy RT, et al. (2014) Best Practices for Scientific Computing. PLoS Biol 12(1): e1001745. https://doi.org/10.1371/journal.pbio.1001745

## Core workflow

### 1. Establish the scientific contract

Before changing code, identify:

- the exact scientific question or claim;
- the governing equations, algorithm, or data transformation;
- inputs, outputs, units, assumptions, and boundary conditions;
- parameters that may change and parameters that must remain fixed;
- the minimum evidence needed to accept the result.

Treat the user's latest explicit correction, the stated governing equations,
and the project's established notation as the scientific contract.
If the equations, code, documentation, or expected result disagree, identify
the conflict before changing the implementation. Do not silently choose a
formulation or change the scientific model to reproduce an expected result.

Do not silently substitute another equation, numerical method, dataset,
parameterization, normalization, or interpretation.

### 2. Inspect before creating

Locate the existing implementation, equations, parameter definitions,
data paths, and plotting routines before writing anything new.

Reuse an existing routine or established scientific library when it
already performs the required operation.

Do not duplicate scripts, constants, equations, or analysis pathways.

### 3. Write code for humans, not computers

Work in small, reversible steps and preserve a working state after each
meaningful step.

Prefer:

- a small number of coherent functions corresponding to real scientific
  operations;
- names taken from the model, experiment, or numerical method;
- a short, traceable path from inputs to scientific outputs;
- modification of the existing pathway rather than parallel replacements.

Do not split short, linear logic into helper functions solely for abstraction,
testing, stylistic uniformity, or possible future reuse.

Do not introduce new classes, frameworks, configuration layers,
directories, helper modules, or generalized interfaces unless the
requested result demonstrably requires them.

Do not implement speculative future requirements.

Use subagents only for bounded, independent checks with explicit inputs,
outputs, and stopping conditions. Do not pass the full parent context, assign
overlapping work, or accept delegated conclusions without verification.

### 4. Automate repeated scientific operations

A repeated, error-prone, or publication-relevant manual operation should
become a reproducible command or script.

For any result intended to be retained, compared, reported, published, or
rerun, retain enough provenance to identify:

- input data or initial condition;
- code revision;
- parameter values;
- random seed, when applicable;
- numerical method and relevant tolerances;
- software or library versions when they affect the result;
- generated output path.

Manually authored code, equations, configurations, and manuscript sources
belong in version control. Generated results should be reproducible from
their recorded inputs rather than manually edited.

### 5. Validate the scientific claim

Validation must match the claim being made. Do not measure quality by the
number of tests.

Use the smallest relevant checks:

- Mathematical derivation:
  rederive critical steps; check signs, dimensions, assumptions, and
  limiting cases.

- Deterministic numerical method:
  compare with a known or simplified case; check physical invariants and
  perform a convergence check when discretization accuracy matters.

- Stochastic calculation:
  use a fixed seed for debugging; use ensembles only when the conclusion
  is statistical.

- Data analysis:
  verify data provenance, units, exclusions, missing-data treatment,
  normalization, aggregation, and the path from raw data to the reported
  quantity.

- Figure generation:
  verify the source data, plotted variables, axes, units, normalization,
  parameter values, and labels. Generate scientific values from the
  computation rather than editing them manually in the figure.

Add assertions only at scientifically meaningful boundaries, such as:

- finite numerical values;
- conserved quantities within expected tolerance;
- valid parameter ranges and units;
- array, grid, and domain consistency;
- positive or otherwise constrained physical fields;
- physically admissible states.

When debugging, first distinguish:

- implementation error:
  the code does not implement the stated scientific model;
- numerical error:
  discretization, resolution, stability, tolerances, or solver behavior
  distort the stated model;
- model limitation:
  the correctly implemented and numerically resolved model does not produce
  the expected scientific behavior.

Reproduce the smallest representative failure. State the expected behavior
from the governing equation, algorithm, or physical constraint. Change one
suspected cause at a time and rerun only the checks relevant to that cause.
Do not alter governing equations, parameter meanings, boundary conditions,
normalizations, or scientific assumptions merely to make a test pass or
recover an expected figure.
Such an alteration is a model revision, not a bug fix. Make it explicit,
justify it scientifically, and report it separately.

Do not add broad test suites, exhaustive parameter sweeps, or unrelated
validation that doesn’t serve the scientific goals. 

### 6. Optimize only after correctness is established

First obtain a clear, verified reference implementation.

Optimize only when runtime or memory is a demonstrated limitation.
Measure the actual bottleneck before modifying the implementation.

After optimization, compare against the simpler reference calculation
using scientifically meaningful tolerances.

Do not move to a lower-level language, parallel execution, specialized
data structures, or approximate algorithms without measured need.

### 7. Document scientific intent, not mechanics

Document:

- purpose;
- equations or numerical method;
- assumptions;
- units and conventions;
- inputs and outputs;
- non-obvious scientific decisions;
- reasons for approximations or exclusions.

Use comments or docstrings beside the implementation for local scientific
intent. Use adjacent documentation only when an explanation spans multiple
files, components, or workflow stages.

Do not narrate obvious code mechanics line by line.

When a section needs a long explanation merely to be understandable,
simplify or reorganize it before adding more commentary.

Keep documentation next to the implementation so that changes to one can
be accompanied by changes to the other.

### 8. Review the changed scientific pathway and stop

Before completion:

1. Inspect only the relevant changes.
2. Confirm that no unrelated behavior, notation, or parameter changed.
3. Run the minimum validation required by the scientific claim.
4. Report the result, evidence, assumptions, and remaining uncertainty.
5. Stop once the requested result is complete and verified.

Do not continue with unrelated cleanup, redesign, additional figures, broader
parameter sweeps, new tests, or new features unless explicitly requested.

## Conditional escalation

Use additional machinery only when its trigger is present:

- Workflow manager:
  when several dependent stages are repeatedly regenerated.

- Separate formal test files:
  when logic is reusable, consequential, or vulnerable to regression.

- Profiler:
  when measured performance prevents the scientific calculation.

- Independent reviewer or auditor:
  when a derivation, numerical method, or central conclusion is
  sufficiently consequential or difficult to verify directly.

- Issue tracking:
  when the work spans multiple distinct tasks or contributors.

- New abstraction:
  when at least two real existing pathways require the same operation,
  not because future reuse is merely imaginable.

## Required completion report

Unless the user requests another format, return only the applicable sections:

### Result
What was established or changed.

### Scientific evidence
The derivation, comparison, invariant, convergence check, or data check
supporting the result.

### Files changed
Only files actually modified.

### Assumptions and uncertainty
Consequential assumptions, limitations, or unresolved scientific issues.

Omit sections that do not apply. Do not invent file changes, validation
results, evidence, or certainty.
