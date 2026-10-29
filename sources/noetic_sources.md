# Noetic Learning Math Contest (NLMC) — sources

Grades 5 and 6 only. Local copies are in `sources/pdfs/noetic/`.

## Used

| Output file | Questions | Source | What it is |
|---|---|---|---|
| `data/raw/noetic/sample-g5.json` | 5 | https://schola.us/wp-content/uploads/2025/03/Noetic-Samples-G5.pdf (`noetic-samples-g5.pdf`) | Official Noetic "Sample Problems Grade 5" (© 2009-2016 Noetic Learning LLC), 5 problems + official answer key. Hosted by Schola (a school). |
| `data/raw/noetic/sample-g6.json` | 5 | https://schola.us/wp-content/uploads/2025/03/Noetic-Samples-G6.pdf (`noetic-samples-g6.pdf`) | Official Noetic "Sample Problems Grade 6", 5 problems + official answer key. |
| `data/raw/noetic/website-g5.json` | 2 | https://www.noetic-learning.com/mathcontest/sample.jsp (`noetic-site-sample.html`, figure `noetic-site-sample.jpg` = `/mathcontest/images/sample.JPG`) | Official website sample questions. The page only has grades 2–5 (no grade 6) and **no answers**, so both answers come from my own solutions (reviewNote set). |
| `data/raw/noetic/fall2016-g5.json` | 20 | https://faculty.sites.uci.edu/asaff/files/2024/09/2016f_grade5_all.pdf (`uci-2016f_grade5_all.pdf`; decrypted copy `uci-2016f_grade5_all_unlocked.pdf`) | Full Fall 2016 Grade 5 test **with the official Noetic answers & solutions**. Posted by a UCI faculty member for their 5th-grade math club (https://faculty.sites.uci.edu/asaff/math-club-24-25/, Meeting 1). The PDF has a password, and the club page prints it right next to the link ("password: noetic"). |
| `data/raw/noetic/fall2023-g5.json` | 20 | https://faculty.sites.uci.edu/asaff/files/2024/10/Grade5_problems.pdf (`uci-fall2023_grade5_problems.pdf`; decrypted copy `uci-fall2023_grade5_problems_unlocked.pdf`) | Full Fall 2023 Grade 5 test (problems only, **no key**). Same UCI math-club page (Meeting 7, "noetic fall 23", password given on the page). Every problem solved independently; each has reviewNote "no official key; answer from own solution". |

Total: 52 questions (47 grade 5, 5 grade 6).

## Found but not usable

- **Spring 2016 Grade 5 answer key**: https://www.ellipsisacademy.com/uploads/1/9/5/3/19539617/grade5_key.pdf (`ellipsis-grade5-key.pdf`, kept for reference). This is an official key, but I couldn't find the matching test anywhere I'm allowed to use (tried grade5.pdf, grade5_test.pdf, grade5_problems.pdf and similar names on Ellipsis, plus web searches). A key with no problems can't be used.
- **Ellipsis Academy Fall 2015 Grade 5 / Grade 6 tests and keys** (`fall2015grade5_noetic.pdf`, `fall2015grade6_noetic.pdf` and `..._key.pdf` under the same uploads folder): I only found these by guessing URLs from the name of a Grade 3 key that turned up in search. Nothing on the Ellipsis site links to them, and the tests are password-protected with no password published anywhere. Opening them would mean bypassing that protection, so they were **not used** and the downloads were deleted. If Ellipsis Academy gives permission (or publishes them), these would add 40 more problems.
- **ellipsisacademy.com `mct-practices-pdf-format.html`**: these files are for Ellipsis's own "Math Challenge Tournament", not NLMC.
- **UCI club page, Meeting 8**: mentions another Noetic exam, but there is no link.

## Rejected

- **pdfcoffee.com** (Spring 2012 Grade 5, Fall 2012 Grade 6), **studocu.com** (Spring 2022 Grade 5 solutions, Fall 2021 Grade 6), **scribd**, **wepdf.com**, **studylib.net** (an NLMC "problem of the week"): document-sharing or piracy sites, so excluded by policy.
- Pages like `*.connect.sangoma.com`, `jupyter.cs.sierracollege.edu/fetch.php/...`, `flexlm.seti.org/fetch.php/...`, `oem.nada.org/...`: SEO spam or redirects to atozpdfbooks.com, not real hosts.
- **mathexplorersclub.com** "Noetic practice problems" for grades 5 and 6: written by a third party in the Noetic style, not real NLMC problems.
- **noetic-learning.com/mathcontest/pasttests.jsp** and `pasttests_s.jsp`: official past tests, but sold ($9 each) or only open to registered team leaders. Not freely available.
- **OSSM (ossm.edu) practice tests**: a different contest.

## Note on copyright

The UCI tests carry "© Noetic Learning LLC". Noetic says its past papers are only for registered team leaders and may not be posted online. The UCI faculty member posted them publicly anyway, password included. They meet this project's policy (a copy posted on a teacher or math-club site), but a human should decide whether that is acceptable before publishing the app.
