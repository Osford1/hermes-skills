# Accessibility for one-screen-at-a-time flows

For pages that swap whole screens in place — a wizard, an invitation, a demo, a report
walkthrough. The visual change is the easy part. To assistive tech, some elements just
disappeared and others appeared: nothing announced, no sense of *where* you now are, and a
"current" state that may be lying.

## Announce each screen

- **One live region for the whole page**, not one per screen:
  `<p class="sr-only" id="announcer" aria-live="polite" aria-atomic="true"></p>`, and set its
  `textContent` to the arriving screen's short name whenever the screen changes.
- **Clip it, never `display: none`.** A `display: none` live region is not announced at all; the
  `.sr-only` clip pattern (absolute, 1px, clipped, `overflow: hidden`) is what keeps it live. Its
  being absolutely positioned is why it costs nothing — it cannot make the document taller or
  shift a single pixel, which is the usual reason people avoid adding one.
- **Name the screens in the flow's own words, and keep it short.** It is spoken, not looked at.
- **Move focus to the arriving screen** (`tabindex="-1"` on the screen element, then `.focus()`).
  Most readers treat the focused element as "where I am"; the live region is the sentence that
  names the place. A focus ring around a whole screen is fine — it is what a keyboard user needs.
- **The announcement must fire wherever the screen ACTUALLY changes.** The standard failure: every
  navigation goes through one `show()`/`navigate()` function *except* the one transition that
  manipulates the DOM itself — a scroll-driven move, a FLIP landing, a fallback path taken when a
  library is missing. The call gets wired into the function that most routes use, so that one
  screen arrives silently and the live region keeps naming the screen *before* it. Put the call at
  the state change, or call it from both paths.
- **Verify by reading, not by assuming.** After each route — not just the main one — read the live
  region's `textContent` and `document.activeElement` and confirm they name the screen that just
  arrived. A route you did not walk is a route that does not announce.

## Which ARIA state means what

| situation | correct state | why |
|---|---|---|
| one item is "current" in a list or carousel | `aria-current` on that item | it is a position, not a toggle |
| a choice among a few buttons (a level, a method) | `aria-pressed` on each, including the `"false"` ones | announces as a toggle button, and the group reads as one choice |
| a locked option that is **still selectable** | nothing on the option itself; `role="status"` on the notice that appears | `aria-disabled` claims it cannot be used — a lie when picking it is a valid, handled response |
| a duplicate card created to wrap a carousel | `aria-hidden="true"` + `tabindex="-1"`, and do **not** copy the current/selected attribute onto it | a favourites announce would otherwise name the chosen item twice |
| a busy moment that is ignoring clicks | `cursor: progress` + the click refused; nothing in the tree needs to change | the interaction guard *is* the state — see the contrast notes in the parent skill |

## Carrying a choice across screens

Someone who returns to a screen they already answered must see their answer still there: keep the
chosen state on the control (`aria-pressed="true"`, or the card rimmed in the accent) and re-render
it from stored state rather than from the animation that played the first time. A choice that
silently resets is worse than no choice, because the earlier answer has become a consent the page
has forgotten.

## The whole check, in one pass

Walk every route with the accessibility tree open and confirm three things per step: the live
region names the screen that just arrived, focus is inside it, and nothing still selectable claims
to be disabled.
