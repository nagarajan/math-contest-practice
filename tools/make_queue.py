#!/usr/bin/env python3
"""Generate extraction work units into sources/work/queue.json (keeps status of existing units)."""
import json
import os

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
CEMC_NOTE = ("Official papers and solutions are in `{d}` (`<Y>_<contest>_paper.pdf`, `<Y>_<contest>_solutions.pdf`). "
             "Use the official solutions as the first approach. Contest name in `source.contest`, e.g. \"Gauss Contest (CEMC)\".")
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
      + " Full-solution contests with parts: one question per part (number like `02c`); short-answer parts numeric/text, explanations/proofs `self`. "
      "Slugs `fryer-<Y>`, `galois-<Y>`, `hypatia-<Y>`. Points as printed.")
for g in groups(range(2011, 2026), 5):
    U(f"cemc-cimc-csmc-{yr(g)}", 1, "cemc", 30 * len(g),
      f"CEMC Canadian Intermediate (CIMC, grades 9-10) and Senior (CSMC, grades 11-12) Mathematics Contests, {', '.join(map(str, g))}. "
      + CEMC_NOTE.format(d=f"{CE}/cimc/, {CE}/csmc/")
      + " Part A short answers (numeric), Part B full solutions (one question per part; `self` where an explanation/proof is required). "
      "They share problems: extract in CIMC, `duplicateOf` in CSMC. Slugs `cimc-<Y>`, `csmc-<Y>`. Points as printed.")

# ---------------------------------------------------------------- phase 1: AMC / AIME (AoPS wiki via tools/aops.py)
AMC_NOTE = ("Source: AoPS wiki via `tools/aops.py page \"<title>\"` (problems page, answer key page, and per-problem pages for reference). "
            "Set `source.url` to the official AoPS wiki page URL (https://artofproblemsolving.com/wiki/index.php/<Title_with_underscores>). "
            "Transcribe the problem text and choices from the LaTeX; download figures with `tools/aops.py fig`. ")
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
      "Slugs `ms-<Y>`, `hs-<Y>`; grades \"6-8\" and \"9-12\"; points as printed (they vary by problem).")
U("mathcounts-2026", 1, "mathcounts", 200,
  "MATHCOUNTS 2026 Competition Series: `sources/pdfs/mathcounts/competitions/` (chapter and state Sprint, Target, Team and Countdown rounds, "
  "with answers and solutions). Slugs `2026-chapter-sprint`, `2026-state-target`, etc.; grade \"6-8\"; points null; contest \"MATHCOUNTS\". "
  "Countdown questions are short: still include them.")
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
    os.makedirs(os.path.dirname(QUEUE), exist_ok=True)
    json.dump(out, open(QUEUE, "w"), indent=1, ensure_ascii=False)
    from collections import Counter
    print(len(out), "units;", dict(Counter(u["phase"] for u in out)), "est questions", sum(u["est"] for u in out))


if __name__ == "__main__":
    main()
