#!/usr/bin/env python3
"""Generate extraction work units into sources/work/queue.json (keeps status of existing units)."""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(ROOT, "sources", "work", "queue.json")
units = []


def U(uid, phase, bank, est, task):
    units.append({"id": uid, "phase": phase, "bank": bank, "est": est, "task": task})


def groups(years, size):
    years = list(years)
    return [years[i:i + size] for i in range(0, len(years), size)]


def yr(g):
    return f"{g[0]}" if len(g) == 1 else f"{g[0]}-{g[-1]}"


# ---------------------------------------------------------------- phase 1: Kangaroo
KA = "sources/pdfs/kangaroo"
KANG_COMMON = (
    "Austrian English edition: `{ka}/austria/<Y>_<Level>.pdf`, answer keys in `{ka}/austria/<Y>_Answers.pdf`. "
    "Kangaroo Canada: `{ka}/canada/<Y>gr<NNNN>e.pdf` (older years `<Y>gr<NNNN>.pdf`); answers in "
    "`{ka}/canada/answerkeys_api_2014-2026.json`, `<Y>_answers_allgrades.pdf`, `<Y>anAllG.pdf` or `<Y>an<NNNN>.pdf`. "
    "Canada papers reprint most of the international (Austrian) problems: extract each problem once (Austrian version first), "
    "then the Canadian paper with `duplicateOf` for the shared problems and full extraction for its own ones. "
    "Slugs `at-<Y>-<level>` (lowercase level name) and `ca-<Y>-g<NNNN>`. Points 3/4/5 as printed (sections). "
    "The Benjamin (grades 5-6) papers are already done (`data/raw/kangaroo/at-<Y>.json`, `ca-<Y>.json`) — do not redo them."
).format(ka=KA)
kang_levels = [
    ("Felix", "0102", "1-2", [list(range(2012, 2019)), list(range(2019, 2026))]),
    ("Ecolier", "0304", "3-4", [[2002, 2003, 2007, 2009, 2010, 2011], list(range(2012, 2016)), list(range(2016, 2020)), list(range(2020, 2026))]),
    ("Kadett", "0708", "7-8", [[2002, 2003, 2007, 2009, 2010, 2011], [2012, 2013, 2014], [2015, 2016, 2017], [2018, 2019, 2020, 2021], [2022, 2023, 2024, 2025]]),
    ("Junior", "0910", "9-10", [[2002, 2003, 2007, 2009, 2010, 2011], [2012, 2013, 2014], [2015, 2016, 2017], [2018, 2019, 2020, 2021], [2022, 2023, 2024, 2025]]),
    ("Student", "1112", "11-12", [[2002, 2003, 2007, 2009, 2010, 2011], [2012, 2013, 2014], [2015, 2016, 2017], [2018, 2019, 2020, 2021], [2022, 2023, 2024, 2025]]),
]
for level, code, grade, gs in kang_levels:
    for g in gs:
        U(f"kangaroo-{level.lower()}-{yr(g)}", 1, "kangaroo", 25 * len(g),
          f"Math Kangaroo level {level} (grades {grade}, Canada `gr{code}`) for the years {', '.join(map(str, g))} "
          f"(whichever of the Austrian and Canadian papers exist for those years; Austrian Felix starts 2014). " + KANG_COMMON
          + (" The 2011 Canadian 'OnlineTraining' files for this level belong to this unit too." if 2011 in g and code in ("0304", "0708") else "")
          + (" The 2007 `sl<NNNN>E.pdf` files are Canadian official solutions — use them." if 2007 in g else ""))

# ---------------------------------------------------------------- phase 1: CEMC
CE = "sources/pdfs/cemc"
CEMC_NOTE = ("Official papers and solutions are in `{d}` (list the directories to confirm file names). "
             "Use the official solutions as the first approach. `source.contest` is e.g. \"Gauss Contest (CEMC)\", "
             "\"Pascal Contest (CEMC)\", \"Euclid Contest (CEMC)\". See `data/raw/cemc/gauss7-2016.json` for the finished format. "
             "Other agents work on other CEMC slugs at the same time; touch only your own.")
for g in groups(range(1998, 2027), 3):
    U(f"cemc-gauss-{yr(g)}", 1, "cemc", 45 * len(g),
      f"CEMC Gauss Contest, grade 7 and grade 8 papers ({', '.join(map(str, g))}). " + CEMC_NOTE.format(d=f"{CE}/gauss/")
      + " Gauss 7 and 8 share several problems each year (the solutions booklet shows which): extract shared ones in the grade 7 paper and mark the grade 8 copies `duplicateOf`. "
      "Slugs `gauss7-<Y>`, `gauss8-<Y>`; grade labels \"7\" and \"8\". Points: Part A 5, Part B 6, Part C 8.")
for g in groups(range(1997, 2027), 2):
    U(f"cemc-pcf-{yr(g)}", 1, "cemc", 70 * len(g),
      f"CEMC Pascal (grade 9), Cayley (grade 10) and Fermat (grade 11) contests ({', '.join(map(str, g))}). "
      + CEMC_NOTE.format(d=f"{CE}/pascal/, {CE}/cayley/, {CE}/fermat/")
      + " The three papers of a year share some problems: extract in the lowest grade's paper and mark the others `duplicateOf`. "
      "Slugs `pascal-<Y>`, `cayley-<Y>`, `fermat-<Y>`. Points: Part A 5, Part B 6, Part C 8.")
for g in groups(range(1998, 2027), 5):
    U(f"cemc-euclid-{yr(g)}", 1, "cemc", 25 * len(g),
      f"CEMC Euclid Contest (grade 12), {', '.join(map(str, g))}. " + CEMC_NOTE.format(d=f"{CE}/euclid/")
      + " Each problem part (1(a), 1(b), ...) is its own question, numbered like `03b`; answer-only parts as numeric/text, "
      "'show that'/'prove' parts and parts asking for several values as `self`. Slug `euclid-<Y>`; grade \"12\"; points as printed.")
for g in groups(range(2003, 2027), 4):
    U(f"cemc-fgh-{yr(g)}", 1, "cemc", 36 * len(g),
      f"CEMC Fryer (grade 9), Galois (grade 10) and Hypatia (grade 11) contests, {', '.join(map(str, g))}. "
      + CEMC_NOTE.format(d=f"{CE}/fryer/, {CE}/galois/, {CE}/hypatia/")
      + " Full-solution contests with parts: one question per part (ids like `cemc-fryer-2012-02c`); short-answer parts with a single value "
      "numeric/text, explanations/proofs and parts asking for several values `self`. Match the conventions of existing "
      "`data/raw/cemc/fryer-*.json` files (else `euclid-2018.json`). Grades \"9\" Fryer, \"10\" Galois, \"11\" Hypatia. "
      "If the three papers of a year share a problem, extract it in the lowest grade and mark the others `duplicateOf`. "
      "Slugs `fryer-<Y>`, `galois-<Y>`, `hypatia-<Y>`. Points as printed (split a problem's 10 marks sensibly if parts are unmarked).")
for g in groups(range(2011, 2026), 5):
    U(f"cemc-cimc-csmc-{yr(g)}", 1, "cemc", 30 * len(g),
      f"CEMC Canadian Intermediate (CIMC, grades 9-10) and Senior (CSMC, grades 11-12) Mathematics Contests, {', '.join(map(str, g))}. "
      + CEMC_NOTE.format(d=f"{CE}/cimc/, {CE}/csmc/")
      + " `source.contest` \"Canadian Intermediate Mathematics Contest (CEMC)\" / \"Canadian Senior Mathematics Contest (CEMC)\". "
      "Part A short answers (numeric/text, ids like `cemc-cimc-2013-a3`), Part B full solutions (one question per part, ids like "
      "`cemc-cimc-2013-b2c`; `self` where an explanation/proof is required or several values are asked). Match existing "
      "`data/raw/cemc/cimc-*.json` files. Grades \"9-10\" CIMC, \"11-12\" CSMC. "
      "They share problems: extract in CIMC, `duplicateOf` in CSMC. Slugs `cimc-<Y>`, `csmc-<Y>`. Points as printed.")

# ---------------------------------------------------------------- phase 1: AMC / AIME (AoPS wiki via tools/aops.py)
AMC_NOTE = ("Source: AoPS wiki via `tools/aops.py page \"<title>\"` (problems page, answer key page, and per-problem pages for reference). "
            "Set `source.url` to the official AoPS wiki page URL (https://artofproblemsolving.com/wiki/index.php/<Title_with_underscores>). "
            "Transcribe the problem text and choices from the LaTeX; download figures with `tools/aops.py fig`. "
            "If a problems page is missing problems, use the per-problem pages. Archived pages are occasionally vandalized: "
            "if a statement looks wrong or disagrees with the answer key, cross-check the per-problem page. Finished-format examples: `data/raw/amc8/2015.json`, "
            "`data/raw/amc10/2015-10a.json`, `data/raw/amc12/2015-12a.json`, `data/raw/aime/2016-i.json`. "
            "Other agents work on other years of the same bank at the same time; touch only your own files. ")
for g in [list(range(1999, 2004)), list(range(2004, 2009)), list(range(2009, 2014)), list(range(2014, 2019)), [2019, 2020, 2022, 2023, 2024, 2025]]:
    U(f"amc8-{yr(g)}", 1, "amc8", 25 * len(g),
      f"AMC 8 for {', '.join(map(str, g))} (titles like \"2015 AMC 8 Problems\", \"2015 AMC 8 Answer Key\"). " + AMC_NOTE
      + "Slug `<Y>`; grade \"6-8\"; points null (1 each); contest \"AMC 8\". If a year was not held, skip it.")
for g in [list(range(1985, 1990)), list(range(1990, 1995)), list(range(1995, 1999))]:
    U(f"amc8-ajhsme-{yr(g)}", 1, "amc8", 25 * len(g),
      f"AJHSME (the AMC 8's predecessor) for {', '.join(map(str, g))} (titles like \"1990 AJHSME Problems\", \"1990 AJHSME Answer Key\"). " + AMC_NOTE
      + "Slug `ajhsme-<Y>`; grade \"6-8\"; points null; contest \"AJHSME\".")
amc1012 = [[2000, 2001]] + [[y] for y in range(2002, 2026)]
for g in amc1012:
    if g == [2021]:
        for part, papers in (("spring", "2021 AMC 10A, 10B, 12A, 12B (spring)"), ("fall", "2021 Fall AMC 10A, 10B, 12A, 12B (titles like \"2021 Fall AMC 10A Problems\")")):
            U(f"amc1012-2021-{part}", 1, "amc10", 75,
              f"{papers}. " + AMC_NOTE + "Bank `amc10` for AMC 10 papers (grade \"9-10\") and `amc12` for AMC 12 papers (grade \"11-12\"), "
              "files `data/raw/amc10/<slug>.json` / `data/raw/amc12/<slug>.json`, slugs like `2021-10a` / `2021f-10a`. "
              "Problems shared by the 10 and 12 versions: extract in the AMC 10 paper, mark the AMC 12 copy `duplicateOf`. Points 6 each.")
        continue
    papers = "AMC 10 and AMC 12 (2000-2001: one paper each; the AMC 10 started in 2000)" if g == [2000, 2001] else "AMC 10A, 10B, 12A, 12B"
    U(f"amc1012-{yr(g)}", 1, "amc10", 75 * len(g),
      f"{papers} for {', '.join(map(str, g))} (titles like \"2003 AMC 10A Problems\", \"2003 AMC 12A Answer Key\", \"2001 AMC 10 Problems\"). " + AMC_NOTE
      + "Bank `amc10` for AMC 10 papers (grade \"9-10\") and `amc12` for AMC 12 papers (grade \"11-12\"): files `data/raw/amc10/<slug>.json` / "
      "`data/raw/amc12/<slug>.json`, slugs like `2003-10a`, `2003-12b`, `2001-10`. Problems shared by the 10 and 12 versions of the same "
      "letter: extract in the AMC 10 paper and mark the AMC 12 copy `duplicateOf`. Points 6 each (blank 1.5 is in banks.json).")
ahsme = [(1950, 1952), (1953, 1955), (1956, 1958), (1959, 1961), (1962, 1964), (1965, 1967), (1968, 1970), (1971, 1973),
         (1974, 1977), (1978, 1981), (1982, 1985), (1986, 1989), (1990, 1993), (1994, 1996), (1997, 1999)]
for a, b in ahsme:
    U(f"ahsme-{a}-{b}", 1, "amc12", 40 * (b - a + 1),
      f"AHSME {a}-{b} (titles like \"1972 AHSME Problems\" / \"1972 AHSME Answer Key\"; some old years are titled e.g. \"1950 AHSME Problems\"). " + AMC_NOTE
      + "Bank `amc12`, file `data/raw/amc12/ahsme-<Y>.json`, grade \"9-12\", contest \"AHSME\". Points: use that year's official rule "
      "(1950-59 part-based 2/3/4 points; 1960-73 by part; 1974-1999 5 per correct with `blankPoints` 2 (1974-1985) / 2 (1986-1993) / 2.5 (1994-1999); "
      "check the AoPS 'Instructions'/AHSME pages, set `points`/`blankPoints` per question and say what you used in the final report).")
for g in [list(range(1983, 1988)), list(range(1988, 1994)), list(range(1994, 2000))]:
    U(f"aime-{yr(g)}", 1, "aime", 15 * len(g),
      f"AIME {', '.join(map(str, g))} (titles like \"1990 AIME Problems\", \"1990 AIME Answer Key\"). " + AMC_NOTE
      + "Bank `aime`, slug `<Y>`, grade \"9-12\", type numeric (integer 0-999), points null.")
for g in [list(range(2000, 2004)), list(range(2004, 2008)), list(range(2008, 2012)), list(range(2012, 2016)), list(range(2016, 2020)), list(range(2020, 2024)), [2024, 2025]]:
    U(f"aime-{yr(g)}", 1, "aime", 30 * len(g),
      f"AIME I and AIME II for {', '.join(map(str, g))} (titles like \"2010 AIME I Problems\", \"2010 AIME II Answer Key\"). " + AMC_NOTE
      + "Bank `aime`, slugs `<Y>-i`, `<Y>-ii`, grade \"9-12\", type numeric (integer 0-999), points null.")

