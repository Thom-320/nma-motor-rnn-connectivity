# Contributing

Everything here is in English, so the whole team can read it. Work from the current Issue, and keep each change small enough that someone can review it in one sitting.

```bash
git switch main
git pull --ff-only
git switch -c your-name/short-task
python3 -m pip install -e '.[dev]'
python3 -m unittest discover -s tests -v
```

Open one Pull Request per idea. Say what changed, why, and how you checked it. Ask one teammate to look at it.

A few things we don't change on our own: the question, the metrics, the seeds, the results, or what we claim they mean. Those need a team decision, written down in the Issue. And nothing secret goes in here — no credentials, no publisher PDFs, no paths from your laptop.
