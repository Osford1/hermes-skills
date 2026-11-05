# hermes-skills

**38 skills I wrote and rewrote for [Hermes Agent](https://github.com/NousResearch/hermes-agent) while using it on real work** — design passes, document pipelines, verification loops, research reading, and a few web-scene recipes. If you run Hermes and want to see how someone else actually structures a skill, this is the most honest thing I can hand you.

These are working notes, not a product. They assume Hermes, and they assume an agent that reads an instruction file carefully.

## What a Hermes skill is

A skill is a directory containing a `SKILL.md`. The file opens with YAML frontmatter:

```yaml
---
name: web-deliverable-verification
description: "Use when shipping a web page: verify it on rendered pixels."
version: 1.0.0
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Web, Verification, Screenshots]
    related_skills: [visual-artifact-verification, offline-single-file-web-builds]
---
```

The body underneath is plain markdown instructions. The `description` is the trigger — the agent reads it to decide whether to load the body, which is why almost every one here is phrased `Use when …`. Optional `references/`, `scripts/` and `templates/` subdirectories carry material the agent loads only when it needs it: long tables, runnable helpers, worked examples.

Two consequences worth knowing before you copy anything. The body is instructions rather than code, so quality shows up as procedure, not cleverness. And because the parts load lazily, several of these skills carry a dozen reference files behind a deliberately short `SKILL.md`.

## What is in here

38 skills in 10 category folders, plus one that sits at the repo root because that is where it lives
in the source tree. The provenance column is defined in [PROVENANCE.md](PROVENANCE.md) — `original`
means the file credits no third party, `adapted` means it does.

### autonomous-ai-agents (1)

| skill | what it does | provenance |
|---|---|---|
| [`claude-hermes-bridge`](autonomous-ai-agents/claude-hermes-bridge/) | Wires Claude Desktop to Hermes as a planner/executor pair over MCP, with a watchdog script. | original |

### creative (4)

| skill | what it does | provenance |
|---|---|---|
| [`interactive-concept-widgets`](creative/interactive-concept-widgets/) | Builds a single-page interactive HTML widget for teaching one concept. | original |
| [`particle-art-pages`](creative/particle-art-pages/) | Builds an interactive particle-art HTML page; ships a verified three.js galaxy recipe. | original |
| [`r3f`](creative/r3f/) | Builds a 3D web scene in React Three Fiber or plain three.js. | original |
| [`web-design-recipes`](creative/web-design-recipes/) | Recipes for HTML pages, frontends and animation, with a site-teardown workflow. | original |

### design (2)

| skill | what it does | provenance |
|---|---|---|
| [`app-theme-and-override-layers`](design/app-theme-and-override-layers/) | Themes or overrides a host app's UI without forking it. | original |
| [`glassy-panel-design`](design/glassy-panel-design/) | Builds a glassmorphic panel or translucent UI from measured values. | adapted |

### hermes (2)

| skill | what it does | provenance |
|---|---|---|
| [`hermes-desktop-plugins`](hermes/hermes-desktop-plugins/) | Manages Hermes desktop UI plugins. | original |
| [`hermes-openai-compat-provider`](hermes/hermes-openai-compat-provider/) | Wires a custom OpenAI-compatible model API into Hermes. | original |

### note-taking (6)

| skill | what it does | provenance |
|---|---|---|
| [`brain1-wiki-agent`](note-taking/brain1-wiki-agent/) | Ingest / query / lint / add passes over an Obsidian vault, driven by the vault's own rules file. | original |
| [`first-principles-thinking`](note-taking/first-principles-thinking/) | Critiques a concept from first principles instead of polishing it. | original |
| [`paper-structure-maps`](note-taking/paper-structure-maps/) | Turns a paper into a zoomable structure map. | original |
| [`parallel-document-ingest`](note-taking/parallel-document-ingest/) | Takes many sources to cross-linked notes in one pass. | original |
| [`teaching-technical-concepts`](note-taking/teaching-technical-concepts/) | Explains a technical concept to the user; 12 reference maps for specific courses and topics. | original |
| [`zoomable-learning-maps`](note-taking/zoomable-learning-maps/) | Builds a zoom-in / zoom-out learning map, with scripts to emit the chart tree. | original |

### productivity (10)

| skill | what it does | provenance |
|---|---|---|
| [`annotated-figures`](productivity/annotated-figures/) | Annotates photos and screenshots for a deck or report. | original |
| [`chinese-job-board-monitoring`](productivity/chinese-job-board-monitoring/) | Monitors Chinese job boards, including sites that fight scrapers. | original |
| [`chinese-pinyin-english-translation`](productivity/chinese-pinyin-english-translation/) | Translates Chinese documents to English and injects tone-marked pinyin. | original |
| [`consolidated-report-deliverables`](productivity/consolidated-report-deliverables/) | Compiles scattered records into one report or deck, and verifies the export. | original |
| [`document-cleanup-pass`](productivity/document-cleanup-pass/) | Cleans a document's markup, grammar and punctuation without changing content. | original |
| [`experiment-report-bilingual`](productivity/experiment-report-bilingual/) | Builds a bilingual EN+CN report with embedded media. | original |
| [`media-reports`](productivity/media-reports/) | Produces reports with embedded figures and video. | original |
| [`session-output-filing`](productivity/session-output-filing/) | Files a task's deliverables into a fixed archive scheme. | original |
| [`session-transcript-recovery`](productivity/session-transcript-recovery/) | Rebuilds an overwritten file from the session transcript. | original |
| [`taobao-project-sourcing`](productivity/taobao-project-sourcing/) | Turns a maker project into a Taobao parts list and a build roadmap. | original |

### research (5)

| skill | what it does | provenance |
|---|---|---|
| [`academic-outreach`](research/academic-outreach/) | Drafts first-contact and follow-up messages to researchers and labs. | original |
| [`build-the-generator`](research/build-the-generator/) | Notices repeated work and builds the generator instead of the output. | original |
| [`cross-domain-ideation`](research/cross-domain-ideation/) | Sources ideas and prior art from outside engineering. | original |
| [`research-gap-ledger`](research/research-gap-ledger/) | Adds a paper to a thesis gap ledger and keeps the ledger comparable. | original |
| [`verifying-source-claims`](research/verifying-source-claims/) | Recomputes a source's numbers before they become your content. | original |

### science (1)

| skill | what it does | provenance |
|---|---|---|
| [`robot-kinematics`](science/robot-kinematics/) | Derives and checks manipulator kinematics and dynamics symbolically. | original |

### software-development (5)

| skill | what it does | provenance |
|---|---|---|
| [`inspecting-hermes-desktop-dom`](software-development/inspecting-hermes-desktop-dom/) | Reads the live Hermes desktop DOM and CSS over CDP. | original |
| [`motion-control-lab`](software-development/motion-control-lab/) | Builds control-system simulation labs, including learned feedforward. | original |
| [`offline-single-file-web-builds`](software-development/offline-single-file-web-builds/) | Builds a web page that runs offline from `file://` with no network. | original |
| [`visual-artifact-verification`](software-development/visual-artifact-verification/) | Verifies a generated HTML/SVG artifact renders correctly, including multiscreen. | original |
| [`web-deliverable-verification`](software-development/web-deliverable-verification/) | Verifies a shipped web page on rendered pixels, not on the source. | original |

### systems (1)

| skill | what it does | provenance |
|---|---|---|
| [`windows-linux-dual-boot`](systems/windows-linux-dual-boot/) | Dual-boots Linux or resizes a Windows disk safely. | original |

### repo root (1)

| skill | what it does | provenance |
|---|---|---|
| [`ubuntu-dualboot-hermes-port`](ubuntu-dualboot-hermes-port/) | Dual-boots Ubuntu and ports a Hermes install to Linux. | original |

## Install

1. Find your skills directory. Windows: `%LOCALAPPDATA%\hermes\skills`. Linux and macOS: `~/.hermes/skills`. A named profile uses `…/hermes/profiles/<name>/skills` instead.
2. Copy the skill folder you want, keeping its category folder. To take the pixel-checking one: copy `software-development/web-deliverable-verification` into `<skills dir>/software-development/`.
3. Reload skills, or restart Hermes. `hermes skills list` shows what loaded — the name that appears is the one in the frontmatter, not the folder.
4. Nothing else is needed. There is no build step and this repo installs no dependencies. Where a skill's script needs a package, the skill body says which.

Do not drop the whole repo into your skills directory unless you want all 38 active. Every loaded skill's description costs context, and the point of a skill library is that most of it stays unloaded.

## What works and what does not

- Written and used on one Windows 11 install of Hermes over about two months of real tasks. Not exercised on Linux or macOS. Several skills are Windows-specific on purpose, and say so in their `platforms` field.
- Skills with scripts were run on this machine while doing the work they describe. There is no test suite and no CI in this repo, so a script that worked here is not a script that works everywhere.
- Every absolute path in here has been reduced to a placeholder — `<vault>`, `<archive>`, `C:\Users\<you>\…`, `%LOCALAPPDATA%\hermes\…`. The procedure still reads correctly, but a handful of steps expect you to substitute your own paths before they will run.
- The verification skills (`web-deliverable-verification`, `visual-artifact-verification`, `verifying-source-claims`, `offline-single-file-web-builds`) are the ones I trust most, because they exist specifically to stop me believing unverified output.
- `design/glassy-panel-design` is the one skill whose authorship I could not settle from the files alone — the frontmatter credits Nous Research. See [PROVENANCE.md](PROVENANCE.md) and [docs/owner-todos.md](docs/owner-todos.md).
- `note-taking/zoomable-learning-maps` and `research/verifying-source-claims` are marked `unverified` there: their numbers are claims I have not re-measured.

<!-- TODO(owner): add screenshots — one verification skill catching a bad render, one particle page, one learning map. See docs/owner-todos.md. -->

## Repository layout

```
hermes-skills/
├── autonomous-ai-agents/
│   └── claude-hermes-bridge/
├── creative/
│   ├── interactive-concept-widgets/
│   ├── particle-art-pages/
│   ├── r3f/
│   └── web-design-recipes/
├── design/
│   ├── app-theme-and-override-layers/
│   └── glassy-panel-design/
├── hermes/
│   ├── hermes-desktop-plugins/
│   └── hermes-openai-compat-provider/
├── note-taking/
│   ├── brain1-wiki-agent/
│   ├── first-principles-thinking/
│   ├── paper-structure-maps/
│   ├── parallel-document-ingest/
│   ├── teaching-technical-concepts/
│   └── zoomable-learning-maps/
├── productivity/
│   ├── annotated-figures/
│   ├── chinese-job-board-monitoring/
│   ├── chinese-pinyin-english-translation/
│   ├── consolidated-report-deliverables/
│   ├── document-cleanup-pass/
│   ├── experiment-report-bilingual/
│   ├── media-reports/
│   ├── session-output-filing/
│   ├── session-transcript-recovery/
│   └── taobao-project-sourcing/
├── research/
│   ├── academic-outreach/
│   ├── build-the-generator/
│   ├── cross-domain-ideation/
│   ├── research-gap-ledger/
│   └── verifying-source-claims/
├── science/
│   └── robot-kinematics/
├── software-development/
│   ├── inspecting-hermes-desktop-dom/
│   ├── motion-control-lab/
│   ├── offline-single-file-web-builds/
│   ├── visual-artifact-verification/
│   └── web-deliverable-verification/
├── systems/
│   └── windows-linux-dual-boot/
├── ubuntu-dualboot-hermes-port/
├── docs/owner-todos.md
├── CREDITS.md
├── PROVENANCE.md
├── LICENSE
└── README.md
```

Each skill folder holds `SKILL.md` plus, where useful, `references/` (long tables and worked examples), `scripts/` (runnable helpers) and `templates/` (scaffolds to copy).

## Credits

See [CREDITS.md](CREDITS.md). The short version: these skills cross-reference other skills from the Hermes library, which I reference but do not redistribute here. Hermes Agent itself is by [Nous Research](https://github.com/NousResearch).

## License

MIT — see [LICENSE](LICENSE). Take what is useful. If you fix something, an issue or a PR is welcome.
