# Repository Structure Patterns

This reference records structural lessons from working biophysics analysis
repositories. It does not prescribe a programming language or copy their source.

## Repeated Pattern

The clearest examples use one visible path:

```text
load -> scientific selection -> observable -> necessary aggregation -> plot
```

They keep physical definitions explicit. Mature libraries contain reusable
domain machinery, while project scripts remain short and direct.

## Useful Examples

- [PhysiCell collective invasion](https://github.com/PhysiCell-Models/collective-invasion/blob/55d25ae04e77fa9208ba2ec43354a7ed2168b60e/python_imaging/basic_cell_plot.py#L7-L60)
  loads one frame, selects requested cell types, and calls the plotting library
  directly.
- [AMEP particle evaluation](https://github.com/amepproject/amep/blob/69f7cd2d66ba21f1c2c57168448d4bf0e2acfbd2/examples/particle-example.py#L42-L53)
  uses established domain operations for named observables. Its
  [plot section](https://github.com/amepproject/amep/blob/69f7cd2d66ba21f1c2c57168448d4bf0e2acfbd2/examples/particle-example.py#L83-L125)
  calls the stored result arrays directly. The fitted curve in that section is
  outside this skill's scope.
- [AMEP continuum analysis](https://github.com/amepproject/amep/blob/69f7cd2d66ba21f1c2c57168448d4bf0e2acfbd2/examples/continuum-example.py#L44-L72)
  keeps several similar plot calls explicit when repetition remains readable.
- [pyTFM vector plotting](https://github.com/fabrylab/pyTFM/blob/757fbe789b18746d5bc6afabeef67918e044c3ad/pyTFM/plotting.py#L309-L344)
  retains the full magnitude field and filters only displayed arrows. Its
  [display helper](https://github.com/fabrylab/pyTFM/blob/757fbe789b18746d5bc6afabeef67918e044c3ad/pyTFM/plotting.py#L806-L839)
  supports regular spacing, magnitude thresholds, and local maxima.
- [Trackpy trajectory filtering](https://github.com/soft-matter/trackpy/blob/186fa02f048ef0902b6f9804874b701345a22398/trackpy/filtering.py#L7-L28)
  expresses one scientifically named track-length rule as one group operation.
- [Trackpy walkthrough](https://github.com/soft-matter/trackpy-examples/blob/09fb3074a173585d48b5001b5b4b7e6479999598/notebooks/walkthrough.ipynb#L842-L851)
  reports the number of trajectories before and after a population-changing
  filter.
- [saenopy aggregation](https://github.com/rgerum/saenopy/blob/5635cc891952d3afc1530e01d60c0c8763874a3a/saenopy/gui/common/PlottingWindowBase.py#L396-L450)
  uses a direct tabular group operation for mean, standard error, and count.
- [MDAnalysis contacts](https://github.com/MDAnalysis/MDAnalysis/blob/ceb2e3e8e0abf8f2031fc12a54e3305cec3ce3c2/package/MDAnalysis/analysis/contacts.py#L143-L189)
  accepts a small observable function instead of requiring a new analysis class.
- [MDTraj native contacts](https://github.com/mdtraj/mdtraj/blob/9ac9c1c84f507e336b645fea0082c5e899a513a8/examples/native-contact.ipynb)
  fixes heavy-atom, sequence-distance, and native-distance selections from the
  reference state, then evaluates those contacts across the trajectory.
- [Simple membrane protein analysis](https://github.com/philipwfowler/simple-membrane-protein-analysis/blob/eba1512d80acab4983a9496fcb9219e5b865a43f/examples/1-count-lipids-mda.py#L12-L28)
  recomputes a proximity selection inside the frame loop because membership can
  change with particle positions.

## Pandas and Tabular Structure

- [Trackpy linking](https://github.com/soft-matter/trackpy/blob/186fa02f048ef0902b6f9804874b701345a22398/trackpy/linking/utils.py#L73-L89)
  requires one particle label per frame. This makes the observation key visible
  before later table operations.
- [Trackpy drift calculation](https://github.com/soft-matter/trackpy/blob/186fa02f048ef0902b6f9804874b701345a22398/trackpy/motion.py#L297-L315)
  sorts by particle and frame, calculates same-particle differences, and then
  changes the grain to one drift row per frame.
- [Trackpy paired displacement](https://github.com/soft-matter/trackpy/blob/186fa02f048ef0902b6f9804874b701345a22398/trackpy/motion.py#L468-L501)
  aligns two frames through the particle key before calculating displacement.
  Its [paired plot path](https://github.com/soft-matter/trackpy/blob/186fa02f048ef0902b6f9804874b701345a22398/trackpy/plots.py#L813-L825)
  joins first and then applies one shared completeness rule.
- [Trackpy individual MSD](https://github.com/soft-matter/trackpy/blob/186fa02f048ef0902b6f9804874b701345a22398/trackpy/motion.py#L211-L224)
  groups by particle, concatenates with named particle and frame levels, and
  unstacks once for the requested lag-time-by-particle result.
- [saenopy file-level aggregation](https://github.com/rgerum/saenopy/blob/5635cc891952d3afc1530e01d60c0c8763874a3a/saenopy/gui/common/PlottingWindowBase.py#L329-L362)
  reduces repeated time values within each result file before group summaries.
  Its [time-curve path](https://github.com/rgerum/saenopy/blob/5635cc891952d3afc1530e01d60c0c8763874a3a/saenopy/gui/common/PlottingWindowBase.py#L405-L434)
  passes mean, standard error, and valid count directly to plotting.
- [PhysiCell comparative analysis](https://github.com/PhysiCell-Models/collective-invasion/blob/55d25ae04e77fa9208ba2ec43354a7ed2168b60e/scripts/invasive_front_vizualization_of_variance.py#L6-L18)
  adds a category before concatenation and sends the resulting
  [long-form table directly to Seaborn](https://github.com/PhysiCell-Models/collective-invasion/blob/55d25ae04e77fa9208ba2ec43354a7ed2168b60e/scripts/invasive_front_vizualization_of_variance.py#L44-L52).

## Patterns Not to Generalize

- A library can offer automatic quantile filtering for specialist use. Do not
  make it a default project-script step.
- A graphical application can justify a large plotting base class. Do not copy
  that architecture into one-off analysis code.
- Meaningful trajectory or array indices do not require an identifier layer.
  Avoid row-position selection only when table order does not define scientific
  identity.
- A result-based arrow filter can be a documented display choice when the full
  field remains visible. Do not make it an analysis filter or a default cleanup
  step.
- For paired calculations, never remove missing values independently from
  related arrays. For separate summaries of each observable, retain its valid
  data, identifiers, and sample count.
- Do not insert manual placeholder values for absent runs. Preserve run identity
  and represent missing data explicitly.
- Do not copy Trackpy's zero replacement for an unmeasurable MSD as general
  imputation. It is meaningful there only because the associated effective
  measurement count is zero.
- Do not recover group identity from an aggregate such as a maximum label.
  Keep stable metadata in the scientific key or verify its mapping once.

Use repository code as evidence for a decision, not as a template to copy
without its scientific context.
