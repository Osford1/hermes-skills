"""Inject tone-marked pinyin into a bilingual template.

Authoring convention: prefix every Chinese segment with `ZH|`; this script replaces
that marker by appending ` (pīnyīn)`. Pinyin always comes from pypinyin — never
hand-written (hand-written pinyin has tone errors).

Usage: python inject_pinyin.py <template> <output>

Placement rule: the pinyin goes after the last Chinese character of the segment —
unless figures still follow (e.g. 书面作业（20%）), in which case it goes at the end of
the segment so it never lands inside a parenthetical.
"""
import re
import sys
from pypinyin import lazy_pinyin, Style

CJK = re.compile(r"[\u4e00-\u9fff]")
CJK_LO, CJK_HI = chr(0x4E00), chr(0x9FFF)
TONE = "āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü"
# CJK punctuation kept in the "pre" part (never inside the pinyin run)
CJK_PUNCT = set("\u3000\u3001\u3002\u3008\u3009\u300a\u300b\u300c\u300d\u3010\u3011\u3014\u3015\u30fb\u30fc\u2014\u2026"
                 "\u2018\u2019\u201c\u201d\uff01\uff1f\uff1b\uff1a\uff0c\uff08\uff09\uff05\uff03\uff20\uff06\uff0a\uff0b\uff0d\uff0f\uff1d\uff5e")
# segment terminators: em-dash separator, table pipe, arrow, run of spaces, math, bold,
# the next marker, end of line
TERM = re.compile(r"(\s—\s|\s\|\s?|\s*→\s*|\s{2,}|\$|\*\*|ZH\||\n)")


def is_cjk(c):
    return bool(CJK.match(c))


def pinyin_of(s):
    """Tone-marked pinyin of the Chinese content of s, punctuation dropped."""
    return " ".join(x for x in lazy_pinyin(s, style=Style.TONE) if any(ch.isalpha() for ch in x))


def annotate(run):
    idx = [k for k, c in enumerate(run) if is_cjk(c)]
    if not idx:
        return run
    py = pinyin_of("".join(run[k] for k in idx))
    if not py:
        return run
    k = idx[-1] + 1
    while k < len(run) and (run[k] in CJK_PUNCT or run[k].isspace()):
        k += 1                                        # step over trailing punctuation/spaces
    if re.search(r"[0-9%]", run[k:]):                # trailing figures -> append at end
        body = run.rstrip()
        return body + f" ({py})" + run[len(body):]
    pre, post = run[:k].rstrip(), run[k:]
    join = " " if post and not post[0].isspace() else ""
    return pre + f" ({py})" + join + post


def tidy_math_gap(line):
    r"""Put a space between an injected pinyin run and a following math span.

    The pinyin is appended to the end of a run, and `$` terminates a run, so the
    caller then appends the maths verbatim: `...扰动 (rao3 dong4)$\\delta b$`.
    Insert the space only when the paren holds real pinyin (it carries a tone
    mark) and sits after "Chinese char + space", so a math paren such as
    `\\operatorname{Cond}(A)$` is never touched.
    """
    body = r"[A-Za-z" + TONE + r" ]"
    pat = re.compile(r"\(" + body + r"*[" + TONE + r"]" + body + r"*\)\$")

    def repl(m):
        j = m.start()
        if j < 2 or line[j - 1] != " ":
            return m.group(0)
        prev = line[j - 2]
        is_zh = (CJK_LO <= prev <= CJK_HI) or ("\u3000" <= prev <= "\u303f")
        is_zh = is_zh or ("\uff00" <= prev <= "\uffef")
        return m.group(0)[:-1] + " $" if is_zh else m.group(0)

    return pat.sub(repl, line)


def main(tpl_path, out_path):
    out, misses = [], []
    for lineno, line in enumerate(open(tpl_path, encoding="utf-8"), 1):
        if "ZH|" not in line:
            out.append(line)
            continue
        res, rest = "", line
        while "ZH|" in rest:
            pre, _, rest = rest.partition("ZH|")
            res += pre
            m = TERM.search(rest)
            run, rest = (rest[: m.start()], rest[m.start():]) if m else (rest, "")
            if not any(is_cjk(c) for c in run):
                misses.append((lineno, run.strip()[:60]))
            res += annotate(run)
        res += rest
        res = tidy_math_gap(res)
        out.append(res)
    text = "".join(out)
    open(out_path, "w", encoding="utf-8").write(text)
    print(f"wrote {out_path} ({len(text)} chars)")
    print(f"ZH| markers remaining: {text.count('ZH|')}")
    print(f"segments with no Chinese (expected: maths/email only): {len(misses)}")
    for ln, r in misses:
        print(f"    line {ln}: {r!r}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
