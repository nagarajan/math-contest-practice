# Question bank format

Each source paper is extracted into one JSON file: `data/raw/<bank>/<paperSlug>.json`.
The file is a JSON **array of question objects**. Figures are saved as **WebP** under
`app/public/qimages/<bank>/<paperSlug>/` (older banks still have PNGs).

`<bank>` is a bank id from `data/banks.json` (one bank per competition family: `kangaroo`, `noetic`,
`moems`, `amc8`, `putnam`, ...). A new competition needs an entry there first (name, colour,
scoring rules, real paper length/time). `tools/build_banks.py` writes one question file per grade
(`app/public/banks/grade-<g>.json`), so the `grade` field decides who sees a question.

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
- `grade`: the US grades the paper is aimed at, as a label: a single grade (`"5"`) or a range
  (`"5-6"`, `"4-6"`, `"9-12"`), or `"undergrad"` / `"grad"`. The build turns it into
  `grades: [..]` (13 = undergraduate, 14 = graduate). Map other countries' levels to US grades
  (UK Year N = US grade N−1; Kangaroo Pre-Ecolier 1-2, Ecolier 3-4, Benjamin 5-6, Cadet 7-8,
  Junior 9-10, Student 11-12). You may also give `grades` explicitly.
  Examples: MOEMS Division E `"4-6"`, Division M `"6-8"`; AMC 8 `"6-8"`; AMC 10 `"9-10"`;
  AMC 12 / AIME `"11-12"`; Putnam `"undergrad"`.
- `points`: points for a correct answer in that contest, when questions are worth different
  amounts (Kangaroo 3/4/5 as printed; CEMC Pascal/Cayley/Fermat Part A/B/C 5/6/8; UKMT JMC 5/6).
  `null` means 1 point. Same-value contests (AMC: 6 each) set it on every question so the exam
  total matches the real one. Blank/wrong-answer rules (e.g. AMC 1.5 points for a blank) live in
  `data/banks.json`; when a paper's rules differ from the bank's, set `blankPoints` /
  `wrongPoints` on its questions (e.g. old AHSME: `points` 5, `blankPoints` 2 or 1 as printed;
  old UKMT JMC Q16-25: `wrongPoints` -1).
- `timeMinutes`: MOEMS only — the suggested time printed with the problem (e.g. 4). Else `null`.
- `type`:
  - `"mc"` — multiple choice. `choices` must list every option in order with `key` A–E.
    If the options are **pictures**, set each `text` to `""` and make sure the cropped `image`
    shows all options with their (A)…(E) labels.
  - `"numeric"` — answer is a single real number (integer, decimal, fraction like `3/4`, or mixed
    `2 1/2`) or an exact value written as an **explicit expression**: `"3*sqrt(2)/4"`,
    `"2^10-1"`, `"pi/6"`, `"5!"`, `"(1+sqrt(5))/2"` (allowed: digits, `+ - * / ^ ( ) !`, `sqrt`,
    `cbrt`, `pi`, `e`, `abs`, `ln`, `log`, `sin`, `cos`, `tan`; always write `*`). Students'
    typed answers are compared **by value**, so any equivalent form is accepted. For expression
    answers also set `answerDisplay` to the nice KaTeX form (`"$\\frac{3\\sqrt{2}}{4}$"`).
    Put the unit, if any, in `answerUnit` (e.g. `"cm"`, `"sq cm"`, `"dollars"`, `"ways"`), NOT
    in `answer`.
  - `"text"` — short non-numeric answer (a name, a day, a time, a letter). `answer` is the
    canonical form, `acceptedAnswers` lists other acceptable spellings
    (e.g. `["Wednesday", "Wed"]`). Matching is case-insensitive and ignores extra spaces.
  - `"self"` — **self-graded**: proofs, and answers that cannot be typed and checked reliably
    (sets, ordered pairs, intervals, "all n such that ...", functions, constructions). The student
    works it out, reveals the solution and marks themselves. `answer` is a short Markdown/KaTeX
    summary of the final result (for proofs: the key claim/idea in one or two sentences, e.g.
    `"$f(x)=x$ for all $x$ (prove injectivity, then set $y=0$)"`). Self-graded questions are
    practice-only (never in exams). Do NOT use `self` when a numeric/text answer would work.
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
  Use `tools/pdf.py crop ... out.webp` at `--dpi 200` (use `--dpi 150` for very large
  figures); figures from web pages: download, then `tools/pdf.py img in.png out.webp --trim`.
  Leave a few points of margin. Check every crop by viewing it — no cut-off parts, no
  neighbouring question bleeding in.
  If a question needs two separate figures, crop one region covering both.
- `solutions`: **1–3 solution approaches, aim for 2 genuinely different approaches** when
  natural (e.g. "Work backwards" vs "Draw a model", "Count systematically" vs "Use symmetry").
  Write for a strong student **at the question's grade level**: for grades 1–6 short steps,
  concrete numbers, no heavy algebra; for middle/high school normal algebra and contest
  techniques; for olympiad and university problems complete, rigorous proofs (a reader should be
  able to follow every step; lemmas stated and proved). Use Markdown lists and KaTeX. End with
  the answer stated clearly (e.g. "**Answer: (D) 5 kg**"; for proofs end with "∎"). If an
  official solution exists in the source, base the first approach on it (re-worded, not
  copied verbatim), and add your own genuinely different second approach when one exists
  (a second proof idea, a cleaner/brute-force check, etc.). One rigorous approach is acceptable
  for hard proof problems where no natural second approach exists.
- `topics`: 1–3 from this fixed list:
  `arithmetic`, `number-theory`, `fractions-decimals`, `algebra`, `patterns`, `geometry`,
  `measurement`, `counting`, `probability`, `logic`, `spatial`, `time-calendar`, `money`, `rates`,
  `polynomials`, `inequalities`, `functional-equations`, `sequences-series`, `trigonometry`,
  `complex-numbers`, `statistics`, `graph-theory`, `games`, `calculus`, `analysis`,
  `linear-algebra`, `abstract-algebra`, `real-analysis`, `complex-analysis`, `topology`,
  `differential-equations`.
- `difficulty`: 1 (easy), 2 (medium), 3 (hard). Kangaroo: 3→1, 4→2, 5→3 points. Others: your
  judgement (MOEMS: ≤4 min → 1, 5–6 min → 2, ≥7 min → 3).
- `duplicateOf`: if this exact problem (same question, same numbers) already exists in another
  extracted paper — in any bank — put that question's `id` here (the original then also shows
  up for this paper's grades, e.g. problems shared by AMC 10A and AMC 12A). You still need prompt/answer/choices, but you
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
