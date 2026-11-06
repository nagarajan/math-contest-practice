#!/usr/bin/env python3
"""Merge data/raw/<bank>/*.json into the app's question files.

Writes app/public/banks/grade-<g>.json (every question for that grade, all banks; g = 1-12,
13 = undergraduate, 14 = graduate) and index.json (bank list from data/banks.json with counts
per grade and the source papers).

- Drops questions marked `duplicateOf` (the original is kept, and gains the duplicate's grades,
  e.g. a problem shared by AMC 10 and AMC 12 shows up for grades 9-12).
- Drops repeated ids (first occurrence wins; MOEMS ids are derived from the book reference so the
  same problem appearing in two Problem-of-the-Week documents collapses to one).
- Reports likely duplicates that were not marked (near-identical prompt text across papers).

Usage: build_banks.py [--strict]   (--strict: exit non-zero on validation errors)
"""
import difflib
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate import check, parse_grades  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "app", "public", "banks")
GRADES = range(1, 15)
KEEP = [
    "id", "bank", "source", "grade", "grades", "points", "blankPoints", "wrongPoints", "timeMinutes", "type", "prompt", "image", "choices",
    "answer", "answerDisplay", "acceptedAnswers", "answerUnit", "solutions", "topics", "difficulty", "reviewNote",
]


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def main():
    strict = "--strict" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    metas = json.load(open(os.path.join(ROOT, "data", "banks.json"), encoding="utf-8"))
    had_errors = False
    seen = {}
    dup_targets = {}
    stats = defaultdict(Counter)
    files_per_bank = Counter()

    for meta in metas:
        bank = meta["id"]
        for f in sorted(glob.glob(os.path.join(RAW, bank, "*.json"))):
            files_per_bank[bank] += 1
            errs, _ = check(f)
            if errs:
                had_errors = True
                print(f"!! {os.path.relpath(f, ROOT)}: {len(errs)} validation errors (first: {errs[0]})")
            try:
                qs = json.load(open(f, encoding="utf-8"))
            except Exception:
                continue
            bad_ids = {e.split(":")[0].split("] ", 1)[-1] for e in errs}
            for q in qs:
                if q.get("id") in bad_ids:
                    stats[bank]["invalid"] += 1
                    continue
                q["grades"] = parse_grades(q)
                if q.get("duplicateOf"):
                    stats[bank]["dup_marked"] += 1
                    dup_targets[q["id"]] = (q["duplicateOf"], q["grades"])
                    continue
                if q["id"] in seen:
                    stats[bank]["dup_id"] += 1
                    continue
                seen[q["id"]] = {k: q.get(k) for k in KEEP}
    for d in sorted({os.path.basename(p) for p in glob.glob(os.path.join(RAW, "*"))} - {m["id"] for m in metas}):
        had_errors = True
        print(f"!! data/raw/{d}/ is not a bank in data/banks.json (skipped)")

    for qid, (target, grades) in sorted(dup_targets.items()):
        # Follow chains (a duplicate of a duplicate).
        hops = 0
        while target in dup_targets and hops < 10:
            target = dup_targets[target][0]
            hops += 1
        if target not in seen:
            had_errors = True
            print(f"!! {qid} is marked duplicateOf {target}, which is not in the banks (question lost)")
            continue
        seen[target]["grades"] = sorted(set(seen[target]["grades"]) | set(grades or []))

    questions = list(seen.values())
    by_bank = defaultdict(list)
    for q in questions:
        by_bank[q["bank"]].append(q)

    index_banks = []
    for meta in metas:
        bank = meta["id"]
        qs = by_bank.get(bank, [])
        by_len = sorted(qs, key=lambda q: len(q["prompt"]))
        normed = [(q["id"], norm(q["prompt"])) for q in by_len]
        suspects = []
        for i, (ida, a) in enumerate(normed):
            for idb, b in normed[i + 1:i + 40]:
                if ida.rsplit("-", 1)[0] == idb.rsplit("-", 1)[0]:
                    continue
                if len(a) > 40 and difflib.SequenceMatcher(None, a, b).ratio() > 0.9:
                    suspects.append((ida, idb))

        src = {}
        for q in qs:
            s = q["source"]
            key = (s["contest"], re.sub(r" \(from .*\)$", "", s["paper"]), s["year"])
            e = src.setdefault(key, {"contest": key[0], "paper": key[1], "year": key[2], "url": s["url"], "count": 0, "grades": set()})
            e["count"] += 1
            e["grades"] |= set(q["grades"])
        sources = sorted(src.values(), key=lambda e: (e["contest"], e["year"] or 0, e["paper"]))
        for e in sources:
            e["grades"] = sorted(e["grades"])
        counts = Counter(g for q in qs for g in q["grades"])
        exam_counts = Counter(g for q in qs if q["type"] != "self" for g in q["grades"])
        index_banks.append({
            **meta,
            "count": len(qs),
            "countsByGrade": {str(g): counts[g] for g in sorted(counts)},
            "examCountsByGrade": {str(g): exam_counts[g] for g in sorted(exam_counts)},
            "sources": sources,
        })
        st = stats[bank]
        types = Counter(q["type"] for q in qs)
        flagged = sum(1 for q in qs if q.get("reviewNote"))
        grade_str = ", ".join(f"{g}:{counts[g]}" for g in sorted(counts))
        print(
            f"{bank}: {len(qs)} questions from {files_per_bank[bank]} files "
            f"(dropped: {st['dup_marked']} marked duplicates, {st['dup_id']} repeated ids, {st['invalid']} invalid) "
            f"types={dict(types)} reviewNotes={flagged} grades={{{grade_str}}}"
        )
        for a, b in suspects:
            print(f"   possible duplicate: {a} ~ {b}")

    grade_counts = {}
    for g in GRADES:
        gq = [q for q in questions if g in q["grades"]]
        grade_counts[str(g)] = len(gq)
        json.dump(gq, open(os.path.join(OUT, f"grade-{g}.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    for old in glob.glob(os.path.join(OUT, "*.json")):
        if not re.search(r"(grade-\d+|index)\.json$", old):
            os.remove(old)
    json.dump(
        {"banks": index_banks, "gradeCounts": grade_counts},
        open(os.path.join(OUT, "index.json"), "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=1,
    )
    print("per grade: " + ", ".join(f"{g}:{n}" for g, n in grade_counts.items()))
    if strict and had_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
