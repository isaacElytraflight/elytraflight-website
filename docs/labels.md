# Labels

New issues and pull requests use the names in [`.github/labels.yml`](../.github/labels.yml). GitHub does not read that file on its own. Create any name that is not already on the repository, with the color and description in the file. Do not rename a label that already exists.

Four names are already on the repository. Keep their current color and description:

| Name | Color | Description |
|---|---|---|
| `type:content` | `0e8a16` | Question banks, explainers, or the skill graph |
| `priority:P1` | `d93f0b` | High priority |
| `priority:P2` | `fbca04` | Normal priority |
| `size:L` | `bfd4f2` | Large: several PRs or batches |

## How to apply them

- One `type:*` label. `type:content` is a bank, an explainer, or the skill graph. `type:infra` is hosting, CI, dependencies, or access.
- One `area:*` label. Course onboarding is `area:courses`. A quality-gate or quota change is `area:content-qa`.
- One `priority:P0` through `priority:P3` label. P0 is broken for learners or blocking a launch. P1 is high. P2 is normal. P3 is low.
- One `size:S`, `size:M`, or `size:L` label.

The open roadmap issues #55 through #69 already have `type:content`, a priority, and `size:L`. Add `area:content-qa` to #55 and `area:courses` to #56 through #69.

The default GitHub labels (`bug`, `enhancement`, and the rest) can stay. New work uses the prefixed names above.
