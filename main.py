#!/usr/bin/env python3
"""make.fun cutest-picture-01 entry.

Copies the bundled artwork (art.png, next to this file) to
/output/entry.png. Standard library only, no network, fully
deterministic: the output bytes are exactly art.png, every run.

The copy is guarded: the source must be a real PNG, must fit the
bounty's 1 MiB artifact cap, and is published atomically (written to
a temp file in the output directory, then renamed into place) so a
partial entry.png can never be observed.
"""

import os
import tempfile
from pathlib import Path

MAX_ARTIFACT_BYTES = 1024 * 1024  # bounty cap: the artifact must be <= 1 MiB
MAX_DIMENSION = 1024  # bounty cap: neither side may exceed 1024 px
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def source_artwork() -> Path:
    """The artwork bundled next to this script, wherever it is run from."""
    return Path(__file__).resolve().parent / "art.png"


def output_dir() -> Path:
    """The harness output directory (/output), falling back to ./output."""
    try:
        out = Path("/output")
        out.mkdir(parents=True, exist_ok=True)
        return out
    except OSError:
        out = Path("output")
        out.mkdir(parents=True, exist_ok=True)
        return out


def png_dimensions(data: bytes) -> tuple[int, int]:
    """(width, height) from the PNG IHDR chunk, which directly follows
    the 8-byte signature: length (4), type 'IHDR' (4), then the width
    and height as big-endian uint32s."""
    if len(data) < 24 or data[12:16] != b"IHDR":
        raise ValueError("PNG has no IHDR chunk where one is required")
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    return width, height


def read_verified_png(src: Path) -> bytes:
    """Read the source artwork, refusing anything that is not a valid,
    in-cap PNG before a single output byte is written."""
    data = src.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError(f"{src} is not a PNG file (bad signature)")
    if len(data) > MAX_ARTIFACT_BYTES:
        raise ValueError(
            f"{src} is {len(data)} bytes, over the {MAX_ARTIFACT_BYTES}-byte cap"
        )
    width, height = png_dimensions(data)
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValueError(
            f"{src} is {width}x{height}, over the {MAX_DIMENSION}x{MAX_DIMENSION} cap"
        )
    return data


def publish(data: bytes, dest: Path) -> None:
    """Write data to dest atomically: temp file in the same directory,
    flushed to disk, then renamed over the destination."""
    fd, tmp_name = tempfile.mkstemp(dir=dest.parent, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, dest)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def main() -> None:
    src = source_artwork()
    data = read_verified_png(src)
    publish(data, output_dir() / "entry.png")


if __name__ == "__main__":
    main()
