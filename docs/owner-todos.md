# Owner TODOs

Open decisions and assets that need Chen Bin's input before this repo is finished. Each line says
what is needed, why, and where it lands.

- **Screenshots.** No images exist and none were fabricated. Three shots are needed — a verification
  skill catching a bad render, one particle page, one learning map — and `docs/screenshots/README.md`
  lists the filename, content and size of each. Once they exist, add them under `docs/img/` and
  replace the `TODO(owner)` comment in `README.md`. Why: three of the strongest claims here are about
  *how things look when they are wrong*, which prose cannot show.
- **`glassy-panel-design` authorship.** Its frontmatter carries `author: Nous Research` and its
  `related_skills` point at the Apple-design family in the Hermes library. `PROVENANCE.md` lists it as
  the only `adapted` row for that reason. Confirm whether the upstream credit is load-bearing: if the
  skill is a rewrite of something in the bundle, the credit line should name it precisely; if the
  `Nous Research` string is just a leftover scaffold default, it should be corrected to you. It is the
  only frontmatter author field in the repo that is not `Hermes Agent` or absent.
- **The deleted outreach roster.** `research/academic-outreach` originally shipped
  `references/hu-group-roster.md` — a roster of a research group's members with names, addresses and
  contact details. It is deleted here and the `SKILL.md` references were rewritten to point at
  `scholarly-api-sourcing` plus your own notes. Confirm that deletion is the fix you want, or
  regenerate a contact-free version (who works on what, which paper to cite) if the skill is much
  weaker without it.
- **The deck maps.** `note-taking/teaching-technical-concepts/references/robotics-bionics-deck-map.md`
  and `lecture-and-course-maps.md` index your own lecture decks by course name and PDF page. They
  contain no slide content, only pointers. Confirm you are comfortable publishing an index of a
  course's slides; if not, the whole `references/` set for that topic comes out cleanly.
- **The gated worked example.** `zoomable-learning-maps` used an unpublished, in-press paper as its
  worked example. That example is not in this repo and the paper is not named anywhere — the slugs in
  `references/spec-format.md` are neutral `paper-*` placeholders. The todo from the earlier decision
  stands: rebuild the worked example against a public CC-BY paper once one is picked, then the
  placeholders can become real output.
- **Provider pricing snapshot.** `hermes/hermes-openai-compat-provider`'s references describe a
  specific third-party model API, including platform and pricing details that were true when written.
  Re-verify before anyone relies on them, and correct or date-stamp them.
- **Status claim.** The README says "learning-in-public" and that nothing here has a test suite. If
  you would rather present these as finished, say so — but the honest wording is currently the
  accurate one, since the scripts were only exercised on this machine.
