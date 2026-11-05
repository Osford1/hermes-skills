---
name: claude-hermes-bridge
description: Use when wiring Claude Desktop to Hermes as planner/exec.
---

# Claude Desktop ↔ Hermes bridge

Claude Desktop has no shell — its only reach into the machine is an MCP connector. This
skill builds that connector as a local **stdio MCP server** that shells out to `hermes chat`,
so Claude plans/verifies and Hermes executes.

```
Claude Desktop ──MCP/stdio──▶ server.py ──subprocess──▶ hermes chat
      ▲                                                      │
      └────── raw evidence: exit code, paths, printed numbers ┘
```

## Live install (this machine)

| Thing | Path |
|---|---|
| Server | `C:\Users\<you>\Projects\claude-hermes-bridge\server.py` |
| Config | `…\claude-hermes-bridge\config.json` |
| Tests | `…\claude-hermes-bridge\test_bridge.py`, `jobtest.py`, `e2e_newmodel.py`, `probe_job.py` |
| Claude config | `%LOCALAPPDATA%\Claude-Data\claude_pzs8sxrjxfjjc\claude_desktop_config.json` |
| Claude logs | `%LOCALAPPDATA%\Claude\logs\` → `mcp.log`, `main.log`, `mcp-server-hermes.log` |
| App AUMID | `Claude_pzs8sxrjxfjjc!Claude` |
| Restart helper | `…\claude-hermes-bridge\watch_and_restart.ps1` (copy in this skill's `scripts/`) |
| Python for the server | `C:\Users\<you>\miniconda3\python.exe` (has `mcp` with FastMCP) |

Claude Desktop is an MSIX/Store app: the config lives under `%LOCALAPPDATA%\Claude-Data\<pkg>`,
not `%APPDATA%\Claude`. Write the server entry to **both** paths — harmless, and it removes
the guess about which one the app reads.

## Hard constraints — each one cost a real failure

**1. Claude Desktop's default MCP tool timeout is 180 s.** From the app bundle:
`function TU(){return kS()??Xl()?.mcpToolTimeoutMs??18e4}`. A tool that blocks longer is
killed and the caller sees a timeout. **Never write a blocking tool here.** Long work runs
as a background job that is polled; that is the entire reason for the job model below.
A per-server `toolTimeoutSec` (schema range 60–3600) can raise it, but polling is the fix.

**2. stdout is the JSON-RPC protocol.** Diagnostics go to stderr *only*. One stray `print()`
corrupts the transport — this is the single most likely way to break the file.

**3. The Hermes CLI cold-starts in 10–40 s**, high variance under load, before doing any work.
A task finishing in under a minute is normal even when trivial. Never treat that as a hang,
and never "fix" it by lowering a timeout.

**4. A tool reporting success is not evidence.** Verify artifacts with `hermes_read` or an
independent check (bytes, hashes). This is the point of the bridge; do not collapse it.

**5. cwd is an unattended shell.** Keep an allow-list of roots and refuse anything outside it.

## The job model — state on disk, never in the process

`hermes_run` launches a background `Popen` whose stdout/stderr go **straight to
`jobs/<id>.log`** (files, not pipes: no reader threads to deadlock, nothing lost when the
server exits), then waits at most `wait_s`.

**Keep `wait_s` at ~5 s.** It was 100 s and that was a live bug: the call outlived the
client's patience, Claude treated it as failed and **re-issued it**, starting a second Hermes
worker on the same directory — two agents editing one folder at once. Return a job id fast
and let the client poll. Note `config.json` overrides the in-file `DEFAULTS`, so change the
value in **both** places or the edit silently does nothing.

- Finished quickly → full result, exact command, exit code, duration, log path.
- Still running → `STATUS: running` + `JOB_ID`, explicitly *not* a failure.
- `hermes_status(job_id)` polls; `hermes_jobs()` lists what is in flight.

**Claude Desktop spawns a *new* server instance per session**, so anything held only in the
`JOBS` dict is invisible to whichever instance asks next. Therefore:

- Job state is written to `jobs/<id>.json` **including its pid**, and every read re-checks
  liveness, so any instance can answer for any job.
- State resolution: pid alive → `running`; pid dead with no exit code → `orphaned` (the owner
  died mid-job: the work may be part or wholly done, so read the log and the working directory
  before re-running); **no pid recorded → `running_untracked`**, never `orphaned`, or a live
  job invites a duplicate re-run.
- `_find_duplicate(cwd, task)` matches a running job on cwd + whitespace-normalised task text
  and reuses it. This guards against client retries and must scan **disk, not memory** — the
  retry normally lands in a different instance.
- Liveness = `ctypes` `OpenProcess` + `GetExitCodeProcess` == 259. **Never `os.kill(pid, 0)`
  on Windows** — that calls `TerminateProcess` and would kill the job you are inspecting.

The server enforces its own hard cap (`default_timeout_s`, 1800) independently of the client.
When it kills, it reports `STATUS: timeout` and warns the task may be part-done — never an
empty success.

## Cheap checks — never spawn the CLI for metadata

- Version: read `…hermes-agent\venv\Lib\site-packages\hermes_agent-*.dist-info` off disk. Instant.
- Skills: parse `SKILL.md` YAML frontmatter off disk. 200+ skills in ~0.1 s.
- `hermes_health` must be spawn-free. The original version ran `hermes --version` and took
  10–40 s — that was the bug that broke the first live attempt.

## Knowing what Hermes can do

An MCP client sees only tool names, so Claude otherwise plans blind against a generic shell.
Two things fix that, and both are needed:

- `FastMCP(name, instructions=…)` — a summary sent at connect time describing Hermes, the
  skill library, the planner/executor split, and the job model.
- A `hermes_capabilities(query, category)` tool that indexes skills from disk, so Claude can
  discover e.g. a LaTeX skill instead of hand-rolling the steps.

## Context: what Claude can and cannot see of Hermes

Claude Desktop's own memory is Anthropic's store, built from Claude chats. It contains **none**
of the Hermes conversations, and no bridge tool feeds it — the server exposes `hermes_run`,
`hermes_resume`, `hermes_status`, `hermes_jobs`, `hermes_read`, `hermes_capabilities`,
`hermes_health` and nothing about memory or history. Do not tell the user Claude "remembers" a
Hermes thread.

What does work, verified by running the bridge's exact command line:

- Every `hermes_run` subprocess gets `MEMORY.md` + `USER.md` injected like any other Hermes
  session, and it has `session_search` (FTS5 over `%LOCALAPPDATA%\hermes\state.db`, ~500
  sessions on this machine). Asked blind, it recited the user's supervisor, paper list, and
  learning preferences correctly.
- So continuity is reachable two ways: `hermes_resume(session_id)` continues one session with
  its history intact; or `hermes_run` a task that says "search my sessions for X, then answer".
  Get ids from `hermes sessions list` (add `--source cli|desktop`, `--limit`, `--workspace`).

Pitfalls learned here:

- **A run's provenance self-labelling is unreliable.** Told "from memory only", one run wrote
  "from memory only:" and then described the research thread it had actually pulled out of
  `session_search` results two turns later. Ask for the memory answer and the search answer as
  two clearly separated parts, and treat a detail that is absent from `MEMORY.md`/`USER.md` as
  coming from the session search, not from memory.
- `session_search` can return >100 KB; the output spills to a file under
  `%LOCALAPPDATA%\hermes\cache\spillover\` and only a pointer is returned. Have the run read
  that path rather than assuming the summary is complete.
- Bridge runs have **approval flags on**: `execute_code` comes back `BLOCKED`, and
  `python -c` / `bash -c` via terminal is flagged as dangerous and can be denied. A brief that
  needs inline Python must say "write a .py file, then run `python <file>`", or it stalls on a
  blocked call.

## Driving Claude Desktop's UI instead of the user pasting

`computer_use` works on this machine and can locate and type into `claude.exe`. Two limits
decide whether it is worth it:

- Claude Desktop is **Electron**: `capture(mode='ax')` returns only the window buttons
  (Minimize/Restore/Close) — the chat UI is *not* in the accessibility tree. Driving it means
  `mode='vision'` screenshots plus pixel coordinates, which is slower and breaks on any UI
  change. For a one-off, asking the user to paste is cheaper and more reliable.
- Approving Claude's **tool-permission prompts** is permission UI — never click it. The user
  still grants permission; automation only covers the mechanical part (open, paste, send).

## Restarting while a job is live

Claude Desktop loads `server.py` at process start, so **an edit does nothing until the app is
restarted — and a restart kills any running job.** Wait for the job first, or lose the work.
Sequence (all of it is in `scripts/watch_and_restart.ps1`):

1. Poll the job's **pid** until it exits. Do not trust its `.json`: when the owning server died
   first, the record keeps saying `running` with no exit code forever. Confirm completion from
   the **DONE artifact** on disk, not the record.
2. `Stop-Process -Name claude -Force`.
3. **Kill orphaned bridge servers** — `python.exe` with `claude-hermes-bridge` in its command
   line. They outlive the parent kill, and if Claude reuses one it serves the *old* code, so the
   fix silently never loads. This step is the difference between "restarted" and "fixed".
4. Relaunch `shell:AppsFolder\Claude_pzs8sxrjxfjjc!Claude`; allow ~45 s.
5. Verify from evidence, not the UI: the new server processes' `CreationDate` must be **later
   than `server.py`'s mtime**, and `main.log` must show `Connected to hermes`. The tool count is
   *identical* before and after a fix, so it proves nothing on its own.

To check for stray workers, filter on process name (`python.exe`/`hermes.exe`) — a bare command
line grep self-matches your own `bash.exe`/`powershell.exe` and reports false positives.

## Rebuild from scratch

1. Confirm Claude Desktop is installed and read its config; note that it is MSIX-packaged.
2. Verify the Hermes CLI answers: `hermes chat -q "say hi" --oneshot`.
3. Copy `references/server.py` into place; edit `config.json` (`hermes_exe`, `allowed_roots`).
4. Add the `mcpServers.hermes` entry (command = the python that has `mcp`, args = server path),
   with `toolTimeoutSec: 600`.
5. Restart the app: `Stop-Process -Name claude -Force`, then
   `Start-Process 'shell:AppsFolder\Claude_pzs8sxrjxfjjc!Claude'`.
6. Confirm from the log, not the UI: `main.log` must say `Connected to hermes (N tools)`.
7. Smoke-test the bridge outside Claude: `python test_bridge.py tools`, then `jobtest.py`.

## Debugging playbook

| Symptom | Check |
|---|---|
| Tool call times out in Claude | `main.log` for the restart; is the tool blocking? Look for `starting; hermes=` repeating |
| Server never starts | `mcp-server-hermes.log` holds the server's own stderr |
| `STATUS: running` returned | Normal. Poll `hermes_status`; do **not** re-run the task |
| Wrong cwd / refused | `config.json` `allowed_roots` |
| Claude plans something Hermes already has a skill for | `hermes_capabilities` not wired, or instructions missing |

Verify the wiring from logs, always — `Connected to hermes (N tools)` in `main.log` is the
proof, and the tab count in the UI is not.

## Pitfalls

- Do not use `hermes mcp serve` as the executor: it is a *messaging* bridge (~10 tools), not a
  task runner. The execution path is `hermes chat`.
- Pass the task over **stdin** (`hermes chat --query-file - -Q --oneshot`) so nothing is
  shell-interpreted and no temp-file path has to be readable by a native Windows binary.
  MSYS `mktemp` paths (`/tmp/…`) are **not** readable by the native `hermes.exe`.
- Include `--oneshot`, or the CLI can sit waiting and blow the call timeout.
- Windows PTY: `process(submit)` for prompts; a bare `\n` is not a line terminator.
- Back up `claude_desktop_config.json` (`.bak`) before editing — it also holds `preferences`
  that must be preserved.
- Overleaf/report work requested through this bridge: fresh project, widely-common template,
  **English first**, translate later (user's standing preference).
- **Hermes resolves "the current directory" to its own home, not `--in`.** A task saying
  "create x.txt in the current directory" landed in `C:\Users\<you>\`, not the `--in` folder,
  and still exited 0. Write briefs with **absolute paths** and verify the artifact where you
  asked for it, not merely that the process succeeded.
- A `hermes update` that pulled new code without restarting gateways prints a stale-modules
  warning to the job log (`mixed sys.modules`). Fix with `hermes gateway restart`; do not
  mistake it for a bridge fault.
- An `exit 0` plus a confident "Done." from Hermes is still not proof the file is where you
  asked. Always resolve the path and stat it.
