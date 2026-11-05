---
name: chinese-pinyin-english-translation
description: "Use when translating Chinese docs to English with pinyin."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [translation, chinese, pinyin, bilingual, annotation]
    related_skills: [ocr-and-documents, docx, pdf]
---

# Chinese → English with Pinyin (Bilingual Annotation)

Translate a Chinese document into English while keeping the original Chinese
characters AND adding tone-marked pinyin. The result is a learn-to-read
annotation (中文 + pīnyīn + English), not a replacement translation.

## When to Use
- User asks to "translate the Chinese docs to English" and wants pinyin + the
  Chinese characters kept ("include the pinyin and the chinese characters, just
  add the english translation").
- Annotating study material, meeting minutes, proposals, lecture slides for
  language learning or to share with an English-speaking partner.

## Output format (default)
Keep the Chinese; add tone-marked pinyin in parentheses and an English gloss.

- **Headings:** `## 中文标题 (Pīnyīn) — English title`
- **Bullets / list items:** `- 中文项 (Pīnyīn) — English item`
- **Prose sentence (one per line):**
  ```
  中文句子 (Pīnyīn)
  English sentence.
  ```
- **Tables:** add a pinyin + English column, or render each cell as
  `中文 (pīnyīn) / English`.
- **Code blocks / identifiers:** leave unchanged. Translate *comments* (keep
  variable names intact).

Segment granularity: one sentence or one list item per block. Don't merge
multiple sentences into one block — matching the doc's natural line structure
keeps it readable.

## Pinyin (the automated part)
Use `pypinyin` with tone marks. It is pure-Python, install to the
ROBOT/study env or any python with network:

```bash
C:/Users/<you>/miniconda3/envs/lerobot/python.exe -m pip install pypinyin
```

Generate tone-marked pinyin for any Chinese string:

```python
from pypinyin import lazy_pinyin, Style
s = '具身智能与数据采集计划建议'
print(' '.join(lazy_pinyin(s, style=Style.TONE)))   # jù shēn zhì néng yǔ shù jù cǎi jí jì huà jiàn yì
```

`scripts/pinyin.py` in this skill does the same from a CLI arg, so it is
reproducible and free of manual romanization errors.

### Word-grouped pinyin (matches the vault's house style)
`pypinyin.contrib.mmseg.seg` **silently degrades to one syllable per character when jieba is not
importable** (`seg.dict is None`): 物流部 comes out `wù liú bù` instead of `wùliú bù`, the output is
still valid-looking and the grouped-vs-flat equality check still passes, so the degradation is
invisible. Verify at least one word spans two characters before trusting a build, or install it:
`python -m pip install jieba` into the *same* interpreter that runs the build. `jieba.lcut` +
`lazy_pinyin(style=TONE)` per word is the explicit fallback.

`lazy_pinyin` returns one syllable per character. For `Xiānjìn zhìzào jìshù`
style grouping, use pypinyin's own segmenter (no jieba needed):

```python
from pypinyin.contrib.mmseg import seg
" ".join("".join(lazy_pinyin(w, style=Style.TONE)) for w in seg.cut(clean_zh))
```

Guard it: compare the grouped string against the per-character output for every
segment (`grouped.replace(' ','') == ''.join(lazy_pinyin(clean, style=Style.TONE))`)
and print mismatches. Segmentation only re-spaces; if a mismatch appears, a
phrase was split and lost its polyphone resolution — fall back for that segment.

### pypinyin's wrong defaults (override with `load_phrases_dict`)
- `重用性` → `zhòng yòng` (wrong; reuse = **chóng**)
- `原子` → `yuán zi` (neutral; should be full 3rd tone **yuán zǐ**)
- `分子` → `fèn zǐ` (wrong; molecule = **fēn zǐ**, as opposed to 知识分子 fènzǐ)
Capture the default output *before* calling `load_phrases_dict`, so the document
can quote tool output as `default → corrected` instead of hand-written tones.

### Term-level overrides for architecture / art-history Chinese

`pypinyin` picks the everyday reading of a character; these terms (all met in a Tsinghua architecture-history syllabus)
need the reading that belongs to the *term*. Generate everything, then override by whole term and quote the tool's
default beside each correction:

| term | default | correct | why |
|---|---|---|---|
| 攒尖 | zǎn jiān | **cuán jiān** | the roof type: 攒 = *cuán* "gather", not *zǎn* "save" |
| 艮 | gěn | **gèn** | the trigram 艮 (of the 八卦) is *gèn* |
| 寺观 / 观 (Taoist temple) | guān | **guàn** | 观 = *guàn* in 道观/寺观庙宇; *guān* is the verb "to look" (phrase dict handles 寺观 but not a bare 观 in a list) |
| 斗栱 terms (栌斗, 交互斗, 齐心斗, 散斗, 造斗之制) | dòu | **dǒu** | 斗 in dougong terminology is the block; *dòu* is the dry measure |
| 诗书济世长 | …zhǎng | **…cháng** | 长 = *cháng* "long/enduring" in the couplet, not *zhǎng* "grow" |
| 金脊枋 | …jí fāng | **…jǐ fāng** | 脊 = *jǐ* (ridge); *jí* is a different character |

One case is genuinely undecided and should be left **flagged, not asserted**: **散斗** — *sàn dǒu* (generator default) or
*sǎn dǒu* ("scattered/loose", as some 营造法式 commentaries read it).

### Context overrides (per-character, for technical Chinese)
Phrase dictionaries miss single characters whose reading is set by the next/previous
char. Use `pinyin(s, style=Style.TONE)` (one entry per char, non-han returned as-is)
and override by context — these four recur in engineering text:

| char | pypinyin default | override when | why |
|---|---|---|---|
| 为 | wèi | `wéi` unless prev == 因 **or** (nxt == "" or nxt in 了/何/此/止) | copula 为零/称为/视为/分为/记为; only 因为/为了 are wèi |
| 地 | dì | `de` unless nxt == 方 | adverbial 特别地/及时地 vs 地方 |
| 量 | liàng | `liáng` if nxt == 测 or prev == 测 | 量测/测量 = to measure; 变量/向量/数量 keep liàng |
| 差 | chà | `chā` if nxt == 分 or prev == 之 | 差分/之差 vs 误差/方差 (chā) and 差的 (chà) |
| 解 | xiè | `jiě` unless prev/next form 押解/解送/解差/解元 | 解法/求解/解向量 — solvable only because a *long* token (线性方程组的直接解法) makes the tool pick 解 = 押解's *xiè*; per-character defaults on the same char are fine |
| 行 | xíng | `háng` when the token is exactly 行 | a matrix row (划去…第 $i$ 行) — the phrase dict already reads 行列式/一行 as háng, only the lone character is wrong |
| 子 | zi (neutral) | `zǐ` inside 子式 | 余子式/代数余子式 = *minor*, not the neutral-tone noun suffix (桌子) |

The `nxt == ""` guard is not optional: `"" not in "了何此止"` is `False` in Python
(the empty string is a substring of everything), so a 为 at the end of a run is
silently read wèi. For headings, join syllables (`zhāiyào`) by deleting the space
only between two pinyin-syllable characters, so `1 离散` does not become `1lí…`.

### Verify hand-written pinyin — but never auto-rewrite it
Table headers, term glosses and flag text often carry a pinyin parenthetical typed by
hand. Have the build script regenerate it and *report* mismatches; do not auto-replace.
A naive `CJK\s*\(latin\)` matcher also catches English glosses (`方差 (variance)`) and
truncates multi-word claims (`先验估计 / 先验 (xiān yàn gū jì)` → `先验 (xiān yàn)`), so
rewriting silently deletes content. Require a tone-marked char in the claim, and scan
backwards from `(` with a while-loop over CJK/delimiters — a `(?:CJK+…)+` regex
backtracks catastrophically on long prose and hangs the build (180 s timeout, no output).

### PDF line wraps fake typos
Extraction of a wrapped line reads `…信号灯具` + `有较小…`; read quickly it looks like the
typo 「具用」, and a flags section was about to enshrine that as a real defect. Before
flagging **any** character-level typo, print `repr()` of the raw context (not the
whitespace-collapsed line) and confirm the exact character sequence — then quote the
source position in the flag so the check is auditable.

### Template-authoring rules that the injector punishes
- **Never hand-type pinyin in the template.** Any `term (pīnyīn)` you type survives *and* the injector adds its own → the page prints the pinyin twice. Scanned for with a tone-mark regex before building; the only tone marks allowed in a template are in prose *about* pinyin.
- **Never let a `ZH|` run continue into an English sentence.** The pinyin is inserted after the last CJK of the run, so a term embedded in prose without a terminator gets its pinyin appended somewhere later in the sentence. Worse, if the run contains **any digit** the trailing-figures rule fires and the pinyin moves to the **end of the whole run** — a term's reading can land 40 words downstream (observed: `单位 (*unit*) … 1s on the diagonal` and `同解 argument as slide 14`). Fix: terminate every in-prose term with ` — ` (or `**`), and split any sentence whose Chinese is followed by `§0, §1, §2`-style digits.
- **Chinese inside halfwidth parens renders as `(term (pīnyīn) )`** — a doubled bracket and a space before the closing paren. Write the term bare before an em dash, or use fullwidth `（ZH|term）`, which the injector handles correctly.
- **Arabic numerals vanish from the pinyin.** `50 万、500 万` becomes `wàn wàn` (the digits are stripped with the Latin text). Write Chinese numerals — 五十万、五百万 — when the term is meant to be read aloud.
- **Tidy the punctuation as a post-pass:** the injector spaces its ` (pīnyīn)` from what follows, giving `(pīnyīn) .` / `(pīnyīn) ,`. Run `re.sub(r"\) ([.,;:])", r"\1", line)` over lines that are not display math, then re-scan for `\).*[\s][.,;:]` — 12 lines needed it in one 700-line deck.
- **`$` is a run terminator, so maths abuts the pīnyīn.** A run ends at `$` and the maths is then appended verbatim, giving `…扰动 (rǎo dòng)$\delta b$` with no gap (the same in the trailing-figures branch, `…（20%） (pīnyīn)$\alpha$`). `scripts/inject_pinyin.py` now carries `tidy_math_gap()`, applied to every injected line: it inserts the space only when the paren carries a tone mark (so it is pīnyīn, not `\operatorname{Cond}(A)$` in a formula) and follows a Han character **or CJK punctuation** — the latter is required because `）` precedes the space in the figures branch. Verified on the five shapes: pīnyīn+`$`, already-spaced, math paren, table pipe, figures branch.

- **A space-plus-pipe ends a `ZH|` run silently.** The terminator set includes `\s\|\s?`, so a maths-heavy line like `ZH|‖𝛼𝑥‖ = |𝛼|‖𝑥‖` (absolute-value bars) is cut at the first ` |`: the run has no CJK, it is reported as an innocent "no Chinese" miss, and every Chinese character after the pipe is emitted **without pīnyīn** with exit code 0. Fix by putting the Chinese before any pipe — `ZH|绝对齐次性 — ‖𝛼𝑥‖ = |𝛼|‖𝑥‖` — or by moving the formula into a code block. Check the miss report rather than assuming a miss is always maths.
- **A `PY|` marker is worth adding for pīnyīn-only cells.** For a `中文 | pīnyīn | English | where it bites` terminology table, `ZH|` would put the pīnyīn inside the 中文 cell. A 4-line extension of the injector — a second marker that emits *only* the pīnyīn — keeps the table's shape with the pīnyīn still machine-generated (author each row as `| ZH|范数 | PY|范数 | norm | … |`).
- **A heading or a table glued to the previous block gets swallowed.** When the page is assembled from part files (`<!--TERMINOLOGY-->`-style placeholders), a placeholder replaced by *stripped* content leaves the table's last row directly above `## …`, and Obsidian folds the heading into the table (the PDF still renders, so only the .md is affected). Normalise the assembled text before writing: `re.subn(r"(?m)([^\r\n])\r?\n(#{1,6} )", r"\1\n\n\2", txt)` for headings and `re.subn(r"(?m)^(\|[^\r\n]*)\r?\n(?!\|)([^\r\n])", r"\1\n\n\2", txt)` for table ends, and print the insertion counts (a non-zero count is the evidence the file needed it).
- **Per-character context overrides belong in the injector, not in flags.** `pypinyin` reads 为 as wèi even in 称为/为范数 position (20 wrong tones in one 32-slide deck) and 地 as dì in 特别地; `行` needs háng in 行范数. Generate with `pinyin(s, style=TONE)` (one token per character), rewrite by neighbouring character, and **print every override as `default → corrected` with a count** so the page can state what it changed instead of asserting tone accuracy.

### The template + injector pattern (use this for anything over ~10 segments)
Do **not** hand-write pinyin beside each segment — for a deck or a long doc that is
hundreds of manual tone decisions and it will contain errors. Instead:

1. Author the whole bilingual document as a **template** in which every Chinese
   segment is prefixed with a literal marker, e.g. `ZH|`:
   ```
   - ZH|教材：关治、陆金甫编著《数值方法》，清华大学出版社 — **Textbook:** Guan Zhi & Lu Jinfu…
   > ZH|数值稳定：一个算法，如果初始数据的微小变化带来最后结果的微小变化，那么称该算法是数值稳定的
   English gloss on the following line.
   ```
   Write the English freely; never type a tone mark.
2. Run an injector that replaces each `ZH|` marker with ` (pīnyīn)` derived from
   `pypinyin` — a working script ships with this skill:
   ```bash
   C:/Users/<you>/miniconda3/python scripts/inject_pinyin.py doc.tpl doc.md
   ```
3. **Strip hand-typed pīnyīn with a BRACKET-MATCHING pass, not a regex.** The cleanup rule ("never hand-type pīnyīn") needs an automated check, and `re.sub(r"\(([^()]*)\)", …)` is not it: a hand-typed parenthetical that itself contains brackets — `(qǔ  𝑥₀ = 𝑒𝑗₀ = (0, 0, …)ᵀ， jí …)` — cannot be matched, so 14 leftovers survived into a draft and the page printed the pīnyīn twice. Walk each marked line with a depth counter to find the span, delete it when it has tone marks and no CJK, and print what was removed. Then re-scan the output for lines carrying two tone-marked parentheticals.
4. **Verify the output, don't trust it.** Assert `'ZH|' not in output` (0 leftover markers)
   markers) and print the segments where no Chinese was found — those should only
   ever be maths/email/URL lines. Then read a sample of transformed lines.
