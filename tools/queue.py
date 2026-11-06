#!/usr/bin/env python3
"""Work queue for extraction agents (sources/work/queue.json).

  queue.py status                       # counts by status, running units
  queue.py next [N]                     # first N pending unit ids
  queue.py prompt <id>                  # the full agent prompt for a unit
  queue.py set <id> <status> [note]     # pending | running | done | failed
"""
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(ROOT, "sources", "work", "queue.json")

PROMPT = """You are an extraction agent for the math-contest-practice app at {root}.
First read {root}/sources/EXTRACT.md (workflow and rules) and {root}/data/SCHEMA.md (format and quality bar). Then do this work unit completely.

Work unit `{id}` — bank `{bank}` (about {est} questions):
{task}

When finished, reply with the short final report described in EXTRACT.md."""


def load():
    return json.load(open(QUEUE))


def save(q):
    json.dump(q, open(QUEUE, "w"), indent=1, ensure_ascii=False)


def main():
    a = sys.argv[1:]
    q = load()
    by = {u["id"]: u for u in q}
    if not a or a[0] == "status":
        c = Counter(u["status"] for u in q)
        print(dict(c), "| est done:", sum(u["est"] for u in q if u["status"] == "done"), "/", sum(u["est"] for u in q))
        for u in q:
            if u["status"] in ("running", "failed"):
                print(f"  {u['status']:8} {u['id']}  {u.get('note', '')}")
    elif a[0] == "next":
        n = int(a[1]) if len(a) > 1 else 1
        print("\n".join([u["id"] for u in q if u["status"] == "pending"][:n]))
    elif a[0] == "prompt":
        u = by[a[1]]
        print(PROMPT.format(root=ROOT, **u))
    elif a[0] == "set":
        for uid in a[1].split(","):
            by[uid]["status"] = a[2]
            if len(a) > 3:
                by[uid]["note"] = " ".join(a[3:])
        save(q)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
