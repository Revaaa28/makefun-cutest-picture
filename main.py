#!/usr/bin/env python3
"""make.fun cutest-picture-01 entry.

Copies the bundled artwork (art.png, next to this file) to
/output/entry.png. Standard library only, no network, fully
deterministic: the output bytes are exactly art.png, every run.
"""

import shutil
from pathlib import Path


def main() -> None:
    src = Path(__file__).resolve().parent / "art.png"
    try:
        out_dir = Path("/output")
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        out_dir = Path("output")
        out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, out_dir / "entry.png")


if __name__ == "__main__":
    main()