5. Placement pitfalls — all three hit in practice, all three visible only if you
   read the output:
   - **Trailing fullwidth punctuation must NOT enter the pinyin run.** Taking the
     chunk as "leading CJK run" puts the pinyin *inside* a bracket:
     `书面作业 (pīnyīn)（20%）` instead of after `）`. Step the insertion point over
     trailing CJK punctuation and spaces first.
   - **Fullwidth `，` (U+FF0C) is easy to omit** from a hand-enumerated CJK-punctuation
     set, and a missing `，` silently truncates every chunk at the first comma.
     Derive the set from the `\u3000-\u303f` / `\uff00-\uffef` ranges, not by hand.
   - **When figures still follow the Chinese** (an assessment line like
     `书面作业（20%）＋计算实习（20%）＋期末考试（60%）`), append the pinyin at the *end* of the
     segment. But test for `[0-9%]` only — a general `[0-9A-Za-z]` test displaces the
     pinyin of every `Chinese term = "English gloss"` line to the end of the line.
   - Keep `ZH|` itself a terminator, so one segment can never swallow the next marker
     on the same line (`幻灯片 = *slides*. §1 ZH|数学模型` is exactly this trap).

This is worth doing even for a short doc: the pinyin becomes reproducible and can be
re-injected after any English edit.

