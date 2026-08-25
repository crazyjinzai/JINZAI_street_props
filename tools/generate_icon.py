"""Deterministically generate the Street Props mod icon from its approved artwork.

The approved JPG is stored with the source tree so rebuilding the icon never
depends on a temporary download path, network access, random state, or time.

本模组由"Crzay津仔"提供美术与资金支持，"QiZhang"提供技术实现与制作。
发布署名仅为"Crzay津仔"，美术素材版权归 "Crzay津仔"所有，模组代码/配置版权归"QiZhang"所有。
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "icon_sources" / "jinzai_street_props_icon.jpg"
OUTPUT = ROOT / "common" / "src" / "main" / "resources" / "icon.png"
OUTPUT_SIZE = (512, 512)
EXPECTED_SOURCE_SHA256 = "EEF5A636F22D54BF534727C0B67F562A5C2A6B29D29DC028C3E1232A8F0D27F5"


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
        upright = ImageOps.exif_transpose(source_image)
        fitted = ImageOps.fit(
            upright.convert("RGB"),
            OUTPUT_SIZE,
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )

        # Copy into a fresh image so source EXIF/ICC metadata cannot enter the PNG.
        icon = Image.new("RGB", OUTPUT_SIZE)
        icon.paste(fitted)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    icon.save(OUTPUT, format="PNG", optimize=False, compress_level=9)

    with Image.open(OUTPUT) as generated:
        if generated.size != OUTPUT_SIZE or generated.format != "PNG":
            raise RuntimeError(
                f"Unexpected generated icon: format={generated.format}, size={generated.size}"
            )

    print(f"Generated {OUTPUT} from {SOURCE}")
    print(f"Source SHA-256: {source_hash}")
    print(f"Output SHA-256: {sha256(OUTPUT)}")


if __name__ == "__main__":
    main()
