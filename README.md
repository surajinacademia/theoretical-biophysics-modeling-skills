# Theoretical Biophysics Modeling Skills

This Codex plugin contains three independent skills.

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

Each complete skill is under `skills/`. The plugin manifest is at
`.codex-plugin/plugin.json`.

The main repository uses the MIT license. The TikZ gallery has entry-specific
terms. See `THIRD_PARTY_NOTICES.md` for all third-party material.
