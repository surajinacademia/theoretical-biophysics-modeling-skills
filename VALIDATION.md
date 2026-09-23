# Release validation

Use a project Python 3.10 or newer with the dependencies in
[tests/requirements.txt](tests/requirements.txt). Run from the package root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -B evals/model-documentation/checker_eval.py
bash -n skills/slurm/assets/cpu-job.sbatch
```

The tests cover bounded document/report checks, numerical example edge cases,
notebook edit integrity and execution status, package version agreement, payload
hashes, and required attribution files. Format checks are not scientific validation
or evidence of reliable agent behavior in every workflow. Slurm syntax and the
unconfigured-job guard are checked locally; no live scheduler compatibility is
claimed. Plotting helpers were smoke-tested with and without the optional personal
theme, including all eight teaching plots without it. Native-theme figures can
differ in appearance from stored specimens.

The release manifest lists SHA-256 hashes for the reviewed package files (excluding
the manifest itself). The annotated Git tag identifies the released commit.
Unchanged published versions are never replaced; corrections receive a new version.
