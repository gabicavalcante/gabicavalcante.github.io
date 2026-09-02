#!/usr/bin/env python3
"""Sentence-shape metrics for every post in the blog, for voice calibration.

Read a draft's row against the rows for the posts already published. What matters
is which way the numbers moved, not whether they clear a threshold. A fixed
target here would go stale the way a written-down draft count does.

    python3 .claude/skills/review-post/references/voice-metrics.py [path ...]

Columns:
    sent    sentences counted (prose only)
    med     median sentence length in words
    p90     90th percentile length; a jump here means long sentences are piling up
    <=9w    share of short sentences; her recent posts run high
    >=35w   share of very long ones; her recent posts run near zero
    para    prose paragraphs
    I/my    first person mentions
    cntr    contractions
    em      em dashes, which the published posts use almost never
"""
import glob
import re
import statistics as st
import sys

HDR = f"{'post':<40}{'sent':>5}{'med':>5}{'p90':>5}{'<=9w':>6}{'>=35w':>7}{'para':>6}{'I/my':>6}{'cntr':>6}{'em':>4}"


def prose(markdown: str) -> str:
    """Strip everything that is not the author writing sentences."""
    body = markdown.split("+++", 2)[-1]
    body = re.sub(r"```.*?```", "", body, flags=re.S)        # code blocks
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)       # comments, incl. TODO notes
    body = re.sub(r"^\s*[-|>#0-9].*$", "", body, flags=re.M)  # lists, tables, headings
    body = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", body)     # keep link text, drop URLs
    body = re.sub(r"\{\{<.*?>\}\}", "", body)                # shortcodes
    return body


def row(path: str) -> str | None:
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    body = prose(raw)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if len(s.strip()) > 1]
    lengths = [len(s.split()) for s in sents]
    if not lengths:
        return None
    paras = [p for p in body.split("\n\n") if len(p.strip()) > 40]
    short = sum(1 for w in lengths if w <= 9) / len(lengths) * 100
    long_ = sum(1 for w in lengths if w >= 35) / len(lengths) * 100
    p90 = sorted(lengths)[max(int(len(lengths) * 0.9) - 1, 0)]
    name = path.split("/")[2][:38] if "/" in path else path[:38]
    first = len(re.findall(r"\b(I|my|me)\b", body))
    contractions = len(re.findall(r"[a-z]'(s|t|re|ve|ll|m)\b", body))
    em_dashes = raw.count("\u2014")
    return (
        f"{name:<40}{len(lengths):>5}{st.median(lengths):>5.0f}{p90:>5}"
        f"{short:>5.0f}%{long_:>6.0f}%{len(paras):>6}"
        f"{first:>6}{contractions:>6}{em_dashes:>4}"
    )


def main() -> None:
    paths = sys.argv[1:] or sorted(glob.glob("content/posts/*/index.md"))
    print(HDR)
    for path in paths:
        line = row(path)
        if line:
            print(line)


if __name__ == "__main__":
    main()
