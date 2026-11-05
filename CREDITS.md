# Credits

## Hermes Agent

These skills are written for **Hermes Agent by [Nous Research](https://github.com/NousResearch/hermes-agent)** — the agent that loads them, and the reason the `SKILL.md` format exists in this shape. Hermes Agent is not covered by this repo's licence.

## Skills from the Hermes library — referenced, not redistributed

Many skills here name other skills in `related_skills` and in their bodies, as things to load
alongside them. Those skills are **not** in this repo and are not mine to licence; install them
from Hermes or the community hub. The count is how many of the 38 skills here reference each one.

| referenced skill | referenced by |
|---|---|
| `file-organization` | 9 |
| `grounded-citations` | 4 |
| `obsidian` | 3 |
| `ocr-and-documents` | 3 |
| `apple-design` | 2 |
| `diagram-design` | 2 |
| `docx` | 2 |
| `experiment-session-report` | 2 |
| `lerobot-embodied-ai` | 2 |
| `lerobot-environment-setup` | 2 |
| `p5js` | 2 |
| `pdf` | 2 |
| `scholarly-api-sourcing` | 2 |
| `arxiv` | 1 |
| `blocked-page-recovery` | 1 |
| `chat-message-delivery` | 1 |
| `coursework-assignment-reports` | 1 |
| `dogfood` | 1 |
| `dokument-skiel` | 1 |
| `hermes-agent` | 1 |
| `node-inspect-debugger` | 1 |
| `okr-smart-project-roadmap` | 1 |
| `plan` | 1 |
| `pretext` | 1 |
| `reddit-reading` | 1 |
| `session-librarian` | 1 |
| `spike` | 1 |
| `staged-deliverable-builds` | 1 |
| `sympy` | 1 |
| `systematic-debugging` | 1 |
| `urdf` | 1 |
| `youtube-content` | 1 |

Some of these are library skills; some are skills a reader may have written. Either way the
credit for them belongs where they live, not here.

## Third-party tools and libraries the skills use

None of the following is vendored into this repo — no third-party source is copied here. They
are the dependencies the bodies and scripts name, and you install them yourself.

**Documents and PDFs**

- [PyMuPDF](https://pymupdf.readthedocs.io/) (`fitz`, `pymupdf`) — PDF text, geometry and rendering
- [python-docx](https://python-docx.readthedocs.io/) and [python-pptx](https://python-pptx.readthedocs.io/) — Word and PowerPoint read/write
- [Pillow](https://python-pillow.org/) — image handling
- [LibreOffice](https://www.libreoffice.org/) headless (`soffice`) — format conversion
- `win32com` ([pywin32](https://github.com/mhammond/pywin32)) — driving Office on Windows

**Text and language**

- [pypinyin](https://github.com/mozillazg/python-pinyin) and [jieba](https://github.com/fxsjy/jieba) — tone-marked pinyin and segmentation
- [FFmpeg](https://ffmpeg.org/) — media probing and frame extraction

**Web and 3D**

- [three.js](https://threejs.org/) (r128 UMD) and [React Three Fiber](https://docs.pmnd.rs/react-three-fiber) — 3D scenes
- [GSAP](https://gsap.com/) and [Lenis](https://github.com/darkroomengineering/lenis) — animation and smooth scroll. **GSAP is not MIT-licensed** — it is free for most uses under its own terms, so read them before shipping anything built from these recipes. Nothing from it is vendored here.
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/) — reading a live DOM and CSS

**Science and maths**

- [NumPy](https://numpy.org/), [SciPy](https://scipy.org/) (`ndimage`) and [Matplotlib](https://matplotlib.org/)
- [SymPy](https://www.sympy.org/) — symbolic kinematics and dynamics

**Agent plumbing**

- [Model Context Protocol](https://modelcontextprotocol.io/) Python SDK (`FastMCP`, `stdio_client`) — used by the Claude bridge
- [Obsidian](https://obsidian.md/) — the vault format the note-taking skills work against

Trademarks and names belong to their owners. Their presence in a skill body is a description of
what I used, not an endorsement by them of this repo.
