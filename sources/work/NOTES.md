# Orchestrator notes for later phases
- kangaroo/austria/2020_* and 2021_* are Brazilian English editions (Canguru Brasil); already extracted as at-2020-*/at-2021-*. Phase-2 Brazil unit must skip/duplicate them.
- Kangaroo cross-level duplicates (Kadett/Junior/Student same year) are only partly marked; dedupe-review-1 handles the rest.
- CEMC blank-answer rule (2 pts per blank up to 10) not modelled.
- at-20xx-student vs at-20xx-junior (same year) overlaps are NOT marked for 2015-2025 Student papers except 2017 Q19; dedupe-review-1 should compare them.
- cemc-cayley-2010-10 is the same problem as cemc-pascal-2010-13 (only the school name differs); mark duplicateOf.
- AMC 10/12 blank scoring: 2.5 points per blank in early years (agent says before 2006; verify whether 2006 itself was 2.5 or 1.5). After amc1012-2002..2006 finish, ensure all those files have blankPoints 2.5 per question (2004/2005 agents were not told).
