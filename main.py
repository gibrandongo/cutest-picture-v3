"""Cutest-picture entry: ship the bundled picture as /output/entry.png.

The picture lives in this repository as entry.jpg (JPEG bytes). The
contract names the output entry.png either way and tells PNG from JPEG by
the file's first bytes, so the program copies the bundled bytes verbatim.
Standard library only, no network, no randomness: every run writes the
same bytes.
"""

import os
import sys

MAX_BYTES = 1_048_576
JPEG_START = b"\xff\xd8"
JPEG_END = b"\xff\xd9"
CHUNK = 65_536


def bundled_path():
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(here, "entry.jpg")
    if os.path.isfile(candidate):
        return candidate
    fallback = os.path.join(os.getcwd(), "entry.jpg")
    if os.path.isfile(fallback):
        return fallback
    raise SystemExit(
        "bundled picture not found (looked in %s and %s)" % (candidate, fallback)
    )


def read_and_check(path):
    with open(path, "rb") as handle:
        head = handle.read(2)
        if head != JPEG_START:
            raise SystemExit("bundled picture is not a JPEG (bad start marker)")
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        if size > MAX_BYTES:
            raise SystemExit("bundled picture exceeds the 1 MiB cap")
        if size < 2:
            raise SystemExit("bundled picture is empty")
        handle.seek(size - 2)
        if handle.read(2) != JPEG_END:
            raise SystemExit("bundled picture is truncated (no JPEG end marker)")
        handle.seek(0)
        return handle.read()


def write_output(data):
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    tmp = target + ".part"
    with open(tmp, "wb") as handle:
        offset = 0
        while offset < len(data):
            offset += handle.write(data[offset:offset + CHUNK])
    os.replace(tmp, target)
    written = os.path.getsize(target)
    if written != len(data):
        raise SystemExit(
            "output size mismatch: wrote %d bytes, expected %d" % (written, len(data))
        )
    return target, len(data)


def main():
    data = read_and_check(bundled_path())
    target, size = write_output(data)
    print("wrote %s: %d bytes" % (target, size))


if __name__ == "__main__":
    sys.exit(main())