# ---------------------------------------------------------------- phase 1: Purple Comet, MATHCOUNTS, MOEMS, Noetic
PC = "sources/pdfs/purplecomet"
for g in groups(range(2004, 2027), 3):
    U(f"purplecomet-{yr(g)}", 1, "purplecomet", 50 * len(g),
      f"Purple Comet! Math Meet middle school and high school papers, {', '.join(map(str, g))}: `{PC}/ms/` and `{PC}/hs/` "
      "(`<Y>_ms_paper.pdf`, `<Y>_hs_paper.pdf`, answers in `*_answers.*` files or at the end of the paper; download missing "
      "answer pages from purplecomet.org). All answers are integers (numeric). MS and HS share problems: extract in MS, `duplicateOf` in HS. "
      "Slugs `ms-<Y>`, `hs-<Y>`; grades \"6-8\" and \"9-12\"; `points: 1` (official results are 'N out of 20/30'). "
      "MS answers may be in `sources/pdfs/purplecomet/ms/answers_ms_2005-2026.json`. Integers too long for a JS number (>15 digits): type text.")
U("mathcounts-2026", 1, "mathcounts", 200,
  "MATHCOUNTS 2026 Competition Series: `sources/pdfs/mathcounts/competitions/` (chapter and state Sprint, Target, Team and Countdown rounds, "
  "with answers and solutions). Slugs `2026-chapter-sprint`, `2026-state-target`, etc.; grade \"6-8\"; points null; contest \"MATHCOUNTS\". "
  "Countdown questions are short: still include them.")
U("mathcounts-samples", 1, "mathcounts", 60,
  "MATHCOUNTS sample School Competition papers: `sources/pdfs/mathcounts/competitions/sample_school_*` (with their answers/solutions). "
  "Slugs from the file names (e.g. `sample-school-sprint`); grade \"6-8\"; points null; contest \"MATHCOUNTS\". Skip anything already in `data/raw/mathcounts/`.")
U("mathcounts-potw", 1, "mathcounts", 190,
  "MATHCOUNTS Problems of the Week: `sources/pdfs/mathcounts/potw/` (each file has several related problems and solutions). "
  "Slugs `potw-<YYYY-MM-DD>`; grade \"6-8\".")
U("noetic-moems-rest", 1, "noetic", 80,
  "Noetic and MOEMS leftovers. Noetic sample tests for grades 2, 3, 4, 7, 8: `sources/pdfs/noetic/noetic-samples-g<N>.pdf` "
  "(grades 5 and 6 are already done in `data/raw/noetic/`; check and skip anything already present). Bank `noetic`, slugs `sample-g<N>`. "
  "Also MOEMS: compare `sources/pdfs/moems/sample_M.pdf`, `current_problems.pdf` and `archived_problems.pdf` against "
  "`data/raw/moems/*.json` and add any problems not yet present (bank `moems`, new slug e.g. `sample-m`, `current-2026`).")

# ---------------------------------------------------------------- phase 1: olympiads (proofs => type self, rigorous)
OLY = ("Olympiad proof problems: type `self` with a one-sentence `answer` summary unless the problem asks for a single number/value "
       "(then numeric/text). Write one complete rigorous proof (base it on the official / Evan Chen solution in the folder, reworded); "
       "a second approach only when it is natural and short. ")
for g in groups([y for y in range(1959, 2027) if y != 1980], 5):
    U(f"imo-{yr(g)}", 1, "imo", 6 * len(g),
      f"IMO problems {', '.join(map(str, g))}: `sources/pdfs/imo/imo/<Y>_imo_paper.pdf`; solutions in `sources/pdfs/imo/evanchen/<Y>_imo_evanchen_notes.pdf` "
      "(1997+), the shortlist booklets `sources/pdfs/imo/shortlist/` (2006+), or the official imo-official.org pages. " + OLY
      + "Bank `imo`, slug `<Y>` (ids `imo-<Y>-01`...), grade \"9-12\", contest \"IMO\".")
for y in range(2006, 2026):
    U(f"isl-{y}", 1, "imo", 30,
      f"IMO Shortlist {y}: `sources/pdfs/imo/shortlist/{y}_shortlist_solutions.pdf` (problems with official solutions). " + OLY
      + f"Bank `imo`, slug `isl-{y}`, ids `imo-isl-{y}-a1`, `-c3`, `-g5`, `-n2` (lowercase category + number), grade \"9-12\", "
      f"contest \"IMO Shortlist\". Problems that became IMO {y} problems: set `duplicateOf` to the IMO id `imo-{y}-0<k>` (even if not yet extracted).")
for g in groups(range(1996, 2027), 4):
    U(f"usamo-{yr(g)}", 1, "usamo", 10 * len(g),
      f"USAMO {', '.join(map(str, g))} and USAJMO for the same years (2010+): `sources/pdfs/usamo/usamo/<Y>_usamo_evanchen_notes.pdf`, "
      "`sources/pdfs/usamo/usajmo/<Y>_usajmo_evanchen_notes.pdf` (problems + solutions). " + OLY
      + "Bank `usamo`, slugs `usamo-<Y>`, `usajmo-<Y>`; grades \"10-12\" (USAMO) and \"7-10\" (USAJMO). Problems on both papers: extract in USAJMO, `duplicateOf` in USAMO.")
for g in [list(range(1972, 1984)), list(range(1984, 1996))]:
    U(f"usamo-{yr(g)}", 1, "usamo", 5 * len(g),
      f"USAMO {g[0]}-{g[-1]} from the AoPS wiki (`tools/aops.py page \"1975 USAMO Problems\"`; per-problem pages have solutions). " + OLY
      + "Bank `usamo`, slug `usamo-<Y>`, grade \"10-12\".")
for g in groups(range(1989, 2027), 6):
    U(f"apmo-{yr(g)}", 1, "apmo", 5 * len(g),
      f"APMO {', '.join(map(str, g))}: `sources/pdfs/apmo/apmo/<Y>_apmo_paper.pdf` and `<Y>_apmo_solutions.pdf`. " + OLY
      + "Bank `apmo`, slug `<Y>`, grade \"9-12\".")
for g in groups(range(2012, 2027), 5):
    U(f"egmo-{yr(g)}", 1, "egmo", 6 * len(g),
      f"EGMO {', '.join(map(str, g))}: `sources/pdfs/egmo/egmo/` (day papers, solutions) and `sources/pdfs/egmo/evanchen/`. " + OLY
      + "Bank `egmo`, slug `<Y>`, grade \"9-12\".")
for g in groups(range(1969, 2027), 7):
    U(f"cmo-{yr(g)}", 1, "cmo", 6 * len(g),
      f"Canadian Mathematical Olympiad {', '.join(map(str, g))}: `sources/pdfs/cmo/cmo/` (papers and solutions where present)"
      + (" and the Canadian Junior MO for the same years: `sources/pdfs/cmo/cjmo/` (shared problems: extract in CJMO, `duplicateOf` in CMO)" if g[-1] >= 2020 else "")
      + ". " + OLY + "Bank `cmo`, slugs `cmo-<Y>`, `cjmo-<Y>`; grades \"9-12\" (CMO), \"7-10\" (CJMO).")
for g in groups(range(2011, 2027), 5):
    U(f"comc-{yr(g)}", 1, "comc", 20 * len(g),
      f"Canadian Open Mathematics Challenge {', '.join(map(str, g))}: `sources/pdfs/comc/comc/<Y>_comc_paper.pdf`, `<Y>_comc_solutions.pdf`. "
      "Part A/B short answers (numeric/text), Part C full-solution parts (`self` where proof/explanation is required, else numeric). "
      "Bank `comc`, slug `<Y>`, grade \"9-12\", points as printed.")
for g in groups(range(1998, 2027), 3):
    U(f"usamts-{yr(g)}", 1, "usamts", 15 * len(g),
      f"USAMTS school years starting {', '.join(map(str, g))}: `sources/pdfs/usamts/usamts/<Y>-<Y+1>_year<N>_round<R>_paper.pdf` and `_solutions.pdf`. "
      "Answer-type problems numeric/text/mc; proof problems `self` with complete proofs (official solutions first). "
      "Bank `usamts`, slug `<Y>-r<R>` (year it started), grade \"7-12\".")

# ---------------------------------------------------------------- phase 1: university
UNI = ("University-level problems: `self` with complete rigorous proofs unless a single value/expression is asked "
       "(then numeric with `answerDisplay`, plus a full derivation). grade \"undergrad\". ")
for g in groups(range(1985, 2026), 3):
    U(f"putnam-{yr(g)}", 1, "putnam", 12 * len(g),
      f"Putnam {', '.join(map(str, g))}: problem statements in `sources/pdfs/putnam/tex/<Y>_putnam_paper.tex` (LaTeX source — easiest) "
      "or `problems/`; Kiran Kedlaya's solutions in `sources/pdfs/putnam/tex/` / `solutions/` where present. " + UNI
      + "Write the solutions in your own words (base on Kedlaya's where available). Bank `putnam`, slug `<Y>`, ids `putnam-<Y>-a1`...`-b6`.")
for g in groups(range(1994, 2027), 3):
    U(f"imc-{yr(g)}", 1, "imc", 11 * len(g),
      f"IMC (International Mathematics Competition for University Students) {', '.join(map(str, g))}: `sources/pdfs/imc/<Y>/` (problems and solutions). "
      + UNI + "Bank `imc`, slug `<Y>`, ids `imc-<Y>-d1-01` style or `imc-<Y>-01`..`10`.")
for g in groups([y for y in range(1991, 2027) if y not in (2020, 2021, 2023)], 4):
    U(f"vjimc-{yr(g)}", 1, "vjimc", 8 * len(g),
      f"VJIMC {', '.join(map(str, g))}: `sources/pdfs/vjimc/<Y>_j<NN>_problems.pdf`, `_solutions.pdf` (categories I and II where present). "
      + UNI + "Bank `vjimc`, slug `<Y>` (or `<Y>-cat1`/`<Y>-cat2`).")
for g in [[2017, 2018, 2019], [2020, 2021, 2022], [2023, 2024, 2025]]:
    U(f"simonmarais-{yr(g)}", 1, "simonmarais", 10 * len(g),
      f"Simon Marais Mathematics Competition {', '.join(map(str, g))}: `sources/pdfs/simonmarais/` (papers and solutions). " + UNI
      + "Bank `simonmarais`, slug `<Y>`.")
for g in groups([y for y in range(1979, 2023) if y not in (2020, 2021)], 6):
    U(f"vtrmc-{yr(g)}", 1, "vtrmc", 7 * len(g),
      f"Virginia Tech Regional Mathematics Contest {', '.join(map(str, g))}: `sources/pdfs/vtrmc/` (papers; solutions where present — "
      "otherwise solve them yourself carefully and set `reviewNote` only when unsure). " + UNI + "Bank `vtrmc`, slug `<Y>`.")

U("dedupe-review-1", 1, "kangaroo", 0,
  "Duplicate review (run after the other phase 1 units). Run `.venv/bin/python tools/build_banks.py` and look at every "
  "'possible duplicate: A ~ B' line. Open both questions (and their figures). If they are the same problem (same question, "
  "same numbers/figure, same answer), edit the file of the HIGHER-grade one: set `duplicateOf` to the lower-grade id, "
  "`solutions: []`, `image: null` (keep `image` if its choices are pictures). If they differ, leave them. Report what you merged. "
  "This is the only unit allowed to edit files written by other units, and only the `duplicateOf`/`solutions`/`image` fields.")


# ---------------------------------------------------------------- phase 2: shared policy text
PD = "sources/pdfs"
SA = ("Short-answer contest: `numeric` (integers, fractions, decimals, or an explicit exact expression such as `3*sqrt(2)/4`, "
      "`2^10-1`, `pi/6` with `answerDisplay` in KaTeX; units in `answerUnit`), `text` (names, words, letters; variants in "
      "`acceptedAnswers`) or `mc` (choices as printed). Use `self` only for "
      "proofs/explanations and answers that are sets, ordered pairs/tuples, several values, intervals or expressions in a variable "
      "(official answer in `answer`). Write full worked solutions (base the first on the official solution, reworded). ")
KEYONLY = ("Answer-key-only papers (no worked solutions): solve every problem yourself, write the full solution, and confirm it "
           "matches the key; if you cannot reconcile them, keep the official answer and set `reviewNote`. Papers with no key at "
           "all: first look for an official key (folder `_sources.json`, the bank's entry in `sources/catalog/*.json`; official "
           "sites only); otherwise solve carefully, check with a second method or a quick script in `/tmp/<unit id>/`, and set "
           "`reviewNote` only when you are not sure. Questions officially withdrawn/discounted: keep them only if the answer is "
           "clear, with a `reviewNote` saying so. ")
CHAIN = ("Relay/shuttle/chained questions (using T, 'the answer to the previous question', etc.): substitute the actual value "
         "into the prompt ('Let $T = 12$.') so each question stands alone, and say where it came from in the solution. "
         "Estimation questions scored by closeness: `self`, with the official answer and scoring rule in the solution. ")
POWER = ("Power/proof rounds: one question per numbered part (ids like `-03b`), each prompt restating the definitions/setup it "
         "needs; single-value parts numeric/text, proofs and constructions `self` with complete proofs. ")
DUPS = ("A problem printed on more than one paper (divisions A/B, levels, rounds, repeated booklets): extract it once in the "
        "lowest-grade/first paper and give the other copies `duplicateOf` that id with `solutions: []` and `image: null`. ")
PTS = "Points as printed (`points`; `blankPoints`/`wrongPoints` where the rules give them). "
SCAN = ("Some pages are scans without a text layer: read them from `tools/pdf.py render` images at a good zoom and "
        "double-check every number and symbol (set `reviewNote` if a word or number stays unreadable). ")
QUAL = ("Graduate qualifying-exam problems: one question per numbered problem (keep its parts (a), (b), ... together in the "
        "prompt and answer each part in the solution). Type `self` with a short `answer` summary and one complete rigorous "
        "solution (standard graduate theorems may be cited by name); use numeric/text only when the whole problem asks for a "
        "single value. Extract every problem even when the exam says 'do 5 of 8'. Grade \"grad\". Topics from the fixed list "
        "(numerical analysis -> `analysis`/`linear-algebra`, geometry/topology -> `topology`, logic -> `logic`). Most exams have "
        "no solutions: solve them yourself; set `reviewNote` only when unsure or when the statement looks wrong. ")