## Workflow
1. **Extract** the Chinese text:
   - markdown/txt → read directly (`read_file`).
   - .docx → miniconda python-docx (`C:/Users/<you>/miniconda3/python`).
   - PDF with a text layer → PyMuPDF (`C:/Users/<you>/miniconda3/python`, `fitz`).
   - Image-only PDF → render pages to PNG with PyMuPDF, then read with
     `vision_analyze`. No text extraction works; expect ~0 chars.
2. **Translate** each segment to English yourself (you are the translator):
   preserve domain terms (VLA, LeRobot, 具身智能=embodied intelligence,
   数据集=dataset, 强化学习=reinforcement learning, 机械臂=robot arm).
   Keep proper nouns (names, model names) romanized/unchanged.
3. **Annotate**: for each segment output `中文 (pīnyīn)` + the English gloss per
   the format above. Get pinyin from the helper — never hand-write it.
4. **Write** the annotated result to a `*_EN.md`. If the user wants a rendered doc
   (e.g. "return as PDF"), build it with **typst** — see *Rendering to PDF* below.
5. **Report** files written + any segments you couldn't confidently translate
   (ambiguous 多音字, OCR errors, unreadable scan).

## Rendering to PDF (typst)
Typst is installed and renders Chinese + tone-marked pinyin + English in one
font stack (verified on this machine). Preamble for every file:

