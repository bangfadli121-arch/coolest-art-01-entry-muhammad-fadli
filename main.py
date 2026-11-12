#!/usr/bin/env python3
"""Copy the submitted artwork to the make.fun output directory."""

import hashlib
import os
import shutil
import struct
import sys


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as source_file:
        for block in iter(lambda: source_file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    destination = os.path.join(output_dir, "entry.png")

    if not os.path.isfile(source):
        fail(f"source file is missing: {source}")

    try:
        os.makedirs(output_dir, exist_ok=True)
        shutil.copyfile(source, destination)
    except OSError as error:
        fail(f"could not copy artwork to {destination}: {error}")

    try:
        with open(destination, "rb") as copied_file:
            header = copied_file.read(24)
    except OSError as error:
        fail(f"could not read copied artwork {destination}: {error}")

    if not (header.startswith(b"\x89PNG\r\n\x1a\n") or header.startswith(b"\xff\xd8\xff")):
        fail(f"copied file has an unsupported format: {destination}")

    try:
        destination_size = os.path.getsize(destination)
    except OSError as error:
        fail(f"could not check copied artwork size: {error}")

    if destination_size > 1_048_576:
        fail(f"copied file exceeds the 1 MiB limit: {destination} ({destination_size} bytes)")

    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        width, height = struct.unpack(">II", header[16:24])
        if width > 1024 or height > 1024:
            fail(f"PNG dimensions exceed 1024 pixels: {width}x{height}")

    try:
        source_size = os.path.getsize(source)
        source_hash = sha256(source)
        destination_hash = sha256(destination)
    except OSError as error:
        fail(f"could not verify copied artwork: {error}")

    if source_size != destination_size or source_hash != destination_hash:
        fail(f"copied file does not match source: {destination}")

    print(f"Wrote {destination} ({destination_size} bytes, sha256 {destination_hash})")


if __name__ == "__main__":
    main()
