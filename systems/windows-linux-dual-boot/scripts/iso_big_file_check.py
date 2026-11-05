#!/usr/bin/env python3
"""List the largest files inside an ISO9660 image and flag any over FAT32's 4 GiB limit.

Usage:
    python iso_big_file_check.py /path/to/image.iso

Why: Rufus' "ISO Image mode" copies the ISO's *files* onto a FAT32 stick, which cannot hold a
member larger than 4 GiB, so an oversized member forces "DD Image mode" (a bit-for-bit write
whose result Windows can no longer browse). Check instead of guessing.

Caveat: ISO9660 stores file size in a 32-bit little-endian field, so a member over 4 GiB wraps.
The script therefore also compares the summed size of what it parsed against the image size and
reports a large shortfall as a likely wrapped (oversized) member.
"""
import os
import struct
import sys

LIMIT = 4 * 1024 ** 3
BLOCK = 2048


def read_dir(fh, extent, length):
    """Return (name, extent, size, flags) for each record in a directory extent."""
    fh.seek(extent * BLOCK)
    data = fh.read(length)
    out, i = [], 0
    while i < len(data):
        reclen = data[i]
        if reclen == 0:                      # padding to the next block boundary
            i = (i // BLOCK + 1) * BLOCK
            if i >= len(data):
                break
            continue
        rec = data[i:i + reclen]
        out.append((
            rec[33:33 + rec[32]].decode("ascii", "replace"),
            struct.unpack("<I", rec[2:6])[0],     # extent
            struct.unpack("<I", rec[10:14])[0],   # data length
            rec[25],                             # flags; bit 1 set = directory
        ))
        i += reclen
    return out


def walk(fh, extent, length, prefix="", depth=0, acc=None):
    acc = [] if acc is None else acc
    if depth > 10:
        return acc
    for name, ext, size, flags in read_dir(fh, extent, length):
        if name in ("\x00", "\x01"):
            continue
        path = prefix + name.split(";")[0]
        acc.append((path, size, bool(flags & 2)))
        if flags & 2:
            walk(fh, ext, size, path + "/", depth + 1, acc)
    return acc


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    with open(path, "rb") as fh:
        fh.seek(16 * BLOCK)                  # primary volume descriptor
        pvd = fh.read(BLOCK)
        if not pvd or pvd[0] != 1:
            sys.exit("no ISO9660 primary volume descriptor at sector 16 (UDF-only image?)")
        root = pvd[156:190]
        entries = walk(fh, struct.unpack("<I", root[2:6])[0], struct.unpack("<I", root[10:14])[0])

    files = [(p, s) for p, s, is_dir in entries if not is_dir]
    total = sum(s for _, s in files)
    image = os.path.getsize(path)

    print(f"image: {image / 1024 ** 3:.2f} GiB, parsed {len(files)} files totalling {total / 1024 ** 3:.2f} GiB")
    for p, s in sorted(files, key=lambda x: -x[1])[:5]:
        print(f"  largest: {s / 1024 ** 3:7.2f} GiB  {p}")

    over = [(p, s) for p, s in files if s > LIMIT]
    if over:
        print("\nOVER FAT32'S 4 GiB LIMIT -> use Rufus DD Image mode:")
        for p, s in over:
            print(f"  {s / 1024 ** 3:.2f} GiB  {p}")
    elif total < image * 0.9:
        print("\nUNEXPLAINED SHORTFALL: parsed content is much smaller than the image, which usually")
        print("means a size field wrapped - assume a member over 4 GiB exists and use DD Image mode.")
    else:
        print("\nno member exceeds 4 GiB -> Rufus ISO Image mode is safe")


if __name__ == "__main__":
    main()
