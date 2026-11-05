---
name: academic-outreach
description: "Use when drafting outreach to a researcher or lab."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Outreach, WeChat, Email, Academia, Messaging, Networking]
    related_skills: [scholarly-api-sourcing, chat-message-delivery]
---

# Academic Outreach Messages

Draft first-contact and follow-up messages to PIs, lab members, and collaborators —
mostly on WeChat, sometimes by email. The deliverable is a reply, so the message has to
be cheap to answer and has to prove you read the person's work.

## When to use

- "Help me message / approach / reach out to <student|professor|collaborator>"
- "Clean up this message to <name>"
- Any follow-up to a paper or citation lookup (see `scholarly-api-sourcing`)

## Context for this user

- Tsinghua master's student under my supervisor (Institute of Mechatronic
  Engineering, Dept of Mechanical Engineering). Mechatronics/robotics background:
  robot arm, ROS2, motion control, learned feedforward.
- Lives on WeChat; my supervisor is reached there too. Peer-to-peer with students is
  informal; with my supervisor, casual-but-respectful — never formal email register.
- Reads Chinese; the peers are Chinese. Supply both EN and 中文 variants and let them
  pick — both land fine on WeChat.

## Procedure

1. **Know what the target actually works on before writing**, so the message can cite a
   real paper. Use `scholarly-api-sourcing` and your own notes on the group. If the
   user says they already know who the person is, skip this and go straight to drafting.
2. **Lead the reply with the drafts.** When the ask is "clean up my message", the
   deliverable is the paste-ready text; rationale goes underneath, 2–3 lines, one line
   each, only for substantive edits. No research dump about the person.
3. **Give 2–3 variants so the user can pick their own register** — normally all three:
   (a) minimal cleanup of their own draft, (b) same length with a specific paper hook,
   (c) 中文 version of (b). 3–5 sentences each, paste-ready.
4. Name the edits that matter: what changed and why, in one clause each.

## Message skeleton

1. Greeting + who you are, one clause: "I'm [Name], just started my master's under
   my supervisor."
2. Proof of reading: their paper or line of work in your own words, plus one concrete
   detail (the method, the number). One sentence.
3. The ask, phrased small and answerable in one line: "a few questions" / "20 minutes", with
   the mode left open ("online or in person, whatever suits you"). A vague "sometime" is the
   single most common reason these messages die; a time-boxed ask with the channel left to them
   gets a one-word yes.
4. Optional: what you bring, or the light ask ("whether there's a way I could get
   involved").
5. Easy out: "happy to work around your schedule."

## 中文 terms of address (decide before writing)

Pick the honorific from the relationship, not from a politeness dial — the wrong one is more
jarring than none:

| Target | Address | When |
|---|---|---|
| Senior student, **same advisor** | 师兄 / 师姐 | the default for a labmate under your own PI |
| Senior student, different group | 学长 / 学姐 | same school, not your PI's student |
| The PI | 老师 | never 师兄 |
| Admin, technician | 老师 | standard courtesy |

- **Write surname + honorific** (师兄) rather than a bare given name — and because a
  romanized author line ("<surname> <given-name>") doesn't tell you the characters of the given name, the
  surname form also avoids guessing wrong.
- **Keep the honorific for the whole thread**, not just the opening line. Switching to 你 once
  things feel friendly is the mistake; later messages open the same way and refer to them as
  师兄 throughout.
- **One soft apology, maximum** (冒昧打扰一下). Stacked apologies read as anxious and burdensome
  rather than polite.
- **Ship the Chinese with tone-marked pinyin + an English back-gloss when the user will paste
  it verbatim** (see `chinese-pinyin-english-translation`). An unannotated 中文 block is a black
  box they cannot check before sending.

## Rules and pitfalls

- **Never assert what the person works on — ask about it.** "I heard you're doing stuff
  related to <area>" invites a correction and shows nothing read, and the category is
  often wrong (a group doing visuomotor skill composition with diffusion policies is
  not doing VLA). Asking costs one word and cannot be wrong.
- **A student cannot let you join a project — the PI decides.** Ask to understand
  first. "Can I join you" turns a peer into a gatekeeper and earns a non-answer;
  "I'd like to understand X — is there a path in?" earns a real reply.
- **One WeChat message, sent whole.** Never a bare "hey" then wait — the classic
  Chinese IM faux pas, and it stalls the thread. No bullet lists, no attachments, no CV
  in a first message, at most one emoji.
- **A cold WeChat contact with no self-intro reads as a stranger's cold call and gets left on
  read.** One clause pinning who you are — which PI, which year, which program — plus the
  specific paper is what buys the reply. "I heard about your research from Prof. X" proves
  nothing and invites a non-answer; naming the paper proves the reading happened.
- **Lead with a specific paper.** Biggest single lever on reply rate, and it gives the
  person an easy, flattering thing to respond to.
- **Clear it with the PI when the target is the PI's student.** Students' time is gated
  by the supervisor; "my supervisor suggested I reach out" beats any wording. If the user
  hasn't cleared it with them, say that plainly instead of writing around it.
- **Never ask for something the user's own context already answers** — their name, lab,
  supervisor, or background. It's in the profile; using it as a question
  wastes the message.
- **Don't pad the reply with target research the user didn't ask for**, especially after
  they've said they know who the person is.

## Reference

- Build the group picture from `scholarly-api-sourcing` plus your own profile notes rather
  than keeping a name list in this repo.
