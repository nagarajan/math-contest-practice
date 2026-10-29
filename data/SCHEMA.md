# Question bank format

Each source paper is extracted into one JSON file: `data/raw/<bank>/<paperSlug>.json`.
The file is a JSON **array of question objects**. Figures are saved as PNGs under
`app/public/qimages/<bank>/<paperSlug>/`.

`<bank>` is one of `kangaroo`, `noetic`, `moems`.

## Question object

```json
{
  "id": "kangaroo-at-2015-07",
  "bank": "kangaroo",
  "source": {
    "contest": "Kangaroo (Austria, English edition)",
    "paper": "Benjamin (Grades 5-6)",
    "year": 2015,
    "number": 7,
    "url": "https://www.matematica.pt/en/docs/kangaroo/enunciados/2015/2015_Benjamin.pdf"
  },
  "grade": "5-6",
  "points": 3,
  "timeMinutes": null,
  "type": "mc",
  "prompt": "Rita and Dita are standing on a see-saw as shown. How much does Dita weigh?",
  "image": "qimages/kangaroo/at-2015/q07.png",
  "choices": [
    { "key": "A", "text": "2 kg" },
    { "key": "B", "text": "3 kg" },
    { "key": "C", "text": "4 kg" },
    { "key": "D", "text": "5 kg" },
    { "key": "E", "text": "6 kg" }
  ],
  "answer": "D",
  "acceptedAnswers": null,
  "answerUnit": null,
  "solutions": [
    { "title": "Compare the two pictures", "body": "Markdown, step by step ..." },
    { "title": "Write equations", "body": "..." }
  ],
  "topics": ["logic", "algebra"],
  "difficulty": 1,
  "duplicateOf": null,
  "reviewNote": null
}
```

### Field rules

- `id`: `<bank>-<paperSlug>-<NN>` with a 2-digit question number (MOEMS/other sources may use
  any stable unique suffix, e.g. `moems-potw-2026-06-29`).
- `source.number`: question number in the original paper (or null if not applicable).
- `grade`: `"5-6"` for Kangaroo Benjamin / Canada grade 5-6; `"5"` or `"6"` for Noetic; `"4-6"` for
  MOEMS Division E, `"6-8"` for MOEMS Division M.
- `points`: Kangaroo only — 3, 4 or 5 as printed on the paper. `null` for other banks.
- `timeMinutes`: MOEMS only — the suggested time printed with the problem (e.g. 4). Else `null`.
- `type`:
  - `"mc"` — multiple choice. `choices` must list every option in order with `key` A–E.
    If the options are **pictures**, set each `text` to `""` and make sure the cropped `image`
    shows all options with their (A)…(E) labels.
  - `"numeric"` — answer is a number (integer, decimal, fraction like `3/4`, or mixed `2 1/2`).
    `answer` is the canonical value as a string (`"42"`, `"3/4"`, `"12.5"`). Put the unit, if
    any, in `answerUnit` (e.g. `"cm"`, `"sq cm"`, `"dollars"`, `"ways"`), NOT in `answer`.
  - `"text"` — short non-numeric answer (a name, a day, a time, a letter). `answer` is the
    canonical form, `acceptedAnswers` lists other acceptable spellings
    (e.g. `["Wednesday", "Wed"]`). Matching is case-insensitive and ignores extra spaces.
- `choices`: `null` unless `type` is `"mc"`.
- `answer`: for `mc` the correct key letter. **Must match the official answer key.**
- `acceptedAnswers`: optional array of additional accepted answer strings (numeric or text).
  E.g. a time answer `"3:00 PM"` with `["3 PM", "3pm", "15:00"]`.
- `prompt`: the question text, faithfully transcribed and lightly cleaned (fix obvious
  typos/German leftovers in translated papers, e.g. "und" → "and", "mehr als" → "more than").
  Do not include the answer choices in the prompt. Markdown is allowed. Use KaTeX math with
  `$...$` (inline) or `$$...$$` (display) for fractions, exponents, etc. (e.g. `$\frac{19}{8}$`).
  Refer to the figure naturally ("as shown in the picture").
- `image`: path relative to `app/public` (starts with `qimages/`), or `null` when the question
  has no figure. Crop **only the figure (and picture-choices row if the choices are pictures)**,
  not the whole question text, unless the text is embedded in the figure and inseparable.
  Use `tools/pdf.py crop` at `--dpi 200`. Leave a few points of margin. Check every crop by
  viewing it — no cut-off parts, no neighbouring question bleeding in.
  If a question needs two separate figures, crop one region covering both.
- `solutions`: **1–3 solution approaches, aim for 2 genuinely different approaches** when
  natural (e.g. "Work backwards" vs "Draw a model", "Count systematically" vs "Use symmetry").
  Write for a bright 5th grader: short steps, concrete numbers, no heavy algebra unless it is
  simple. Use Markdown lists and KaTeX. End with the answer stated clearly (e.g.
  "**Answer: (D) 5 kg**"). If an official solution exists in the source, base the first
  approach on it (re-worded), and add your own second approach.
- `topics`: 1–3 from this fixed list:
  `arithmetic`, `number-theory`, `fractions-decimals`, `algebra`, `patterns`, `geometry`,
  `measurement`, `counting`, `probability`, `logic`, `spatial`, `time-calendar`, `money`, `rates`.
- `difficulty`: 1 (easy), 2 (medium), 3 (hard). Kangaroo: 3→1, 4→2, 5→3 points. Others: your
  judgement (MOEMS: ≤4 min → 1, 5–6 min → 2, ≥7 min → 3).
- `duplicateOf`: if this exact problem (same question, same numbers) already exists in another
  extracted paper, put that question's `id` here. You still need prompt/answer/choices, but you
  may set `solutions` to `[]` and `image` to `null` for duplicates.
- `reviewNote`: `null` normally. If you could not verify the official answer with your own
  solution, or the scan was unreadable, write a short note here (the question is kept but
  flagged for a human to check).

## Quality bar

- Solve every problem yourself and confirm your answer matches the official key. If they
  disagree, re-read the problem and figure carefully; the official key wins unless it is clearly
  a misprint — then set `reviewNote`.
- Never invent problems. Never skip a problem because it has a figure — crop the figure.
- Validate the output file with `.venv/bin/python tools/validate.py data/raw/<bank>/<file>.json`.
