# Versioning

Computational Modeling Skills has one package version using the
`MAJOR.MINOR.PATCH` format. Portable, Codex, Claude, and Gemini manifests carry
the same value. Individual skills do not have independent release numbers.
A scientific model's version is a separate identity.

The maintainer decides when to publish a release and selects its version after
reviewing the accumulated changes. A README edit, artwork correction, or packaging
cleanup does not automatically trigger a release or version bump. Once a release
is published, subsequent changes normally receive a new version when the
maintainer next releases them.

For future releases, [Semantic Versioning](https://semver.org/) guides the choice:

- **Patch:** compatible corrections, clearer guidance, attribution fixes, and
  repairs that preserve supported workflows and interfaces.
- **Minor:** new skills or optional features and compatible extensions.
- **Major:** incompatible plugin identifiers or qualified invocations, removed
  or renamed skills, incompatible documented helper CLI or output changes,
  changed required inputs or completion contracts, or newly required dependencies
  that break supported use.

The supported contract covers plugin and extension identifiers, qualified skill
invocations, public skill names and documented triggers, required inputs,
completion and output contracts, and documented runtime-helper arguments and
output formats. Development tests, evaluations, and development-only checkers are
outside this contract. Internal prose and example rendering details are outside
it unless explicitly documented as interfaces.

The corrected `2.0.0` combines the collection rename, ninth skill
`paper-reproduce`, plugin packaging, scientific schematic remake, README cleanup,
and removal of the VIGIL example. The package identifier changes from
`theoretical-biophysics-modeling-skills` to `computational-modeling-skills`,
changing qualified skill invocations. The VIGIL sources and figure paths and the
previously documented `build_example.py vigil` case are no longer available.

On 2026-09-24, the maintainer explicitly requested a one-time version correction:
the current package is `2.0.0`; the original `2.0.0` is archived as
`archive/v2.0.0-original`; and the former `3.0.0` is archived as
`archive/v3.0.0-before-correction`. Both archives retain their original commits,
release IDs, asset bytes and hashes, attribution, and licenses, and are marked
as prereleases. The historical `v2.0.1` tag remains. The short-lived `2.0.1` and
`3.0.0` are superseded by the corrected `2.0.0`, which targets a new reviewed
commit. This exception departs from the normal immutable-tag policy and does not
erase those publications. The original `1.0.0` remains unchanged. The earlier
unpublished `1.0.1` cleanup is included; there was no separate `1.0.1` release.

Future release tags are immutable `vMAJOR.MINOR.PATCH` tags. Do not move a
published tag or silently replace release assets. Prepare a changelog entry and
synchronize all manifests before tagging the reviewed commit. A draft version in
source does not by itself mean a release has been published.

Review material license or reuse-permission changes before release and describe
them in the changelog. A version correction or removal from the current package
cannot retroactively relicense a distributed copy. Earlier VIGIL copies retain
their attribution and CC BY-NC 4.0 terms; remaining material retains its own terms.
