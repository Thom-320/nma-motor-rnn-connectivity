#!/usr/bin/env bash
# Build a self-contained arXiv upload (main.tex, main.bbl, figures/) in
# paper/latex/arxiv/ and zip it.  Does not upload anything.
set -euo pipefail
cd "$(dirname "$0")"
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
rm -rf arxiv arxiv.zip
mkdir -p arxiv/figures
cp ../../results/robustness/figures/*.png arxiv/figures/
# arXiv needs the .bbl next to the .tex; point \bibliography at it.
sed 's#\\bibliography{../../literature/references}#\\bibliography{main}#' main.tex > arxiv/main.tex
cp main.bbl arxiv/main.bbl
(cd arxiv && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex >/dev/null && latexmk -c >/dev/null && rm -f main.pdf)
(cd arxiv && zip -qr ../arxiv.zip .)
echo "Wrote paper/latex/arxiv.zip"
