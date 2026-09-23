# Model Versioning

Use [Semantic Versioning](https://semver.org/) as a project convention for model releases: `MAJOR.MINOR.PATCH`, with nonnegative integers and no leading zeroes. Define compatibility by the scientific contract: equations and assumptions, parameter meanings and units, default formulation, input/output interpretation, and numerical guarantees.

- **MAJOR:** an incompatible scientific change; reset MINOR and PATCH to zero. A changed hypothesis or governing equation is a model revision, never an implementation bug fix.
- **MINOR:** optional capabilities that preserve the established contract; reset PATCH to zero.
- **PATCH:** corrections that implement the same intended model and preserve its contract. Computed values may change; record affected results and whether they require regeneration or reassessment.

Use `0.y.z` for initial development (`0.1.0` is a suggested first release) and `1.0.0` for the first stable contract. Compatibility is not guaranteed during initial development; still describe scientific changes explicitly. A prerelease may append an identifier such as `-rc.1`.

Inspect version metadata and release records before assigning a version. Keep the descriptive model name, release number, version control name, and source revision distinct. Preserve the recorded naming convention; otherwise, for an authorized release, use `<model-slug>-v<MAJOR.MINOR.PATCH>`, such as `active-gel-v1.2.0` or `active-gel-v1.2.0-rc.1`. The `v` prefix belongs to the name, not the version number.

Run-specific parameters, initial conditions, and seeds under the same formulation do not each create a release. Changes to versioned defaults, parameter meanings, or formulation may break compatibility. Record run configuration separately from model version and source identity, retaining revision and dirty state in either case.

Only for an authorized release, record its version control name, rationale, source revision, verification and validation evidence, and impact on existing results in the project's release record. Released contents and tags are immutable; corrections require a new version. Use the existing release mechanism without creating release records or tags for each edit. Release work does not authorize pushing or publication.
