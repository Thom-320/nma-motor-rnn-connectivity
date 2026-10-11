# Release checklist: preprint and public repository

Prepared on branch `preprint-2026-10` (11 Oct 2026). Nothing has been
submitted, nobody has been contacted, and repository visibility has not been
changed. Everything below is a decision or an action that only Thomas can
take.

## Blocking: do not submit or make the repository public until these are done

- [ ] **Team consent, in writing.** Ask @paulovictormourao, @Keshi and
      @ferorizarmas whether each wants to be (a) a co-author, (b) thanked by
      full name, or (c) not named. For co-authors, also agree on author order,
      affiliations and contributions, and get their approval of the final text.
      Then edit the commented author block and the Acknowledgements in
      `paper/latex/main.tex`, plus the author line in `paper/NOTE.md`. Until
      then they appear only by GitHub handle in the Acknowledgements.
- [ ] **Teammate data in git history.** Two old commits (`3021081`,
      `36ff167`, July 2026) contain a Colab notebook whose metadata includes
      a teammate's Google display name ("Paulo victor Mourão") and Google user
      ID, 74 times. It is no longer in the current files, but making the
      repository public exposes the history. Options: ask him whether he
      minds; or publish a fresh public repository from a squashed snapshot of
      this branch. History was **not** rewritten here.
- [ ] **Verify the numbers yourself.** The AI-use statement says that you
      checked the reported numbers against the analysis outputs. Make that
      true before submitting: compare each table in `main.pdf` with
      `results/robustness/analysis/` (`contrast_summary.csv`,
      `paired_change.csv`, `r3_summary.csv`, `summary_table.md`).
- [ ] **Final read in your own voice.** Read `paper/latex/main.pdf` end to
      end and rewrite anything that does not sound like you, especially the
      Introduction, which now cites Wärnberg & Kumar (2019), Khona et al.
      (2023) and Fruengel & Oberlaender (2025). Each citation was checked
      against Crossref/arXiv metadata and abstracts only; read at least the
      abstract and results of each to confirm it is cited fairly.
- [ ] **Choose the venue.**
      - arXiv (q-bio.NC, cross-list cs.NE): a first-time submitter usually
        needs an **endorsement** from an established arXiv author in that
        category. Ask a supervisor or an NMA mentor; you cannot self-endorse.
      - bioRxiv: no endorsement, but a screening step; choose the
        "New Results" article type and the Neuroscience subject area.
- [ ] **Text licence.** Pick the licence for the preprint at submission time
      (CC BY 4.0 was requested). It applies to the paper text only.
- [ ] **Code licence.** `LICENSE` already exists and is **BSD-3-Clause**
      (copyright "NMA Motor-RNN Connectivity contributors"), not MIT. It was
      not changed: relicensing code that teammates contributed needs their
      agreement, and BSD-3 is already a permissive open-source licence. If you
      still want MIT, decide it together with the team, then update
      `LICENSE`, `CITATION.cff`, `THIRD_PARTY.md` and the Code-availability
      paragraph of `main.tex`.

## Before submission

- [ ] Confirm or edit the **Author contributions** and **Competing
      interests** statements (marked `TODO(Thomas)` in `main.tex`).
- [ ] Confirm your **affiliation** wording ("Universidad del Rosario,
      Bogotá, Colombia") and whether the university expects a department or
      a note that this was independent work. Add an e-mail address and an
      ORCID if you want to be the corresponding author.
- [ ] **Freeze the code.** Merge or tag the release (e.g. `v1.0-preprint`)
      and, optionally, archive it on Zenodo for a DOI. Then replace
      "branch `preprint-2026-10`" in the Code-availability paragraph of
      `main.tex` and in `paper/NOTE.md`.
- [ ] Build the upload with `paper/latex/make_arxiv_bundle.sh` and check
      that `arxiv.zip` compiles on arXiv's preview before you confirm.
- [ ] Update `CITATION.cff`: it currently names "NMA Motor-RNN Connectivity
      contributors" as the software author (the field was missing and is
      required). Replace it with real names once consent is settled, and add
      the preprint as `preferred-citation` once it has an ID.

## Before making the repository public

- [ ] Resolve the git-history item above.
- [ ] Decide what goes on `main`: merge `preprint-2026-10` (it contains the
      robustness branch plus this preparation) or keep `main` as the original
      course project. The README Colab badge points to `main`.
- [ ] Skim `docs/` once more. `docs/CLOUD-SESSION-2026-10.md` and
      `docs/RESEARCH_OVERVIEW.md` are working records that mention an
      "independent audit" and earlier wrong claims. That is honest, but make
      sure you are comfortable publishing them.
- [ ] Change visibility (GitHub settings). Only you can do this.

## Already done on this branch (for reference)

- LaTeX source `paper/latex/main.tex` and compiled `paper/latex/main.pdf`
  (12 pages, no LaTeX errors or undefined references).
- `literature/references.bib`: Khona et al. fixed (authors Khona, Chandra,
  Ma, Fiete; *Neural Computation* 35(11) 2023, not NeurIPS); Fruengel &
  Oberlaender (2025) added; Wärnberg & Kumar (2019) and Gao et al. (2017)
  were already present and are now verified. All seven DOIs/IDs resolve on
  Crossref or arXiv to the recorded metadata.
- "Preregistered": `src/nma_motor_rnn/connectivity.py` already says
  "exploratory, not preregistered"; no change was needed.
- README states the result as "the advantage disappears under a matched
  budget (16 seeds)", and the 8-seed sign reversal is labelled as superseded.
- Secrets scan of the working tree and full git history: no API keys, tokens,
  private keys or Kaggle credentials found. The only e-mail address in history
  is the upstream template author's public contact line. Kaggle metadata uses
  the placeholder `KAGGLE_USERNAME`.
- Tests: 40/40 pass. `scripts/analyze_robustness.py` regenerates every
  analysis table and figure byte-identically to the committed files.
