"""Deterministically generate the Street Props mod icon from its approved artwork.

The approved JPG is stored with the source tree so rebuilding the icon never
depends on a temporary download path, network access, random state, or time.
Keep the complete original frame at its native resolution: decode to RGB and
write PNG without cropping, resizing, recoloring, or redrawing the artwork.

本模组由"Crzay津仔"提供美术与资金支持，"QiZhang"提供技术实现与制作。
发布署名仅为"Crzay津仔"，美术素材版权归 "Crzay津仔"所有，模组代码/配置版权归"QiZhang"所有。
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "icon_sources" / "jinzai_street_props_icon.jpg"
OUTPUT = ROOT / "common" / "src" / "main" / "resources" / "icon.png"
OUTPUT_SIZE = (1024, 1024)
EXPECTED_SOURCE_SHA256 = "8980681C247A286243BF20858F79D29955AC68583F75F34802DEC0C5AC265037"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> None:
    source_hash = sha256(SOURCE)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(
            f"Approved icon source hash mismatch: {source_hash} != {EXPECTED_SOURCE_SHA256}"
        )

    with Image.open(SOURCE) as source_image:
        if source_image.format != "JPEG" or source_image.size != OUTPUT_SIZE:
            raise RuntimeError(
                f"Unexpected approved artwork: format={source_image.format}, size={source_image.size}"
            )
        decoded = source_image.convert("RGB")

        # Copy into a fresh image so source EXIF/ICC metadata cannot enter the PNG.
        # Preserve every decoded pixel; the customer's artwork needs no fitting.
        icon = Image.new("RGB", decoded.size)
        icon.paste(decoded)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    icon.save(OUTPUT, format="PNG", optimize=False, compress_level=9)

    with Image.open(OUTPUT) as generated:
        if generated.size != OUTPUT_SIZE or generated.format != "PNG":
            raise RuntimeError(
                f"Unexpected generated icon: format={generated.format}, size={generated.size}"
            )
        if generated.convert("RGB").tobytes() != icon.tobytes():
            raise RuntimeError("Generated icon pixels differ from the approved artwork")

    print(f"Generated {OUTPUT} from {SOURCE}")
    print(f"Source SHA-256: {source_hash}")
    print(f"Output SHA-256: {sha256(OUTPUT)}")


if __name__ == "__main__":
    main()
