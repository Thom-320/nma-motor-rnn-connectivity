# Contributing

All repository communication is in English. Every change starts from a GitHub Issue and has one scientific purpose.

## Scientific ownership

The research question, hypothesis, primary outcome, and claim boundary require approval from every team member. The coordinator records the decision but does not make it alone. Before a protocol is frozen, each member contributes a proposed question or design change, a falsifying observation, and a limitation.

Each work-block assignment must affect at least one part of the scientific project: protocol, model conditions, analysis, measurement validity, interpretation, or communication. Running checks is valuable, but it is not a person's only contribution.

The notebook is generated after the relevant PRs are reviewed. One person performs that mechanical step, while authorship remains visible in the protocol, code, tests, analyses, figures, and PR history.

## How work is split

Work is divided by scientific responsibility. Separate files and PRs make those contributions easier to review, but file ownership is not a substitute for scientific ownership.

For the current control:

| Responsibility | Main working area |
|---|---|
| Research question and protocol | Shared decision in Issue #6; recorded in `docs/CONTROL_PROTOCOL.md` |
| Model conditions and execution | `src/nma_motor_rnn/connectivity.py`, `results/` |
| Paired statistical analysis and figures | analysis and figure code, result tables, results paragraph |
| Measurement validity | `tests/`, metadata audit, validity statement |
| Integration and claim boundary | research overview, notebook builder, PR review |

Do not edit `notebooks/*.ipynb` by hand. Change `scripts/build_notebook.py` and regenerate the notebook after its source, tests, analysis, and results are reviewed. If one branch depends on another, record that dependency in both Issues and rebase after the prerequisite merges.

If one person is making the scientific decisions while others only run checks, stop and reassign scientific ownership before continuing.

## 1. Claim an issue

Comment on the issue, confirm the deliverable and reviewer, and note whether the work is confirmatory or exploratory. Do not change metrics, seeds, hypotheses, or inclusion rules after inspecting results without documenting that change as exploratory.

## 2. Create a branch

```bash
git switch main
git pull --ff-only
git switch -c your-name/short-task
```

Only one person should edit the project notebook at a time. Put reusable logic in `src/nma_motor_rnn/`; the notebook should explain and orchestrate it.

## 3. Run checks

```bash
python3 -m pip install -e '.[dev]'
python3 -m unittest discover -s tests -v
python3 -m json.tool notebooks/Motor_RNN_Project.ipynb > /dev/null
python3 -m jupyter nbconvert \
  --to notebook --execute notebooks/Motor_RNN_Project.ipynb \
  --output /tmp/Motor_RNN_Project.executed.ipynb \
  --ExecutePreprocessor.timeout=180
```

## 4. Commit and open a Pull Request

```bash
git status
git diff --check
git add <specific-files>
git commit -m "Describe the focused change"
git push -u origin HEAD
```

The Pull Request must link its issue, identify scientific status, list checks, and state whether results or claim boundaries change. A different team member reviews it. Resolve all review conversations before merge.

## Scientific invariants

- The independent replicate is the network seed, not a trial or time point.
- Primary performance uses the original fixed motor decoder; PCA never replaces it.
- Online feedback loss and held-out velocity NMSE remain separate.
- Density conditions remain paired within seed.
- Null, contradictory, and pilot results remain visible.
- The completed Q2 claim applies only to architectures where all existing recurrent weights are plastic.
- The full control cannot start until all team members approve `docs/CONTROL_PROTOCOL.md`.
- Never commit credentials, access tokens, publisher PDFs, or local absolute paths.