```typst
#set page(paper: "a4", margin: (x: 1.8cm, y: 1.6cm))
#set text(font: ("Libertinus Serif", "Microsoft YaHei"), size: 11pt)
#set par(justify: true)
#set heading(numbering: none)
```

Compile: `typst compile file.typ` (CLI installed; `cd` to the dir). Render to
check with PyMuPDF: `fitz.open(...)[0].get_pixmap(dpi=100).save(png)` then
`vision_analyze` the PNG.

Code blocks / ASCII diagrams: keep *verbatim* (they don't translate); use
`` ```python `` … ``` blocks. Annotate the Chinese in the prose/headings/tables
around them.

## Typst math gotchas (the file WILL error without these)
The source markdown uses LaTeX-ish math that doesn't map cleanly. Fixes:
- Bare multi-letter identifiers are unknown variables → quote them:
  `pos` → `"pos"`, `text(token_id)` → `text("token_id")`, `cal(V)` → `V`.
- Multi-letter subscripts must be separated: `S_(ij)` → `S_(i j)`.
- Avoid `overset`; render labeled arrows as text: `` `A —[a, +2]→ B` ``.
- `` `<t>` in a subscript breaks; use `y_(t-1)` instead.
After each compile, fix the next error it reports (it stops at the first one);
typically 2–5 iterations. Scan first with `grep -nE '\$[^$]*_\\([A-Za-z]{2,}\\)' file`
for multiline-subscript and `grep -n 'pos\|cal(' ` for identifier traps.

## Verifying a rendered PDF: trust vision, not the script's table checker
- **A "ragged table" warning is usually the checker, not the table.** A naive cell split counts `\|` (escaped norm bars, `$\|x\|_\infty$`) as column separators, so a 3-column table with two norms in a cell reports counts like `[3, 5, 7, 9, 11]`. Before editing anything, re-split with a lookbehind-aware pattern (`re.split(r"(?<!\\)\|", line)`) — if that gives one cell count for every row, the markdown is fine and the warning is a false positive.
- **The same applies to "unrendered markup left in the text layer".** If the flagged `\times` sits inside a deliberate inline code span that quotes raw markup (…`$A\in R^{n\times n}$`…), the PDF is correct. Locate the hit in the extracted text (`'\\times' in page.get_text()`) and read 90 characters of context before touching the source.
- **Render the PDF in the same pass as the markdown.** Where sibling pages in the same folder carry a PDF (`2.1 … (+ .pdf)`), produce the new one from the *final* markdown at the same time; a later edit silently outdates a snapshot (one vault page had to warn that its PDF predated a LaTeX pass). Check the page count the script prints against the number written into the page's own "Rendered copy" line, add that line only after the count is known, and delete the build by-products (`.body.md`, `.body.typ`, `.main.typ`, `.check*.png`, stray `body.typ`) from the vault folder — the house style is one `.md` + one `.pdf` per page.

## Multi-language output
The annotated result is the *default*. Variants the user may want:
- Ascii-only pinyin: `lazy_pinyin(s, style=Style.NORMAL)` (no tone marks).
- Pinyin+sentence-only (drop Chinese): same format without the 中文 run.

## Pitfalls
- **Never filter pypinyin output tokens for CJK characters.** `lazy_pinyin`
  returns *romanized* tokens, so `[t for t in lazy_pinyin(s) if CJK.search(t)]`
  silently returns `[]` and every `(pīnyīn)` in the document comes out empty
  with exit code 0. Strip punctuation from the **input** (`''.join(ch for ch in
  s if '\u4e00' <= ch <= '\u9fff')`) and join the output unchanged; then assert
  no `()` or unexpanded `{py:...}` placeholders remain in the built file.
- **Legacy `.doc` files extract fine with `read_file`** (it returns
  `extracted_document: true`). Don't reach for python-docx or antiword first.
- **Keep the source's own numbering.** A syllabus that prints `1.1 … 1.4` inside
  *every* chapter looks like an error; it is not — it is chapter-local numbering.
  Reproduce it verbatim and explain it in a flags section rather than renumbering
  to `2.1`, `5.6`, … which breaks cross-references elsewhere in the vault.
- **Quote the mojibake filename exactly, and read it from disk** (`os.listdir`)
  rather than retyping the `½ÌÑ§´ó¸Ù` garbage — retyping drops or swaps
  characters and the frontmatter then points at a non-existent file.
- **多音字 (polyphonic characters):** pypinyin picks the most common reading.
  Flag notes (e.g. 行 háng/xíng, 长 cháng/zhǎng, 地 de/dì) where context changes
  the reading; don't silently accept a wrong tone.
- **Never translate code/identifiers or paths** — only comments (and even then,
  only when presenting a clean annotated copy, not a runnable file).
- **Image PDFs: pypinyin can't run on pixels.** You must OCR or vision-read first
  (see `brain1-wiki-agent` PDF extraction, or `ocr-and-documents`), then
  annotate the recovered text. Expect ~0 chars from text extraction.
- **Formatting drift:** keep heading levels, bullet dashes, and table columns
  aligned so the annotated doc opens cleanly.
- **Length:** pinyin + English roughly doubles text; for long documents split
  into multiple output files by section.

## Every translation ends with
- Output file(s) preserving 中文 + tone-marked pinyin + English: `*_EN.md` and,
  if requested, compiled `*_EN.pdf` (typst).
- A short report: source → output path(s), segments translated, and any
  uncertain items flagged.
