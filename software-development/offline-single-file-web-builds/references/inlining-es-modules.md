# Inlining ES modules into one offline file

Trigger: the source is modular (external `<script type="module" src=…>` plus `import`
statements) and the deliverable has to open from `file://`.

## The failure this solves

Chrome refuses to load ES modules over `file://` — the fetch from an opaque origin
fails CORS. Symptom: the static markup renders, and **everything the JavaScript
builds is missing**. If the hero figure is SVG assembled with `createElementNS` (or a
canvas), it is not there at all; controls do nothing; the console shows
`net::ERR_FAILED Script` and `window.<seam>` is `undefined`.

Confirm it in one navigation before changing anything: load the `file://` URL, read
the seam, read the console. The same page over http is fine — that is the tell that
this is packaging, not code.

## Never concatenate — scope each source and register its exports

Four files in one scope collided on `const clamp` (a vendored library and app.js both
declared it) → `SyntaxError: Identifier 'clamp' has already been declared` → the
entire bundle dead, the page looking exactly as dead as before for a new reason. Give
one function scope per source and a registry:

```js
const __libs = Object.create(null);
__libs["vendor/lenis.mjs"] = (function(){ /* body */ return { default: Lenis }; })();
__libs["projects.js"]     = (function(){ /* body */ return { PROJECTS, SIDE_WORK, default: undefined }; })();

const { laptop } = __libs["vendor/hairline.js"];   // was: import { laptop } from './vendor/hairline.js'
const Lenis      = __libs["vendor/lenis.mjs"].default;
```

Rules that matter:

- Rewrite the forms you will actually meet: `export { a, B as C };`, `export default X;`,
  `export const|let|var|function|class X`. Key the registry by the specifier with the
  leading `./` normalised away, so `./vendor/x.js` and `vendor/x.js` are one key.
- **An export form the rewriter does not understand must fail the build**, never be
  guessed at — a page that silently does nothing is the failure mode being prevented.
- Assign straight into the registry inside the wrapper: `__libs[p] = (function(){…})()`.
  A named temp (`const __mod = (function(){…})();`) is a *top-level* declaration and
  collides with itself on the second unit — `Identifier '__mod' has already been
  declared`. That is the same class of bug, one level up, and it is easy to reintroduce.
- Keep the bundle `<script type="module">`. An **inline** module executes fine from
  `file://` (there is nothing to fetch) and preserves module strict-mode semantics.
  Only external module loads are blocked.
- A default import becomes `.default`; a named import `{ a, b }` becomes destructuring.

## Gate the build, then load the built file for real

Fail the build on: leftover `^import` / `^export`, any load-time reference
(`<script src>`, `<link href>`, `<img src>`, `@import`, `url()` in CSS), and any
unhandled export form. Report clickable links (`https:`/`mailto:` the reader chooses to
follow) and URLs sitting in comments *separately* — they are not load-time and must not
fail the gate.

Two regex traps in that gate: blank every `url("data:…")` before scanning the CSS, or
the grain texture's internal `filter='url(#n)'` reads as a fetch; and never match
`href=`/`src=` inside a script — a JS template holding `href="${esc(x)}"` is not a
reference.

Then verify the **built file over `file://`**, not the source over http: assert the
JS-drawn element exists (child count and a non-zero rect), a click changes state,
content counts are non-zero, and the console has no exceptions. Compare those counts
and a geometry number (a morph rect, a row height) against the served build — "it works
offline" is a parity claim, so measure it as one.

## State this limit up front

Inlining carries code and CSS, not media. The moment real images or video land, decide:
base64 the small ones, or ship the folder — and then it is no longer a single file.
