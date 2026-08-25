"""Verify generated source resources and optional Fabric/Forge release JARs.

本模组由"Crzay津仔"提供美术与资金支持，"QiZhang"提供技术实现与制作。
发布署名仅为"Crzay津仔"，美术素材版权归 "Crzay津仔"所有，模组代码/配置版权归"QiZhang"所有。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MOD_ID = "jinzai_street_props"
VERSION = "1.0.0"
FABRIC_ARCHITECTURY_RANGE = ">=9.0.6 <10.0.0"
FORGE_ARCHITECTURY_RANGE = "[9.0.6,10.0.0)"
RESOURCES = ROOT / "common" / "src" / "main" / "resources"
ASSETS = RESOURCES / "assets" / MOD_ID
DATA = RESOURCES / "data" / MOD_ID
CATALOG_ENTRY = f"assets/{MOD_ID}/block_catalog.json"
LOCALES = (
    "zh_cn", "en_us", "ar_sa", "de_de", "es_es", "fr_fr", "hi_in",
    "id_id", "ja_jp", "ko_kr", "pt_br", "ru_ru", "tr_tr",
)
EXPECTED_CATEGORY_COUNTS = Counter({"street_lights": 82, "road_signs": 30, "bus_stops": 7})
EXPECTED_KIND_COUNTS = Counter({
    "light_head": 31, "side_branch": 30, "top_assembly": 3,
    "street_pole": 18, "sign_pole": 7, "decoration": 30,
})
EXPECTED_PRECISE = {
    "jinzai_street_pole_1", "jinzai_street_pole_1a", "jinzai_street_pole_1b",
    "jinzai_street_pole_1c", "jinzai_street_pole_1d", "jinzai_street_pole_2",
    "jinzai_street_pole_2a", "jinzai_street_pole_2b", "jinzai_street_pole_2c",
    "jinzai_street_pole_2d", "jinzai_street_pole_3", "jinzai_street_pole_3a",
    "jinzai_street_pole_3b", "jinzai_street_pole_3c", "jinzai_street_pole_3d",
    "jinzai_street_pole_4", "jinzai_street_pole_4a", "jinzai_street_pole_5",
    "signpost_pole_1", "signpost_pole_2", "signpost_pole_3", "signpost_pole_4",
    "signpost_pole_5", "signpost_pole_6", "signpost_pole_7",
}
EXPECTED_SIDE = {
    "jinzai_street_post_1", "jinzai_street_post_1a", "jinzai_street_post_1b",
    "jinzai_street_post_1c", "jinzai_street_post_1d", "jinzai_street_post_1e",
    "jinzai_street_post_2", "jinzai_street_post_2a", "jinzai_street_post_3",
    "jinzai_street_post_3a", "jinzai_street_post_3b", "jinzai_street_post_3c",
    "jinzai_street_post_4", "jinzai_street_post_4a", "jinzai_street_post_4b",
    "jinzai_street_post_4c", "jinzai_street_post_5", "jinzai_street_post_5a",
    "jinzai_street_post_6", "jinzai_street_post_7", "jinzai_street_post_7a",
    "jinzai_street_post_7b", "jinzai_street_post_8", "jinzai_street_post_9",
    "jinzai_street_post_9a", "jinzai_street_post_9b", "jinzai_street_post_10",
    "jinzai_street_post_12", "jinzai_street_post_13", "jinzai_street_post_13a",
}
EXPECTED_TOP = {"jinzai_street_post_11", "jinzai_street_post_14", "jinzai_street_post_14a"}
COPYRIGHT_SENTENCE = (
    '发布署名仅为"Crzay津仔"，美术素材版权归 "Crzay津仔"所有，'
    '模组代码/配置版权归"QiZhang"所有。'
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def forge_dependency_block(metadata: str, dependency_mod_id: str) -> str:
    blocks = re.findall(
        rf"\[\[dependencies\.{re.escape(MOD_ID)}\]\](.*?)(?=\n\[\[|\Z)",
        metadata,
        flags=re.DOTALL,
    )
    matches = [
        block for block in blocks
        if re.search(rf'modId\s*=\s*"{re.escape(dependency_mod_id)}"', block)
    ]
    assert len(matches) == 1, f"Expected one {dependency_mod_id} dependency block"
    return matches[0]


def source_ids() -> set[str]:
    ids: set[str] = set()
    for folder in ("公交站", "路灯杆与支架", "路牌"):
        directory = ROOT / folder
        models = {path.stem for path in directory.glob("*.bbmodel")}
        textures = {path.stem for path in directory.glob("*.png")}
        assert models == textures, f"Unpaired source files in {folder}"
        assert not ids & models, f"Duplicate source stems across folders: {ids & models}"
        ids.update(models)
    assert len(ids) == 119, f"Expected 119 source pairs, found {len(ids)}"
    assert "jinzai_street_post_5b" not in ids, "Deprecated post_5b is still present"
    assert "jinzai_street_post_4c" in ids, "Corrected post_4c is missing"
    return ids


def validate_catalog(document: Any, expected_ids: set[str]) -> list[dict[str, Any]]:
    assert isinstance(document, dict) and set(document) == {"schema", "blocks"}
    assert document["schema"] == 1
    blocks = document["blocks"]
    assert isinstance(blocks, list) and len(blocks) == 119
    fields = {
        "id", "category", "kind", "placement", "collision_mode", "light_level",
        "source_folder", "source_stem", "collision_boxes",
    }
    assert all(isinstance(block, dict) and set(block) == fields for block in blocks)
    ids = [block["id"] for block in blocks]
    assert len(ids) == len(set(ids)) and set(ids) == expected_ids
    assert Counter(block["category"] for block in blocks) == EXPECTED_CATEGORY_COUNTS
    assert Counter(block["kind"] for block in blocks) == EXPECTED_KIND_COUNTS

    precise = {block["id"] for block in blocks if block["collision_mode"] == "detailed"}
    bounding = {block["id"] for block in blocks if block["collision_mode"] == "bounding"}
    side = {block["id"] for block in blocks if block["placement"] == "side_only"}
    top = {block["id"] for block in blocks if block["placement"] == "top_only"}
    lit = {block["id"] for block in blocks if block["light_level"] == 15}
    assert precise == EXPECTED_PRECISE and len(bounding) == 94
    assert side == EXPECTED_SIDE and top == EXPECTED_TOP
    assert len(lit) == 31 and all(identifier.startswith("jinzai_street_light_") for identifier in lit)
    assert all(block["light_level"] in (0, 15) for block in blocks)
    assert all(len(block["collision_boxes"]) == 1 for block in blocks if block["id"] in bounding)
    assert sum(len(block["collision_boxes"]) for block in blocks) == 257
    for block in blocks:
        boxes = block["collision_boxes"]
        assert isinstance(boxes, list) and boxes
        for box in boxes:
            assert isinstance(box, list) and len(box) == 6
            assert all(isinstance(value, (int, float)) for value in box)
            assert box[0] < box[3] and box[1] < box[4] and box[2] < box[5]
    return blocks


def validate_source_resources() -> None:
    expected_ids = source_ids()
    blocks = validate_catalog(load_json(ASSETS / "block_catalog.json"), expected_ids)
    by_id = {block["id"]: block for block in blocks}

    expected_resource_dirs = {
        ASSETS / "models" / "block": ".json",
        ASSETS / "models" / "item": ".json",
        ASSETS / "blockstates": ".json",
        ASSETS / "textures" / "block": ".png",
        DATA / "loot_tables" / "blocks": ".json",
    }
    for directory, suffix in expected_resource_dirs.items():
        actual = {path.stem for path in directory.glob(f"*{suffix}")}
        assert actual == expected_ids, f"Resource inventory mismatch: {directory}"

    raw_elements = visible_elements = 0
    for identifier, entry in by_id.items():
        source_model = ROOT / entry["source_folder"] / f"{entry['source_stem']}.bbmodel"
        source_texture = ROOT / entry["source_folder"] / f"{entry['source_stem']}.png"
        generated_texture = ASSETS / "textures" / "block" / f"{identifier}.png"
        source = load_json(source_model)
        generated_model = load_json(ASSETS / "models" / "block" / f"{identifier}.json")
        raw_elements += len(source.get("elements", []))
        visible = [
            element for element in source.get("elements", [])
            if element.get("type", "cube") == "cube"
            and element.get("export", True) is not False
            and element.get("visibility") is not False
        ]
        visible_elements += len(visible)
        assert len(generated_model["elements"]) == len(visible)
        assert sha256(source_texture) == sha256(generated_texture)
        assert load_json(ASSETS / "models" / "item" / f"{identifier}.json") == {
            "parent": f"{MOD_ID}:block/{identifier}"
        }
        state = load_json(ASSETS / "blockstates" / f"{identifier}.json")
        assert set(state["variants"]) == {
            "facing=north", "facing=east", "facing=south", "facing=west"
        }
        loot = load_json(DATA / "loot_tables" / "blocks" / f"{identifier}.json")
        assert loot["pools"][0]["entries"][0]["name"] == f"{MOD_ID}:{identifier}"
    assert (raw_elements, visible_elements) == (1015, 1014)

    expected_keys: set[str] | None = None
    for locale in LOCALES:
        language = load_json(ASSETS / "lang" / f"{locale}.json")
        assert isinstance(language, dict) and len(language) == 122
        assert all(isinstance(value, str) and value.strip() for value in language.values())
        assert not any(key.startswith("tooltip.") for key in language)
        keys = set(language)
        expected_keys = keys if expected_keys is None else expected_keys
        assert keys == expected_keys
    assert len(list((ASSETS / "lang").glob("*.json"))) == 13

    pack = load_json(RESOURCES / "pack.mcmeta")
    assert pack["pack"]["pack_format"] == 15
    icon = (RESOURCES / "icon.png").read_bytes()
    assert icon.startswith(b"\x89PNG\r\n\x1a\n")
    assert struct.unpack(">II", icon[16:24]) == (512, 512)

    java_files = list(ROOT.glob("**/src/main/java/**/*.java"))
    assert len(java_files) == 7
    for path in java_files:
        text = path.read_text(encoding="utf-8")
        assert COPYRIGHT_SENTENCE in text, f"Missing current copyright header: {path}"
        assert "双方联合署名发布" not in text
        assert "tooltip." not in text
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert readme.index("## English") < readme.index("## 中文")
    assert COPYRIGHT_SENTENCE in readme and "双方联合署名发布" not in readme
    assert "119" in readme and "94" in readme and "13" in readme
    assert all(version in readme for version in ("9.0.6", "10.0.0", "9.2.14"))

    fabric_metadata = load_json(ROOT / "fabric" / "src" / "main" / "resources" / "fabric.mod.json")
    assert fabric_metadata["depends"]["architectury"] == FABRIC_ARCHITECTURY_RANGE
    forge_metadata = (
        ROOT / "forge" / "src" / "main" / "resources" / "META-INF" / "mods.toml"
    ).read_text(encoding="utf-8")
    architectury_block = forge_dependency_block(forge_metadata, "architectury")
    assert f'versionRange = "{FORGE_ARCHITECTURY_RANGE}"' in architectury_block


def archive_json(archive: zipfile.ZipFile, name: str) -> Any:
    return json.loads(archive.read(name).decode("utf-8"))


def validate_jar(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)), f"Duplicate ZIP entries in {path}"
        files = {name for name in names if not name.endswith("/")}
        expected_ids = source_ids()
        validate_catalog(archive_json(archive, CATALOG_ENTRY), expected_ids)
        assert "icon.png" in files and struct.unpack(">II", archive.read("icon.png")[16:24]) == (512, 512)
        for identifier in expected_ids:
            for entry in (
                f"assets/{MOD_ID}/models/block/{identifier}.json",
                f"assets/{MOD_ID}/models/item/{identifier}.json",
                f"assets/{MOD_ID}/blockstates/{identifier}.json",
                f"assets/{MOD_ID}/textures/block/{identifier}.png",
                f"data/{MOD_ID}/loot_tables/blocks/{identifier}.json",
            ):
                assert entry in files, f"Missing JAR resource: {entry}"
        for locale in LOCALES:
            language = archive_json(archive, f"assets/{MOD_ID}/lang/{locale}.json")
            assert len(language) == 122 and not any(key.startswith("tooltip.") for key in language)

        class_entries = [name for name in files if name.endswith(".class")]
        own_classes = [name for name in class_entries if name.startswith("cn/crazyjinzai/streetprops/")]
        assert own_classes, f"No mod classes in {path}"
        for name in own_classes:
            data = archive.read(name)
            assert data[:4] == b"\xca\xfe\xba\xbe"
            assert struct.unpack(">H", data[6:8])[0] == 61, f"Not Java 17 bytecode: {name}"
            assert b"tooltip." not in data, f"Tooltip constant found in {name}"

        if "Fabric" in path.name:
            metadata = archive_json(archive, "fabric.mod.json")
            assert metadata["id"] == MOD_ID and metadata["version"] == VERSION
            assert metadata["authors"] == ["Crzay津仔"]
            assert metadata["depends"]["architectury"] == FABRIC_ARCHITECTURY_RANGE
            assert "fabric-api" in metadata["depends"]
            assert "JINZAI Street Props" in metadata["description"]
            assert metadata["description"].index("JINZAI Street Props") < metadata["description"].index("津仔的街道设施")
        elif "Forge" in path.name:
            text = archive.read("META-INF/mods.toml").decode("utf-8")
            assert re.search(r'modId\s*=\s*"jinzai_street_props"', text)
            assert re.search(r'version\s*=\s*"1\.0\.0"', text)
            assert re.search(r'authors\s*=\s*"Crzay津仔"', text)
            assert 'modId = "architectury"' in text
            architectury_block = forge_dependency_block(text, "architectury")
            assert f'versionRange = "{FORGE_ARCHITECTURY_RANGE}"' in architectury_block
            assert text.index("JINZAI Street Props") < text.index("津仔的街道设施")
        else:
            raise AssertionError(f"Cannot infer loader from filename: {path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("jars", nargs="*", type=Path)
    arguments = parser.parse_args()
    validate_source_resources()
    for jar in arguments.jars:
        assert jar.is_file(), f"Missing JAR: {jar}"
        validate_jar(jar)
    print(
        "VERIFY_PASS: source resources"
        + (f" and {len(arguments.jars)} release JAR(s)" if arguments.jars else "")
    )


if __name__ == "__main__":
    main()
