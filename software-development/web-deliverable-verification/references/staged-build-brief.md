# The staged build brief, and the iteration prompt

The two prompt shapes for any HTML/widget/page build, plus the brief sections that decide
whether the result looks designed or generic. Written for this user's stack: the measured
palettes in `Projects/Web-Design-System/Reference/hubspot-html-websites-teardown.md`, and the
pinned libraries in `_Knowledge/vendor/` (GSAP 3.15 + Lenis 1.3.26, offline, no CDN).

---

## The rule behind both prompts

A good **first prompt** does the designer's job — decide the single idea, pick the mood, fix the
content — and leaves the coding to the model.

A good **iteration prompt** changes ONE thing, describes the SYMPTOM not the fix, points at a
REFERENCE, and says what to KEEP.

Most bad AI web output is not bad CSS. It is a decision the brief left open, which the model
filled with a guess.

---

## Template A — the first prompt

```
Build me a single-page website. Everything below is the brief — don't invent content.

WHAT IT IS
Page: [what it is / what it's for]
Read by: [who, on what device, over how long]
The one idea: [the single feeling or concept, one short phrase]

CONTENT (use this exactly; do not add filler sections)
1. [Section name] — [the actual words / the actual options]
2. [Section name] — [...]
What happens at the end: [the outcome when the reader acts — where the answer lands]

LOOK
Mood: [pick one from the measured palettes]
Palette + type + radii: take the measured numbers from
<archive>/Projects/Web-Design-System/Reference/hubspot-html-websites-teardown.md

RULES (non-negotiable)
- One HTML page. Inline CSS + JS. No build step. Must open on a double-click from file://
- Any library comes from <archive>/_Knowledge/vendor/ — never a CDN
- Laptop-first, or phone-first — and the other width is a fallback that must not break
- box-sizing reset, then :root tokens for palette, type scale, spacing on a 4px grid, radii, easing
- Flexbox or grid for every alignment — never magic margins to nudge things
- Body text >= 16px, line-height ~1.5, line length <= 70 characters
- Text contrast >= 4.5:1 against its background — measured, not assumed
- Respect prefers-reduced-motion

BUILD ORDER (stop and show me after each stage)
1. Skeleton + flow only — all screens, real words, working Next/Back, plain styling
2. The look — tokens, type, spacing, material, both widths
3. Background + transitions
4. Motion
5. Audio, the final shake, the external link
Don't start a stage until I say go.

TEACH ME WHILE YOU BUILD
- Comment the CSS in plain English: what each block is FOR, not what it does
- In a comment, name which rule above is doing the work at each decision point
- Keep NOTES.md beside the page: one line per decision, what it is for and where the code lives
- End each stage with "Try these 3 edits": three one-line changes I can make myself,
  each with what I should expect to see

OUTPUT
Save to: <archive>/Projects/<name>/Deliverables/WebApps/<app>/index.html
Then give me the file:// path so I can open it.
```

### The five blanks that decide the result

| Blank | What goes there | Why |
|---|---|---|
| **The one idea** | One feeling, e.g. "quiet hotel spa" | One concept executed fully beats ten half-ideas |
| **Content** | The real words, the real options | An empty brief = invented filler = generic-looking page |
| **What happens at the end** | Where the choice/answer lands | The functional core; models happily build a pretty dead end |
| **Mood** | A palette name from the measured set | Palette = emotion, and the values are already measured |
| **Output path** | Absolute, inside the project's own app folder | `Projects/x` alone resolves to the wrong place, and a bare path invites a collision |

---

## Template B — the iteration prompt (revision 2 onward)

```
ROUND [N] — one change only.

What's wrong: [the symptom, in plain words — not the fix]
Where: [the section or element]
Make it like: [a path to a reference file, if you have one]
Keep: everything else exactly as it is — don't restyle anything I didn't name.

Then tell me, in one line each:
- what you changed
- what CSS property to look at to understand it
```

1. **One change per round.** Five at once and you cannot tell which helped or which broke.
2. **Symptom, not fix.** "The gaps between the cards feel random" makes the model diagnose;
   "add 24px" makes it obey and teaches nothing.
3. **A reference beats an adjective.** A file path is checkable; "make it pop" is a guess.
4. **Say what to keep**, or already-liked parts get "improved" beyond recognition.
5. **Ask what changed** — that one line per change is the lesson.

### Prompts that waste a round

- Adjectives with no anchor: *make it pop, more modern, cleaner, more premium*.
- A stack of fixes in one message → an unpredictable rebuild.
- Re-pasting the whole brief → that is a rewrite, not a revision.
- Omitting "keep the rest" → silent regressions.

### Make rounds reversible

Copy `index.html` → `index-v<N>.html` before each round. One deleted file beats a paragraph of
prose trying to describe the undo.

---

## Reference material: what can and cannot be read from it

A reference is worth what survives the reading. Verified on a real page: the source file gave a
background of `#0b0f14` and a 15 px body; a screenshot of the same page yielded `#0d1117` at
65 % confidence and `20px` at 85 % — both wrong, the size by a third.

| Reference | What comes out | What is lost |
|---|---|---|
| HTML/CSS/JS source | everything exact | nothing |
| Token/theme JSON | exact palette, type, spacing | the layout they were meant for |
| A live URL | measured computed styles — real hex, sizes, spacing | some dynamic content |
| Screenshot / photo | layout, hierarchy, mood, rough colour | **every exact value** |
| PDF | text plus rendered pages | interaction, real CSS |
| Video | extracted frames — the look | the timing, which was the point |
| Sketch | structure and intent | everything precise |
| Figma/Canva | nothing directly | — (export a PNG or copy the CSS out) |

Two rules matter more than the format: **2–3 references max, each with a job** (one for mood, one
for structure, one for motion — ten give you a collage), and **a path beats a description**.

---

## Acceptance checks, in full

Run before claiming a stage is done; report the numbers.

1. The whole flow runs with the network off.
2. Back works on every screen.
3. Any audio fires inside a click handler (never on load — browsers block it) and does not gate
   the flow when blocked.
4. With `prefers-reduced-motion` on: no drift, no float, no zoom, no magnetic pull — and the flow
   still completes.
5. Contrast measured over the real surfaces and quoted (`scripts/verify-contrast.py`).
6. Renders at laptop and phone widths with 0 px horizontal overflow.
7. No `http`/`https` left in the file — list every one if any remain.

If a check fails, say which one and what the real behaviour is. Do not paper over it.
