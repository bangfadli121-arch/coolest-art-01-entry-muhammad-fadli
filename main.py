import hashlib
import os
import shutil
import sys


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as image_file:
        for chunk in iter(lambda: image_file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    destination = os.path.join(output_dir, "entry.png")

    try:
        if not os.path.isfile(source):
            raise FileNotFoundError(f"source image is missing: {source}")
        os.makedirs(output_dir, exist_ok=True)
        shutil.copyfile(source, destination)
        with open(destination, "rb") as image_file:
            signature = image_file.read(8)
        if signature != b"\x89PNG\r\n\x1a\n" and not signature.startswith(b"\xff\xd8\xff"):
            raise ValueError(
                "format validation failed: destination is not a PNG or JPEG image"
            )
        source_size = os.path.getsize(source)
        destination_size = os.path.getsize(destination)
        source_hash = sha256(source)
        destination_hash = sha256(destination)
        if source_size != destination_size:
            raise ValueError(
                f"copy verification failed: size differs "
                f"(source {source_size} bytes, destination {destination_size} bytes)"
            )
        if source_hash != destination_hash:
            raise ValueError(
                "copy verification failed: SHA-256 differs "
                f"(source {source_hash}, destination {destination_hash})"
            )
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Wrote {destination} ({source_size} bytes, sha256 {destination_hash})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
