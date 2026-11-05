# Search Playbook (verified commands)

Every command below was run successfully on this machine (Windows, Git-Bash, Python 3.11),
September 2026. Chinese-network notes are marked **[proxy]**: add
`--proxy http://127.0.0.1:7897` to `curl` (local Clash), or use the `browser_exec` tool.

---

## 1. OpenAlex — "which fields already publish on my function?" [no proxy needed]

Free, no key, fast. The `group_by` call is the single best cross-domain probe: it tells
you which disciplines own your function's literature before you search any of them.

```bash
# field distribution for a function (26 fields on the gecko example)
curl -s 'https://api.openalex.org/works?search=gecko%20adhesion&group_by=primary_topic.field.id'

# broader view
curl -s 'https://api.openalex.org/works?search=gecko%20adhesion&group_by=primary_topic.domain.id'

# then pull actual papers from the surprising field
curl -s 'https://api.openalex.org/works?search=hygromorphic%20actuator&per_page=10&select=title,doi,publication_year,cited_by_count'
```

Notes: `search=` is full-text-ish; `select=` returns just the fields you need; combine
`&filter=from_publication_date:2015-01-01`. Do **not** pass `select=` on a `group_by`
call — it suppresses the buckets.

Surprising-field buckets ARE the ideation signal: if "Agricultural and Biological
Sciences" shows up on an actuator query, go read why.

**Do not stop at this probe.** Generic function words return an Engineering-dominated
bucket almost every time ("cable routing robot manipulator" → Engineering 3997 vs
Neuroscience 212), which is your own field reflected back. The probe tells you which
fields are adjacent; then search each donor in **its own vocabulary** (patent classes,
donor-term papers) — that is where the non-obvious hits live.

## 2. Google Patents XHR — other industries that already reduced it to practice [proxy]

The highest-yield cross-field move: take your function's words and scope the search to a
**CPC section you don't work in**, or to a date before your field cared about it. The
internal XHR endpoint returns JSON (works headless; the HTML page is a JS app).

```bash
Q='q%3D%22compliant%2Bmechanism%22%26country%3DUS%26cpc%3DF16H%26before%3Dpriority%3A20100101'
curl -s --proxy http://127.0.0.1:7897 \
  "https://patents.google.com/xhr/query?url=$Q&exp=" -o gp.json
```

Validated: `total_num_results` 6290 unscoped, 7 when scoped to CPC F16H before 2010 —
that 7 is a list of *another field's* take on your problem.

- The `url=` argument is a **URL-encoded** query string: `q=`, `country=`, `cpc=`, `before=priority:YYYYMMDD`, `after=priority:YYYYMMDD`. Spaces must encode as `+` (NOT `%20`) or the query silently returns nothing usable; `%22` wraps an exact phrase.
- **Throttling is the main failure mode.** Queries run back-to-back return either an empty body or an HTML `Sorry...` page. Sleep 4-8s between queries and retry up to 4 times with growing backoff; do not conclude the syntax is wrong from a single failure (a bare function word with no `cpc` scope is also throttled hardest — always scope).
- Parse with `json.loads(text, strict=False)` — the payload contains raw control chars, and Google sometimes truncates it mid-object; treat a parse error as "retry", not "no results".
- Result shape: `results.total_num_results`, `results.cluster[0].result[i].patent.{publication_number,title,snippet}`.
- Cross-section recipe: find the CPC of your own device (e.g. F16H gearing, A61B surgical, B25J manipulators, G02B optics), then re-run the same function words in the *other* sections and diff.

Espacenet and WIPO Patentscope also return 200 through the proxy if you need a second
corpus (`worldwide.espacenet.com/patent/search?q=`, `patentscope.wipo.int/search/en/`),
but they are bot-walled headless — prefer the browser tool for interactive use.

## 3. AskNature — biology by **function** [browser tool only]

Cloudflare returns 403 to curl; it renders fine in `browser_exec`. Search by function
word, not by organism:

```python
# in browser_exec
new_tab("https://asknature.org/?s=damping&post_type=strategies")
js("document.body.innerText.slice(0,3000)")   # BIOLOGICAL STRATEGIES n / INNOVATIONS n
```

`post_type=strategies` gives biological mechanisms, `post_type=innovations` gives
companies that already commercialised one — read both: strategies are the donors,
innovations are the prior-art/buyable check.

Companion biology queries for OpenAlex: `"functional morphology"`, `"biomechanics of X"`,
species + action. Journal of Experimental Biology and J. R. Soc. Interface are the usual homes.

## 4. Museum and design-object APIs — craft/art donors at object level [no proxy]

Artists solved material problems in physical objects; APIs make those searchable.

```bash
# V&A (94 origami-related objects)
curl -s 'https://api.vam.ac.uk/v2/objects/search?q=origami&page_size=10'

# Met Museum
curl -s 'https://collectionapi.metmuseum.org/public/collection/v1/search?q=folding%20stool'
# then: /public/collection/v1/objects/<id>
```

Search material + action ("folding", "collapsible", "tension", "joint", "hinge",
"retractable"), plus craft-specific words ("karakuri", "jacquard", "astrolabe").

**Verified limitation: these APIs are object-level, not mechanism-level.** V&A `q=fusee`
matched a *typeface* (Neville Brody's "Fuse") because the search hits titles and object
metadata loosely; only the Met returned usable mechanism-ish objects for `swivel hook`.
Use museum APIs for material/construction/form donors (how an object is made, what it is
made of, how it articulates as an artefact) and go to patents for mechanisms. Log the
negative result rather than pretending the donor produced something.

## 5. Historical and trade literature [proxy for archive.org]

Nineteenth- and twentieth-century trade manuals are dense with mechanisms modern
engineering forgot, all public domain:

```bash
curl -s --proxy http://127.0.0.1:7897 \
  'https://archive.org/advancedsearch.php?q=title%3A%22mechanical+movements%22&fl%5B%5D=identifier&rows=10&output=json'
```

Recurring targets: *507 Mechanical Movements* (Brown), Reuleaux *Kinematics of
Machinery*, *Mechanisms and Mechanical Movements* (Jones), Model Engineer bound volumes,
Holtzapffel *Turning and Mechanical Manipulation*, Hiscox *Mechanical Movements*,
Al-Jazari and Vitruvius for pre-modern automatons. Gutenberg mirrors some of them.

## 6. Practitioners' own vocabulary — forums, video, subreddits

The transfer language lives in communities, not journals.

- `reddit-reading` on the donor field's subreddit (r/luthier, r/blacksmith, r/AskEngineers,
  r/maker, r/knitting, r/lockpicking) — search the *problem*, e.g. "creep", "backlash",
  "why does this keep slipping".
- `youtube-content` for the donor craft's technique channels; transcripts carry the
  vocabulary the journals don't.
- `web_search` with donor words plus `forum`, `build log`, `teardown`.
- `blocked-page-recovery` when a donor paper or museum page walls you.

## 7. Generation assist when the slate is thin

Not retrieval, but useful to force distance once you have candidates: TRIZ 40 principles
and the contradiction matrix (map your conflict pair onto the matrix, read the suggested
principles as *search directions* in other fields), SCAMPER, Design Heuristics cards,
BIOS/Design-by-Analogy literature. Treat outputs as **queries**, never as answers —
an unretrieved principle is not a citation.

## 8. Logging

Every donor hit goes into the ledger in the same pass you find it (donor, source URL,
mechanism, conflict, analogy type, invariants, cheapest test). Do not batch this to the
end of the session — retrieval context is lost by then.
