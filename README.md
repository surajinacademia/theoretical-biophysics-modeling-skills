# Theoretical Biophysics Modeling Skills

Five reusable, platform-neutral agent skills.

## Install

- **Codex:** ask `$skill-installer` to install the desired folder under `skills/` from this repository.
- **Claude Code:** `git clone https://github.com/surajinacademia/theoretical-biophysics-modeling-skills.git ~/.claude/skills/theoretical-biophysics-modeling-skills`
- **Gemini CLI:** `gemini extensions install https://github.com/surajinacademia/theoretical-biophysics-modeling-skills`
- **Perplexity Computer:** upload a skill as a ZIP with `SKILL.md` at the ZIP root from **Skills → Create skill → Upload a skill**.

## `computational-modeling`

Core workflow for implementing, modifying, debugging, validating, or
reviewing scientific computations, simulations, data analyses, and
figure-generation code.

Preserve the stated scientific model, modify the smallest existing pathway,
validate the exact scientific claim, and stop.

## `model-documentation`

Plan, write, revise, or audit one physics-focused model document from code,
approved goals, or an existing methods record. It requires approval before
writing and follows a fixed nine-section structure: physical rationale and
defined notation first, governing equations next, then reproducible numerical
methods and an implementation record. It has no dependency on a writing skill.

The skill includes a [fixed template](skills/model-documentation/references/model-document-template.md),
a [worked oscillator example](skills/model-documentation/examples/overdamped-harmonic-oscillator/model.md),
and a read-only format checker. Independent verification and scientific review
remain necessary: a format pass does not establish physical validity.

## `schematic-designer`

Use it to create or reconstruct a scientific schematic. It inventories the
scientific content, selects Matplotlib, TikZ, or a hybrid workflow, renders the
figure, and checks the final PDF and outlined-text SVG. It includes two complete
scientific examples, a TikZ starter template, and a 17-entry TikZ gallery with
editable sources and rendered specimens.

## `lets-be-clear`

Use it to confirm a request before work starts. It restates the goal and scope,
asks for confirmation, and does not start the underlying task until the user
confirms the unchanged meaning.

## `gotcha`

Use it to save explicit agent-performance feedback. It finds the applicable
`AGENTS.md`, adds or revises one durable rule, checks authority and security
boundaries, and reports the exact change.

Each complete skill is under `skills/`. Platform manifests are included at the
repository root.

The main repository uses the MIT license. The TikZ gallery has entry-specific
terms. See `THIRD_PARTY_NOTICES.md` for all third-party material.

## Verify Model Documentation

Run the regression tests and adversarial format cases from the repository root:

```bash
python3 -B -m unittest discover -s tests -v
python3 -B evals/model-documentation/checker_eval.py
```

These check format enforcement, checker error handling, and the oscillator's
numerical behavior. They do not measure an agent's workflow reliability or
establish experimental validity. The evaluator reports incorrect physical claims
as manual-review controls, not as something the format checker can reject.
