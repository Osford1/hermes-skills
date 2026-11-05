# Provenance

Every skill here was developed in the same Hermes install, and all of them are published
because I judged them to be my own work or my own substantial adaptation of something
general. This file records the evidence behind each row rather than asking you to take
that on faith.

## Method, and what it cannot tell you

The install keeps a skills ledger (`<skills dir>/.usage.json`) and a hub lock file
(`<skills dir>/.hub/lock.json`). Four things follow from reading them, and each row below
quotes them:

- **`created by`** — whether the ledger flags the skill as created by the agent inside
  this install (`agent-created`) or carries no creator flag (`not recorded`). The flag is
  only set when a skill is made through the skill tool; writing the files directly leaves
  it empty, so `not recorded` is not evidence of anything except the route it was made by.
- **`patches`** — how many times the skill was edited in place after creation. A high
  number is the strongest signal in the ledger that a skill was lived in rather than
  pasted once.
- **`created`** — first recorded use, which is a lower bound on when the skill appeared,
  not a creation date.
- **`author` frontmatter** — a default field in this install. Most skills in the library
  carry `Hermes Agent` there because that is what the scaffold writes, so it is not a
  credit and not a claim. The one exception is called out below.

What the evidence **cannot** settle is the line between writing a skill from scratch and
rewriting someone else's skill until it is unrecognisable. The files carry no edit history,
so for most rows I cannot prove which happened. The provenance column is therefore defined
narrowly and checkably:

- **`original`** — the file credits no third party anywhere in its body, frontmatter or
  references.
- **`adapted`** — the file credits a third party.

That is a weaker claim than "written from scratch", and it is the one I can actually
support. Nothing in this repo came from the community hub: the lock file lists 11
hub-installed skills and none of them are in this repo.

## Per-skill evidence

