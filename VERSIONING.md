# Versioning

Computational Modeling Skills has one package version using [Semantic Versioning](https://semver.org/).
Portable, Codex, Claude, and Gemini manifests carry the same `MAJOR.MINOR.PATCH` value.
Individual skills do not have independent release numbers. A scientific model's
version is a separate identity and does not change with this package version.

The stable contract begins at `1.0.0`: plugin/extension identifiers, qualified
skill invocations, public skill names and documented triggers, required inputs
and completion/output contracts, and documented runtime-helper
CLI arguments and output formats. Development test/evaluation assets and
development-only checkers are not part of the stable skill API. Internal prose,
implementation details, and example rendering details are not stable APIs unless
explicitly documented as such. This distinction does not permit removing a
helper required by a supported skill workflow as a patch change.

- **Patch:** compatible corrections, clearer guidance, attribution fixes, and
  repairs that preserve the documented workflow and interfaces, including removal
  of development-only packaging assets that supported workflows do not need.
- **Minor:** new skills or optional features and compatible extensions.
- **Major:** changed plugin/extension identifiers or incompatible qualified
  skill invocations, removed or renamed skills, incompatible CLI or output
  changes, changed required inputs/completion contracts, or newly required
  dependencies that break existing supported use.

Version `2.0.0` renames the package identifier
from `theoretical-biophysics-modeling-skills` to `computational-modeling-skills`,
changing the namespace of qualified skill invocations while retaining all eight
individual skill names and adding `paper-reproduce` as the ninth skill. This
breaking identity change requires a major version.
It includes the earlier unpublished `1.0.1` cleanup; no `1.0.1` release is implied.
The published `1.0.0` release remains unchanged.

Version `3.0.0` removes the VIGIL example from the public package, including the
previously documented `build_example.py vigil` case and its bundled source and
figure paths. Removing this runtime-helper case breaks the stable contract and
requires a major version, even though all nine skills remain available. Earlier
tags and release assets remain unchanged, with the attribution and license terms
that apply to their VIGIL copies.

A material license or reuse-permission change must be reviewed before release,
called out in the changelog, and treated as a major change if it restricts a
previously supported use. A version number cannot retroactively relicense an
already distributed copy.

Release tags are immutable `vMAJOR.MINOR.PATCH` tags, for example `v1.0.0`.
Never move or overwrite a published tag or replace its assets silently. Publish
a new version for a correction. Prepare a matching changelog entry and synchronize
all manifests before tagging the reviewed commit; a draft version in source does
not by itself mean a release has been published.
