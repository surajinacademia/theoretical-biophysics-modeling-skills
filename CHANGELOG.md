# Changelog

## 2.0.0 — 2026-09-23

This release incorporates the previously unpublished 1.0.1 cleanup; there is
no separate 1.0.1 release.

- Renames the collection from **Theoretical Biophysics Modeling Skills** to
  **Computational Modeling Skills**, and the plugin/extension identifier from
  `theoretical-biophysics-modeling-skills` to `computational-modeling-skills`.
  This is a breaking package identity change; the eight individual skill names
  remain unchanged.
- Adds `paper-reproduce` as the ninth skill, with its reviewed operational
  references, target-card validator, and current decision diagram. Development
  notes and superseded diagrams remain outside the distribution.
- Adds portable root plugin metadata, Codex and Claude repository catalogs,
  and package logo assets. The package contains no MCP server, app, hook, or
  automatic installation action.
- Documents scoped handoffs between modeling and documentation, notebooks and
  visualization, and schematic design and request clarification. Existing
  approvals and the coordinating skill's requested outputs remain authoritative.
- Changes qualified skill invocations from
  `theoretical-biophysics-modeling-skills:<skill-name>` to
  `computational-modeling-skills:<skill-name>`. For example,
  `theoretical-biophysics-modeling-skills:model-documentation` becomes
  `computational-modeling-skills:model-documentation`. Update saved qualified
  invocations when adopting the renamed package.
- Moves the derived local checkout to `public/computational-modeling-skills/`.
  The current GitHub hosting address remains
  `https://github.com/surajinacademia/theoretical-biophysics-modeling-skills`
  until the owner renames the remote repository. No installation or registration
  changes are performed by this local rename.
- Limits the distribution to skills and their runtime dependencies, supporting
  material, package metadata, and licensing information.
- Removes development tests and evaluation suites, the development-only
  `check_model_doc.py` checker, and unused build files.
- Routes five manual TikZ recipes through the private build workflow and keeps
  VIGIL's generated compilation inputs private before publishing retained sources.
- Publishes quantitative PDF outputs through private staging and opened output
  directories; assembles the gallery from private inputs before publishing it.
  File replacements are atomic individually, not as a multi-file transaction.
- Rejects escaped or comment-obfuscated SVG CSS, unsupported style properties
  and functions, and SMIL animation; requires UTF-8 XML and rejects invalid XML
  control characters. Rejects nonregular TeX source/include files without
  blocking on FIFOs.
- Preserves the eight skill names, runtime helper interfaces, diagram creator
  credits, and third-party license terms. The published `v1.0.0` release and its
  history remain unchanged.

## 1.0.0

First stable eight-skill collection. This establishes the compatibility contract
in [VERSIONING.md](VERSIONING.md).

- Retains computational modeling, model documentation, schematic design, and
  request clarification.
- Adds scientific notebooks, linear stability analysis, data visualization, and
  a portable single-job CPU Slurm workflow.
- Removes `gotcha` from the current package; this does not erase prior releases
  or repository history. Private skills are outside this release.
- Aligns platform manifest versions and documents mixed licensing, per-example
  diagram attribution, notebook provenance, and font notices. VIGIL remains
  CC BY-NC 4.0; share-alike examples retain their applicable terms.