| skill | provenance | version | author field | created by | patches | first recorded | files |
|---|---|---|---|---|---|---|---|
| [`claude-hermes-bridge`](autonomous-ai-agents/claude-hermes-bridge/) | original | - | — | not recorded | 8 | 2026-10-30 | 5 |
| [`interactive-concept-widgets`](creative/interactive-concept-widgets/) | original | 1.0.0 | Hermes Agent | agent-created | 54 | 2026-09-09 | 6 |
| [`particle-art-pages`](creative/particle-art-pages/) | original | - | — | agent-created | 2 | 2026-10-21 | 3 |
| [`r3f`](creative/r3f/) | original | 1.0.0 | Hermes Agent | not recorded | 6 | 2026-09-26 | 4 |
| [`web-design-recipes`](creative/web-design-recipes/) | original | - | — | not recorded | 5 | 2026-08-30 | 2 |
| [`app-theme-and-override-layers`](design/app-theme-and-override-layers/) | original | 1.0.0 | Hermes Agent | agent-created | 2 | 2026-09-20 | 2 |
| [`glassy-panel-design`](design/glassy-panel-design/) | adapted | 1.0.0 | Nous Research | not recorded | 5 | 2026-09-20 | 2 |
| [`hermes-desktop-plugins`](hermes/hermes-desktop-plugins/) | original | 1.0.0 | — | agent-created | 0 | 2026-10-29 | 1 |
| [`hermes-openai-compat-provider`](hermes/hermes-openai-compat-provider/) | original | - | — | agent-created | 30 | 2026-08-28 | 5 |
| [`brain1-wiki-agent`](note-taking/brain1-wiki-agent/) | original | 1.0.0 | Hermes Agent | not recorded | 20 | 2026-08-24 | 1 |
| [`first-principles-thinking`](note-taking/first-principles-thinking/) | original | 1.0.0 | Hermes Agent | not recorded | 5 | 2026-09-16 | 3 |
| [`paper-structure-maps`](note-taking/paper-structure-maps/) | original | 1.0.0 | Hermes Agent | agent-created | 1 | 2026-10-20 | 1 |
| [`parallel-document-ingest`](note-taking/parallel-document-ingest/) | original | 1.0.0 | Hermes Agent | agent-created | 6 | 2026-09-15 | 2 |
| [`teaching-technical-concepts`](note-taking/teaching-technical-concepts/) | original | 1.0.0 | Hermes Agent | agent-created | 127 | 2026-09-09 | 15 |
| [`zoomable-learning-maps`](note-taking/zoomable-learning-maps/) | original | 1.0.0 | Hermes Agent | not recorded | 12 | 2026-10-22 | 9 |
| [`annotated-figures`](productivity/annotated-figures/) | original | 1.0.0 | Hermes Agent | agent-created | 1 | 2026-10-23 | 2 |
| [`chinese-job-board-monitoring`](productivity/chinese-job-board-monitoring/) | original | - | — | not recorded | 2 | 2026-10-18 | 1 |
| [`chinese-pinyin-english-translation`](productivity/chinese-pinyin-english-translation/) | original | 1.0.0 | Hermes Agent | not recorded | 21 | 2026-09-03 | 3 |
| [`consolidated-report-deliverables`](productivity/consolidated-report-deliverables/) | original | 1.0.0 | Hermes Agent | agent-created | 15 | 2026-09-13 | 4 |
| [`document-cleanup-pass`](productivity/document-cleanup-pass/) | original | - | — | agent-created | 12 | 2026-10-09 | 5 |
| [`experiment-report-bilingual`](productivity/experiment-report-bilingual/) | original | 1.0.0 | Hermes Agent | agent-created | 8 | 2026-09-09 | 2 |
| [`media-reports`](productivity/media-reports/) | original | 1.0.0 | Hermes Agent | agent-created | 1 | 2026-09-09 | 1 |
| [`session-output-filing`](productivity/session-output-filing/) | original | 1.0.0 | — | agent-created | 1 | 2026-08-22 | 2 |
| [`session-transcript-recovery`](productivity/session-transcript-recovery/) | original | 1.0.0 | Hermes Agent | agent-created | 2 | 2026-09-29 | 1 |
| [`taobao-project-sourcing`](productivity/taobao-project-sourcing/) | original | 1.1.0 | — | not recorded | 5 | 2026-08-30 | 3 |
| [`academic-outreach`](research/academic-outreach/) | original | 1.0.0 | Hermes Agent | agent-created | 4 | 2026-09-10 | 1 |
| [`build-the-generator`](research/build-the-generator/) | original | 1.0.0 | Hermes Agent | not recorded | 0 | 2026-10-13 | 1 |
| [`cross-domain-ideation`](research/cross-domain-ideation/) | original | 1.0.0 | Hermes Agent | not recorded | 6 | 2026-09-15 | 4 |
| [`research-gap-ledger`](research/research-gap-ledger/) | original | 1.0.0 | Hermes Agent | not recorded | 1 | 2026-09-17 | 1 |
| [`verifying-source-claims`](research/verifying-source-claims/) | original | 1.0.0 | Hermes Agent | agent-created | 42 | 2026-09-15 | 5 |
| [`robot-kinematics`](science/robot-kinematics/) | original | 1.0.0 | Hermes Agent | agent-created | 59 | 2026-10-13 | 4 |
| [`inspecting-hermes-desktop-dom`](software-development/inspecting-hermes-desktop-dom/) | original | 1.0.0 | Hermes Agent | not recorded | 3 | 2026-09-01 | 1 |
| [`motion-control-lab`](software-development/motion-control-lab/) | original | - | — | agent-created | 1 | 2026-08-31 | 2 |
| [`offline-single-file-web-builds`](software-development/offline-single-file-web-builds/) | original | 1.0.0 | Hermes Agent | agent-created | 33 | 2026-09-29 | 9 |
| [`visual-artifact-verification`](software-development/visual-artifact-verification/) | original | - | — | agent-created | 37 | 2026-09-22 | 8 |
| [`web-deliverable-verification`](software-development/web-deliverable-verification/) | original | 1.0.0 | Hermes Agent | agent-created | 28 | 2026-09-29 | 5 |
| [`windows-linux-dual-boot`](systems/windows-linux-dual-boot/) | original | 1.0.0 | Hermes Agent | agent-created | 8 | 2026-09-21 | 2 |
| [`ubuntu-dualboot-hermes-port`](ubuntu-dualboot-hermes-port/) | original | 1.0.0 | Hermes Agent | agent-created | 6 | 2026-09-21 | 2 |

## Notes on individual rows

- **`glassy-panel-design`** — the only `adapted` row. Its frontmatter carries
  `author: Nous Research` and its `related_skills` point at the Apple-design family in the
  Hermes library, so its lineage is library-derived. It is published here because the body
  and its `references/metrics-source.md` record measurements taken on this machine against
  a real UI, which are its own. If the upstream credit is load-bearing it needs correcting —
  see [docs/owner-todos.md](docs/owner-todos.md).
- **`note-taking/zoomable-learning-maps`** — marked unverified. The chart-tree scripts ran,
  but the example slugs in `references/spec-format.md` come from an unpublished paper and
  have been replaced with the neutral `paper-*` placeholders here; treat the examples as
  shape, not as real output.
- **`research/verifying-source-claims`** — marked unverified. The recomputation rules are
  written from reasoning about nested confidence ellipses rather than from a source I
  re-derived them against, and the body says as much where it matters.
- **`research/academic-outreach`** — published without its reference file. The original had
  a roster of a research group's members with their names, addresses and contact details.
  That is other people's information and it is not in this repo; the skill body now points
  at `scholarly-api-sourcing` plus your own notes instead.
- **`note-taking/teaching-technical-concepts`** — the course and lecture maps reference
  slide decks by name and page. They contain no slide content, only an index of where to
  look, but the deck maps are the rows most worth a second opinion before reuse.
