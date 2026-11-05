# Recovering a clobbered file

`write_file` overwrites with no confirmation and no error. When a file has just been
emptied or replaced and its previous content is still needed:

1. **Stop writing.** Every further write to that path destroys the next candidate copy.
2. If the content was read earlier **in the same code-kernel session**, it is still in
   memory: `execute_code` keeps its variables across calls, so the earlier `read_file`
   result is recoverable (`cur` above) even though the file on disk is now 0 bytes.
   Strip the `N|` line-number prefixes and write it straight back.
3. Only then re-apply the intended edit — and re-read the file afterwards to prove the
   result, because a partial reconstruction looks plausible.
4. If it is not in memory: `session_search` for the file path or a distinctive line, and
   rebuild from the transcript. Never reconstruct from memory of what it probably said.

**Do not use `patch` to append.** An `old_string` that matches the first line will
happily replace that line instead of adding a section, and the result passes a size
check. Append with `write_file` on the full content, or `patch` on a trailing anchor
string that is genuinely unique to the end of the file.
