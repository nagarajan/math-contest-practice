#!/usr/bin/env python3
"""Merge data/raw/<bank>/*.json into the app's question files.

Writes app/public/banks/q/<bank>-<hash>.json, one file per bank and set of grades (g = 1-12,
13 = undergraduate, 14 = graduate; a grade loads every file that lists it) with what is needed to
pick questions (id, type, topics, difficulty, points; null fields and per-paper source details
factored out), c/<bank>/<paper>-<hash>.json (prompt, choices, answers and review notes by question
id, loaded when a question is shown), sol/<bank>/<paper>.json (solutions by question id, loaded
when a solution is opened) and
index.json (bank list from data/banks.json with counts
per grade and the source papers, and the question files).

- Drops questions marked `duplicateOf` (the original is kept, and gains the duplicate's grades,
  e.g. a problem shared by AMC 10 and AMC 12 shows up for grades 9-12).
- Drops repeated ids (first occurrence wins; MOEMS ids are derived from the book reference so the
  same problem appearing in two Problem-of-the-Week documents collapses to one).
- Reports likely duplicates that were not marked (near-identical prompt text across papers),
  except pairs already checked in data/review/not_duplicates.json.

Usage: build_banks.py [--strict]   (--strict: exit non-zero on validation errors)
"""
import difflib
import glob
import hashlib
import json
import os
import re
import shutil
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
CONTENT = ["prompt", "image", "choices", "answer", "answerDisplay", "acceptedAnswers", "answerUnit", "reviewNote"]
CHUNK_DROP = {"bank", "source", "sol", "file", "grade", "grades", "solutions", *CONTENT}


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def same_problem(a, b):
    """Unmarked duplicates that are safe to merge: same text, answer and choices, no picture."""
    if a["type"] != b["type"] or str(a["answer"]).strip() != str(b["answer"]).strip():
        return False
    if a.get("image") or b.get("image"):
        return False
    if difflib.SequenceMatcher(None, norm(a["prompt"]), norm(b["prompt"])).ratio() < 0.97:
        return False
    if a["type"] == "mc":
        ca = [norm(c.get("text") or "") for c in a["choices"] or []]
        cb = [norm(c.get("text") or "") for c in b["choices"] or []]
        return ca == cb and all(ca)
    return True


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
                seen[q["id"]]["sol"] = seen[q["id"]]["file"] = f"{bank}/{os.path.splitext(os.path.basename(f))[0]}"
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

    checked_file = os.path.join(ROOT, "data", "review", "not_duplicates.json")
    checked_pairs = {tuple(sorted(p)) for p in json.load(open(checked_file))["pairs"]} if os.path.exists(checked_file) else set()

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
                if len(a) <= 40 or len(b) > len(a) * 1.25:
                    continue
                sm = difflib.SequenceMatcher(None, a, b)
                if sm.real_quick_ratio() > 0.9 and sm.quick_ratio() > 0.9 and sm.ratio() > 0.9:
                    suspects.append((ida, idb))
        merged = set()
        for ida, idb in list(suspects):
            qa, qb = seen.get(ida), seen.get(idb)
            if not qa or not qb or ida in merged or idb in merged or not same_problem(qa, qb):
                continue
            keep, drop = sorted((qa, qb), key=lambda q: (min(q["grades"] or [99]), q["id"]))
            keep["grades"] = sorted(set(keep["grades"]) | set(drop["grades"]))
            merged.add(drop["id"])
            suspects.remove((ida, idb))
        if merged:
            for qid in merged:
                del seen[qid]
            qs = [q for q in qs if q["id"] not in merged]
            stats[bank]["auto_merged"] = len(merged)

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
            f"(dropped: {st['dup_marked']} marked duplicates, {st['dup_id']} repeated ids, {st['invalid']} invalid, {st['auto_merged']} auto-merged) "
            f"types={dict(types)} reviewNotes={flagged} grades={{{grade_str}}}"
        )
        for a, b in suspects:
            if tuple(sorted((a, b))) not in checked_pairs:
                print(f"   possible duplicate: {a} ~ {b}")

    questions = list(seen.values())
    sol_dir = os.path.join(OUT, "sol")
    shutil.rmtree(sol_dir, ignore_errors=True)
    by_sol = defaultdict(dict)
    for q in questions:
        if q["solutions"]:
            by_sol[q["sol"]][q["id"]] = q["solutions"]
        else:
            q["sol"] = None
    for key, sols in by_sol.items():
        path = os.path.join(sol_dir, key + ".json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump(sols, open(path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    c_dir = os.path.join(OUT, "c")
    shutil.rmtree(c_dir, ignore_errors=True)
    by_file = defaultdict(dict)
    for q in questions:
        by_file[q["file"]][q["id"]] = {k: q[k] for k in CONTENT if q.get(k) not in (None, [], "")}
    cfile = {}
    for key, content in by_file.items():
        body = json.dumps(content, ensure_ascii=False, separators=(",", ":"))
        cfile[key] = f"{key}-{hashlib.sha1(body.encode()).hexdigest()[:8]}"
        path = os.path.join(c_dir, cfile[key] + ".json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(body)
    chunks = defaultdict(list)
    for q in questions:
        chunks[(q["bank"], tuple(q["grades"]))].append(q)
    q_dir = os.path.join(OUT, "q")
    shutil.rmtree(q_dir, ignore_errors=True)
    os.makedirs(q_dir)
    chunk_index = []
    for (bank, grades), qs in sorted(chunks.items()):
        papers, out = {}, []
        for q in qs:
            src = {k: v for k, v in q["source"].items() if k != "number"}
            p = papers.setdefault(json.dumps([q["sol"], src, cfile[q["file"]]], ensure_ascii=False), len(papers))
            c = {k: v for k, v in q.items() if k not in CHUNK_DROP and v not in (None, [], "")}
            c["p"] = p
            if q["source"].get("number") is not None:
                c["n"] = q["source"]["number"]
            out.append(c)
        body = json.dumps(
            {"bank": bank, "grades": list(grades), "papers": [json.loads(k) for k in papers], "questions": out},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        name = f"{bank}-{hashlib.sha1(body.encode()).hexdigest()[:10]}.json"
        open(os.path.join(q_dir, name), "w", encoding="utf-8").write(body)
        chunk_index.append({"file": f"q/{name}", "bank": bank, "grades": list(grades), "count": len(qs)})
    grade_counts = {str(g): sum(1 for q in questions if g in q["grades"]) for g in GRADES}
    for old in glob.glob(os.path.join(OUT, "*.json")):
        if not old.endswith("index.json"):
            os.remove(old)
    json.dump(
        {"banks": index_banks, "gradeCounts": grade_counts, "chunks": chunk_index},
        open(os.path.join(OUT, "index.json"), "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=1,
    )
    print("per grade: " + ", ".join(f"{g}:{n}" for g, n in grade_counts.items()))
    if strict and had_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
