# Versioning

The collection has one package version using [Semantic Versioning](https://semver.org/).
Codex, Claude, and Gemini manifests carry the same `MAJOR.MINOR.PATCH` value.
Individual skills do not have independent release numbers. A scientific model's
version is a separate identity and does not change with this package version.

The stable contract begins at `1.0.0`: public skill names and documented triggers,
required inputs and completion/output contracts, and documented helper CLI
arguments and output formats. Internal prose, implementation details, and example
rendering details are not stable APIs unless explicitly documented as such.

- **Patch:** compatible corrections, clearer guidance, attribution fixes, and
  repairs that preserve the documented workflow and interfaces.
- **Minor:** new skills or optional features and compatible extensions.
- **Major:** removed or renamed skills, incompatible CLI or output changes,
  changed required inputs/completion contracts, or newly required dependencies
  that break existing supported use.

A material license or reuse-permission change must be reviewed before release,
called out in the changelog, and treated as a major change if it restricts a
previously supported use. A version number cannot retroactively relicense an
already distributed copy.

Release tags are immutable `vMAJOR.MINOR.PATCH` tags, for example `v1.0.0`.
Never move or overwrite a published tag or replace its assets silently. Publish
a new version for a correction. Prepare a matching changelog entry and synchronize
all manifests before tagging the reviewed commit; a draft version in source does
not by itself mean a release has been published.
