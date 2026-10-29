#!/usr/bin/env python3
"""Merge data/raw/<bank>/*.json into app/public/banks/<bank>.json + index.json.

- Drops questions marked `duplicateOf` (the original is kept).
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
from validate import check  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "app", "public", "banks")
BANKS = ["kangaroo", "noetic", "moems"]
KEEP = [
    "id", "bank", "source", "grade", "points", "timeMinutes", "type", "prompt", "image", "choices",
    "answer", "acceptedAnswers", "answerUnit", "solutions", "topics", "difficulty", "reviewNote",
]


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def main():
    strict = "--strict" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    index = []
    had_errors = False
    for bank in BANKS:
        files = sorted(glob.glob(os.path.join(RAW, bank, "*.json")))
        seen = {}
        dup_targets = {}
        dup_marked = dup_id = invalid = 0
        for f in files:
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
                    invalid += 1
                    continue
                if q.get("duplicateOf"):
                    dup_marked += 1
                    dup_targets[q["id"]] = q["duplicateOf"]
                    continue
                if q["id"] in seen:
                    dup_id += 1
                    continue
                seen[q["id"]] = {k: q.get(k) for k in KEEP}
        questions = list(seen.values())
        for qid, target in sorted(dup_targets.items()):
            if target not in seen:
                had_errors = True
                print(f"!! {qid} is marked duplicateOf {target}, which is not in the bank (question lost)")

        # Flag likely unmarked duplicates (same problem in two papers).
        by_len = sorted(questions, key=lambda q: len(q["prompt"]))
        normed = [(q["id"], norm(q["prompt"])) for q in by_len]
        suspects = []
        for i, (ida, a) in enumerate(normed):
            for idb, b in normed[i + 1:i + 40]:
                if ida.rsplit("-", 1)[0] == idb.rsplit("-", 1)[0]:
                    continue
                if len(a) > 40 and difflib.SequenceMatcher(None, a, b).ratio() > 0.9:
                    suspects.append((ida, idb))

        json.dump(questions, open(os.path.join(OUT, f"{bank}.json"), "w", encoding="utf-8"), ensure_ascii=False)
        src = defaultdict(lambda: {"count": 0})
        for q in questions:
            s = q["source"]
            key = (s["contest"], re.sub(r" \(from .*\)$", "", s["paper"]), s["year"])
            e = src[key]
            e.update(contest=key[0], paper=key[1], year=key[2], url=s["url"])
            e["count"] += 1
        index.append({
            "id": bank,
            "count": len(questions),
            "sources": sorted(src.values(), key=lambda e: (e["contest"], e["year"] or 0, e["paper"])),
        })
        types = Counter(q["type"] for q in questions)
        flagged = sum(1 for q in questions if q.get("reviewNote"))
        print(
            f"{bank}: {len(questions)} questions from {len(files)} files "
            f"(dropped: {dup_marked} marked duplicates, {dup_id} repeated ids, {invalid} invalid) "
            f"types={dict(types)} reviewNotes={flagged}"
        )
        for a, b in suspects:
            print(f"   possible duplicate: {a} ~ {b}")
    json.dump(index, open(os.path.join(OUT, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if strict and had_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
