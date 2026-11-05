---
name: chinese-job-board-monitoring
description: Monitor Chinese job boards; scrape bot-walled CN sites.
---

# Chinese job-board monitoring

For recurring digests of Chinese job postings (实习/校招/社招), or any time a Chinese
site has to be read programmatically. Verified 2026-10-18 from a China-network Windows box.

## Rule zero: name the account risk before automating

China's big consumer job apps are login-walled and bot-detected. **Never automate
messaging (打招呼) or high-rate browsing on a user's logged-in account** — a flag on a
fresh account is worse than searching slowly by hand. Read-only, no-login sources first;
tell the user plainly which sites are manual-only instead of half-working them.

## Access reality (this changes over time — retest before trusting)

| Site | Status | Access |
| --- | --- | --- |
| BOSS 直聘 (zhipin.com) | **Blocked** | Serves a `安全验证` page: "当前 IP 地址可能存在异常访问行为". No public API. |
| 智联招聘 (zhaopin.com) | **Blocked** | Same security-verification wall. |
| 牛客 (nowcoder.com) | Works | Open JSON API, no login. |
| 清华就业网 (thu.ncss.cn) | Works | Open GET, no login. School boards in general are the highest-signal, least-defended source — check the user's own university first. |
| 实习僧 (shixiseng.com) | Works | Nuxt SSR payload. Titles partially masked (see below). |

## Verified endpoints

**牛客** — `POST https://www.nowcoder.com/np-api/u/job/square-search`
content-type `application/x-www-form-urlencoded`, body:
`careerJobId=&jobCity=&page=1&query=<KW>&random=true&recommend=false&recruitType=1&salaryType=2&pageSize=20&requestFrom=1&order=0&pageSource=5001`
- `recruitType` 1 = 校招, 2 = 实习. A JSON body returns 0 rows — it must be form-encoded.
- Response `data.datas[].data`: `jobName`, `jobCity`, `salaryMin/Max`, `salaryType`,
  `salaryMonth`, `eduLevel`, `graduationYear`, `id`, and `ext.infos` = **the complete JD text**.
- Detail page: `https://www.nowcoder.com/jobs/detail/<id>`
- Two shapes appear in one response: internal rows (`jobName`) and "直达官网" rows
  (`jobTitle` + `companyName`). Fall back across both or you lose several.

**清华就业网** — `GET https://thu.ncss.cn/student/jobs/jobslist/ajax/?jobName=<KW>&offset=1&limit=20`
- Fields: `jobName`, `recName` (company), `areaCodeName`, `degreeName`, `headCount`,
  `publishDate`, `sourcesNameCh` (`清华大学` = posted via the school).
- Count endpoint: `/student/jobs/jobslist/jobcount`.
- Detail links 302 from `/student/jobs/detail.html?jobId=<id>`; that is fine, browsers follow it.

**实习僧** — `GET https://www.shixiseng.com/interns?keyword=<KW>`
- Pull `window.__NUXT__` out of the HTML and eval it (Node can do this natively);
  jobs live at `$.data[0].interns.data[]`: `cname`, `city`, `minsalary`/`maxsalary`,
  `degree`, `industry`, `uuid` (→ `https://www.shixiseng.com/intern/inn_<uuid>`).
- **Titles are deliberately obfuscated**: a per-request icon font (`/interns/iconfonts/file?rand=`)
  swaps some characters for `&#xE000`–`&#xF8FF` PUA codepoints, differently on every fetch.
  Strip them and mark the gap (`运动控制…`) — do not pretend the title is complete. Company,
  city, pay and 学历 are unmasked. Union several fetches to recover most characters if needed.
- Entity regexes must make the semicolon **optional** (`&#x([0-9a-fA-F]{4});?`) — many arrive bare.

## Finding a site's real API

1. `js("performance.getEntriesByType('resource').map(r=>r.name)")` after load — lists every
   request the page made, no interception needed. Fastest first pass.
