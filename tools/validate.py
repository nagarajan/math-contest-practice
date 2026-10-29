#!/usr/bin/env python3
"""Validate extracted question files against data/SCHEMA.md.

Usage: validate.py <file.json> [<file.json> ...]
Exit code is non-zero if any errors are found. Warnings do not fail.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ROOT, "app", "public")
BANKS = {"kangaroo", "noetic", "moems"}
TYPES = {"mc", "numeric", "text"}
TOPICS = {
    "arithmetic", "number-theory", "fractions-decimals", "algebra", "patterns", "geometry",
    "measurement", "counting", "probability", "logic", "spatial", "time-calendar", "money", "rates",
}
NUMERIC_RE = re.compile(r"^-?(\d+(\.\d+)?|\d+/\d+|\d+ \d+/\d+|\.\d+)$")


def check(path):
    errors, warnings = [], []
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        return [f"cannot parse JSON: {e}"], []
    if not isinstance(data, list):
        return ["top level must be an array"], []
    ids = set()
    for i, q in enumerate(data):
        tag = f"[{i}] {q.get('id', '?')}"
        e = lambda m: errors.append(f"{tag}: {m}")
        w = lambda m: warnings.append(f"{tag}: {m}")
        for k in ("id", "bank", "source", "grade", "type", "prompt", "answer", "solutions", "topics", "difficulty"):
            if k not in q:
                e(f"missing field {k}")
        if q.get("id") in ids:
            e("duplicate id in file")
        ids.add(q.get("id"))
        if q.get("bank") not in BANKS:
            e(f"bad bank {q.get('bank')}")
        if q.get("type") not in TYPES:
            e(f"bad type {q.get('type')}")
        src = q.get("source") or {}
        for k in ("contest", "paper", "year", "url"):
            if k not in src:
                e(f"source missing {k}")
        if not str(q.get("prompt", "")).strip():
            e("empty prompt")
        t = q.get("type")
        ans = q.get("answer")
        if t == "mc":
            ch = q.get("choices")
            if not isinstance(ch, list) or len(ch) < 2:
                e("mc needs choices")
            else:
                keys = [c.get("key") for c in ch]
                if ans not in keys:
                    e(f"answer {ans} not among choice keys {keys}")
                if all(not c.get("text") for c in ch) and not q.get("image"):
                    e("picture choices but no image")
        else:
            if q.get("choices"):
                e("non-mc question has choices")
            if t == "numeric" and not NUMERIC_RE.match(str(ans).strip()):
                e(f"numeric answer not a plain number: {ans!r}")
        if q.get("bank") == "kangaroo" and q.get("points") not in (3, 4, 5):
            e("kangaroo question needs points 3/4/5")
        img = q.get("image")
        if img:
            if not img.startswith("qimages/"):
                e("image path must start with qimages/")
            elif not os.path.exists(os.path.join(PUBLIC, img)):
                e(f"image file missing: {img}")
        for c in q.get("choices") or []:
            ci = c.get("image")
            if ci and not os.path.exists(os.path.join(PUBLIC, ci)):
                e(f"choice image missing: {ci}")
        sols = q.get("solutions")
        if not isinstance(sols, list):
            e("solutions must be a list")
        elif not sols and not q.get("duplicateOf"):
            e("no solutions")
        else:
            for s in sols:
                if not s.get("title") or not s.get("body"):
                    e("solution needs title and body")
            if len(sols) == 1 and not q.get("duplicateOf"):
                w("only one solution approach")
        tp = q.get("topics") or []
        bad = [x for x in tp if x not in TOPICS]
        if bad or not tp:
            e(f"bad/missing topics {bad}")
        if q.get("difficulty") not in (1, 2, 3):
            e("difficulty must be 1/2/3")
        if q.get("reviewNote"):
            w(f"reviewNote: {q['reviewNote']}")
    return errors, warnings


def main():
    bad = 0
    for p in sys.argv[1:]:
        errs, warns = check(p)
        n = len(json.load(open(p))) if not errs or "parse" not in errs[0] else 0
        print(f"{p}: {n} questions, {len(errs)} errors, {len(warns)} warnings")
        for m in errs:
            print("  ERROR", m)
        for m in warns:
            print("  warn ", m)
        bad += bool(errs)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
