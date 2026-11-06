# Source catalog brief (for research agents)

Project: `/Users/rnagarajan/dev/math-contest-practice` — a practice app for kids/students built from
**past math competition papers**. It already has grade 5–6 banks (Math Kangaroo Benjamin from the
Austrian English edition 2009–2025 and Kangaroo Canada grades 5–6 2007, 2012–2023; Noetic grade 5/6
free samples; MOEMS Division E free Problem-of-the-Week sets and samples). It is now being extended
to **every level: grades 1–12, undergraduate and graduate**. Your job is to build a catalog of
every competition at your assigned level and, for each one, exactly which past papers are
**publicly and freely available from legitimate sources**, so extraction agents can then turn them
into question banks.

## Legitimate sources only

OK: the organiser's own website (and its official CDN/API/Google Drive links), official national
organisers of the same contest (e.g. Kangaroo country organisers), long-standing archives that the
community and organisers treat as the canonical public record (e.g. the AoPS Wiki problem pages
for AMC/AIME/USAMO, Kiran Kedlaya's Putnam archive, imo-official.org, university department pages).

NOT OK: document-sharing / piracy sites (scribd, pdfcoffee, studocu, coursehero, dokumen.pub,
vdocuments, idoc, pdfslide, yumpu, issuu reposts, intereseducation, random Google Drive reposts by
third parties, Telegram, etc.), paid content, "practice problems in the style of" sites, and
tutoring-company reposts of papers they do not own.

## What to do

1. List every competition you can find for your level (international, US, Canada, UK, Australia,
   Asia, Europe — anything that publishes papers in English). Use web search plus the organisers'
   sites. Be thorough: include small/regional ones if they publish papers.
2. For each competition, determine: levels/divisions and their grade range (map to US grades;
   UK Year N = US grade N−1; "undergraduate" = 13, "graduate" = 14), format (multiple choice /
   short answer / proof), question count per paper, which years are freely available, whether
   **answer keys** and **worked solutions** are available, whether the PDFs are text or scanned
   images, and the exact URL (or URL pattern) of the papers, keys and solutions.
3. **Verify** availability by actually fetching (curl/WebFetch) at least the newest and the oldest
   paper of every competition/level and one answer key. Record what you verified. If a site
   rate-limits, slow down; if downloads return HTML instead of PDF, find the real link.
4. Download the freely available PDFs (papers + answer keys + solutions) for competitions you
   catalog into `sources/pdfs/<bankId>/<subfolder>/` with clear file names
   (`<year>_<level>_paper.pdf`, `<year>_<level>_solutions.pdf`, ...). For HTML-only sources (e.g. AoPS
   wiki) do not scrape everything — just record the URL pattern and confirm one page.
   Skip downloading anything over ~2 GB total for your band; record the rest by URL.
5. Record competitions whose papers are **not** publicly available (paid, members-only, only the
   latest sample, etc.) with what *is* available and how one could legitimately get the rest
   (purchase page, school registration, etc.). The project owner will obtain those separately.

## Output (write both files)

`sources/catalog/<band>.json` — a JSON array, one entry per competition level:

```json
{
  "bankId": "amc",                       // proposed bank id (lowercase, short; one bank per competition family)
  "bankName": "AMC (MAA)",
  "competition": "AMC 8",
  "level": "AMC 8",
  "grades": [6, 7, 8],                   // US grades the level is aimed at (13 = undergrad, 14 = grad)
  "format": "mc",                        // mc | short-answer | proof | mixed
  "questionsPerPaper": 25,
  "minutes": 40,
  "scoring": "1 point per correct, no penalty",
  "years": "1999-2025",                  // freely available years
  "yearsMissing": "2021 not held",
  "papersPerYear": 1,
  "answerKeys": "yes (AoPS wiki answer key pages)",
  "solutions": "yes (AoPS wiki, multiple community solutions)",
  "pdfType": "html",                     // text | scanned | html | mixed
  "urlPattern": "https://artofproblemsolving.com/wiki/index.php/2023_AMC_8_Problems",
  "verified": "fetched 2023 and 1999 problem pages + answer key",
  "downloadedTo": null,                  // or "sources/pdfs/amc/amc8/"
  "estimatedQuestions": 650,
  "public": true,                        // false if not freely available
  "howToGet": null,                      // for non-public: purchase/registration link
  "notes": "figures are Asymptote images on the wiki pages"
}
```

`sources/catalog/<band>.md` — a readable summary: a table of available competitions with years and
estimated question counts, then a section **"Not publicly available"** listing competitions or
years the owner would need to purchase/obtain, with links.

Final reply: total estimated questions available, a short table per competition, the not-public
list, and anything surprising (broken archives, mislabeled files, licensing statements that
forbid reuse).
