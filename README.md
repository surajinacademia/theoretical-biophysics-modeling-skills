# Theoretical Biophysics Modeling Skills

Four reusable, platform-neutral agent skills.

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
