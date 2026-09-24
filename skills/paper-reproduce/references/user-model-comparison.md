# User-Model Comparison

Use this reference when a user's computational model is evaluated against published experimental measurements or another model's reported results.

## 1. State the comparison target

Identify the selected claim or reported result independently of either method. Record its observable, contrast, controls, domain, sample unit, aggregation, uncertainty, and conditions as applicable. A result-only comparison does not require inventing a broader paper claim. Do not describe a different model as reproducing the paper's data-generating mechanism.

Preserve the user's original model. Record every authorized change and isolate modified outputs from both the original user-model baseline and any paper-method baseline.

## 2. Build the measurement mapping

Map explicitly:

- variables and units;
- geometry, dimensionality, boundary conditions, and parameter domain;
- intervention, controls, and sampling times;
- simulated state to measured signal;
- sampling, aggregation, normalization, and uncertainty.

For experimental data, the measurement operator may include resolution, point-spread function, binning, background, noise, detection threshold, missing values, or segmentation. Compare like with like; a latent simulation field is not automatically an experimental intensity.

Record unmatched conditions and their materiality. Agreement under a changed condition does not validate the original published claim.

## 3. Choose evidence and comparison strength

Prefer reference evidence in this order:

1. author-provided raw or processed data;
2. official or published repository data;
3. supplementary or manuscript tables;
4. digitized values from a published figure.

For digitization record source image and hash, panel, axes and scale, calibration points, extraction method, transformations, and extraction uncertainty. Label values `digitized`; never call them author-provided raw data or infer unseen replicate distributions from plotted summaries.

Choose qualitative comparison, quantitative comparison, or both before generating assessment evidence:

- `qualitative`: direction, ordering, trend, regime, transition, morphology, or spatial/temporal structure;
- `quantitative`: harmonized numerical metric, reported and model uncertainty, and a frozen tolerance or decision rule.

When both are needed, define separate criteria and report separate conclusions; agreement in one does not imply agreement in the other. Visual resemblance alone is neither mode. Comparison strength is a setting for this target, not a separate implementation level or mandatory third decision stage.

## 4. Distinguish prediction from fit

Record how the model output was determined, including for existing runs:

- `prediction`: target evaluation data were not used for calibration, tuning, or model selection; this includes parameter-free predictions and models with independently specified parameters. If calibration was required, its data must be separate from evaluation data;
- `fit`: target data are reused for calibration or model selection.

A fit may be consistent with its fitted data, but it is not an independent prediction. When evaluation reuses fitting data, retain the fit label in every relevant table, figure, and verdict. Do not introduce fitting solely to satisfy a workflow field. For mixed studies, identify fitted and predictive conditions separately.

Record assessment status separately. Criteria specified before inspecting assessment outcomes are prospective; criteria chosen after inspection are exploratory. A fixed independent prediction can receive an exploratory assessment. Viewing the reference after the prediction was fixed does not turn it into a fit. Use a descriptive comparison with an explicit limitation when available provenance cannot establish predictive independence; do not invent that provenance.

Do not tune undocumented parameters, search seeds, choose preprocessing, or select evaluation subsets using target agreement unless the result is explicitly reported as exploratory fitting.

## 5. Report the result

Report separately:

- user-model implementation validity;
- mapping fidelity and unmatched assumptions;
- data provenance and extraction uncertainty;
- prediction provenance (`prediction`, `fit`, or undetermined independence) and assessment status (prospective, exploratory, or descriptive without an inferential decision rule);
- qualitative and/or quantitative consistency under mapped conditions, with separate criteria and conclusions when both were requested;
- disagreement or inconclusiveness;
- scientific limitations.

Describe whether each predeclared criterion is met, not met, inconclusive, or not evaluated, and explain the evidence and limitations. If using the optional schema-v1 helper for a supported case, its agreement verdicts are `qualitatively_consistent` or `quantitatively_consistent` for independent evaluation and `fit_consistent` when target data were reused. Those helper labels do not replace a separate account of each requested comparison. Never use paper-method agreement labels for a different model. Consistency does not establish model equivalence, parameter identifiability, causal mechanism, or uniqueness; agreement with another model's outputs alone is not validation against physical evidence.
