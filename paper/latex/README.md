# Preprint source

`main.tex` is the submission source for the note in `../NOTE.md`; `main.pdf`
is the compiled version, committed so the result can be read without a TeX
install. Figures are read directly from `results/robustness/figures/` and the
bibliography from `literature/references.bib`, so the PDF cannot drift from
the analysis.

```bash
# Debian/Ubuntu: apt-get install texlive-latex-extra texlive-fonts-recommended lmodern latexmk
cd paper/latex
latexmk -pdf main.tex          # builds main.pdf
./make_arxiv_bundle.sh         # self-contained arxiv.zip (tex + bbl + figures); uploads nothing
```

Regenerate the figures first with `python scripts/analyze_robustness.py` if
the results change.
