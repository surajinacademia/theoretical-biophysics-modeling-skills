# Source Audit

Use this reference to specify a target from primary sources before scientific implementation or evaluation.

## Contents

- [1. Limit the audit to the target](#1-limit-the-audit-to-the-target)
- [2. Extract the complete target specification](#2-extract-the-complete-target-specification)
- [3. Classify each item](#3-classify-each-item)
- [4. Freeze before evidence](#4-freeze-before-evidence)
- [Source-audit completion check](#source-audit-completion-check)

## 1. Limit the audit to the target

Read the final paper, formal corrections, supplementary material, first-party code/data, and cited methods required by the selected objective and target. Do not extract unrelated parts of the paper.

Use this authority order while preserving conflicts rather than hiding them:

1. formal correction or erratum;
2. final paper;
3. supplementary methods or tables;
4. first-party repository, release, or dataset;
5. explicitly cited inherited method;
6. prior reproduction as secondary evidence only.

Author code may clarify implementation but does not silently override the paper. Record version, hash, and license for copied or adapted code/data, and preserve both sources when they disagree.

## 2. Extract the complete target specification

Record applicable items and exact locators:

- target statement, observable, contrast, uncertainty, sample count, baseline;
- equations, variables, assumptions, constitutive relations;
- parameters, values, units, ranges, and defaults;
- initial and boundary conditions;
- inputs, preprocessing, normalization, exclusions, and controls;
- sampling unit, independence structure, ensembles, replicates, and seeds;
- algorithm, discretization, resolution, precision, tolerances, convergence, stopping, and failure rules;
- aggregation, statistics, uncertainty, and plotting transformations;
- language, dependencies, author code/data, and cited-method inheritance.

A source reference is structured:

```yaml
source_id: S1
locator: "Methods, p. 7, Eq. 4"
```

For code use a repository version plus file and line/function/config key. For a figure use panel, axes, and caption or text location. For a dataset use release or record version, file/table, columns, and filtering rule. A document-level citation without a locator is insufficient.

## 3. Classify each item

Classify the source support for each required item with one status:

- `reported`: directly present in the identified source;
- `inherited`: explicitly delegated to a cited method; cite both delegation and inherited locator;
- `ambiguous`: wording permits materially different interpretations;
- `conflicting`: authoritative sources disagree;
- `missing`: required but absent from inspected sources;
- `not_applicable`: outside this target or model class.

Separately label any inferred, reconstructed, or proposed choice and its rationale. For extracted data, identify whether values came from a published dataset, table, or digitized figure, and retain extraction uncertainty. Candidate models from brainstorming remain proposals; they cannot replace the reported model or resolve a source gap merely because they produce plausible output.

Assign unresolved items one materiality:

- `blocking`: the current target cannot be defined or validly evaluated; prohibit its evidence and use `not_evaluated`, never `inconclusive`;
- `sensitivity_required`: evaluate declared plausible alternatives and retain only conclusions robust across them;
- `nonmaterial`: cannot change the scientific conclusion; document and proceed;
- `not_applicable`: no gap analysis required.

For each applicable ambiguous, conflicting, or missing item state:

1. why it matters;
2. materiality;
3. effect on exact reproduction;
4. any unique source-backed reconstruction;
5. remaining alternatives;
6. evidence or user decision needed to resolve it.

Do not infer an undocumented parameter from curve agreement. A reconstructed choice remains a reconstruction even if it reproduces the published plot. A blocked claim-level or result-level target may be explicitly re-scoped to a model-level target. Record the changed scope and label any reconstruction. Its implementation evidence does not establish the original claim or reproduce the original result. The levels identify targets, not a required sequence of work.

## 4. Freeze before evidence

Use one maintained project-native target record to identify the objective, target, sources, audit decisions, protocol, exclusions, and completion criteria. When comparison is needed, record qualitative criteria, quantitative criteria, or both, with separate criteria and conclusions for each. Record numerical tolerances and uncertainty treatment where applicable. For a proof, implementation check, or new application result that needs no paper comparison, state the required evidence and why comparison is not applicable.

Freeze these scientific choices before generating the evidence used to assess the target. Preserve a dated or versioned record and the source/code/data versions needed to trace it. A material change starts a new revision or declared iteration; retain the previous protocol and its evidence. Routine execution metadata can be appended without silently changing the scientific choices.

The bundled schema-v1 target card and validator are optional helpers for the computational cases their schema supports. They are not the universal target record: the schema requires one comparison mode, comparison for claim/result targets, positive execution evidence, and its existing implementation routes. Do not distort a target to satisfy those constraints. When using that helper, the validator hashes the listed scientific fields plus revision identity and lineage as compact, key-sorted UTF-8 JSON with SHA-256 and a `sha256:` prefix. Changes to those fields create a new revision; execution/evaluation metadata alone do not. Preserve each predecessor card and bind its contained relative path and canonical hash in the successor. The validator checks that chain without following absolute or escaping paths; do not cite a revision ID whose card is unavailable. Link any helper card from the maintained target record.

A cheap diagnostic may precede the freeze only when it is labeled diagnostic and excluded from the scientific verdict.

## Source-audit completion check

Before implementation, verify that the user can tell:

- what the sources report exactly;
- what is inherited, reconstructed, unresolved, or inapplicable;
- which gaps block evidence or require sensitivity;
- which source locator supports every retained fact;
- which target-record revision governs the assessment or execution.
