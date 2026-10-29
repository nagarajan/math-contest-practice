# Math Contest Practice

A local web app for practicing past Math Kangaroo, Noetic and Math Olympiad (MOEMS) problems
at the grade 5–6 level.

## Run it

```sh
./start.sh
```

This rebuilds the question banks and opens http://localhost:5175. Everything (profiles,
history, settings) is stored in the browser on this device; nothing is sent anywhere.
To use it on an iPad on the same Wi-Fi, run `cd app && npx vite --host --port 5175` and open
the printed "Network" address on the iPad (history is then stored in the iPad's browser).

## Layout

| Path | What |
| --- | --- |
| `sources/pdfs/` | Downloaded source papers (see `sources/noetic_sources.md` for Noetic) |
| `data/SCHEMA.md` | Question format and quality rules |
| `data/raw/<bank>/<paper>.json` | One file per source paper |
| `app/public/qimages/` | Figures cropped from the papers |
| `app/public/banks/` | Generated bank files (from `tools/build_banks.py`) |
| `tools/pdf.py` | Render / crop helper for PDFs |
| `tools/validate.py` | Checks a paper file against the schema |
| `app/` | React + TypeScript app (`npm test` runs the unit tests) |

## Adding purchased papers later

1. Put the PDFs in `sources/pdfs/<bank>/purchased/` (bank = `kangaroo`, `noetic` or `moems`).
2. Ask the agent to extract them following `data/SCHEMA.md` into `data/raw/<bank>/<slug>.json`
   (one file per paper, figures into `app/public/qimages/<bank>/<slug>/`), with 2 solution
   approaches per question and the official answer key.
3. Run `.venv/bin/python tools/validate.py data/raw/<bank>/<slug>.json`, then `./start.sh`.

Duplicates are handled at build time: questions with `duplicateOf` are dropped, and the build
prints "possible duplicate" pairs for near-identical prompts across papers.

## How practice picks questions

- Unseen questions have weight 1, questions last answered **wrong** weight 3, questions last
  answered **right** weight 0.2 (and less after repeated correct answers).
- A question that was just answered cannot come back until at least 10 other questions have been
  answered or 1 hour has passed.
- Exam answers count too: questions missed in an exam come back more often in practice.

## Exams

30 questions (configurable in Settings), ordered easy → hard, with a running clock and an
optional time limit. Scoring follows each competition: Kangaroo questions are worth 3/4/5 points
(no penalty for wrong answers, as in Math Kangaroo USA), Noetic and MOEMS questions 1 point
each. A mixed exam splits its questions evenly across the three banks. A focused Kangaroo exam uses ten 3-point, ten 4-point and ten 5-point questions.
