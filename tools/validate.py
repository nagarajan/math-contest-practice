#!/usr/bin/env python3
"""Validate extracted question files against data/SCHEMA.md.

Usage: validate.py <file.json> [<file.json> ...]
Exit code is non-zero if any errors are found. Warnings do not fail.
"""
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ROOT, "app", "public")
BANKS = {b["id"] for b in json.load(open(os.path.join(ROOT, "data", "banks.json"), encoding="utf-8"))}
TYPES = {"mc", "numeric", "text", "self"}
TOPICS = {
    # elementary / middle school
    "arithmetic", "number-theory", "fractions-decimals", "algebra", "patterns", "geometry",
    "measurement", "counting", "probability", "logic", "spatial", "time-calendar", "money", "rates",
    # high school and beyond
    "polynomials", "inequalities", "functional-equations", "sequences-series", "trigonometry",
    "complex-numbers", "statistics", "graph-theory", "games", "calculus", "analysis",
    "linear-algebra", "abstract-algebra", "real-analysis", "complex-analysis", "topology",
    "differential-equations",
}
NUMERIC_RE = re.compile(r"^-?(\d+(\.\d+)?|\d+/\d+|\d+ \d+/\d+|\.\d+)$")
EXPR_NAMES = {"sqrt", "cbrt", "pi", "e", "abs", "ln", "log", "sin", "cos", "tan", "arcsin", "arccos", "arctan"}
EXPR_ENV = {
    "sqrt": math.sqrt, "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x), "pi": math.pi, "e": math.e,
    "abs": abs, "ln": math.log, "log": math.log10, "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "arcsin": math.asin, "arccos": math.acos, "arctan": math.atan,
    "factorial": math.factorial,
}


def expr_value(s):
    """Value of an explicit expression answer like '3*sqrt(2)/4', '2^10-1', '5!'. None if invalid."""
    s = s.strip()
    if not re.fullmatch(r"[0-9a-z+\-*/^().! ]+", s):
        return None
    if set(re.findall(r"[a-z]+", s)) - EXPR_NAMES:
        return None
    py = re.sub(r"(\d+|\))!", r"factorial(\1)", s).replace("^", "**")
    try:
        v = eval(py, {"__builtins__": {}}, EXPR_ENV)  # noqa: S307 - restricted names/chars above
        v = float(v)
    except Exception:
        return None
    return v if math.isfinite(v) else None


def parse_grades(q):
    """US grades a question is for: explicit `grades`, else derived from the `grade` label."""
    if isinstance(q.get("grades"), list) and q["grades"]:
        return q["grades"]
    g = str(q.get("grade", "")).strip().lower()
    if g in ("undergrad", "undergraduate", "13"):
        return [13]
    if g in ("grad", "graduate", "14"):
        return [14]
    m = re.fullmatch(r"(\d+)\s*[-–]\s*(\d+)", g)
    if m:
        return list(range(int(m.group(1)), int(m.group(2)) + 1))
    if g.isdigit():
        return [int(g)]
    return None


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
            e(f"bad bank {q.get('bank')} (add it to data/banks.json)")
        elif not str(q.get("id", "")).startswith(q["bank"] + "-"):
            e(f"id must start with '{q['bank']}-'")
        for k in ("blankPoints", "wrongPoints"):
            if q.get(k) is not None and not isinstance(q[k], (int, float)):
                e(f"{k} must be a number or null")
        if q.get("type") not in TYPES:
            e(f"bad type {q.get('type')}")
        grades = parse_grades(q)
        if not grades or any(not isinstance(g, int) or not 1 <= g <= 14 for g in grades):
            e(f"cannot work out grades from grade={q.get('grade')!r} grades={q.get('grades')!r}")
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
                if all(not c.get("text") for c in ch) and not q.get("image") and not q.get("duplicateOf"):
                    e("picture choices but no image")
        else:
            if q.get("choices"):
                e("non-mc question has choices")
            if t == "numeric" and not NUMERIC_RE.match(str(ans).strip()) and expr_value(str(ans)) is None:
                e(f"numeric answer is neither a plain number nor an explicit expression like 3*sqrt(2)/4: {ans!r}")
            if t == "self" and not str(ans or "").strip():
                e("self-graded question needs an answer summary (Markdown)")
        pts = q.get("points")
        if q.get("bank") == "kangaroo" and pts not in (3, 4, 5):
            e("kangaroo question needs points 3/4/5")
        elif pts is not None and (not isinstance(pts, (int, float)) or pts <= 0):
            e("points must be a positive number or null")
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