2. When you need the exact method/body: inject a hook with
   `cdp('Page.addScriptToEvaluateOnNewDocument', source=...)` that wraps `window.fetch` and
   `XMLHttpRequest.prototype.open/send` into `window.__cap`, then navigate and read it back.
   The hook survives later navigations, so one call can profile several sites.
3. Read a JSON-ish SSR blob by slicing from its assignment to `</script>` and `eval`ing it in Node.

## Pitfalls that cost real time

- **Native tools ignore MSYS paths.** `curl -o /tmp/x.html` writes to `C:\tmp`, not the bash
  `/tmp`. Use `$LOCALAPPDATA/Temp/...` for scratch files any native binary must read back.
- **Never sort dated filenames lexically.** `2026-10-18.json` sorts *after* `2026-10-18-1140.json`
  (`-` < `.`), so "newest" silently picks the stale file. Sort by `os.path.getmtime`.
- **A zero-new run must not overwrite the rankable corpus.** Keep a cumulative
  `snapshot.json` of everything currently matching and rank from that; deriving the
  shortlist from the newest per-run file means a quiet day blanks it.
- **CRLF line endings** break multi-line `old_string` matches in files written on Windows;
  anchor patches on a single line.
- **`salaryType` semantics differ inside one response**: `1` = 元/天 (interns),
  `2` = K/月 with `salaryMonth` giving 13/15薪. `min=0, max≥999999` means 面议. Never
  assume one unit — a naive formatter prints `0.012-0.03K`.
- **`eduLevel` codes are undocumented** (0/5000/6000/7000). Infer only from postings whose
  titles state the degree, and label the mapping as inferred.
- **Don't silently drop 博士及以上 rows** — that hides whole companies that are hiring.
  Sort them last and let the user see them.

## Digest design

- Dedupe on a stable `<source>:<id>` key in a `seen.json`; report only new items, and keep
  `latest.md` (what the cron sends) plus timestamped copies so history survives.
- Rank before sending: 实习 above 校招, target cities first, control/robotics/domain keywords
  first, 硕士 above 本科. A raw dump of 99 postings is useless in a chat message.
- Keep the digest engineering-only. A keyword hit can be a false positive: 运动控制 matches
  运动户外 and 运动数据 (e-commerce / data-ops roles), and a robotics company (图云机器人) posts
  客服/审核/交易 roles. Read the surviving characters of a masked title and drop 客服/运营/电商/
  采购/产品 rows rather than ranking them — four 客服 rows from one employer can otherwise fill
  half the message. The header's "n of total shown" carries the filtering; put the counts in the
  watch log, not in the message.
- Chat delivery is plain text on WeChat — no markdown tables. Cap **1800 characters for the whole
  message**, not 2500: the Weixin adapter splits at 1800 and the cron footer rides the last chunk,
  so an over-long digest arrives as two bubbles with the Chinese half looking like its own message.
  Check `len(text)` and drop items from the bottom to fit; 6 items ≈ 1,200 chars.
- **Deliver bilingual, English first**, mirroring the `daily-briefing` skill: items in English, then
  a `——— 中文 · pinyin ———` divider, then the SAME items in Chinese with pinyin in parentheses
  (lowercase, tone marks, grouped by word — 运动控制 → yùndòng kòngzhì). Pinyin the job-title words
  only; company names stay in Chinese. Links go in the English half only.
- When a title is masked, keep the site's `…` in BOTH halves — translating a masked title means
  showing the mask, never inventing the hidden characters.
- Bind the job's `deliver` to `<platform>:<chat_id>` and make the final response BE the message:
  a job that calls `hermes send` itself under `deliver: local` records `last_status: ok` while
  delivering nothing, so the outage reads as green for weeks.
- Write the finished message to `%LOCALAPPDATA%/hermes/deliveries/<job>-<date>.md` before finishing,
  so a later session can resend it verbatim.
- Schedule 2–3×/week, not daily; no-login boards don't turn over that fast and 0-new digests train
  the user to ignore them.
