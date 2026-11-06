# High school (US grades 9-12), non-olympiad contests

Answer-based contests: multiple choice or short numeric/expression answers. Proof olympiads (USAMO, BMO, CMO, IrMO, NZMO, SAMO round 3, HMIC, USAMTS, BAMO, Math Prize Olympiad) are in `olympiad.json`. They are named here only so the two bands do not overlap.

The machine-readable catalog is `high-school.json` (52 entries).

**Estimated freely available questions: about 120,000.** About 40,500 of these come from the curated contests. The other ~80,000 is a rough estimate for the FAMAT and Mu Alpha Theta archives, which I recorded by URL list and did not download.

The PDFs are in `sources/pdfs/<bankId>/` and take about 1.6 GB. AoPS wiki contests are HTML and were not downloaded; only the URL pattern is recorded.

## Available competitions

| Competition / level | Grades | Format | Free years | Keys / solutions | Type | Est. questions | Location |
|---|---|---|---|---|---|---|---|
| AMC 10 (A/B) | 9-10 | MC 25 | 2000-2025 | AoPS key + solutions | html | 1,325 | AoPS wiki |
| AMC 12 (A/B) | 11-12 | MC 25 | 2000-2025 | AoPS | html | 1,325 | AoPS wiki |
| AHSME | 9-12 | MC 30-50 | 1950-1999 | AoPS | html | 1,810 | AoPS wiki |
| AIME I/II | 9-12 | integer 15 | 1983-2026 | AoPS | html | 1,065 | AoPS wiki |
| Kangaroo Austria (English) Junior | 9-10 | MC 30 | 2009-2025 | key (scanned) | text | 510 | kangaroo/austria |
| Kangaroo Austria (English) Student | 11-12 | MC 30 | 2009-2025 | key (scanned) | text | 510 | kangaroo/austria |
| Kangaroo Austria Cadet (grades 7-8, boundary) | 7-8 | MC 30 | 2009-2025 | key | text | 510 | kangaroo/austria |
| Kangaroo Canada gr 9-10 | 9-10 | MC 30 | 2002, 2003, 2007, 2012-2023 | keys 2002/03/07 + API 2014+ | text | 450 | kangaroo/canada |
| Kangaroo Canada gr 11-12 | 11-12 | MC 30 | same | same | text | 450 | kangaroo/canada |
| CEMC Pascal / Cayley / Fermat | 9 / 10 / 11 | MC 25 | 1997-2026 | official solutions | text | 750 each | cemc/{pascal,cayley,fermat} |
| CEMC Euclid | 12 | mixed 10 | 1998-2026 | official | text | 290 | cemc/euclid |
| CEMC Fryer / Galois / Hypatia | 9 / 10 / 11 | mixed 4 (multi-part) | 2003-2026 | official | text | 96 each | cemc/{fryer,galois,hypatia} |
| CEMC CIMC / CSMC | 9-10 / 11-12 | mixed 9 | 2011-2025 | official | text | 135 each | cemc/{cimc,csmc} |
| CEMC CTMC (team) | 9-12 | short ~50 | 2012-2026 | official | text | 750 | cemc/ctmc |
| UKMT IMC | 8-10 | MC 25 | 2012, 2015-2026 | official | text | 325 | ukmt/imc |
| UKMT SMC | 11-12 | MC 25 | 2009, 2012-13, 2015-2026 | official | text | 375 | ukmt/smc |
| UKMT Grey / Pink Kangaroo | 8 / 9-10 | MC 25 | 2015-2026 | official | text | 300 each | ukmt/{grey,pink} |
| UKMT Senior Kangaroo | 11-12 | integer 20 | 2015-2025 | official | text | 220 | ukmt/senior-kangaroo |
| UKMT Senior Team Maths Challenge | 10-12 | short | 4 finals, 2 regionals | answers | text | 240 | ukmt/stmc, stmc-nf |
| Purple Comet HS | 9-12 | integer 30 | 2004-2026 | answers 2005+ (HTML) | text | 690 | purplecomet/hs |
| HMMT February | 9-12 | short | 1998-2026 | official | text | 2,600 | hmmt/feb |
| HMMT November | 9-12 | short | 2008-2025 | official | text | 1,190 | hmmt/nov |
| PUMaC | 9-12 | short | 2007-2025 | official | text | 1,900 | pumac |
| BMT (Berkeley) | 9-12 | short | 2012-2025 | official | text | 1,700 | bmt |
| SMT (Stanford) | 9-12 | short | 2011-14, 2018-25 | official | text | 1,500 | smt |
| CMIMC | 9-12 | short | 2016-2026 | official | text | 900 | cmimc |
| CHMMC / Caltech Math Meet | 9-12 | short | 2010-2021, 2023-2026 | official | text | 950 | chmmc |
| ARML | 9-12 | short | 1995-2020 (books), 2019, 2023, 2025 | official | mixed | 1,260 | arml |
| ARML Local | 9-12 | short | 2008-2019 | official | text | 360 | arml (books), arml/local |
| Math Prize for Girls | 9-12 | short 20 | 2009-2019, 2021-2026 | official | text | 340 | mathprize/main |
| NYCIML (4 divisions) | 9-12 | short | 1984-85 to 2025-26 | in file | mixed | ~8,000 | nyciml |
| Duke Math Meet | 9-12 | short | 2005-2022 | official | text | 650 | dmm |
| Rice Math Tournament | 9-12 | short | 2003-2016 (ended) | official | text | 960 | rmt |
| MMATHS (Yale) | 9-12 | short | 2014-16, 2018-25 | official | mixed | 650 | mmaths |
| JHMT (Johns Hopkins) | 9-12 | short | 2020 only (PDF) | partial | text | 80 | jhmt |
| Lehigh HS Math Contest | 9-12 | short ~25-40 | 1997, 1999, 2002-22, 2024-26 | solutions in file | text | 750 | lehigh |
| FAMAT (Florida) | 9-12 | MC 30 | ~1990s-2026 | yes | mixed | ~60,000 (rough) | URL list: famat/_pdf_urls.json |
| Mu Alpha Theta National | 9-12 | MC 30 | ~2000s-2026 | yes | mixed | ~20,000 (rough) | URL list: mualphatheta/_pdf_urls.txt |
| SAMO senior rounds 1-2 (South Africa) | 10-12 | MC/integer 20 | 1997-2026 | official | text | 1,150 | samf/senior |
| SAMO junior rounds 1-2 | 8-9 | MC 20 | 1998-2026 | official | text | 800 | samf/junior |
| COMC (Canada) | 9-12 | mixed 12 | 1997-2025 | official | text | 350 | comc |
| PRMO / IOQM (India) | 8-12 | integer 30 | 2017-2024 | keys | text | 240 | ioqm |

