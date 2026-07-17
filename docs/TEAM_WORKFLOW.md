# Team workflow

This workflow supports 3–5 students while preserving NMA's goals: balanced skills, peer teaching, iterative questions, TA feedback, and participation by every member.

## Shared scientific decisions

The project question, hypothesis, primary outcome, and interpretation are group decisions. Before freezing a protocol, every member proposes a change, identifies a result that would count against the hypothesis, and names a limitation. The coordinator records the consensus and TA feedback; the coordinator does not decide for the group.

## Rotating roles

Assign roles at the start of each project block or issue; do not make one person the permanent coder.

- **Scientific coordinator:** records the agreed question, hypotheses, and claim boundary.
- **Implementation owner:** authors the focused code or analysis change.
- **Reproducibility reviewer:** independently runs checks and reviews the Pull Request.
- **Literature/documentation lead:** maintains citations, proposal, abstract, and explanations.
- **Presentation/status lead:** updates project status and prepares the shared story.

With three students, combine the last two roles. Every student should author at least one contribution, review at least one contribution, and explain one figure or result.

## GitHub coordination

Use labeled Issues and the `NMA W3D5 Final Project` milestone. There is no separate Project board.

Each issue records:

- owner and reviewer;
- scientific purpose;
- confirmatory or exploratory status;
- concrete deliverable;
- definition of done;
- blocker or TA decision, if any.

Recommended labels are `q1`, `q2`, `code`, `science`, `literature`, `documentation`, `figure`, `confirmatory`, `exploratory`, `blocked`, and `needs-review`.

The pinned status issue receives a short end-of-block comment: completed work, current result, blocker, next owner, and next decision. Use GitHub to record code and decisions; keep group discussion, abstract workshopping, and TA conversations collaborative.

## Pull Request rule

One issue maps to one focused branch and normally one Pull Request. The author cannot be the only reviewer. A PR must:

1. link its issue;
2. state why the change is needed;
3. identify confirmatory or exploratory status;
4. list tests and Colab checks;
5. disclose any result or claim change;
6. receive one peer approval and pass `scientific-checks`.

The notebook is regenerated after the relevant source, tests, analysis, figures, and results are reviewed. One person performs the regeneration step to avoid notebook conflicts; this does not make that person the scientific owner. Every contributor's PR must affect the protocol, model, analysis, validity assessment, interpretation, or communication that the notebook reports.

## Suggested project rhythm

- **Start of block, 10 minutes:** review the pinned status issue, assign roles, claim issues.
- **During work:** use issue comments for decisions and small branches for implementation.
- **Before merge:** reviewer reruns tests and checks the scientific interpretation.
- **End of block, 10 minutes:** update status, record TA feedback, and assign the next decision.
- **Abstract/presentation days:** every member drafts or rehearses independently before the group combines the strongest version, following NMA guidance.

## Onboarding checklist

1. Read `README.md` and `docs/RESEARCH_OVERVIEW.md`.
2. Open the project notebook in Colab using `RUN_MODE="view"`.
3. Run `RUN_MODE="smoke"` once.
4. Claim a labeled issue and name a reviewer.
5. Create a branch and open a small first Pull Request.
6. Add your name, GitHub handle, and current rotating role to the pinned status issue.
