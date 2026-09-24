# Scientific Validation

Verify the production implementation and data before treating their outputs as scientific evidence. Select checks by model class and the conclusion at stake. Physical validation additionally requires relevant physical evidence under stated conditions.

## Common sequence

1. Translate the frozen source specification into independent tests.
2. Run the smallest diagnostic that can expose sign, unit, indexing, boundary, conservation, sampling, or stopping errors.
3. Test the production implementation directly; an oracle does not replace it.
4. Benchmark representative work before changing algorithms, precision, parallelism, storage, or language.
5. Freeze the accepted implementation/configuration before the evidentiary run.
6. Verify raw coverage and invariants before analyzing or plotting outcomes.

Do not use a visually plausible result as a test oracle.

The verification reviewer must derive applicable checks from the source specification independently of the implementation. Independently recompute decisive observables and uncertainty from raw outputs, or check the mathematical argument for an analytical target. Repeating the implementation's formula or accepting its summary alone is insufficient. Record any check that could not be performed; planned checks are not passed checks.

## Validation profiles

### Algebraic or analytic

- check dimensions, signs, limiting cases, and exact identities;
- compare with a hand calculation or independent symbolic/numerical evaluation;
- test singular, zero, boundary, and symmetry cases when applicable.

### ODE, PDE, continuum, or field model

- verify initial and boundary conditions independently;
- test conservation or balance laws with the correct geometric measure;
- use manufactured solutions or known limits when available;
- demonstrate time-step, grid, domain, and solver convergence appropriate to the claimed precision;
- check stability, positivity, residuals, and stopping criteria without relying on clipping or silent early termination.

### Stochastic or agent-based

- bind and record deterministic seeds while preserving independent draws;
- verify update order, distribution parameterization, and random-number scope;
- test sampling units, inclusion rules, replicate coverage, and denominators;
- report ensemble uncertainty rather than a favorable realization;
- distinguish a fixed displayed instance from a population-level claim.

### Optimization, learning, or inference

- verify objective, constraints, gradients or update rules, and convergence;
- separate training/calibration, validation, and held-out evaluation;
- preserve seeds, initialization, baselines, preprocessing, and checkpoint rules;
- report failed or nonconverged attempts under the source-defined policy.

### Experimental data analysis

- verify sample identity, independence, exclusions, normalization, units, and preprocessing order;
- reproduce the reported estimator, uncertainty, statistical test, and multiple comparison rule;
- audit whether plotted error bars describe replicates, samples, or fitted uncertainty.

### Optimized, parallel, or translated implementation

- define a prospective differential-equivalence contract;
- compare the authoritative and changed paths on adversarial and representative cases;
- preserve precision, randomness, update order, convergence, failures, and output semantics;
- accept the changed path only after all declared equivalence tests pass.

## Evidence checks

For each evidentiary run record target ID, governing revision/hash, source IDs, code version/hash, configuration, command, minimal environment, raw-output path, exit state, and failures. For detached, retried, multi-worker, or expensive work also record manifests, logs, checkpoints, complete key coverage, duplicates, missing groups, and file hashes.

Verify in this order:

1. provenance and correct configuration;
2. expected parameter/replicate keys and complete denominators;
3. finite values, schema, units, and scientific invariants;
4. recomputed analysis and uncertainty;
5. declared scientific assessment criteria;
6. figure as a representation of verified values.

Stop affected execution and preserve evidence when an implementation invariant, execution/data-validity check, or predeclared stopping rule fails. Diagnose the cause before using affected output as evidence. Failing to establish agreement may mean disagreement or inconclusive evidence; apply the declared decision rule and uncertainty treatment. Either outcome can complete the assessment. Finish the authorized protocol unless its declared stopping rule applies. Never alter the target or discard disagreeing data merely to improve agreement.

Account for every material attempt: completed, failed, excluded, missing, and nonconverged cases, with reasons and correct denominators. Identify which outputs entered each calculation. A zero exit code or a plot file alone does not establish successful scientific execution. Preserve raw evidence and the original outcome when changing analysis or criteria; mark the new analysis exploratory until separately assessed.

## Keep fidelity and outcome separate

Methodology fidelity describes how closely the executed method follows the source. The scientific verdict describes the selected observable. A known deviation or incomplete nonblocking method can numerically agree, just as an exactly faithful method can disagree. Report both labels. `exact_agreement` means exact equality only for the frozen deterministic observable; it never means that the implementation or mechanism is identical to the author's.
