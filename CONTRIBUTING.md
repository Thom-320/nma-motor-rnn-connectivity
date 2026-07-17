# Contributing

Repository work is in English. Use only the current GitHub Issue and keep each change small.

```bash
git switch main
git pull --ff-only
git switch -c your-name/short-task
python3 -m pip install -e '.[dev]'
python3 -m unittest discover -s tests -v
```

Open one focused Pull Request, explain what changed and how it was checked, and request one teammate review.

Do not change the question, metrics, seeds, results, or claims without a recorded team decision. Never commit credentials, publisher PDFs, or local paths.
