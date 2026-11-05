# primitive-gif.sh — photo → triangle-mosaic drawing GIF (fogleman/primitive + PIL)
# Run in git-bash. Usage: bash primitive-gif.sh <input-image> <output.gif>
# Produces the "draws itself shape-by-shape" animation: ~120 triangles accumulate,
# then the GIF holds on the finished image at the end.

set -e
IN="$1"; OUT="$2"
export GOPATH='C:\Temp\galaxy-build\gopath' GOMODCACHE='C:\Temp\galaxy-build\gopath\pkg\mod' GOCACHE='C:\Temp\galaxy-build\gocache'
export PATH="/c/Temp/go/go/bin:$PATH"
WORK=/c/Temp/primitive-work; mkdir -p "$WORK"; cd "$WORK"

# 1. GOMODCACHE must be a NATIVE Windows path (C:\...) — MSYS /c/... is rejected as
#    "relative path" by the Go tool.
# 2. Go toolchain needs >= 1.26 for primitive's deps (x/image). Portable 1.27 lives at
#    C:\Temp\go\go\bin; if gone: curl -sL -o go.zip https://go.dev/dl/go1.27.3.windows-amd64.zip
#    and unzip to C:\Temp\go.
go install github.com/fogleman/primitive@latest

# 3. Feed primitive a plain PNG at a sane size:
python -c "from PIL import Image; Image.open(r'$IN').convert('RGB').resize((600,600)).save('in.png')"

# 4. CRITICAL: -o must contain %d (frame pattern). A bare name exits 4 silently.
#    -nth N writes one frame per N shapes (~40 frames for -n 120 -nth 3).
#    -m 1 = triangles; -r 300 = analysis size; -s 480 = output size.
rm -f f*.png
"$GOPATH/bin/primitive.exe" -i 'C:\Temp\primitive-work\in.png' -o 'C:\Temp\primitive-work\f%d.png' -n 120 -nth 3 -m 1 -r 300 -s 480

# 5. Assemble GIF with PIL: ONE shared 128-color palette, dithering OFF
#    (per-frame palettes flash; dithering shimmers). Hold the last frame ~2.6s.
python - "$OUT" <<'EOF'
from PIL import Image
import glob, re, sys
files = sorted(glob.glob('f*.png'), key=lambda f: int(re.search(r'(\d+)', f).group(1)))
rgb = [Image.open(f).convert('RGB') for f in files]
pal = rgb[-1].convert('P', palette=Image.ADAPTIVE, colors=128)
frames = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in rgb]
durs = [55]*len(frames); durs[-1] = 2600
frames[0].save(sys.argv[1], save_all=True, append_images=frames[1:], duration=durs, loop=0, optimize=True)
print('frames:', len(frames))
EOF
