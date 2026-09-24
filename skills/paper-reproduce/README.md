# Paper Reproduce

[SKILL.md](SKILL.md) is the maintained entrypoint. Choose one objective—reproduction, assessment, or application—and one target depth—model, claim, or result—for each target. Any objective can use any depth. Set qualitative, quantitative, or both comparison criteria when comparison is needed; these are not additional decision stages or a mandatory ladder of work. Existing implementations and analytical evidence can satisfy appropriately scoped targets.

## Package contents

The public skill contains these 14 files:

- [Skill instructions](SKILL.md), [this resource index](README.md), and [invocation metadata](agents/openai.yaml).
- [Agent assignments and review requirements](references/multi-agent-workflow.md), [source audit](references/source-audit.md), [scientific validation](references/scientific-validation.md), and [user-model comparison](references/user-model-comparison.md).
- Current decision diagram: [SVG](assets/decision-stages.svg), [PDF](assets/decision-stages.pdf), [editable TikZ source](assets/decision-stages.tex), and [Mermaid decision specification](assets/decision-stages.mmd).
- Optional legacy target-card resources: [schema-v1 template](assets/target-card-template.yaml), [validator](scripts/validate_target_card.py), and [Python dependency declaration](requirements.txt).

The skill coordinates evidence research, verification, and scientific critique. [Computational Modeling](../computational-modeling/SKILL.md) supplies scientific checks within the selected target. [Model Documentation](../model-documentation/SKILL.md) governs a requested model document, including its plan approval and independent reviews. Use [Scientific Notebook](../scientific-notebook/SKILL.md) and [Data Visualization](../data-visualization/SKILL.md) only for applicable notebook and plotting work. The coordinating workflow preserves one target record and reuses existing authorization.

Execution uses the user's configured project workflow. [Slurm](../slurm/SKILL.md) supports a single CPU batch job when that scope fits; arrays, sweeps, GPUs, and distributed workloads require a suitable user-provided workflow. The package does not supply site accounts, hosts, partitions, or execution permission.

## Diagram preview

The diagram groups the three objectives and three target depths into two stages. One arrow connects the groups; alternatives within each group have equal status, and any objective can pair with any depth. Geometry encodes choices and ordering, not measured quantities. Stage labels retain the distinction without color. The SVG uses outlined lettering and can be viewed without Mermaid support or installed fonts.

The editable layout is `assets/decision-stages.tex`. Keep its labels aligned with `assets/decision-stages.mmd` when changing the decisions. The supplied PDF/SVG pair is approximately 180.18 × 109.50 mm. It uses CMU Sans Serif text and the [Schematic Designer](../schematic-designer/SKILL.md) shared profile. This is an original drawing of the workflow; no upstream example source or artwork was copied.

Rendering requires the sibling schematic-designer resources, a prepared Python environment with Matplotlib, LuaLaTeX/TikZ and its required packages, CMU fonts, and a supported converter (`dvisvgm` or the renderer's validated `pdf2svg` fallback). The optional personal `minimalist` theme is not distributed. Without it, the profile uses Matplotlib's default color cycle and warns that colors differ from the supplied specimens; the labels and diagram structure remain the same. Do not install a namesake package to imitate the theme.

From this skill directory, generate the support style and render into a temporary directory using the bundled helpers:

```sh
paper_diagram_dir="$(python3 -c 'from pathlib import Path; import tempfile; print(Path(tempfile.mkdtemp()).resolve())')"
python3 ../schematic-designer/assets/styles/minimalist_profile.py --tikz > "$paper_diagram_dir/minimalist-profile.sty"
python3 ../schematic-designer/scripts/render_tikz.py assets/decision-stages.tex \
  --include "$paper_diagram_dir/minimalist-profile.sty" \
  --output-dir "$paper_diagram_dir" --basename decision-stages
```

Read the [renderer workflow](../schematic-designer/references/renderer-workflows.md#tikz) for declared inputs and rendering constraints. Inspect both temporary exports at their intended physical size before replacing the supplied pair. Keep generated styles and build debris out of the package. Regeneration is optional for readers and does not execute a scientific simulation.

## Legacy target-card helper

The [schema-v1 template](assets/target-card-template.yaml) and [validator](scripts/validate_target_card.py) remain optional for existing, compatible computational workflows. They require Python and [PyYAML 6.x](requirements.txt). They have not been migrated to the current objective choices or general target record.

The helper accepts `paper_method` or `user_model`, with `model_or_method`, `claim`, or `result` depth. It permits one comparison strength per card, forces `not_applicable` at model level, and requires a comparison at claim/result level. A completed computational card requires run provenance. User-model claim/result prediction also requires nonempty disjoint calibration and evaluation condition lists. Therefore it cannot faithfully represent all current tasks, including a proof without execution, both comparison strengths in one target, or a prediction with no calibration stage. Its agreement verdicts do not certify model validity.

Use a project-native target record for those cases and review it against the current skill's evidence and completion rules. Do not invent runs, calibration, claims, or comparisons to satisfy the helper. Added fields are not automatically validated or included in its specification hash.

For a compatible completed card, from this skill directory:

```sh
python3 scripts/validate_target_card.py /path/to/target-card.yaml
```

Use `--compute` to print the canonical specification hash. A template with unfilled fields is not a valid completed card. Changes to frozen fields require preserved revisions and, for this schema, the declared predecessor-card lineage.
