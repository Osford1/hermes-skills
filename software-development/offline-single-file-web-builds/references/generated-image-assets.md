# Generated image/GIF assets (fogleman/primitive)

When a build needs a "photo assembling itself shape-by-shape" animation (triangle/ellipse
primitives, fogleman/primitive style), generate the GIF locally — do not hand the user a
toolchain to run themselves.

## Recipe

1. **Toolchain**: portable Go zip from `go.dev/dl` unzipped to scratch (`C:\Temp\go`) — no
   installer, no system pollution. On this host set `GOPROXY=https://goproxy.cn,direct` and use
   **native absolute Windows paths** for `GOPATH`/`GOMODCACHE`/`GOCACHE` — Go rejects MSYS-style
   env paths (`\c\Temp\...`) with "entry is relative; must be absolute path".
2. **Install**: `go install github.com/fogleman/primitive@latest`. Current deps need a recent
   Go; a `requires go >= X.Y` error means re-download the newest toolchain zip, not patch the
   module graph.
3. **Frames**: `primitive -i in.png -o 'frame%d.png' -n 140 -m 1 -r 300 -s 512`
   (`-m 1` = triangles; `-n` = shape count; `%d` writes every iteration as a frame).
   - **Always render frames with `-o 'frame%d.png'` and assemble the GIF yourself.** Direct
     `-o out.gif` exited `status 4` with no message even on valid input; the `%d` path worked on
     the same inputs. Rerun with `-v` and the `%d` pattern whenever an exit-4 shows up silent.
4. **Assemble**: PIL — sort frames numerically, `convert('P', palette=Image.ADAPTIVE, colors=64)`,
   `save_all=True, duration=90, loop=0`. ~140 frames at 512px ≈ 1.2 MB GIF.
5. Ship the GIF in the page's `assets/` like any other media (SKILL.md §1); declare the filename
   in the assets README so swapping in the user's real photo later is a one-file replace.

## Regenerating with the user's real photo

Same command, new input. Tell the user: drop the photo in, run steps 3-4, done — the page never
changes.