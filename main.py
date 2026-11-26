#!/usr/bin/env python3
"""Copy the rendered front page to the grader's output directory.

The entry image is rendered ahead of time by draw.py and shipped in this
repository as entry.png. This program only moves it into place: it checks
the file really is a complete, well-formed PNG (magic bytes, every chunk
with a valid CRC, an IEND chunk at the end), checks the gate limits (at
most 1 MiB, at most 1024 by 1024 pixels), refuses to copy a file onto
itself, writes the copy to $MAKEFUN_OUTPUT_DIR/entry.png (default
/output), and logs how many bytes were written. Standard library only,
no network, no clock.
"""

import os
import shutil
import struct
import sys
import zlib

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1048576
MAX_SIDE = 1024
SOURCE_NAME = "entry.png"
OUTPUT_NAME = "entry.png"


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def check_png(path):
    """Validate the whole PNG and return (width, height, size in bytes)."""
    with open(path, "rb") as handle:
        data = handle.read()

    if len(data) > MAX_BYTES:
        fail(f"{path} is {len(data)} bytes, over the 1 MiB limit")
    if data[: len(PNG_MAGIC)] != PNG_MAGIC:
        fail(f"{path} is not a PNG file (bad magic bytes)")

    pos = len(PNG_MAGIC)
    width = height = None
    saw_iend = False
    while pos + 8 <= len(data):
        length, kind = struct.unpack(">I4s", data[pos : pos + 8])
        end = pos + 12 + length
        if end > len(data):
            fail(f"{path} has a truncated {kind.decode('latin1')} chunk")
        chunk = data[pos + 4 : end - 4]
        stored_crc, = struct.unpack(">I", data[end - 4 : end])
        if zlib.crc32(chunk) & 0xFFFFFFFF != stored_crc:
            fail(f"{path} has a bad CRC in its {kind.decode('latin1')} chunk")
        if kind == b"IHDR":
            width, height = struct.unpack(">II", data[pos + 8 : pos + 16])
        if kind == b"IEND":
            saw_iend = True
            pos = end
            break
        pos = end

    if width is None:
        fail(f"{path} has no IHDR chunk")
    if width > MAX_SIDE or height > MAX_SIDE:
        fail(f"{path} is {width}x{height}, over the 1024x1024 limit")
    if not saw_iend:
        fail(f"{path} has no IEND chunk")
    if pos != len(data):
        fail(f"{path} has trailing bytes after its IEND chunk")
    return width, height, len(data)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    dest = os.path.join(out_dir, OUTPUT_NAME)

    if not os.path.isfile(source):
        fail(f"missing source image: {source}")

    width, height, size = check_png(source)

    if os.path.abspath(source) == os.path.abspath(dest):
        fail("source and destination are the same file; refusing to copy")

    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(source, dest)

    written = os.path.getsize(dest)
    if written != size:
        fail(f"copy is {written} bytes, expected {size}")
    print(f"wrote {dest} ({written} bytes, {width}x{height} PNG)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