def first(bank, slug):
    return (f"This is the convention-setting unit for bank `{bank}`: write `data/raw/{bank}/{slug}.json` first and keep the "
            "rest consistent with it — later units of this bank copy its id style, `source.contest`/`source.paper` naming, "
            "grade labels, answer types and solution style, so follow this task text exactly. ")


def follow(bank, uid, slug):
    return (f"Conventions: first read `data/raw/{bank}/{slug}.json` (written by unit `{uid}`) and match its id style, "
            "source naming, grade labels and answer types; if it does not exist yet, follow this task text. "
            "Other agents work on other units of this bank at the same time; touch only your own files. ")


def skip(*files):
    return "Do NOT extract (not problem papers, or duplicate/mislabelled copies): " + "; ".join(f"`{f}`" for f in files) + ". "


def bank2(bank, slug, rows):
    """rows: [(uid, est, task)] — the first row is the convention-setting unit and writes `slug`."""
    for i, (uid, est, task) in enumerate(rows):
        U(uid, 2, bank, est, task + (first(bank, slug) if i == 0 else follow(bank, rows[0][0], slug)))


def ys(g):
    return ", ".join(map(str, g))


def bal(items, n):
    """Split into consecutive chunks of about n (sizes differ by at most one)."""
    k = max(1, round(len(items) / n))
    return [items[i * len(items) // k:(i + 1) * len(items) // k] for i in range(k)]


# ---------------------------------------------------------------- phase 2: elementary / middle school
D = f"{PD}/ma-pmc"
MAPMC = ("Bank `mapmc` (Mathematical Association, UK; files are in `{d}/`). Mixed format: choices -> `mc`, write-in answers "
         "numeric/text. `source.contest` \"Primary Mathematics Challenge\" or \"First Mathematics Challenge\", `source.paper` "
         "e.g. \"November 2020\", \"February 2021 Bonus Round\", \"2022\". The answers-and-notes files give the answers and short "
         "solutions. ").format(d=D)
bank2("mapmc", "fmc-2019", [
    ("mapmc-fmc-2019-2024", 120, f"First Mathematics Challenge 2019-2024: `{D}/fmc/<Y>_fmc_paper.pdf` with `<Y>_fmc_answers-notes.pdf` "
     "(2019: `2019_fmc_instructions-and-answers.pdf` holds the answers). " + MAPMC + "Slugs `fmc-<Y>`, ids `mapmc-fmc-<Y>-NN`, grade \"2-3\" (UK Years 3-4). "),
    ("mapmc-pmc-nov", 100, f"Primary Mathematics Challenge November papers 2018, 2020, 2021, 2022: `{D}/pmc/<Y>-11_pmc_paper.pdf` and "
     "`<Y>-11_pmc_answers-notes.pdf`. Nov 2019 has only `2019-11_pmc_answers-notes.pdf` (no paper): extract 2019 only if the notes "
     "restate each problem completely, otherwise skip it and say so. " + MAPMC + "Slugs `pmc-<Y>-11`, ids `mapmc-pmc-<Y>-11-NN`, grade \"4-5\". "),
    ("mapmc-pmc-bonus", 150, f"PMC Bonus Round (February) 2018-2023: `{D}/pmc/<Y>-02_pmc-bonus_paper.pdf` with the answers files. "
     "The 2018 paper is scanned; `2018-02_pmc-bonus_paper-alt.pdf` is a second (spread) copy of it — use it only to read unclear "
     "pages. " + SCAN + MAPMC + "Slugs `pmc-bonus-<Y>`, ids `mapmc-pmc-bonus-<Y>-NN`, grade \"4-5\". "),
])

D = f"{PD}/simcc"
bank2("simcc", "sasmo-2019-g2", [
    ("simcc-sasmo-g2-4", 150, f"SASMO grades 2, 3, 4 for 2019 and 2020: each `{D}/sasmo/2019_sasmo-g<N>_paper.pdf` contains BOTH the "
     "2019 and the 2020 paper with full solutions — extract both years from it; the `2020_sasmo-g<N>_*` files repeat the 2020 part "
     "(headers say 'GEP Practice 2020') and are only for cross-checking. " + DUPS + SA + PTS
     + "Bank `simcc`, slugs `sasmo-<Y>-g<N>`, ids `simcc-sasmo-<Y>-g<N>-NN`, contest \"SASMO\", paper \"2019 Grade 3\", grade \"<N>\" "
     "(Primary N = grade N, Secondary 1-2 = grades 7-8). "),
    ("simcc-sasmo-g5-6", 100, f"SASMO grades 5 and 6, 2019 and 2020 (same file layout as unit `simcc-sasmo-g2-4`: `{D}/sasmo/2019_sasmo-g<N>_paper.pdf` "
     "holds both years). " + DUPS + SA + PTS + "Slugs `sasmo-<Y>-g<N>`, grade \"<N>\". "),
    ("simcc-sasmo-g7-8", 100, f"SASMO grades 7 and 8 (Secondary 1-2), 2019 and 2020 (`{D}/sasmo/2019_sasmo-g<N>_paper.pdf` holds both years). "
     + DUPS + SA + PTS + "Slugs `sasmo-<Y>-g<N>`, grade \"<N>\". "),
    ("simcc-simoc-g1", 75, f"SIMOC grade 1, 2021-2023: `{D}/simoc/` (papers and `2021-2023_simoc-g1_answers.pdf`; answer key only). "
     + KEYONLY + SA + PTS + "Slugs `simoc-<Y>-g1`, contest \"SIMOC\", grade \"1\". "),
])

bank2("seamo", "sample-a", [
    ("seamo-samples", 60, f"SEAMO official sample papers `{PD}/seamo/samples/sample_paper-{{A,B,C,D}}.pdf` (A = Primary 1-2, "
     "B = Primary 3-4, C = Primary 5-6, D = Secondary 1-2). The text layer garbles letters/symbols (e.g. '!\"#'): read every "
     "question from the rendered page. The papers contain only some questions with solutions/answers. " + KEYONLY + SA
     + "Slugs `sample-a` ... `sample-d`, ids `seamo-sample-a-NN` (NN = printed number), contest \"SEAMO\", paper \"Sample Paper A\"; "
     "grades \"1-2\", \"3-4\", \"5-6\", \"7-8\". "),
])
bank2("hkimo", "sample", [
    ("hkimo-sample", 20, f"HKIMO official sample questions `{PD}/hkimo/sample_paper.pdf` (bilingual Chinese/English; use the "
     "English text). Skip the Kindergarten group. Answers are given without solutions. " + KEYONLY + SA
     + "Slug `sample`, ids `hkimo-sample-p1-01` (group code + number: `p1`..`p6` primary, `s1`, `s2` secondary), contest \"HKIMO\", "
     "paper \"Sample Questions (Primary 3)\"; grade = the group's US grade (Primary N -> \"N\", Secondary 1-2 -> \"7\", \"8\"). "),
])
bank2("smo", "sample", [
    ("smo-sample", 10, f"Singapore Mathematical Olympiad sample questions `{PD}/smo/samples/sample_smo_questions.pdf` (Junior, Senior "
     "and Open examples; no key). " + KEYONLY + SA + "Slug `sample`, ids `smo-sample-junior-01`, contest \"SMO\", paper \"Sample Questions (Junior Section)\"; "
     "grades Junior \"7-8\", Senior \"9-10\", Open \"11-12\". "),
])
bank2("amt", "aimo-2017", [
    ("amt-aimo-amc-practice", 65, f"Australian Intermediate Mathematics Olympiad 2017 and 2018: `{PD}/amt/aimo/<Y>_aimo_paper-and-solutions.pdf` "
     "(10 questions each, integer answers 0-999, full solutions) and the AMC practice sets `{PD}/amt/amc-practice/set1_{{MPR,UPR,JUN}}.pdf` "
     "(with solutions; mc then integer answers). " + SA + PTS
     + "Slugs `aimo-<Y>`, `amc-practice-1-mpr`, `-upr`, `-jun`; contests \"Australian Intermediate Mathematics Olympiad\", "
     "\"Australian Mathematics Competition\" (paper \"Practice Set 1 Middle Primary\"); grades AIMO \"7-10\", MPR \"3-4\", UPR \"5-6\", JUN \"7-8\". "
     "(`sources/pdfs/amo-aus/aimo/2017_aimo_solutions.pdf` is a byte-identical copy — ignore it.) "),
])
D = f"{PD}/mathleague"
ML = (f"Math League (Math League Press) contests in `{D}/samples/` and `{D}/`: each contest has a paper and a solutions/answers "
      "file. " + SA + "Slugs `<YYYY-YY>-g<N>` (grade contests) and `<YYYY-YY>-hs-c<K>` (HS contest K); contest \"Math League\", "
      "paper \"2012-13 Grade 6 Contest\"; grade \"<N>\" (HS: \"9-12\"). ")
bank2("mathleague", "2018-19-g4", [
    ("mathleague-2018-19-g4-6", 95, f"Math League 2018-19 grade 4, 5, 6 sample contests in `{D}/samples/`. " + ML),
    ("mathleague-2018-19-g7-hs", 75, f"Math League 2018-19 grade 7 and 8 sample contests (`{D}/samples/`) and the HS contest `2018-19_hs_contest5_*`. " + ML),
    ("mathleague-2012-13-g4-6", 95, f"Math League 2012-13 grade 4, 5, 6 sample contests in `{D}/samples/`. " + ML),
    ("mathleague-2012-13-g7-hs", 75, f"Math League 2012-13 grade 7 and 8 sample contests and HS contest `2012-13_hs_contest1_*`. " + ML),
    ("mathleague-2004-05-g4-6", 95, f"Math League 2004-05 grade 4, 5, 6 sample contests (`{D}/samples/`, scanned). " + SCAN + ML),
    ("mathleague-2004-06-g7-hs", 75, f"Math League 2004-05 grade 7 and 8 sample contests (scanned) and HS contest `2005-06_hs_contest1_*` (scanned). " + SCAN + ML),
])
bank2("prism", "2019", [
    ("prism-all", 75, f"PRISM (Irish problem-solving competition) papers in `{PD}/prism/`: 2006 junior paper with `2006_answers.html`, "
     "2016 and 2017 papers (no key), 2019 solutions (problems included). Multiple choice. " + KEYONLY + SA
     + "Slugs `<Y>` (2006: `2006-junior`), ids `prism-<Y>-NN`, contest \"PRISM\"; grade \"7-9\" for the junior paper, \"7-12\" for the "
     "single all-second-level papers. "),
])

# ---------------------------------------------------------------- phase 2: UKMT
D = f"{PD}/ukmt"
UK = ("Bank `ukmt`, contest names \"UKMT Junior Mathematical Challenge\", \"UKMT Intermediate Mathematical Challenge\", \"UKMT Senior "
      "Mathematical Challenge\", \"UKMT Junior Kangaroo\", \"UKMT Grey Kangaroo\", \"UKMT Pink Kangaroo\", \"UKMT Senior Kangaroo\", "
      "\"UKMT Primary Kangaroo\", \"UKMT Junior Mathematical Olympiad\", \"UKMT Cayley Olympiad\" etc.; `source.paper` = the year. "
      "Use the official solutions (and extended solutions / reports) as the first approach. UK Year N = US grade N-1. ")
UKKANG = ("The UKMT Kangaroo papers reuse many international Kangaroo problems: if a problem is identical to one already in "
          "`data/raw/kangaroo/at-<Y>-<level>.json` (same year; Grey ~ Kadett, Pink ~ Junior, Senior ~ Student, Junior ~ Benjamin), "
          "set `duplicateOf` to that id. ")
JMC = [list(range(2015, 2019)), list(range(2011, 2015)), list(range(2019, 2023)), list(range(2023, 2027))]
rows = []
for g in JMC:
    rows.append((f"ukmt-jmc-{yr(g)}", 25 * len(g), f"UKMT Junior Mathematical Challenge {ys(g)}: `{D}/jmc/<Y>_jmc_paper.pdf`, "
                 "`_solutions.pdf`, `_extended-solutions.pdf`, `_problem-comments.pdf`"
                 + (" (2011-2014 have only the extended solutions, which restate the problems and the choices)" if 2011 in g else "")
                 + ". 25 mc questions; points 5 (Q1-15) and 6 (Q16-25), older papers deduct 1 or 2 marks for wrong answers on Q16-25 "
                 "(`wrongPoints` as printed in the instructions). " + UK + "Slugs `jmc-<Y>`, ids `ukmt-jmc-<Y>-NN`, grade \"6-7\". "))
for g in [[2012, 2015, 2016, 2017], list(range(2018, 2022)), list(range(2022, 2027))]:
    rows.append((f"ukmt-imc-{yr(g)}", 25 * len(g), f"UKMT Intermediate Mathematical Challenge {ys(g)}: `{D}/imc/<Y>_imc_paper.pdf`, "
                 "`_solutions.pdf`, `_solutions_extended.pdf` (2012 paper is scanned). 25 mc; points and penalties as printed "
                 "(5 for Q1-15, 6 for Q16-25). " + UK + "Slugs `imc-<Y>`, grade \"8-10\". " + (SCAN if 2012 in g else "")))
for g in [[2009, 2012, 2013, 2015], list(range(2016, 2020)), list(range(2020, 2024)), list(range(2024, 2027))]:
    rows.append((f"ukmt-smc-{yr(g)}", 25 * len(g), f"UKMT Senior Mathematical Challenge {ys(g)}: `{D}/smc/<Y>_smc_paper.pdf`, "
                 "`_solutions.pdf`, `_solutions_extended.pdf`"
                 + (" (2009 paper is only 2 pages — check it is complete; 2012-2013 have only extended solutions that restate the problems)" if 2009 in g else "")
                 + ". 25 mc; points/penalties as printed. " + UK + "Slugs `smc-<Y>`, grade \"11-12\". "))
for g in [list(range(2015, 2019)), [2019, 2021, 2022, 2023], list(range(2024, 2027))]:
    rows.append((f"ukmt-jk-{yr(g)}", 25 * len(g), f"UKMT Junior Kangaroo {ys(g)}: `{D}/jk/<Y>_jk_paper.pdf`, `_solutions.pdf` "
                 "(25 questions, three-digit answers -> numeric). " + UKKANG + UK + "Slugs `jk-<Y>`, grade \"6-7\". "))
for g in groups(range(2015, 2027), 3):
    rows.append((f"ukmt-greypink-{yr(g)}", 50 * len(g), f"UKMT Grey Kangaroo and Pink Kangaroo {ys(g)}: `{D}/grey/<Y>_grey_*`, "
                 "`{D}/pink/<Y>_pink_*` (25 mc each). The Grey and Pink papers share problems: extract in Grey, `duplicateOf` in Pink. "
                 .replace("{D}", D) + UKKANG + PTS + UK + "Slugs `grey-<Y>`, `pink-<Y>`; grades Grey \"8\", Pink \"9-10\". "))
for g in [list(range(2015, 2020)), list(range(2020, 2026))]:
    rows.append((f"ukmt-sk-{yr(g)}", 20 * len(g), f"UKMT Senior Kangaroo {ys(g)} (years present): `{D}/senior-kangaroo/<Y>_senior-kangaroo_*` "
                 "(20 questions, three-digit answers -> numeric). " + UKKANG + UK + "Slugs `sk-<Y>`, grade \"11-12\". "))
rows.append(("ukmt-pk", 65, f"UKMT Primary Kangaroo 2025-2026 (`{D}/pk/<Y>_pk_paper.pdf`, `_solutions.pdf`) and "
             "`pk_Sample-problems-from-previous-Primary-Kangaroo-Challenges.pdf` (slug `pk-sample`). 25 mc each. "
             + skip(f"{D}/pk/pk_Primary-Kangaroo-practice-answer-sheet-1-1.pdf") + UKKANG + PTS + UK + "Slugs `pk-<Y>`, grade \"3-4\". "))
for g in [[2015, 2016, 2017, 2018, 2019, 2021], list(range(2022, 2027))]:
    rows.append((f"ukmt-jmo-{yr(g)}", 16 * len(g), f"UKMT Junior Mathematical Olympiad {ys(g)}: `{D}/jmo/<Y>_jmo_paper.pdf`, "
                 "`_solutions.pdf`, `_solutions_2.pdf`, `_sample-solutions.pdf`, `_report.pdf`. Section A: 10 short answers "
                 "(numeric/text, 1 mark each); Section B: 6 full-solution problems (`self` unless only a value is asked; 10 marks). "
                 + skip(f"{D}/jmo/jmo_Olympiad-Sample-Answer-Sheet.pdf") + UK + "Slugs `jmo-<Y>`, ids `ukmt-jmo-<Y>-a01`, `-b03`, grade \"6-7\". "))
for g in groups(range(2015, 2027), 3):
    rows.append((f"ukmt-olympiads-{yr(g)}", 18 * len(g), f"UKMT Cayley, Hamilton and Maclaurin Olympiads {ys(g)}: `{D}/cayley/`, "
                 "`{D}/hamilton/`, `{D}/maclaurin/` (`<Y>_<name>_paper.pdf`, `_solutions.pdf`, `_report.pdf`; "
                 "`maclaurin/2018_maclaurin_paper_2.pdf` is actually the 2018 solutions). 6 problems each; shared problems: extract in "
                 "the lowest level (Cayley), `duplicateOf` in the others. ".replace("{D}", D) + OLY
                 + skip(f"{D}/cayley/cayley_Olympiad-Sample-Answer-Sheet.pdf") + UK
                 + "Slugs `cayley-<Y>`, `hamilton-<Y>`, `maclaurin-<Y>`, ids `ukmt-cayley-<Y>-c1` (printed labels C1-C6, H1-H6, M1-M6); "
                 "grades Cayley \"8\", Hamilton \"9\", Maclaurin \"10\"; points 10 each. "))
TMC = ("Rounds: group (one question each), crossnumber (one `self` question per puzzle: grid image + all clues in the prompt, "
       "completed grid in the answer/solution), shuttle and relay (chained), circus (stations). Answers come from the supervisors' "
       "booklets / 'with answers' versions. " + CHAIN + SA + KEYONLY)
rows.append(("ukmt-tmc-2016-2017", 90, f"UKMT Team Maths Challenge: regional 2016 and 2017, national final 2016 (`{D}/tmc/<Y>_tmc-<regional|national>_*`). "
             + TMC + UK + "Slugs `tmc-<Y>-regional-<round>`, `tmc-<Y>-national-<round>`, ids `ukmt-tmc-2016-national-relay-NN`; grade \"7-8\". "))
rows.append(("ukmt-tmc-2024-2025", 90, f"UKMT Team Maths Challenge: regional 2024 and 2025, national final 2025 (`{D}/tmc/<Y>_tmc-*`). "
             + TMC + UK + "Slugs `tmc-<Y>-regional-<round>`, `tmc-<Y>-national-<round>`; grade \"7-8\". "))
rows.append(("ukmt-stmc-2014-2016", 60, f"UKMT Senior Team Maths Challenge national finals 2014-15 and 2015-16: `{D}/stmc-nf/2014-15_*`, `2015-16_*` "
             "(answers in `_solutions_final` / `_supervisors_booklet`). " + TMC + UK
             + "Slugs `stmc-<YYYY-YY>-final-<round>`, grade \"10-12\". "))
rows.append(("ukmt-stmc-2018-2020", 120, f"UKMT Senior Team Maths Challenge 2018-19 and 2019-20, regional (`{D}/stmc/`) and national final "
             f"(`{D}/stmc-nf/`; the regional and final papers differ). 2019-20 regional files include answers; 2019-20 final has "
             "no supervisors' booklet. " + TMC + UK + "Slugs `stmc-<YYYY-YY>-regional-<round>`, `stmc-<YYYY-YY>-final-<round>`, grade \"10-12\". "))
rows[0] = (rows[0][0], rows[0][1], rows[0][2] + skip(f"{D}/jmc/jmc_Sample-Answer-Sheet-1.pdf", f"{D}/jk/jk_Sample-Answer-Sheet-1.pdf",
                                                    f"{D}/_sources_highschool.json", f"{D}/manifest_elementary-middle.json"))
bank2("ukmt", "jmc-2015", rows)

# ---------------------------------------------------------------- phase 2: high school short answer
D = f"{PD}/samf"
SAMO = (f"South African Mathematics Olympiad (SAMF) papers `{D}/senior/` and `{D}/junior/` (`<Y>_<senior|junior>_round<R>_<paper|solutions>.pdf`). "
        "Round 1 is multiple choice, round 2 mc + integer answers. " + PTS + SA + KEYONLY
        + "Slugs `senior-<Y>-r<R>`, `junior-<Y>-r<R>`, ids `samf-senior-<Y>-r2-NN`, contest \"South African Mathematics Olympiad\", "
        "paper \"2019 Senior Round 2\"; grades senior \"10-12\", junior \"8-9\". ")
rows = []
for g in [sorted(g) for g in groups(range(2026, 1996, -1), 3)]:
    rows.append((f"samf-senior-{yr(g)}", 40 * len(g) - (20 if 2026 in g else 0), f"SAMO Senior rounds 1 and 2, {ys(g)} (whatever exists; 2026 has only round 2). " + SAMO))
for g in [[1998, 1999, 2000], [2001, 2002, 2003], [2004, 2005, 2006], [2007, 2008, 2009], [2010, 2011, 2012, 2013],
          [2014, 2016, 2017, 2018, 2019, 2020], list(range(2021, 2027))]:
    rows.append((f"samf-junior-{yr(g)}", sum(40 if y < 2011 else 20 for y in g), f"SAMO Junior {ys(g)}: rounds 1 and 2 up to 2010, round 2 only from 2011 "
                 "(no 2015; 2004 round 2 has only the solutions file — use it if it restates the problems). " + SAMO))
bank2("samf", "senior-2024-r1", rows)

D = f"{PD}/ioqm"
IOQM = (f"Files `{D}/` (papers, answer keys; `sample_prmo_questions.pdf`). 30 questions, integer answers 0-99 -> numeric; points 2/3/5 "
        "(or as printed). " + KEYONLY + SA + "Slugs `prmo-<Y>`, `ioqm-<Y>`, `prmo-sample`; contest \"PRMO\"/\"IOQM\"; grade \"8-12\". ")
bank2("ioqm", "ioqm-2024", [
    ("ioqm-2021-2024", 110, "IOQM 2021 (Part A only), 2022, 2023, 2024 and the PRMO sample questions. " + IOQM),
    ("ioqm-2017-2020", 120, "PRMO 2017, 2018 (no key — solve), 2019 and IOQM 2020. " + IOQM),
])

D = f"{PD}/mathprize"
rows = []
for g in [list(range(2022, 2027)), list(range(2015, 2020)) + [2021], list(range(2009, 2015))]:
    rows.append((f"mathprize-main-{yr(g)}", 20 * len(g), f"Math Prize for Girls {ys(g)}: `{D}/main/<Y>_mathprize<Y>problems.pdf` and solutions "
                 "(2026 has no solutions — solve). 20 short-answer problems. " + SA + KEYONLY
                 + "Slugs `<Y>`, ids `mathprize-<Y>-NN`, contest \"Math Prize for Girls\", grade \"9-12\". "))
rows.append(("mathprize-olympiad", 56, f"Math Prize for Girls Olympiad 2010-2019, 2022-2025: `{D}/olympiad/<Y>_mpfg_olympiad_{{paper,solutions}}.pdf` "
             "(4 proof problems each). " + OLY + "Slugs `olympiad-<Y>`, contest \"Math Prize for Girls Olympiad\", grade \"9-12\". "))
bank2("mathprize", "2022", rows)

D = f"{PD}/arml"
ARML = (f"ARML books in `{D}/` (find each year's pages with `tools/pdf.py text`). Rounds: Team (10), Power (multi-part proof round), "
        "Individual (10 + tiebreaker), Relays, Super Relay. " + POWER + CHAIN + SA
        + "Slugs `<Y>-team`, `<Y>-power`, `<Y>-individual`, `<Y>-relay`, `<Y>-superrelay` (Local: `local-<Y>-<round>`, rounds team/theme/"
        "individual/relay); ids `arml-<Y>-team-NN`; contest \"ARML\" / \"ARML Local\", paper \"2016 Team Round\"; grade \"9-12\". "
        "Licence: ARML allows non-commercial educational reproduction but not posting whole contests — the app shows single questions, fine. ")
rows = []
for g in [[2015, 2016, 2017], [2018, 2019, 2020], [2009, 2010, 2011], [2012, 2013, 2014]]:
    rows.append((f"arml-{yr(g)}", 50 * len(g), f"ARML {ys(g)} from `{D}/{'2015-2020' if g[0] >= 2015 else '2009-2014'}_arml_book.pdf`"
                 + (" (`2019_arml_contest.pdf` is the same contest; use either)" if 2019 in g else "") + ". " + ARML))
rows.append(("arml-2023-2025", 100, f"ARML 2023 and 2025: `{D}/2023_arml_contest.pdf`, `{D}/2025_arml_contest.pdf` (problems and solutions). " + ARML))
for g in [[2004, 2005, 2006], [2007, 2008]]:
    rows.append((f"arml-{yr(g)}", 50 * len(g) + (35 if 2008 in g else 0), f"ARML {ys(g)} from the scanned `{D}/2004-2008_arml_book.pdf`"
                 + (" (plus ARML Local 2008 if it is in the book)" if 2008 in g else "") + ". " + SCAN + ARML))
for g in [[1995, 1996, 1997], [1998, 1999, 2000], [2001, 2002, 2003]]:
    rows.append((f"arml-{yr(g)}", 50 * len(g), f"ARML {ys(g)} from the scanned `{D}/1995-2003_arml_book.pdf` (422 pages). " + SCAN + ARML))
for g in [[2009, 2010, 2011], [2012, 2013, 2014]]:
    rows.append((f"arml-local-{yr(g)}", 35 * len(g), f"ARML Local {ys(g)} from `{D}/2009-2014_arml_book.pdf`. " + ARML))
rows.append(("arml-local-2015-2017", 105, f"ARML Local 2015-2017 from `{D}/local/2015-2019_armllocal_solutions.pdf` (answers: `2015-2019_armllocal_answers.pdf`). " + ARML))
rows.append(("arml-local-2018-2019", 70, f"ARML Local 2018-2019 from `{D}/local/2015-2019_armllocal_solutions.pdf` (answers: `2015-2019_armllocal_answers.pdf`). " + ARML))
bank2("arml", "2015-team", rows)

D = f"{PD}/hmmt"
HM = ("Files `{d}/<Y>_<round>_problems.pdf` / `_solutions.pdf`. " + SA + CHAIN + POWER + PTS
      + "Team rounds with proofs: `self`. Slugs `feb-<Y>-<round>` / `nov-<Y>-<round>` (round as in the file name), ids "
        "`hmmt-feb-<Y>-<round>-NN`; contest \"HMMT February\" / \"HMMT November\", paper \"2024 Algebra and Number Theory\"; grade \"9-12\". ")
rows = []
for g in [[2025, 2026], [2023, 2024], [2021, 2022], [2019, 2020], [2017, 2018], [2015, 2016], [2013, 2014], [2012]]:
    rows.append((f"hmmt-feb-{yr(g)}", 76 * len(g), f"HMMT February {ys(g)}: all rounds (algnt/alg, comb, geo, team, guts). " + HM.format(d=f"{D}/feb")))
rows.append(("hmmt-feb-2011", 140, "HMMT February 2011: algcalc, algcomb, alggeo, calccomb, calcgeo, combgeo, guts, team1, team2. " + HM.format(d=f"{D}/feb")))
for y in range(2003, 2011):
    rows.append((f"hmmt-feb-{y}", 125, f"HMMT February {y}: all rounds (alg, calc, comb, geo, gen1, gen2, guts, team/team1/team2). "
                 + HM.format(d=f"{D}/feb") + (skip(f"{D}/feb/{y}_results_short.pdf") if y in (2005, 2006) else "")))
for g in [[2002], [2001], [2000], [1999], [1998]]:
    rows.append((f"hmmt-feb-{yr(g)}", 80 if 1998 in g else 110, f"HMMT February {ys(g)}: all rounds present (adv, alg, calc, geo, team, oral, gen/gen1/gen2, guts, pow). "
                 + HM.format(d=f"{D}/feb")))
for g in groups(range(2024, 2007, -1), 2):
    g = sorted(g)
    rows.append((f"hmmt-nov-{yr(g)}", 66 * len(g), f"HMMT November {ys(g)}: all rounds (gen/thm or gen1/gen2, guts, team). " + HM.format(d=f"{D}/nov")))
rows.append(("hmmt-nov-2025", 66, "HMMT November 2025: all rounds (gen, thm, guts, team). " + HM.format(d=f"{D}/nov")))
bank2("hmmt", "feb-2025-algnt", rows)

D = f"{PD}/pumac"
PU = (f"Files in `{D}/` (names vary by year; list `{D}/<Y>_*`). Division A and B subject tests (algebra, combinatorics, geometry, "
      "number theory), team round, individual finals (proof problems -> `self`), live round where present. " + DUPS
      + "(extract in Division B, Division A copies `duplicateOf`). " + SA + CHAIN + KEYONLY
      + "Slugs `<Y>-<round>-<a|b>` (e.g. `2019-algebra-a`, `2019-team`, `2019-finals-a`), ids `pumac-2019-algebra-a-NN`; contest \"PUMaC\", "
        "paper \"2019 Algebra A\"; grade \"9-12\". Power rounds are separate units — skip them here. ")
rows = []
for y in [2019, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2020, 2021, 2022, 2023, 2024, 2025, 2018]:
    extra = {
        2007: "Also `numbertheoryb_e2ng.pdf` (2007 NT B) and `teamab.pdf` (2007 team) — confirm the year in their headers. ",
        2008: skip(*(f"{D}/2008_pumac2008_{s}" for s in ("algebrasol_4b87.pdf", "combinatoricssol_49yr.pdf", "geometrysol_sar4.pdf", "numbertheorysol_j4w8.pdf"))),
        2012: skip(f"{D}/2012_pumac2012_teamanswersheet.pdf"),
        2017: "NT A solutions: `2017_pumac_2017_nt_a_solrevised.pdf`. ",
        2019: "Also the undated `live.pdf` / `liveroundanswers.pdf`: identify the year from the content; extract as `<Y>-live` unless it repeats a live round already extracted (2016, 2017, 2019). ",
        2023: "Each 2023 test has `<name>_2023.pdf` and `<name>_2023_2.pdf` — one is the problems, the other the solutions (check). ",
        2024: "2024 has problems only — solve everything. ",
        2025: "2025 solutions are the undated files `algebra_a_solutions_8m9y.pdf`, `algebra_b_solutions_tm7w.pdf`, `combinatorics_a_solutions_dxnt.pdf`, "
              "`combinatorics_b_solutions_tdgk.pdf`, `geometry_a_solutions_6t2d.pdf`, `geometry_b_solutions_nmxh.pdf`, `number_theory_a_solutions_b7c9.pdf`, "
              "`number_theory_b_solutions_e3rc.pdf`, `individual_finals_a_solutions_ztd5.pdf`, `individual_finals_b_solutions_flzg.pdf`, `team_solutions.pdf` "
              "(confirm each matches the 2025 problems). ",
        2018: "PUMaC 2018 files are undated: `algebra_{a,b}_test.pdf`, `algebra_{a,b}_solutions.pdf`, `combinatorics_{a,b}_test.pdf`/`_solutions.pdf`, "
              "`geometry_a_test.pdf`, `geobtest.pdf`, `geometry_{a,b}_solutions.pdf`, `number_theory_{a,b}_test.pdf`/`_solutions.pdf`, "
              "`individual_finals_{a,b}_test.pdf`, `individual_finals_a_solutions_293a.pdf`, `individual_finals_b_solutions.pdf`, `2018_team_round.pdf`, "
              "`team_round_solutions.pdf` (confirm the year in each header). ",
    }.get(y, "")
    rows.append((f"pumac-{y}", 75 if y in (2007, 2008) else 100, f"PUMaC {y} (all rounds except power). " + extra + PU))
PW = ("PUMaC power round (long proof-based round). " + POWER + KEYONLY
      + "Slug `<Y>-power`, ids `pumac-<Y>-power-01a`; contest \"PUMaC\", paper \"2019 Power Round\"; grade \"9-12\". ")
rows.append(("pumac-power-2007-2011", 75, f"PUMaC power rounds 2007-2011: `{D}/<Y>_pumac<Y>_power*.pdf` and `powersol`. " + PW))
rows.append(("pumac-power-2012-2016", 75, f"PUMaC power rounds 2012-2016 (`2015_pumac2015_powerwithsol.pdf` has the solutions; "
             "`2016_pumac2016_powersol_n7bg.pdf`). " + PW))
rows.append(("pumac-power-2017-2020", 60, f"PUMaC power rounds 2017, 2018 (undated `power_round.pdf`, `power_solutions.pdf`), 2019, 2020 "
             "(`2020_pumac_2020_power_round_problem_statements_f5gg.pdf`, `_solutions.pdf`). " + PW))
rows.append(("pumac-power-2021-2025", 75, f"PUMaC power rounds 2021-2025. Year quirks: `2021_pumac2021v20.pdf` + `2021_pumac2021powersols.pdf` = 2021; "
             "`2023_pumac2023powerroundmarch28update.pdf` + `2023_pumac_2023_power_round_sol.pdf` = the 2022 round (posted spring 2023); "
             "`pumacpowerround_6.pdf` = 2023 (no solutions); `2024_power2024_updated_1117.pdf` = 2024; `2025_power_2025.pdf` = 2025. Confirm in the text. " + PW))
bank2("pumac", "2019-algebra-b", rows)

D = f"{PD}/bmt"
BM = (f"Files `{D}/<Y>_*` (2012-2018 short names: `is` individual, `ts` team, `pows` power, `tors` tournament round, `anas` analysis, "
      "`diss` discrete, `geos` geometry, 2018 `alsp18`/`casp18`/`cosp18`/`geosp18`/`ntsp18`/`powsp18`/`tesp18`; suffix `s` = solutions, "
      "`a` = answer key, `tb` = tiebreaker; 2019+ `<round>_problems/solutions`). " + SA + CHAIN + POWER + KEYONLY
      + skip(*(f"{D}/{f}" for f in ("2023_results.pdf", "2023_results_china.pdf", "2023_results_online.pdf", "2024_results.pdf",
                                     "2025_results.pdf", "2025_results_china.pdf", "2025_results_online.pdf")))
      + "Slugs `<Y>-<round>` (e.g. `2021-algebra`, `2021-algebra-tiebreaker`, `2018-spring-geometry`), ids `bmt-2021-algebra-NN`; contest "
        "\"Berkeley Math Tournament\", paper \"2021 Algebra\"; grade \"9-12\". ")
rows = [(f"bmt-{y}", 120, f"BMT {y}: all rounds. " + BM) for y in range(2025, 2018, -1)]
rows += [("bmt-2018", 110, "BMT 2018 (spring 2018 rounds `*sp18*`). " + BM),
         ("bmt-2016-2017", 120, "BMT 2016-2017 (mostly answer keys only; the 2017 geometry paper is missing — skip it). " + BM),
         ("bmt-2014-2015", 120, "BMT 2014-2015 (2014 answer keys; 2015 individual has no key — solve). " + BM),
         ("bmt-2012-2013", 110, "BMT 2012-2013 (with solutions). " + BM)]
bank2("bmt", "2025-algebra", rows)

D = f"{PD}/smt"
SM = (f"Stanford Math Tournament files `{D}/<Y>_*` (rounds: advanced, algebra, calculus, discrete/combo, general, geometry, nt, "
      "team, power, guts, tiebreakers; 2025 also the integration bee and its qualifier — integrals policy: definite integrals "
      "numeric with `answerDisplay`, antiderivatives `self`). " + SA + CHAIN + POWER + KEYONLY
      + skip(*(f"{D}/{f}" for f in ("2022_international_results.pdf", "2022_results.pdf", "2023_results.pdf", "2023_results_online.pdf")))
      + "Slugs `<Y>-<round>`, ids `smt-<Y>-<round>-NN`; contest \"Stanford Math Tournament\", paper \"2024 Algebra\"; grade \"9-12\". ")
bank2("smt", "2025-algebra", [(f"smt-{y}", 130, f"SMT {y}: all rounds. " + SM) for y in [2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2014, 2013, 2012, 2011]])

D = f"{PD}/rmt"
RM = (f"Rice Math Tournament files `{D}/<Y>_*` (adv, alg, calc, gen, geo, power, team; 2016 has no gen/power; 2003 gen/geo solutions "
      "are scanned). " + SA + POWER + KEYONLY + "Slugs `<Y>-<round>`, ids `rmt-<Y>-<round>-NN`; contest \"Rice Math Tournament\"; grade \"9-12\". ")
bank2("rmt", "2015-alg", [(f"rmt-{yr(g)}", 70 * len(g), f"RMT {ys(g)}. " + RM) for g in [[2015, 2016], [2013, 2014], [2011, 2012], [2009, 2010], [2007, 2008], [2005, 2006], [2003, 2004]]])

D = f"{PD}/chmmc"
CH = (f"Caltech Harvey Mudd Math Competition files `{D}/<Y>_*`. " + SA + CHAIN + POWER + KEYONLY
      + "Mixer/mini-relay rounds are chained. Slugs `<Y>-<season>-<round>` when a year has two contests, else `<Y>-<round>` "
        "(CMM: `cmm-<Y>-<round>`); ids `chmmc-<slug>-NN`; contest \"CHMMC\" (from 2023 \"Caltech Math Meet\"); grade \"9-12\". "
        "Integration bee: definite integrals numeric with `answerDisplay`, antiderivatives `self`. ")
bank2("chmmc", "2013-individual", [
    ("chmmc-2013-2014", 110, "CHMMC 2013 (`2013_chmmc2013_*`) and 2014 (`2014_*`). " + CH),
    ("chmmc-2010", 110, "CHMMC 2010 — two contests: February 2010 (`2010_problems_*`, `2010_solutions_*`, slug `2010-winter-<round>`) and "
     "November 2010 (`2010_test_*`, `2010_key_*`, `2010_sol_*`, slug `2010-fall-<round>`). " + CH),
    ("chmmc-2012", 110, "CHMMC 2012 — two contests: Winter (`2012_chmmc2012_*`, slug `2012-winter-<round>`) and Fall "
     "(`2012_individual/mixer/power/team/tiebreaker.pdf` with `2012_solutions_short.pdf`, slug `2012-fall-<round>`). " + CH),
    ("chmmc-2015-2016", 100, "CHMMC 2015 and 2016. " + CH),
    ("chmmc-2017-2018", 100, "CHMMC 2017 and 2018. " + CH),
    ("chmmc-2019-2021", 135, "CHMMC 2019, 2020, 2021 (proof rounds 2020-2021 -> `self`). " + CH),
    ("chmmc-cmm-2023", 80, "Caltech Math Meet 2023 (`2023_cmm_NN_*`; files 00 and 04 are both power rounds — check whether they are the same). " + CH),
    ("chmmc-cmm-2024", 80, "Caltech Math Meet 2024 (`2024_cmm_NN_*`, including the TCS round). " + CH),
    ("chmmc-cmm-2025-2026", 150, "Caltech Math Meet 2025 and 2026 (2026 integration bee finals have no solutions — solve). " + CH),
])

D = f"{PD}/cmimc"
CM = (f"CMIMC files `{D}/<Y>_*` (algebra/NT, combinatorics/CS, geometry, team, power, finals, TCS; 2021-2022 have d1/d2 versions; "
      "2021 papers are scans but the solutions have text). " + SA + CHAIN + POWER + KEYONLY
      + "Programming/TCS questions: keep only those with a mathematical answer that can be checked (else `self`). "
        "Slugs `<Y>-<round>`, ids `cmimc-<Y>-<round>-NN`; contest \"CMIMC\"; grade \"9-12\". ")
rows = [(f"cmimc-{y}", 110, f"CMIMC {y}: all rounds"
         + {2024: " (TCS has no solutions; also `2024_mathdash_cmimc.pdf`, a 20-question activity without key — slug `2024-mathdash`)",
            2022: " (also the 2022 guts/individual/relay files)", 2023: " (plus the integration bee)", 2025: " (plus the integration bee)",
            2026: " (TCS has no solutions)"}.get(y, "") + ". " + CM) for y in [2025, 2026] + list(range(2024, 2015, -1))]
rows.append(("cmimc-cmwmc", 100, "CMWMC (CMU Math & Women Math Competition) 2023-2024: guts, individual, relay with answers "
             "(check the year printed in each file — labels may be off by one). Slugs `cmwmc-<Y>-<round>`, contest \"CMWMC\". " + CM))
bank2("cmimc", "2025-algebra", rows)

D = f"{PD}/lehigh"
LE = (f"Lehigh University High School Math Contest `{D}/<Y>_*` (mostly `paper_with_solutions`; 2015 separate paper/solutions; "
      "1997 and 1999 answers only; 2006 and 2019 scanned). " + SA + KEYONLY + SCAN
      + "Slug `<Y>`, ids `lehigh-<Y>-NN`; contest \"Lehigh HS Math Contest\"; grade \"9-12\". ")
bank2("lehigh", "2024", [(f"lehigh-{yr(g)}", 40 * len(g), f"Lehigh {ys(g)}. " + LE)
                         for g in [[2024, 2025, 2026], [2020, 2021, 2022], [2017, 2018, 2019], [2014, 2015, 2016], [2011, 2012, 2013],
                                   [2008, 2009, 2010], [2005, 2006, 2007], [2002, 2003, 2004], [1997, 1999]]])

D = f"{PD}/dmm"
DM = (f"Duke Math Meet files `{D}/<Y>_*` (individual, team, relay, devil, power, tiebreaker; answers for 2007-2009 and some "
      "solutions 2015-2022; otherwise no key). " + SA + CHAIN + POWER + KEYONLY
      + "Slugs `<Y>-<round>`, ids `dmm-<Y>-<round>-NN`; contest \"Duke Math Meet\"; grade \"9-12\". ")
bank2("dmm", "2020-individual", [(f"dmm-{yr(g)}", 45 * len(g), f"DMM {ys(g)}. " + DM)
                                 for g in [[2020, 2021, 2022], [2017, 2018, 2019], [2014, 2015, 2016], [2011, 2012, 2013], [2008, 2009, 2010], [2005, 2006, 2007]]])

D = f"{PD}/mmaths"
MM = (f"MMATHS files `{D}/<Y>_*` (individual, mathathon/marathon, mixer, team, tiebreaker, guts 2025, lightning finals 2023-2024 "
      "slides; 2014 individual has only solutions; answer keys only for 2020-2022 and none for 2021 mathathon). " + SA + CHAIN + KEYONLY
      + "Slugs `<Y>-<round>`, ids `mmaths-<Y>-<round>-NN`; contest \"MMATHS\"; grade \"9-12\". ")
bank2("mmaths", "2023-individual", [(f"mmaths-{yr(g)}", 50 * len(g), f"MMATHS {ys(g)}. " + MM)
                                    for g in [[2023, 2024, 2025], [2020, 2021, 2022], [2016, 2018, 2019], [2014, 2015]]])

bank2("jhmt", "2020-general", [
    ("jhmt-2020", 120, f"Johns Hopkins Math Tournament 2020 (`{PD}/jhmt/`): HS General, Geometry, Calculus, Algebra/NT, Prob/Combo, MS Long/Short/Team "
     "solutions, proof rounds TR1 (posets), TR2 (synthetic calculus), MS proof round (graph theory). `2020_PeobCombo.pdf` is actually the "
     "JHMT 2019 Prob/Combo test (slug `2019-probcombo`). " + SA + POWER + KEYONLY
     + "Slugs `<Y>-<round>`, ids `jhmt-2020-general-NN`; contest \"JHMT\"; grades HS \"9-12\", MS \"6-8\". "),
])

D = f"{PD}/nyciml"
NY = ("NYCIML files `{d}/<YYYY-YYYY>_<fall|spring>_<division>.pdf` (problems, answers and solutions; question labels like F15A01). "
      + SA + CHAIN + KEYONLY + SCAN
      + "Slug `<YYYY-YY>-<fall|spring>-<division>` (e.g. `2015-16-fall-seniora`), ids `nyciml-2015-16-fall-seniora-NN` (NN = printed number); "
        "contest \"NYCIML\", paper \"Fall 2015 Senior A\"; grades Senior A/B \"9-12\", Junior and Soph-Frosh \"9-10\". "
      + skip(f"{D}/2018-2019_fall_junior.pdf (= 2017-2018_fall_junior)", f"{D}/2011-2012_fall_junior.pdf (= 2011-2012_spring_junior; Fall 2011 Junior is missing)",
             f"{D}/2022-2023_spring_senior.pdf (= 2022-2023_spring_a)")).format(d=D)
NY_SKIP = {"2018-2019_fall_junior.pdf", "2011-2012_fall_junior.pdf", "2022-2023_spring_senior.pdf"}
ny = {}
if os.path.isdir(os.path.join(ROOT, D)):
    for f in sorted(os.listdir(os.path.join(ROOT, D))):
        if not f.endswith(".pdf") or f in NY_SKIP:
            continue
        sy, div = f[:9], f[:-4].split("_")[-1]
        kind = "junior" if div.startswith("junior") or div == "sophfrosh" else "senior"
        ny.setdefault((kind, sy), []).append(f)
rows = []
for kind, cap, per in (("senior", 130, 30), ("junior", 160, 20)):
    batch = []
    for sy in sorted({k[1] for k in ny if k[0] == kind}, reverse=True) + [None]:
        fs = ny.get((kind, sy), [])
        if batch and (sy is None or (sum(len(b[1]) for b in batch) + len(fs)) * per > cap):
            yrs = sorted(b[0] for b in batch)
            files = [f for b in sorted(batch) for f in b[1]]
            rows.append((f"nyciml-{kind}-{yrs[0][:4]}-{yrs[-1][5:]}", per * len(files),
                         f"NYCIML {kind} divisions, school years {', '.join(yrs)}: " + ", ".join(f"`{f}`" for f in files) + ". " + NY))
            batch = []
        if sy:
            batch.append((sy, fs))
bank2("nyciml", "2025-26-fall-seniora", rows)

rows = [("famat-samples", 60, f"FAMAT samples `{PD}/famat/`: 2021 State Alpha individual test + solutions (30 mc, choice E = NOTA) and "
         "`sample_1992_test.pdf` (scanned, check for a key). " + skip(f"{PD}/famat/_pdf_urls.json (URL list, files not downloaded)")
         + PTS + SA + KEYONLY + SCAN + "Points 4 / blank 0 / wrong -1 if printed. Slugs `2021-state-alpha-individual`, `1992-sample`; contest "
         "\"FAMAT\"; grade Alpha \"11-12\" (precalculus), else as the test's division (Theta \"9-10\", Mu \"11-12\"). ")]
bank2("famat", "2021-state-alpha-individual", rows)
bank2("mualphatheta", "2026-alpha-individual", [
    ("mualphatheta-samples", 60, f"Mu Alpha Theta samples `{PD}/mualphatheta/`: 2026 Alpha individual test + solutions, and the old Theta "
     "'Triangles' topic test #111 (no key). " + skip(f"{PD}/mualphatheta/_pdf_urls.txt (URL list)") + PTS + SA + KEYONLY
     + "30 mc each (E = NOTA). Slugs `2026-alpha-individual`, `theta-triangles-111`; contest \"Mu Alpha Theta National Convention\"; grades Alpha \"11-12\", Theta \"9-10\". "),
])

# ---------------------------------------------------------------- phase 2: olympiads
bank2("bamo", "2026", [(f"bamo-{yr(g)}", 8 * len(g), f"BAMO {ys(g)}: `{PD}/bamo/bamo/<Y>_bamo_solutions.pdf` (problems + solutions). "
                         "BAMO-8 (problems A-E) and BAMO-12 (1-5) share problems: extract in BAMO-8, `duplicateOf` in BAMO-12. " + OLY
                         + "Slugs `bamo8-<Y>`, `bamo12-<Y>`, ids `bamo-bamo8-<Y>-a`, `bamo-bamo12-<Y>-3`; contest \"BAMO\"; grades BAMO-8 \"6-8\", BAMO-12 \"9-12\". ")
                        for g in [[2022, 2023, 2024, 2025, 2026], list(range(2015, 2021)), list(range(2010, 2015)), list(range(2005, 2010)), list(range(1999, 2005))]])
bank2("usatst", "tstst-2024", [
    ("usatst-tstst-2021-2024", 33, f"USA TSTST 2021-2024: `{PD}/usatst/tstst/<Y>_tstst_paper.pdf`, `_solutions.pdf`. " + OLY + "Bank `usatst`, slug `tstst-<Y>`, contest \"USA TSTST\", grade \"10-12\". "),
    ("usatst-tstst-2016-2020", 42, f"USA TSTST 2016-2020 (same layout). " + OLY + "Slug `tstst-<Y>`, grade \"10-12\". "),
    ("usatst-tstst-2011-2015", 40, f"USA TSTST 2011-2015 (same layout). " + OLY + "Slug `tstst-<Y>`, grade \"10-12\". "),
    ("usatst-tst-2020-2025", 40, f"USA TST for IMO 2020, 2021, 2023, 2024, 2025: `{PD}/usatst/tst/<Y>_tst_paper.pdf`, `_solutions.pdf`. " + OLY + "Slug `tst-<Y>`, contest \"USA TST\", grade \"10-12\". "),
    ("usatst-tst-2012-2019", 50, f"USA TST 2012-2019 (2012-2013 papers only, no solutions — prove them yourself). " + OLY + "Slug `tst-<Y>`, grade \"10-12\". "),
])
bank2("usemo", "2019", [("usemo-2019-2025", 42, f"USEMO 2019-2025: `{PD}/usemo/usemo/<Y>_usemo_paper.pdf`, `_report_solutions.pdf`. " + OLY
                         + "Slug `<Y>`, ids `usemo-<Y>-01`; contest \"USEMO\"; grade \"9-12\". ")])
bank2("elmo", "2016", [
    ("elmo-2016-2022", 36, f"ELMO 2016-2022: `{PD}/elmo/elmo/<Y>_elmo_paper.pdf` (solutions only for 2016 — prove the rest yourself). " + OLY + "Slug `<Y>`, contest \"ELMO\", grade \"9-12\". "),
    ("elmo-2010-2014", 30, f"ELMO 2010-2014 (`{PD}/elmo/elmo/`, solutions for 2010, 2011, 2013, 2014). " + OLY + "Slug `<Y>`, grade \"9-12\". "),
] + [(f"elmo-sl-{y}", 30, f"ELMO Shortlist {y}: `{PD}/elmo/shortlist/{y}_elmo_shortlist.pdf`. Problems that were on the ELMO {y} paper: "
       "`duplicateOf` the ELMO id. " + OLY + f"Slug `sl-{y}`, ids `elmo-sl-{y}-a1` (category + number), contest \"ELMO Shortlist\", grade \"9-12\". ")
      for y in (2013, 2014, 2017, 2018, 2019)])
D = f"{PD}/bmo"
BMO = ("Bank `bmo` (UKMT British olympiads). Use the official solutions/reports where present (`_ukmt` files are the UKMT-site copies "
       "of the same papers — use either, extract once). " + OLY + "UKMT copyright: practice use only. ")
bank2("bmo", "bmo1-2020", [
    ("bmo-bmo1-2020-2026", 40, f"BMO Round 1 2020-2026: `{D}/bmo1/<Y>_bmo1_paper.pdf`, reports. `2025_bmo1_report_ukmt.pdf` is actually the 2026 report "
     "(= `2026_bmo1_report.pdf`). " + BMO + "Slug `bmo1-<Y>`, contest \"British Mathematical Olympiad Round 1\", grade \"10-12\". "),
    ("bmo-bmo1-2013-2019", 42, f"BMO Round 1 2013-2019 (`{D}/bmo1/`, reports from 2017). " + BMO + "Slug `bmo1-<Y>`, grade \"10-12\". "),
    ("bmo-bmo1-2006-2012", 40, f"BMO Round 1 2006-2012 (`{D}/bmo1/`, no solutions). " + BMO + "Slug `bmo1-<Y>`, grade \"10-12\". "),
    ("bmo-bmo1-1999-2005", 40, f"BMO Round 1 1999-2005 (`{D}/bmo1/`). " + BMO + "Slug `bmo1-<Y>`, grade \"10-12\". "),
    ("bmo-bmo1-1992-1998", 35, f"BMO Round 1 1992-1998 (`{D}/bmo1/`). " + BMO + "Slug `bmo1-<Y>`, grade \"10-12\". "),
    ("bmo-bmo2-2016-2026", 44, f"BMO Round 2 2016-2026 (`{D}/bmo2/`, solutions 2021+). " + skip(f"{D}/bmo2/2018_bmo2_paper_ukmt.pdf (it is BMO1 2018)")
     + BMO + "Slug `bmo2-<Y>`, contest \"British Mathematical Olympiad Round 2\", grade \"11-12\". "),
    ("bmo-bmo2-2004-2015", 48, f"BMO Round 2 2004-2015 (`{D}/bmo2/`). " + BMO + "Slug `bmo2-<Y>`, grade \"11-12\". "),
    ("bmo-bmo2-1992-2003", 48, f"BMO Round 2 1992-2003 (`{D}/bmo2/`). " + BMO + "Slug `bmo2-<Y>`, grade \"11-12\". "),
    ("bmo-pre1992-1973-1981", 54, f"BMO (single round) 1973-1981: `{D}/bmo-pre1992/<Y>_bmo_paper.pdf` (scans). " + SCAN + BMO + "Slug `bmo-<Y>`, contest \"British Mathematical Olympiad\", grade \"11-12\". "),
    ("bmo-pre1992-1982-1991", 60, f"BMO (single round) 1982-1991 (`{D}/bmo-pre1992/`, scans). " + SCAN + BMO + "Slug `bmo-<Y>`, grade \"11-12\". "),
    ("bmo-fist-1972-1981", 36, f"FIST (Further International Selection Test) 1972-1981: `{D}/fist/<Y>_fist_paper.pdf` (scans). " + SCAN + BMO + "Slug `fist-<Y>`, contest \"BMO FIST\", grade \"11-12\". "),
    ("bmo-fist-1982-1991", 36, f"FIST 1982-1991 (`{D}/fist/`, scans). " + SCAN + BMO + "Slug `fist-<Y>`, grade \"11-12\". "),
    ("bmo-ukmog-2019-2026", 40, f"UK Mathematical Olympiad for Girls 2019-2026: `{D}/ukmog/` (paper, solutions, report). " + BMO + "Slug `ukmog-<Y>`, contest \"UK MOG\", grade \"9-12\". "),
    ("bmo-ukmog-2011-2018", 40, f"UK MOG 2011-2018 (`{D}/ukmog/`). " + BMO + "Slug `ukmog-<Y>`, grade \"9-12\". "),
    ("bmo-mcg", 20, f"Mathematical Competition for Girls 2025-2026: `{D}/mcg/` (paper + solutions; short answers). " + SA + BMO + "Slug `mcg-<Y>`, contest \"UKMT Mathematical Competition for Girls\", grade \"9-12\". "),
])
D = f"{PD}/irmo/irmo"
IR = (f"Irish Mathematical Olympiad from `{D}/1988-2026_irmo_compendium_dukes.pdf` (problems with hints) and `1988-2014_irmo_collection.pdf` "
      "(problems). 10 problems per year (2 papers). " + OLY + "No full official solutions: write your own complete proofs. "
      "Slug `<Y>`, ids `irmo-<Y>-01`..`10`; contest \"Irish Mathematical Olympiad\"; grade \"9-12\". ")
bank2("irmo", "2023", [(f"irmo-{yr(g)}", 10 * len(g), f"IrMO {ys(g)}. " + IR) for g in groups(range(2026, 1987, -1), 4) for g in [sorted(g)]])
D = f"{PD}/india"
IN = ("Bank `india`. " + OLY + "Slugs `inmo-<Y>`, `rmo-<Y>` (several regional papers in a year: `rmo-<Y>-p<K>` / `crmo-<Y>-p<K>`, "
      "region-specific papers `rmo-<Y>-mumbai`), ids `india-inmo-<Y>-01`; contests \"INMO\", \"RMO\", \"CRMO\"; grades INMO \"9-12\", RMO \"8-12\". " + DUPS)
bank2("india", "inmo-2014", [
    ("india-inmo-2014-2026", 48, f"INMO 2014-2026 (years present): `{D}/inmo/<Y>_inmo_paper_*.pdf`, `_solutions_*`. 2020/2021 papers are scans; the 2021 "
     "file may be password-protected (the password is printed on the HBCSE page) — if it cannot be opened, skip and report. " + SCAN + IN),
    ("india-inmo-2002-2012", 54, f"INMO 2002-2012 (years present; 2010 scanned). " + SCAN + IN),
    ("india-rmo-2001-2009", 54, f"RMO 2001-2009: `{D}/rmo/<Y>_rmo_*`. " + IN),
    ("india-rmo-2010-2014", 60, f"RMO 2010, CRMO 2013 (5 papers), 2014 (4 papers) with solutions. " + IN),
    ("india-rmo-2015-2016", 54, f"CRMO/RMO 2015 (5 papers) and 2016 (4 papers). " + IN),
    ("india-rmo-2017-2025", 36, f"RMO 2017, 2019, 2023 (2 papers), 2025 (2 papers) incl. the KV/JNV and Mumbai-region variants. " + IN),
])
bank2("amo-aus", "amo-2016", [("amo-aus-2016-2020", 40, f"Australian Mathematical Olympiad 2016-2020: `{PD}/amo-aus/amo/<Y>_amo_solutions.pdf` (8 problems each). "
                               + OLY + skip(f"{PD}/amo-aus/aimo/2017_aimo_solutions.pdf (byte-identical to the amt copy; extracted in bank `amt`)")
                               + "Slug `amo-<Y>`, contest \"Australian Mathematical Olympiad\", grade \"10-12\". ")])
bank2("nzmo", "2026-r1", [(f"nzmo-{yr(g)}", 13 * len(g), f"NZMO {ys(g)}: `{PD}/nzmo/nzmo/<Y>_round<R>_{{paper,solutions}}.pdf`. " + OLY
                          + "Slugs `<Y>-r1`, `<Y>-r2`; contest \"New Zealand Mathematical Olympiad\"; grade \"9-12\" (licence CC BY 4.0). ")
                         for g in [[2023, 2024, 2025, 2026], [2019, 2020, 2021, 2022]]])
D = f"{PD}/tot/tot"
TT = (f"Tournament of Towns `{D}/<Y>_<fall|spring>_<O|A>_tot<NN>_paper.pdf` (solutions only in `2019_fall_*_tot41_solutions`, "
      "`2021_spring_all_tot42_solutions`, `2026_fall_all_tot48_solutions`; else prove them yourself). Each paper has Junior and Senior "
      "problem sets; problems on both: extract in Junior, `duplicateOf` in Senior. " + OLY + PTS
      + "Slugs `<Y>-<fall|spring>-<o|a>-<junior|senior>`, ids `tot-2019-fall-a-junior-03`; contest \"Tournament of Towns\", paper \"Fall 2019 A-level Junior\"; "
        "grades Junior \"8-9\", Senior \"10-12\". ")
bank2("tot", "2019-fall-a-junior", [(f"tot-{y}", 23 if y in (2015, 2026) else 45, f"ToT {y} (all seasons/levels present). " + TT)
                                     for y in [2019] + [y for y in range(2015, 2027) if y != 2019]])
bank2("igo", "2021-elementary", [("igo-all", 35, f"Iranian Geometry Olympiad `{PD}/igo/igo/`: 2019 and 2021 booklets (elementary, intermediate, advanced "
                                  "with solutions), 2025 elementary paper. " + OLY + DUPS + "Slugs `<Y>-<level>`, ids `igo-2021-advanced-03`; contest \"Iranian Geometry Olympiad\"; "
                                  "grades elementary \"7-8\", intermediate \"9-10\", advanced \"11-12\". ")])
bank2("emc", "2025-junior", [(f"emc-{yr(g)}", 8 * len(g), f"European Mathematical Cup {ys(g)}: `{PD}/emc/emc/<Y>_<junior|senior>_{{paper,solutions}}.pdf`"
                              + (" and the 2008 BSMC papers (`2008_bsmc_*`, slug `bsmc-2008-<level>`)" if 2012 in g else "") + ". " + OLY
                              + "Slugs `<Y>-junior`, `<Y>-senior`; contest \"European Mathematical Cup\"; grades junior \"7-10\", senior \"9-12\". ")
                             for g in [list(range(2021, 2026)), list(range(2016, 2021)), list(range(2012, 2016))]])
bank2("balticway", "2025", [(f"balticway-{yr(g)}", 20 * len(g), f"Baltic Way {ys(g)}: `{PD}/balticway/balticway/<Y>_bw_paper.pdf`, `_solutions.pdf` "
                             "(no solutions for 2009, 2019, 2022 — prove yourself; 2011 paper scanned). " + OLY
                             + "Slug `<Y>`, ids `balticway-<Y>-01`..`20`; contest \"Baltic Way\"; grade \"9-12\". ")
                            for g in [sorted(g) for g in groups(range(2025, 1989, -1), 2)]])
D = f"{PD}/nordic/nmc"
bank2("nordic", "2026", [(f"nordic-{yr(g)}", 4 * len(g), f"Nordic Mathematical Contest {ys(g)}: `{D}/<Y>_nmc_paper.pdf`, `_solutions.pdf`; "
                          "`1987-2011_nmc_all_solutions.pdf` has all problems and solutions to 2011 (use it for years without files; 1999 solutions, "
                          "2001/2003 papers are scans). " + OLY + "Slug `<Y>`, contest \"Nordic Mathematical Contest\", grade \"9-12\". ")
                         for g in [list(range(2017, 2027)), list(range(2007, 2017)), list(range(1997, 2007)), list(range(1987, 1997))]])
bank2("bxmo", "2026", [(f"bxmo-{yr(g)}", 4 * len(g), f"Benelux MO {ys(g)}: `{PD}/bxmo/bxmo/<Y>_bxmo_paper.pdf`, `_solutions.pdf` (2009 has no solutions). "
                        + OLY + "Slug `<Y>`, contest \"Benelux Mathematical Olympiad\", grade \"9-12\". ") for g in [list(range(2018, 2027)), list(range(2009, 2018))]])
bank2("memo", "2025-individual", [
    ("memo-2021-2025", 36, f"MEMO 2021, 2023, 2025: `{PD}/memo/memo/<Y>_solutions.pdf` (+ papers). 4 individual + 8 team problems. " + OLY
     + "Slugs `<Y>-individual`, `<Y>-team`, ids `memo-<Y>-i1`, `-t5`; contest \"Middle European Mathematical Olympiad\"; grade \"9-12\". "),
    ("memo-2010-2020", 36, f"MEMO 2010 (individual/team papers, no solutions), 2015 and 2020 solution booklets (`{PD}/memo/memo/`). " + OLY + "Same slugs/ids. "),
])
bank2("balkan", "bmo-2024", [("balkan-all", 20, f"Balkan MO 2024 (paper + solutions), 2025, 2026 (solutions) `{PD}/balkan/bmo/`; Junior Balkan MO 2013, 2025 "
                              f"`{PD}/balkan/jbmo/`. " + OLY + "Slugs `bmo-<Y>`, `jbmo-<Y>`; contests \"Balkan MO\", \"Junior Balkan MO\"; grades \"9-12\", \"7-10\". ")])
bank2("rmm", "2023", [(f"rmm-{yr(g)}", 6 * len(g), f"Romanian Masters of Mathematics {ys(g)}: `{PD}/rmm/rmm/<Y>_day<D>_paper.pdf` (solutions only for 2021 and 2023). "
                       + OLY + "Slug `<Y>`, contest \"RMM\", grade \"9-12\". ") for g in [[2021, 2023, 2024, 2025, 2026], [2013, 2015, 2016, 2017, 2018, 2019]]])

# ---------------------------------------------------------------- phase 2: university
INTB = ("Integrals: definite integrals -> numeric (the exact value as an explicit expression, `answerDisplay` in KaTeX); "
        "antiderivatives, or values needing functions outside the allowed list (arctan, erf, ...) -> `self` with the official answer. ")
D = f"{PD}/mitintbee"
bank2("mitintbee", "qual-2026", [
    ("mitintbee-qual-2018-2026", 150, f"MIT Integration Bee qualifying tests 2018-2020, 2022-2026: `{D}/qualifying_round_<Y>_test.pdf`, `_answers.pdf` "
     "(answers only). " + INTB + KEYONLY + "Slug `qual-<Y>`, ids `mitintbee-qual-<Y>-NN`; contest \"MIT Integration Bee\", paper \"2024 Qualifying Round\"; grade \"undergrad\". "),
    ("mitintbee-qual-2010-2017", 160, f"MIT Integration Bee qualifying tests 2010-2017 (`{D}/qualifying_round_<Y>_*`). " + INTB + KEYONLY + "Slug `qual-<Y>`, grade \"undergrad\". "),
    ("mitintbee-rounds-2022-2026", 150, f"MIT Integration Bee rounds 2022-2026: `{D}/<Y>_{{regular_season,quarterfinal,semifinal,finals}}.pdf` (slides; each "
     "integral is followed by its answer). Skip repeated slides. " + INTB + KEYONLY + "Slugs `<Y>-<round>`, grade \"undergrad\". "),
])
bank2("gre_math", "gr3768", [("gre_math-gr3768", 66, f"GRE Mathematics practice book `{PD}/gre_math/GR3768_practice_book.pdf` (66 mc with key, no solutions). "
                              + KEYONLY + "Slug `gr3768`, ids `gre_math-gr3768-NN`; contest \"GRE Mathematics Subject Test\", paper \"Practice Book GR3768\"; grade \"undergrad\". "
                              "ETS copyright: practice use only. ")])
MSQ = ("Multiple-select questions (MSQ, one or more correct): `text` with `answer` like `\"AC\"` and `acceptedAnswers` [\"A,C\", \"A, C\", \"CA\"], "
       "options listed in the prompt. Numerical-answer questions (NAT) given as a range in the key: `numeric` with the exact value, range in the solution. ")
D = f"{PD}/iitjam"
JAM = (f"IIT JAM Mathematics (MA) papers `{D}/<Y>_ma_paper.pdf` (60 questions: MCQ -> `mc`, MSQ, NAT). Only 2026 has a key "
       "(`2026_ma_key.pdf`) — for other years solve every question carefully. " + MSQ + KEYONLY + PTS
       + "Negative marks only for MCQ (-1/3, -2/3 as printed). Slug `<Y>`, ids `iitjam-<Y>-NN`; contest \"IIT JAM\", paper \"2024 Mathematics (MA)\"; grade \"undergrad\". ")
bank2("iitjam", "2026", [(f"iitjam-{yr(g)}", 60 * len(g), f"IIT JAM MA {ys(g)}. " + JAM + (SCAN if set(g) & {2013, 2014, 2017} else ""))
                         for g in [[2026], [2024, 2025], [2022, 2023], [2020, 2021], [2018, 2019], [2016, 2017], [2014, 2015], [2012, 2013]]])
D = f"{PD}/gate_ma"
GA = (f"GATE Mathematics (MA) papers `{D}/` with keys 2021-2026. Extract only the 55 mathematics questions; skip the 10 General Aptitude "
      "questions. " + MSQ + KEYONLY + PTS + "Slug `<Y>`, ids `gate_ma-<Y>-NN` (printed MA number); contest \"GATE\", paper \"2024 Mathematics (MA)\"; "
      "grade \"undergrad\" with `grades: [13, 14]`. ")
bank2("gate_ma", "2026", [(f"gate_ma-{yr(g)}", 55 * len(g), f"GATE MA {ys(g)}" + (" (2019 and 2021 papers are images; 2021 key too)" if set(g) & {2019, 2021} else "") + ". " + GA
                           + (SCAN if set(g) & {2019, 2021} else "")) for g in [[2025, 2026], [2023, 2024], [2021, 2022], [2019, 2020]]])
D = f"{PD}/nbhm"
NB = (f"NBHM scholarship tests `{D}/` (`msc<YY>` MSc papers 2005-2019 + keys, `nbhmra<YY>` PhD papers 2005-2022 + keys (2014 has no key; "
      "2005 key is `nbhmra05ans.pdf`), `comb<YY>` combined papers 2023-2026 + keys). Questions are short answers, true/false, or "
      "'which of the following' with several correct options. True/false -> `text` (\"True\"/\"False\", variants T/F). " + MSQ + SA + KEYONLY
      + "Slugs `msc-<Y>`, `phd-<Y>`, `comb-<Y>`, ids `nbhm-phd-<Y>-NN` (section letter + number if numbering restarts per section); contest \"NBHM\"; "
        "grades MSc \"undergrad\", PhD \"grad\", combined \"undergrad\" with `grades: [13, 14]`. ")
rows = [("nbhm-comb-2023-2026", 140, "NBHM combined papers 2023-2026. " + NB)]
rows += [(f"nbhm-phd-{yr(g)}", 35 * len(g), f"NBHM PhD papers {ys(g)}. " + NB) for g in [sorted(g) for g in bal(list(range(2022, 2004, -1)), 3)]]
rows += [(f"nbhm-msc-{yr(g)}", 35 * len(g), f"NBHM MSc papers {ys(g)}. " + NB) for g in [sorted(g) for g in bal(list(range(2019, 2004, -1)), 3)]]
bank2("nbhm", "comb-2023", rows)
D = f"{PD}/madhava"
MA = (f"Madhava Mathematics Competition papers `{D}/` with answers/solutions files (names vary: `MadhavaPaper2010`, `MMCpaper11`, `MMC14-QP`, "
      "`MMC15-JAN-QP`, `MMC-Jan-2017`, `MMC2020-solutions`, ...; 2021 and 2022 also have second rounds). Part A mc/short answers, later parts "
      "proofs (`self`). " + SA + KEYONLY + PTS + SCAN + "Slug `<Y>` (`<Y>-r2` for second rounds; Dec 2014 vs Jan 2015 papers: `2014-dec`, `2015-jan`), "
        "ids `madhava-<Y>-NN`; contest \"Madhava Mathematics Competition\"; grade \"undergrad\". ")
bank2("madhava", "2026", [(f"madhava-{yr(g)}", 20 * len(g) + (20 if 2021 in g else 0), f"Madhava {ys(g)}. " + MA)
                          for g in [[2023, 2024, 2025, 2026], [2019, 2020, 2021, 2022], [2015, 2016, 2017, 2018], [2010, 2011, 2012, 2013, 2014]]])
D = f"{PD}/seemous"
bank2("seemous", "2025", [
    ("seemous-2017-2026", 40, f"SEEMOUS 2017-2026 from `{D}/2007-2025_compilation_uoa.pdf`, the 2020 and 2024 official papers+solutions, the 2025 "
     "NKUA team report and the 2026 problem 1-4 solutions. " + UNI + "Slug `<Y>`, contest \"SEEMOUS\". "),
    ("seemous-2007-2016", 40, f"SEEMOUS 2007-2016 from `{D}/2007-2025_compilation_uoa.pdf`. " + UNI + "Slug `<Y>`. "),
])
D = f"{PD}/irish_iv"
bank2("irish_iv", "2011", [
    ("irish_iv-2000-2011", 90, f"Irish Intervarsity Mathematics Competition 2000-2003, 2006-2008, 2009, 2011: `{D}/<Y>.pdf` + `.tex` (+ `-ans.pdf` answers; "
     "2009 and 2011 only `.tex`). The LaTeX source is easiest. " + UNI + KEYONLY + "Slug `<Y>`, contest \"Irish Intervarsity Mathematics Competition\". "),
    ("irish_iv-1990-1999", 70, f"Irish Intervarsity 1990-1994, 1997, 1999 (`{D}/`, same layout). " + UNI + KEYONLY + "Slug `<Y>`. "),
])
bank2("icmc", "2025-26-r1", [("icmc-all", 90, f"Imperial College Mathematics Competition `{PD}/icmc/`: 2018-19 to 2025-26 Round 1 and Round 2 (solutions "
                              "from 2019-20) and team rounds from 2021-22. " + UNI + KEYONLY
                              + "Slugs `<YYYY-YY>-r1`, `-r2`, `-team`; contest \"ICMC\". ")])
D = f"{PD}/schweitzer"
bank2("schweitzer", "2024", [(f"schweitzer-{yr(g)}", 11 * len(g), f"Miklós Schweitzer Competition {ys(g)}: `{D}/` (English papers where present, "
                              "otherwise Hungarian — translate carefully; Hungarian solutions 2009-2025: translate/summarise them). Research-level: "
                              "write complete proofs; when you cannot produce a full proof, give the strongest argument you can and set `reviewNote`. "
                              + "Type `self` unless a single value is asked. Slug `<Y>`, ids `schweitzer-<Y>-NN`; contest \"Miklós Schweitzer\"; grade \"grad\". ")
                             for g in [[2022, 2023, 2024, 2025], [2018, 2019, 2020, 2021], [2014, 2015, 2016, 2017], [2010, 2011, 2012, 2013],
                                       [2006, 2007, 2008, 2009], [2002, 2003, 2004, 2005], [1998, 1999, 2000, 2001], [1987, 1995, 1997]]])

# ---------------------------------------------------------------- phase 2: graduate qualifying exams
D = f"{PD}/quals"
QB = ("Bank `quals`. Slugs `<university>-<subject>-<YYYY><f|s|w|su>` (term from the exam header; Berkeley without subject: `berkeley-2026s`), "
      "ids `quals-<slug>-NN` (`-a03`/`-b03` for exams with parts A/B or days); `source.contest` e.g. \"UCLA Algebra Qualifying Exam\", "
      "`source.paper` \"Fall 2005\". " + QUAL)


def qkey(f):
    m = re.search(r"(19|20)\d\d", f)
    if m:
        return (int(m.group()), f)
    m = re.search(r"(?<!\d)(\d\d)(?!\d)", f)
    return ((1900 if int(m.group(1)) > 50 else 2000) + int(m.group(1)) if m else 9999, f)


def qfiles(sub, skipset=()):
    p = os.path.join(ROOT, D, sub)
    return sorted((f for f in os.listdir(p) if f.endswith(".pdf") and f not in skipset), key=qkey) if os.path.isdir(p) else []


def qsubject(f, table):
    s = f.lower()
    for key, pats in table:
        if any(x in s for x in pats):
            return key
    return "misc"


def qunits(uni, files, table, per, note, size=50):
    by = {}
    for f in files:
        by.setdefault(qsubject(f, table), []).append(f)
    out = []
    for subj, fs in by.items():
        for i, chunk in enumerate(bal(fs, max(1, round(size / per.get(subj, 8))))):
            out.append((f"quals-{uni}-{subj}-{i + 1}", per.get(subj, 8) * len(chunk),
                        f"{note} Subject: {subj}. Files (in `{D}/{uni if uni != 'gatechold' else 'gatech_old'}/`): " + ", ".join(f"`{f}`" for f in chunk) + ". "))
    return out


rows = [("quals-berkeley-1", 54, f"Berkeley Preliminary Exam Spring 2026, Fall 2025, Spring 2025: `{D}/berkeley/spring_26_prelimexam.pdf` + "
         "`spring_2026_prelim_solutions_0.pdf`, `fall_2025_prelimexam.pdf` + `fall2025prelimexam_solutions.pdf`, `prelimexam_spring_2025.pdf` + "
         "`_solutions.pdf`. 18 problems per exam (two days, 1A-9A / 1B-9B -> ids `-a01`, `-b09`). Use the official solutions. "),
        ("quals-berkeley-2", 54, f"Berkeley Preliminary Exam Fall 2024, Spring 2024, Fall 2023 (`{D}/berkeley/prelimexam_<term>_<Y>.pdf` + `_solutions.pdf`). "),
        ("quals-berkeley-3", 36, f"Berkeley Preliminary Exam Spring 2023 (`spr23prelim.pdf` + `sp23prelimsol.pdf`) and Fall 2022 (`prelimexam.pdf`, no "
         "solutions; confirm the term in the header). ")]
rows = [(u, e, t + QB) for u, e, t in rows]
wis = [f for f in qfiles("wisconsin_algebra") if not f.startswith("qualans")]
wis.sort(key=lambda f: (int(f[-6:-4]) + (1900 if int(f[-6:-4]) > 50 else 2000), f))
for i, g in enumerate(bal(wis, 10)):
    ans = [f"qualans{f[4:]}" for f in g if f"qualans{f[4:]}" in qfiles("wisconsin_algebra")]
    rows.append((f"quals-wisconsin-algebra-{i + 1}", 5 * len(g), f"Wisconsin algebra qualifying exams (D. Passman's archive) `{D}/wisconsin_algebra/`: "
                 + ", ".join(f"`{f}`" for f in g) + (f"; solutions: " + ", ".join(f"`{f}`" for f in ans) if ans else "; no solutions") + ". "
                 "Contest \"Wisconsin Algebra Qualifying Exam\". " + QB))
GT_OLD_SKIP = {"compFall01.pdf", "compFall03AlgSol.pdf", "compFall03AnSol.pdf", "compFall04AlgSol.pdf", "compFall04AnSol.pdf", "compFall05AlgSol.pdf",
               "compSpring04AlgSol.pdf", "compSpringl04AnSol.pdf", "compSpring05AlgSol.pdf", "compSpring05AnSol.pdf"}
GT_TABLE = [("numerical", ["num"]), ("algebra", ["alg"]), ("analysis", ["anal", "comp_summer2019"]), ("discrete", ["discrete"]),
            ("diffeq", ["diffeq", "decomp", "differential"]), ("topology", ["top"]), ("probability", ["prob"])]
rows += [(u, e, t + QB) for u, e, t in qunits(
    "gatech", qfiles("gatech"), GT_TABLE, {"algebra": 8, "analysis": 8, "discrete": 6, "diffeq": 8, "numerical": 8, "probability": 8, "topology": 7, "misc": 8},
    "Georgia Tech comprehensive exams. Many 12-13 page files are a cover sheet + one problem per page; `Sample_Comp_*` (2001-2016) often include "
    "solutions — use them; `Comp<Subject>Problems.pdf` are official practice-problem lists (slug `gatech-<subject>-practice`); "
    "`Sample_Comp_Fa01Alg_Anal_0.pdf`, `Sample_Comp_Fa02Alg_Anal.pdf`, `Sample_Comp_Sp03Alg_Anal.pdf` hold both algebra and analysis (extract both). "
    "Contest \"Georgia Tech Comprehensive Exam\".")]
rows.append(("quals-gatechold-1", 50, f"Georgia Tech comps from E. Harrell's archive `{D}/gatech_old/`: `compFall02.pdf` + `compFall02answers.pdf`, "
             "`compSpring03.pdf`, `compFall04Alg.pdf`, `compFall04An.pdf`, `compFall05Alg.pdf`, `compFall05An.pdf`, `compSpring04Alg.pdf`, `compSpring04An.pdf` "
             "— first compare each with the `gatech/Sample_Comp_*` file of the same term (another unit extracts those): skip exams that are the same, use "
             "the answers files as solutions for them only if they add something (do not edit other units' files). Also the 2003 problem/solution sets "
             "`func1.pdf`, `func2.pdf`, `group1.pdf`, `real1.pdf`, `real2.pdf` (slugs `gatech-practice-<name>`; student-written solutions — verify). "
             + skip(*(f"{D}/gatech_old/{f} (byte-identical to a gatech/Sample_Comp_* file)" for f in sorted(GT_OLD_SKIP))) + QB))
UCLA_TABLE = [("onla", ["onla"]), ("ade", ["ade"]), ("na", ["numerical", "na-", "na_"]), ("algebra", ["algebra"]), ("analysis", ["analysis"]),
              ("basic", ["basic"]), ("gt", ["gt", "geo"]), ("logic", ["logic"])]
rows += [(u, e, t + QB) for u, e, t in qunits(
    "ucla", qfiles("ucla", {"na-07S.pdf"}), UCLA_TABLE, {"ade": 8, "algebra": 10, "analysis": 11, "basic": 12, "gt": 9, "logic": 8, "na": 8, "onla": 12},
    "UCLA qualifying exams (file names `<subject>-<YY><F|S|W>.pdf` up to 2020, mixed names after; `Geo-Top-Exam.pdf` and `Logic-Exam.pdf` are undated — "
    "take the term from the header). About half are scans. `na-07S.pdf` is byte-identical to `na-07F.pdf` (extracted once; check which term it is). "
    + SCAN + "Contest \"UCLA <Subject> Qualifying Exam\" (Basic, Algebra, Analysis, Geometry/Topology, Logic, Numerical Analysis, Applied Differential "
    "Equations, Optimization/Numerical Linear Algebra).")]
IND_SKIP = {"syllabus-algebra.pdf", "syllabus-analysis.pdf", "algebra-complete.pdf", "AnalysisCompleteToAug2023.pdf"}
rows += [(u, e, t + QB) for u, e, t in qunits(
    "indiana", qfiles("indiana", IND_SKIP), [("algebra", ["alg"]), ("analysis", ["anal"])], {"algebra": 8, "analysis": 8},
    "Indiana University Tier 1 exams (about a quarter are scans). `algebra-complete.pdf` and `AnalysisCompleteToAug2023.pdf` are compilations of the "
    "same exams — use them only to read an unclear scan. " + skip(f"{D}/indiana/syllabus-algebra.pdf", f"{D}/indiana/syllabus-analysis.pdf") + SCAN
    + "Contest \"Indiana Tier 1 Algebra Exam\" / \"Indiana Tier 1 Analysis Exam\".")]
rows += [(u, e, t + QB) for u, e, t in qunits(
    "utaustin", qfiles("utaustin"), [("algebra", ["algebra"]), ("analysis", ["analysis"]), ("applied", ["appl"]), ("numerical", ["num"]),
                                     ("probability", ["prob"]), ("topology", ["top"])], {"algebra": 4, "analysis": 4, "applied": 4, "numerical": 3, "probability": 3, "topology": 3},
    "UT Austin prelims (`<YYYY>_<MM>_<Subject>_<A|B>.pdf`, A and B are the two parts of one exam: ids `-a01`, `-b02`; 19 files are scans). "
    + SCAN + "Contest \"UT Austin <Subject> Prelim\".", size=45)]
rows += [(u, e, t + QB) for u, e, t in qunits(
    "uw", qfiles("uw"), [("algebra", ["alg"]), ("complex", ["complex"]), ("linear", ["linear"]), ("manifolds", ["manifold"]), ("reals", ["real", "analysis"])],
    {"algebra": 7, "complex": 7, "linear": 7, "manifolds": 7, "reals": 7},
    "University of Washington prelims (`prelim-exam-<subject>-<Y>.pdf` 2005-2016 may contain more than one sitting — extract all; 2017-2020 mixed "
    "names). Contest \"UW <Subject> Prelim\".")]
rows += [(u, e, t + QB) for u, e, t in qunits(
    "stanford", qfiles("stanford"), [("algebra", ["algebra"]), ("analysis", ["real_analysis"]), ("geomtop", ["geometry"]), ("applied", ["applied"])],
    {"algebra": 8, "analysis": 6, "geomtop": 8, "applied": 10},
    "Stanford qualifying exams `<Y>_<Autumn|Spring>_<Subject>_Qual.pdf` (no solutions; `Practice_*` files are official practice sets, slug "
    "`stanford-<subject>-practice`). Contest \"Stanford <Subject> Qualifying Exam\".")]
rows += [(u, e, t + QB) for u, e, t in qunits(
    "minnesota", qfiles("minnesota"), [("complex", ["complex"]), ("real", ["real"]), ("algebra", [".pdf"])], {"complex": 7, "real": 7, "algebra": 7},
    "University of Minnesota written prelims (P. Garrett's archive; unprefixed files are algebra). Contest \"Minnesota <Subject> Written Prelim\".")]
bank2("quals", "berkeley-2026s", rows)


def main():
    old = {}
    if os.path.exists(QUEUE):
        old = {u["id"]: u for u in json.load(open(QUEUE))}
    out = []
    for u in units:
        o = old.get(u["id"], {})
        u["status"] = o.get("status", "pending")
        for k in ("agent", "note", "result"):
            if k in o:
                u[k] = o[k]
        out.append(u)
    ids = {u["id"] for u in units}
    out += [o for o in old.values() if o["id"] not in ids]
    os.makedirs(os.path.dirname(QUEUE), exist_ok=True)
    json.dump(out, open(QUEUE, "w"), indent=1, ensure_ascii=False)
    from collections import Counter
    print(len(out), "units;", dict(Counter(u["phase"] for u in out)), "est questions", sum(u["est"] for u in out))


if __name__ == "__main__":
    main()
