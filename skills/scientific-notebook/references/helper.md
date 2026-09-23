# Notebook helper

## Contents

- [Create and inspect](#create-and-inspect)
- [Patch only the intended cells](#patch-only-the-intended-cells)
- [Execution and verification](#execution-and-verification)

Run `scripts/notebook.py` from this skill directory, or use its absolute path.
The helper requires `nbformat` and `nbclient`; execution also needs the selected
kernel and the notebook's scientific packages. Use the project's environment.

The helper maintains one `.ipynb`. Its JSON patches are temporary authoring
inputs, not another maintained implementation. It rejects symlink notebook and
patch paths, requires existing parent directories, validates notebook structure,
and checks the current file hash before replacing a notebook. These checks detect
intervening changes; they do not lock the file against simultaneous writers.
Reinspect and reconcile when a hash differs. Review code before execution: the
helper is not a sandbox.

## Create and inspect

```bash
python scripts/notebook.py create /path/to/study.ipynb \
  --title "Scientific question" \
  --point "Explain the question and the intended calculation."
python scripts/notebook.py inspect /path/to/study.ipynb
python scripts/notebook.py validate /path/to/study.ipynb
```

Supply at least one nonempty `--point` argument; there is no fixed bullet count.
Creation loads
[`assets/notebook-template.ipynb`](../assets/notebook-template.ipynb), updates its
opening, and refuses to overwrite an existing file. Replace its authoring prompts
before execution. Preserve the user's shortened structure when editing an
existing notebook. The template omits interpretation and uses an installed owner `minimalist`
theme when available, otherwise Matplotlib's built-in default. See the skill's
plotting-style section for the distinction; no owner theme source is bundled.

Inspection reports the file's `sha256`, notebook metadata, cell IDs and sources,
cell metadata, attachment names, execution counts, and output types/MIME types.
It does not render figures or expose full attachment/output content. Use a
notebook viewer or `nbformat` to inspect those. For legacy version-4 notebooks
missing IDs, inspection calculates deterministic IDs in memory; a later mutation
persists them. Existing duplicate IDs are rejected.

`validate` performs the same structural checks without execution or mutation and
returns a concise summary. `create`, `edit`, and `execute` also return concise
summaries; call `inspect` when the next action requires cell sources and IDs.

## Patch only the intended cells

Capture the current hash and IDs from `inspect`. Write a JSON patch with this
shape, substituting the actual hash and cell IDs:

```json
{
  "sha256": "copy-the-current-inspect-sha256-here",
  "operations": [
    {
      "op": "replace",
      "id": "methods-explanation",
      "source": "## Method\n\nThe revised scientific explanation goes here."
    }
  ]
}
```

```bash
python scripts/notebook.py edit /path/to/study.ipynb --patch /path/to/patch.json
```

Operations run in order:

| Operation | Fields | Effect |
| --- | --- | --- |
| `replace` | `op`, `id`, `source` | Replace only that cell's source. |
| `insert` | `op`, `after`, `cell_type`, `source`; optional `id` | Insert after an existing ID, or at the beginning when `after` is `null`. Types: `code`, `markdown`, `raw`. |
| `delete` | `op`, `id` | Delete the selected cell. |

Unknown fields or IDs are rejected. Source replacement retains the cell's ID,
metadata, and attachments. Markdown-only changes retain outputs and execution
state. Do not use a delete-and-reinsert sequence for an ordinary source edit.

For code changes, an optional top-level `invalidate` array identifies surviving
code cells whose saved outputs and execution counts must be cleared. Include
every changed or inserted code cell and every dependent result cell. For example,
changing `parameters` in the template normally requires
`"invalidate": ["parameters", "run"]`; first inspect the actual notebook for
additional dependents. Deleted code may also have surviving dependents. An empty
array is only appropriate when no surviving code outputs are affected, such as
deleting independent code.

Omit `invalidate` when dependencies are uncertain: the helper then clears all code
outputs and execution counts, including notebook-level widget state. Explicit
invalidation preserves widget state needed by retained outputs. The helper does
not infer dependency graphs. Computational changes set
`metadata.scientific_notebook.execution` to `stale`. Interpretation remains
`not_requested` when already in that state or absent; existing requested
interpretation becomes `review_required`. These flags do not visibly annotate
prose or authorize adding interpretation. Review affected existing claims and
clearly mark them unverified if rerunning is outside the request. The helper
cannot detect external changes to data, imports, or assumptions.

For metadata, attachment, cell-type, or other edits outside this vocabulary, use
`nbformat` while preserving unrelated content and checking the file has not
changed before saving.

## Execution and verification

```bash
python scripts/notebook.py execute /path/to/study.ipynb --kernel python3 --timeout 600
```

Execution always starts a fresh kernel, runs every code cell in order, and uses
the notebook's parent directory as its working directory. `--timeout` is seconds
per cell, defaulting to 600. If `--kernel` is omitted, kernel selection follows
the notebook metadata and `nbclient` defaults. Set an explicit kernel when the
project environment could otherwise be ambiguous.

On success, outputs are saved to the same file and execution becomes `succeeded`.
Interpretation stays `not_requested` by default; existing requested interpretation
becomes `review_required`. This records execution, not scientific or visual
verification. Always inspect the relevant scientific checks and figures. Only
when interpretation is explicitly requested, write or update that prose and set
`metadata.scientific_notebook.interpretation` to `reviewed` with `nbformat`.
On error or timeout, the helper saves the notebook with code outputs cleared and
execution `failed`, then exits with an error. It refuses to overwrite a notebook
whose hash changed during the run. Computation may have external file side
effects even when execution fails or the final save is refused.

For a narrow request, use affected-cell execution with its prerequisites or an
isolated check instead of automatically invoking this full-run command. Record
the scope of verification honestly. Inspect affected figures at reading size;
revise requested interpretation without rerunning a prose-only edit. Ordinary
`validate` or `inspect` checks notebook format; format validity alone does not
establish execution, result freshness, or scientific validity.
