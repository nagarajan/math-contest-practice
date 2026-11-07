# Extraction brief (for every extraction agent)

Project root: `/Users/rnagarajan/dev/math-contest-practice`. A personal practice app for kids
(and later adults) turns past competition papers into question banks. You are given ONE work
unit (a bank and a set of papers). Turn every problem in those papers into question objects.

**Read `data/SCHEMA.md` first** — it defines the JSON format, grade labels, points, answer
types (`mc`, `numeric` incl. expressions, `text`, `self` for proofs), solution standards and the
quality bar. This brief only adds the workflow.

## Rules

- Write ONLY your unit's files: `data/raw/<bank>/<slug>.json` (one file per paper, or per
  year when a year's papers belong together) and figures in
  `app/public/qimages/<bank>/<slug>/`. Do not edit any other file, do not run
  `tools/build_banks.py`, do not use git. Other agents are working in parallel.
- Use the Python venv: `.venv/bin/python`.
- Scratch files (renders, helper scripts) go in `/tmp/<your unit id>/` only — other agents use
  `/tmp` at the same time. Pass `--out /tmp/<unit id>/...` to `pdf.py render`.
- Sources: the official PDFs already in `sources/pdfs/<bank>/...` (see the unit). If a paper or
  answer key you need is missing, download it from the official site / URL pattern given in
  `sources/catalog/*.json` (or the Wayback Machine copy of the official site) into the same
  folder. Never use document-sharing / piracy sites (scribd, pdfcoffee, studocu, coursehero,
  dokumen, etc.), not even to look up scoring rules or other facts, and never invent problems.
- Answers must match the official answer key/solutions. Solve every problem yourself; if you
  disagree with the key, re-read; keep the key's answer unless it is clearly a misprint and set
  `reviewNote`.
- Write each paper's JSON as soon as that paper is done (so progress survives interruptions),
  then validate it: `.venv/bin/python tools/validate.py data/raw/<bank>/<slug>.json`. Fix all
  errors. If a file for your slug already exists (a previous attempt), check it, keep what is
  good, and complete it.

## Tools

- `tools/pdf.py info|text|render|crop` — see the header of the file. `text` gives text blocks with
  coordinates; `render --grid` draws a coordinate grid so you can pick crop boxes; view the PNG
  with your file-reading tool. Crop figures to **WebP**:
  `tools/pdf.py crop <pdf> <page> x0 y0 x1 y1 app/public/qimages/<bank>/<slug>/q07.webp`.
  Always look at the crop.
- Scanned PDFs (no text layer): render pages (`--dpi 130`) and read them visually.
- `tools/aops.py page "<AoPS wiki title>"` — AoPS wiki pages (blocked for scripts) via the
  Wayback Machine, converted to text with the LaTeX of every formula and `[FIGURE k: url]` lines
  (with Asymptote source). `tools/aops.py fig <url> <out.webp>` downloads a figure. Examples:
  `"2015 AMC 8 Problems"`, `"2015 AMC 8 Answer Key"`, `"2003 AMC 10A Problems"`,
  `"1985 AIME Problems"`, `"1972 AHSME Problems"`. Dollar amounts in the LaTeX may have lost
  their backslash (`$$24$` means `\$24`) — write money as plain text (`$24` → "\$24" in KaTeX or
  "24 dollars"). The per-problem pages (`"2015 AMC 8 Problems/Problem 2"`) contain community
  solutions you may use as a reference, but write your own solutions.
- `tools/validate.py <file>` — must report no errors.
- The app renders math with KaTeX: convert what it can't render — `tabular` → `array`,
  `eqnarray` → `aligned`, `\[...\]` → `$$...$$`, `\overarc` → `\overgroup` or `\stackrel\frown{AB}`,
  `\$` for money inside math; no `\begin{center}`, `\hfill`, `\vspace`, `\textsc`.

## IDs, slugs and duplicates

- Slug: short, lowercase, unique within the bank, e.g. `at-2015-ecolier`, `ca-2014-g0304`,
  `2015`, `2003-10a`, `gauss7-2012`, `imo-2019`, `isl-2019`. Question id:
  `<bank>-<slug>-<NN>` (2-digit number; for shortlist-style numbering use `a1`, `c3`, `g5`, `n2`).
- Same problem in two papers (AMC 10A/12A share ~10-15 problems; Kangaroo Canada reprints most
  of the Austrian paper; IMO problems appear in the shortlist): extract the problem fully once
  (in the paper with the lower grade) and in the other paper write the question with
  `duplicateOf: <original id>`, `solutions: []`, `image: null`. Before marking a cross-unit
  duplicate, check the original id exists in `data/raw/`.
- `grade`: the label for the paper's level (see SCHEMA.md). Use the most natural US mapping.

## Efficiency

You have many problems to do. Keep moving: transcribe faithfully, solve, write clear
solutions at the right level (short for young kids; complete proofs for olympiad/university),
and don't over-polish. Two approaches when natural; one is fine for proofs and for very
routine problems.

## Final report (your last message)

Short: files written with question counts, any problems you could not complete (and why),
the number of `reviewNote`s, and anything the orchestrator should know (missing papers,
broken sources).
