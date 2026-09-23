# Theoretical Biophysics Modeling Skills

Version **1.0.0** contains eight independently triggered agent skills.

| Skill | Scope |
| --- | --- |
| [computational-modeling](skills/computational-modeling/SKILL.md) | Scientific model development, verification, and evidence |
| [model-documentation](skills/model-documentation/SKILL.md) | Physics-focused model and methods documents |
| [scientific-notebook](skills/scientific-notebook/SKILL.md) | Editable scientific research notebooks |
| [linear-stability-analysis](skills/linear-stability-analysis/SKILL.md) | Linear stability of specified stationary states |
| [data-visualization](skills/data-visualization/SKILL.md) | Quantitative plots from completed simulation data |
| [schematic-designer](skills/schematic-designer/SKILL.md) | Scientific schematics with editable examples and attribution |
| [lets-be-clear](skills/lets-be-clear/SKILL.md) | Confirm shared understanding before acting |
| [slurm](skills/slurm/SKILL.md) | Prepare and manage one CPU batch job with native Slurm |

Model-related notebook work uses the bundled `computational-modeling` workflow.
Other optional integrations are identified in the relevant skill and are not
required merely to load this collection. Execution and rendering need the tools
specified by the selected workflow, such as a Python/Jupyter environment, a TeX
engine, or access to an existing Slurm cluster. These runtimes are not bundled.
Platform manifests describe this package; they do not install runtimes or grant
permission to submit jobs.

Original code and documentation use MIT terms, with **third-party exceptions**.
Diagram adaptations include share-alike licenses and a **noncommercial VIGIL
example**. Read [LICENSE](LICENSE), [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md),
and each example's attribution before reuse. This is not an unrestricted,
uniformly MIT collection.

See [VALIDATION.md](VALIDATION.md) for reproducible release checks.

See [VERSIONING.md](VERSIONING.md) for compatibility rules and
[CHANGELOG.md](CHANGELOG.md) for this release. The package version is separate
from any scientific model version recorded while using a skill.