URL patterns, verification details and per-file notes are in `high-school.json`.

## Licensing to respect

- **CEMC:** the materials are CC BY-NC 4.0, and CEMC states: "Under no circumstances shall anyone be permitted to charge fees for accessing past contests." A free app is fine; a paywalled app is not.
- **ARML:** "Commercial usage of ARML problems without permission and posting entire contests or contest books are prohibited." Get permission before showing whole ARML contests.
- **AMC/AIME:** the problems are MAA copyright. The AoPS wiki is the accepted public record.
- **Purple Comet:** the problems are copyright of the authors (Kane, Andreescu, Harris, Samaranayake).
- **SMT:** reuse is allowed with citation.

## Not publicly available

| Competition | What is free | How to get the rest |
|---|---|---|
| Australian Mathematics Competition (Intermediate/Senior) | 6-question practice sets only | [AMT shop, 2-year past-paper packs ($10 AUD)](https://shop.amt.edu.au/products/amc-past-papers-2-year-pack) |
| Singapore Mathematical Olympiad (Senior/Open) | nothing official (only pirate reposts, which are not allowed) | [SMS publications](https://sms.math.nus.edu.sg/) and World Scientific SMO books |
| Math League HS (mathleague.com) | 3 sample contests (2005-06 #1, 2012-13 #1, 2018-19 #5), downloaded to `mathleague/` | [Math League contest books](https://www.mathleague.com) |
| TMSCA / UIL (Texas) | nothing | TMSCA practice packs ($40-60, membership) via [tmsca.org](https://www.tmsca.org); [UIL academic store](https://www.uiltexas.org/academics/academic-store) |
| UKMT IMC/SMC 2004-2014 (except 2009/2012/2013) | none | [UKMT past-paper shop](https://ukmt.org.uk/product-category/past-paper) |
| ARML 1976-1994; 2021, 2022, 2024 contests | 1995-2020 books are free on arml3.com | 1983-88 and 1989-94 books via [arml.com books page](https://www.arml.com/ARML/arml_2019/page/index.php?page=books&page_type=public) (Amazon) |
| ARML Local 2020+ | 2022 problems linked on [armlcontest.com](https://armlcontest.com/?page_id=477) (links not machine-readable) | download by hand |
| Purple Comet worked solutions | answers only | AwesomeMath Purple Comet books |
| Kangaroo Canada 2024+ papers; 2004-06 and 2008-11 | answer keys only (API) | ask [Math Kangaroo Canada](https://mathkangaroo.ca) |
| Math Kangaroo USA (Levels 9-10, 11-12) | a few sample questions | members-only past papers, [mathkangaroo.org](https://mathkangaroo.org) (participants) |
| Duke Math Meet 2023+ | none posted | ask DUMU |
| JHMT 2018-2019 and 2021+ | AoPS threads; 2025 Drive link on the official site | [JHMT past papers](https://www.johnshopkinsmathtournament.com/past-papers) |
| SMT 2015-2017 | none (run with AlphaStar) | not available |
| CTMC 2009-2011 | none | ask CEMC |
