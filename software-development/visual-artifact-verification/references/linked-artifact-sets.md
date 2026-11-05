# Linked artifact sets: anchors, back-links, and the round trip

Trigger: the deliverable is more than one file read as zoom levels — a parent map whose numbered
anchors each open a child page. Parent and child must stay traceable in both directions, and the
pair is verified as a flow, not as two screenshots.

## The set's shape

- Parent: one node per step in the argument, plus a small numbered anchor chip (Z1…Zn) top-right of
every node that has a child.
- Child: repeats the parent's chip top-left, names the node it re-enters, and lists its own next
anchors under one "then zoom into" line.
- One folder per source, children named `<source-slug>-z<n>-<topic>-zoom.html`, so the zoom order is
legible in a directory listing without opening a file.
- Every anchor resolves to a real file. When the child is not built yet, ship a placeholder page **at
the child's final filename**, stating what that zoom will cover — a chip that leads nowhere or dies
reads as a bug, and the placeholder doubles as the build spec for the next zoom. Drawing the real page
later is then a drop-in replacement at that path: no parent or sibling link has to be re-pointed.
- **Grow the set from its own files, not from a template.** Build each new child by copying the
previous child and swapping its content — same canvas width, zone geometry, chip shape, legend row.
The set reads as one document at every zoom level, and the back-link markup is inherited rather than
re-invented.

## Wiring the chip

- Wrap the chip's rect **and** its label in a real `<a href="sibling-name.html">`. A handler that
only works inside the chat surface is not enough: the set must open from `file://` in any browser.
- Add a transparent hit rect larger than the chip (36×24 around a 24×12 chip) so the anchor is
clickable without pixel-hunting.
- Put a `<title>` in the anchor naming the destination section, so hover explains the door.
- Style hover on the anchor class, and give the child's back-link the same chip shape — parent and
child then read as the same door from both sides.
- Give a child more than one way back: its top-left chip, plus any re-enter oval or "then zoom into"
line pointing at the parent.

## Patching markup in code

- Rebuild a whole element when patching. A run-level regex that matches a `<text>` opening tag and
replaces through its close drops the element's inner text and silently ships an empty label —
invisible in review, obvious in a pixel read. Assert every label string is non-empty afterward.
- Compose replacement strings with explicit joins (`chr(10)`, `''.join([...])`) rather than
escape-laden literals: a code payload mangles the escapes and the patch arrives as a syntax error
instead of an edit.
- Re-run the generating skill's checker on every touched file (`EXIT=0`) after each edit, then resolve
every `href` in every file of the set against the filesystem — including the links *into* the file you
just replaced, which is how a same-name replacement is proved to have kept every door working.

## Verification, four passes

1. The generating skill's own checker on parent and each child.
2. DOM assertions on the chips: label text non-empty, text `getBBox()` narrower than the chip rect,
   computed fill and visibility as intended.
3. Walkthrough across files: click the anchor, assert `location.href` and `document.title`, then
   follow a back-link and assert the parent again. Arrival alone is not the assertion — the return
   trip is.
4. Pixel read of the chips (the smallest text on the page, and the first casualty of any rewrite) and
   of every label whose position moved — a mask rect left at stale coordinates prints a pill over
   blank canvas while the text assertion still passes. Capture path and the 2× wrapper render: step 2
   and step 6 of the parent skill.
