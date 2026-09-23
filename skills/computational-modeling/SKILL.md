---
name: computational-modeling
description: "Develop, modify, test, or review scientific models and their records, with or without code changes. Use for model formulation, hypothesis testing, numerical verification, and physical validation; coordinate model documents with model-documentation. Exclude generic software engineering, standalone non-model analysis or plotting, and isolated explanations."
---

# Computational Modeling

Use the scientific method to develop, test, and revise models, keeping the equations, implementation, evidence, and records consistent.

## 1. Understand the model before changing it

Inspect the existing equations, implementation, parameter sources, scientific evidence, and model records. Establish the question, hypothesis, intended result, and whether the model is proposed or implemented.

- Identify state variables, governing equations or discrete and stochastic rules, assumptions, domain, and initial and boundary conditions.
- Check symbols, units, signs, parameter meanings and provenance, physical constraints, and observables. Distinguish physical parameters from numerical controls.
- Preserve established notation and the authorized scientific scope. Resolve disagreements between intended equations, code, records, and expected results before changing scientific meaning.

Label unsupported choices as assumptions and unimplemented choices as proposals. An expected result is a prediction to assess, not a reason to change the physics until it appears.

## 2. Reuse existing code and keep changes simple

Locate and reuse existing routines, parameter definitions, and established scientific libraries when they perform the required operation. Keep the path from inputs through equations to observables readable and traceable.

Implement the intended equations faithfully, including update order, state dependencies, boundary treatment, and stochastic scaling. Prefer a small number of coherent scientific operations; avoid duplicated pathways, speculative abstractions, and infrastructure that the requested work does not need.

Optimize only for a demonstrated runtime or memory limitation, then compare with a verified reference using scientifically meaningful tolerances.

## 3. Distinguish bugs, numerical errors, and model limitations

When a result fails a check, isolate a representative case and determine which explanation the evidence supports:

- **Implementation bug:** code differs from the intended mathematical model.
- **Numerical error:** resolution, convergence, stability, solver tolerances, or sampling prevents an accurate calculation.
- **Model limitation:** the correctly implemented and sufficiently resolved formulation does not describe the target behavior under its stated assumptions.

Insufficient or unsuitable observations can also leave the cause unresolved. Use targeted checks to distinguish plausible causes before interpreting a discrepancy as evidence against a hypothesis.

Changes to equations, assumptions, parameter meanings, or boundary conditions are scientific model revisions. State their rationale, retain the earlier findings, and reassess affected predictions; do not present changed physics as a bug fix.

## 4. Validate the scientific claim with appropriate evidence

Before inspecting decisive results, define the prediction, relevant alternative, observable, and criteria for support, failure, or an inconclusive result. For numerical checks, specify the reference, error measure, and justified tolerance. Label exploratory analysis and later changes to criteria honestly.

Use the smallest checks that can support the scientific claim:

- **Code verification:** compare the implementation with derivations, exact or manufactured solutions, or independent reference calculations.
- **Solution verification:** assess numerical error through appropriate convergence, resolution, stability, conservation, or sampling checks.
- **Physical validation:** compare predictions with empirical observations for the intended use, accounting for measurement uncertainty and applicable regimes.

Separate calibration and model selection data from independent evaluation evidence where available. Disclose reuse of the same evidence and assess sensitivity, identifiability, and uncertainty when they affect the conclusion. A fixed seed supports debugging; statistical conclusions require appropriate sampling. Agreement supports tested predictions without proving the mechanism or validity outside the tested regime.

Run the checks authorized by the request or session. Designing tests or writing documentation does not authorize simulation runs or sweeps; keep unperformed tests explicit without adding approval gates to already authorized work.

See the [NASA verification and validation overview](https://www.grc.nasa.gov/www/wind/valid/tutorial/overview.html) for these distinctions.

## 5. Record enough to reproduce and interpret results

Use existing project record locations. For retained results, record the question and criteria, model and input identity, source revision and dirty state with recoverable uncommitted changes, parameter values and units, conditions and seeds, numerical method and controls, relevant software versions, ordered procedure and output processing, and output links.

Preserve actual evidence, negative and inconclusive results, failed checks, uncertainty, and applicability. Distinguish observations, computed results, interpretations, and predictions; retain earlier findings when conclusions change.

Keep maintained formulation and methods documents synchronized through [$model-documentation](../model-documentation/SKILL.md), following its plan approval, template, and review workflow. An approved matching scope remains approved. Identify pending document changes explicitly; its document gate does not block unrelated authorized model work or require a full document for every minor task. Keep run-specific results in existing experiment or analysis records.

Keep model name, release identity, source revision, and run settings distinct. Include `Model version control name:` in model-document headers with the applicable recorded name or a literally blank value. Do not manufacture versions or releases for individual run configurations. Read [model versioning](references/model-versioning.md) only when assigning or assessing a release version or name.

Use the [MIASE reporting guideline](https://doi.org/10.1371/journal.pcbi.1001122) and [NASEM reproducibility guidance](https://www.nationalacademies.org/read/25303/chapter/7) as references for reproducible records, adapting them to the project's existing format.

## 6. Stop when the requested work is complete and verified

Review the affected scientific pathway, complete the relevant authorized checks, and preserve the evidence and records. Satisfy the applicable model-documentation completion gate for document work.

Report what changed or was established, supporting evidence, record locations, remaining uncertainty, pending documentation, and unperformed work that limits the conclusion. Distinguish proposed versions from established releases when relevant. Do not claim successful tests, execution, or physical validity beyond the evidence.

A supported negative or inconclusive finding can complete the investigation; a hypothesis need not prove true. Stop without unrelated cleanup, extra features, broader sweeps, or unrequested execution.
