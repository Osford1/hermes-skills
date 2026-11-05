# The CDP step harness: driving a served build through its states

**When:** the build cannot be opened from disk (ES modules, `fetch`, relative assets), or the thing
to verify is a *flow* — several states reached by real clicks, scrolls and hovers, each of which has
to be screenshotted and measured. Generic headless `--dump-dom` in the parent skill is the lighter
path; use this one when the states need driving.

## Shape: two files, one output folder

- `tools/shot.mjs` — serves the build folder over http, launches Chrome once, connects to it over
  CDP, walks a list of steps, prints one compact line per step, writes a PNG per state.
- `tools/steps-<pass>.json` — the pass: `{config:{root, port, cdpPort, size:[w,h]}, steps:[…]}`.
  One file per verification pass, so a run is reproducible and two passes can be compared.
- Screenshots go to the project's `Working/verify/`, one file per state, state-named. Re-shoot the
  whole set after any edit — a leftover shot from the previous build is the classic false evidence.
- No npm dependencies: `node:http`, `node:child_process`, `node:fs` and a raw WebSocket to the CDP
  endpoint (`GET /json/version` on the debugging port gives `webSocketDebuggerUrl`).

## The static server

- `const ROOT = path.resolve(cfg.root)` once, and resolve every request against it:
  `const p = path.resolve(ROOT, '.' + decodeURIComponent(pathname))`; refuse unless
  `p.startsWith(ROOT)`. **Never build the prefix with `path.join` and compare it to a
  forward-slash string**: on Windows `path.join` returns `\`, the guard then matches nothing, and
  every request 403s — which presents as "the page did not load", not as a harness bug.
- Serve `.mjs`/`.js` as `text/javascript`. A module script served as `application/octet-stream` is
  refused by the module loader, again as "the page did not load".
- Send an explicit 404 for anything missing, and never list directories — a directory response hides
  a wrong filename.

## Launching Chrome

- Fresh `--user-data-dir` per run, `--headless=new`, `--hide-scrollbars`, an explicit
  `--window-size`, and `--remote-debugging-port=<cdpPort>`.
- **Pass `--no-proxy-server`, and `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY` for the
  run.** Exported proxy variables are inherited by the child and route `127.0.0.1` through the proxy,
  so nothing local loads.
- **Do not add `--proxy-bypass-list=<-loopback>`**: it is the opposite of what it reads as — it sends
  loopback *through* the proxy and fails with `ERR_HTTP_RESPONSE_CODE_FAILURE`.
- Give each step script its **own pair of ports** (http + CDP) and increment them per pass. On a
  reused CDP port the client attaches to the previous run's Chrome and returns a stale DOM — which
  reads as an app bug, or as duplicated tool output. Kill stale `node`/`chrome` processes on those
  ports before starting.

## Waiting, and reading back

- Wait on events, not sleeps: `Page.loadEventFired` with a fallback timer. A fixed sleep is either
  slow or flaky, and its failure looks like a page error.
- Then wait on the **build's own readiness seam** (`window.__app`/`window.__cover` returning a real
  value) before the first step, so step one is not racing the page's boot.
- Steps: `move{selector|xy}`, `click`, `scroll{y}`, `wait{ms}`, `eval{js,label}` (print
  `label: value`), `shot{name}`. Keep each step short and sleep between steps in the harness, not
  inside one long `js()` — a single evaluate that sleeps for seconds is cut off, and the timeout
  arrives looking like a page failure.
- Have the page expose a small read-back handle for the harness (`window.__cover = {open, close, cam,
  lid, …}`). Asserting through the build's own controls is what makes a walkthrough test the flow
  instead of the harness.

## Debug ladder when the page does not load

In this order, because each rung looks like the next one:

1. Curl the served URL directly and check the status code and `Content-Type`. This separates the
   server from the browser in one call.
2. Confirm the port is listening and no stale process owns it.
3. Turn on `Network.enable` and `Log.enable` and print the failures — `ERR_HTTP_RESPONSE_CODE_FAILURE`
   is the proxy flag, a 403 from your own server is the path guard, a refused module is the MIME type.
4. Only then suspect the page.

## Reporting

Print the numbers per state (the assertions, the counts, the geometry) and the screenshot path.
Name which states were shot and which were not — the pass is evidence only for the states it walked.
