"""Verify generated source resources and optional Fabric/Forge release JARs.

本模组由"Crzay津仔"提供美术与资金支持，"QiZhang"提供技术实现与制作。
发布署名仅为"Crzay津仔"，美术素材版权归 "Crzay津仔"所有，模组代码/配置版权归"QiZhang"所有。
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
import struct
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MOD_ID = "jinzai_street_props"
VERSION = "1.1.2"
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
EXPECTED_CATEGORY_COUNTS = Counter({
    "street_lights": 117, "road_signs": 30, "bus_stops": 20, "municipal": 6, "vehicles": 40,
})
EXPECTED_KIND_COUNTS = Counter({
    "light_head": 41, "side_branch": 46, "top_assembly": 3,
    "street_pole": 27, "sign_pole": 7, "decoration": 89,
})
GUI_FIT_IDS = frozenset({
    "jinzai_street_light_14", "jinzai_street_post_14a", "jinzai_street_pole_6",
    "signpost_12a", "jinzai_bus_stop_1", "jinzai_bus_stop_2",
    "jinzai_bus_stop_3", "jinzai_bus_stop_4", "jinzai_bus_stop_5",
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
EXPECTED_SIDE.update(f"jinzai_street_post_{suffix}" for suffix in (
    "15", "16", "17", "18", "19", "b1", "b2", "b3", "b3b", "b4",
    "b5", "b6", "b7", "b8", "b9", "b10",
))
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
    for folder in ("公交站", "路灯杆与支架", "路牌", "市政设施", "汽车载具"):
        directory = ROOT / folder
        models = {path.stem for path in directory.glob("*.bbmodel")}
        textures = {path.stem for path in directory.glob("*.png")}
        assert models == textures, f"Unpaired source files in {folder}"
        assert not ids & models, f"Duplicate source stems across folders: {ids & models}"
        ids.update(models)
    assert len(ids) == 213, f"Expected 213 source pairs, found {len(ids)}"
    assert "jinzai_street_post_b11" not in ids, "Unnamed, unapproved b11 must remain excluded"
    assert "jinzai_street_post_5b" not in ids, "Deprecated post_5b is still present"
    assert "jinzai_street_post_4c" in ids, "Corrected post_4c is missing"
    return ids


def validate_catalog(document: Any, expected_ids: set[str]) -> list[dict[str, Any]]:
    assert isinstance(document, dict) and set(document) == {"schema", "blocks"}
    assert document["schema"] == 1
    blocks = document["blocks"]
    assert isinstance(blocks, list) and len(blocks) == 213
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
    assert precise == EXPECTED_PRECISE and len(bounding) == 188
    assert side == EXPECTED_SIDE and top == EXPECTED_TOP
    assert len(lit) == 41 and all(identifier.startswith("jinzai_street_light_") for identifier in lit)
    assert all(block["light_level"] in (0, 15) for block in blocks)
    assert all(len(block["collision_boxes"]) == 1 for block in blocks if block["id"] in bounding)
    assert sum(len(block["collision_boxes"]) for block in blocks) == 351
    for block in blocks:
        boxes = block["collision_boxes"]
        assert isinstance(boxes, list) and boxes
        for box in boxes:
            assert isinstance(box, list) and len(box) == 6
            assert all(isinstance(value, (int, float)) for value in box)
            assert box[0] < box[3] and box[1] < box[4] and box[2] < box[5]
    return blocks


def placed_model_bounds(model: dict[str, Any]) -> list[float]:
    """Measure exported geometry independently of the collision generator."""
    points = []
    for element in model["elements"]:
        assert all(-16 <= value <= 32 for value in element["from"] + element["to"])
        for coordinates in itertools.product(*zip(element["from"], element["to"])):
            point = list(coordinates)
            rotation = element.get("rotation")
            if rotation:
                assert not rotation.get("rescale", False), "Rescaled geometry needs explicit bounds support"
                first, second = {"x": (1, 2), "y": (2, 0), "z": (0, 1)}[rotation["axis"]]
                origin = rotation["origin"]
                a, b = point[first] - origin[first], point[second] - origin[second]
                angle = math.radians(rotation["angle"])
                point[first] = origin[first] + a * math.cos(angle) - b * math.sin(angle)
                point[second] = origin[second] + a * math.sin(angle) + b * math.cos(angle)
            points.append(point)
    assert points
    return ([min(point[axis] for point in points) for axis in range(3)]
            + [max(point[axis] for point in points) for axis in range(3)])


def gui_projected_bounds(model: dict[str, Any]) -> list[float]:
    """Conservative GUI pixel bounds using Minecraft's XYZ quaternion order."""
    def rotate(point: list[float], axis: str, degrees: float, origin: list[float]) -> list[float]:
        first, second = {"x": (1, 2), "y": (2, 0), "z": (0, 1)}[axis]
        a, b = point[first] - origin[first], point[second] - origin[second]
        angle = math.radians(degrees)
        rotated = point.copy()
        rotated[first] = origin[first] + a * math.cos(angle) - b * math.sin(angle)
        rotated[second] = origin[second] + a * math.sin(angle) + b * math.cos(angle)
        return rotated

    gui = model["display"]["gui"]
    scale = gui.get("scale", [1, 1, 1])
    rotation = gui.get("rotation", [0, 0, 0])
    translation = gui.get("translation", [0, 0, 0])
    points = []
    for element in model["elements"]:
        for coordinates in itertools.product(*zip(element["from"], element["to"])):
            point = list(coordinates)
            if element_rotation := element.get("rotation"):
                assert not element_rotation.get("rescale", False)
                point = rotate(point, element_rotation["axis"], element_rotation["angle"], element_rotation["origin"])
            point = [(point[axis] - 8) * scale[axis] for axis in range(3)]
            for axis, degrees in reversed(list(zip("xyz", rotation))):
                point = rotate(point, axis, degrees, [0, 0, 0])
            points.append([point[axis] + translation[axis] for axis in range(3)])
    return ([min(point[axis] for point in points) for axis in range(2)]
            + [max(point[axis] for point in points) for axis in range(2)])


def validate_legacy_compatibility(legacy_root: Path) -> None:
    old_assets = legacy_root / "assets" / MOD_ID
    old_blocks = load_json(old_assets / "block_catalog.json")["blocks"]
    current = {entry["id"]: entry for entry in load_json(ASSETS / "block_catalog.json")["blocks"]}
    assert len(old_blocks) == 119
    changed_gui = {"signpost_5", "signpost_6", "signpost_7"} | GUI_FIT_IDS
    for entry in old_blocks:
        identifier = entry["id"]
        assert current[identifier] == entry, f"Legacy registration/collision changed: {identifier}"
        old_model = load_json(old_assets / "models" / "block" / f"{identifier}.json")
        new_model = load_json(ASSETS / "models" / "block" / f"{identifier}.json")
        if identifier in changed_gui:
            new_gui = new_model.get("display", {}).pop("gui", None)
            old_model.get("display", {}).pop("gui", None)
            assert new_gui is not None, f"Missing requested GUI transform: {identifier}"
        assert old_model == new_model, f"Legacy world model changed: {identifier}"
        for subdirectory, extension in (("models/item", ".json"), ("blockstates", ".json"),
                                       ("textures/block", ".png")):
            relative = Path(subdirectory) / f"{identifier}{extension}"
            assert (old_assets / relative).read_bytes() == (ASSETS / relative).read_bytes(), str(relative)
        loot_relative = Path("data") / MOD_ID / "loot_tables" / "blocks" / f"{identifier}.json"
        assert (legacy_root / loot_relative).read_bytes() == (RESOURCES / loot_relative).read_bytes()
    for locale in LOCALES:
        original = load_json(old_assets / "lang" / f"{locale}.json")
        current_language = load_json(ASSETS / "lang" / f"{locale}.json")
        assert all(current_language[key] == value for key, value in original.items()), locale
    print("LEGACY_PASS: all 119 IDs, collisions, world geometry, textures and names retained; only the 11 allowed legacy GUI transforms may differ")


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
        if identifier in GUI_FIT_IDS:
            source_gui = source.get("display", {}).get("gui", {})
            fitted_gui = generated_model["display"]["gui"]
            assert fitted_gui["rotation"] == source_gui.get("rotation", [0, 0, 0])
            assert fitted_gui["translation"][2] == source_gui.get("translation", [0, 0, 0])[2]
            old_scale = source_gui.get("scale", [1, 1, 1])
            factors = [actual / old for actual, old in zip(fitted_gui["scale"], old_scale)]
            assert 0 < factors[0] < 1 and max(factors) - min(factors) < 1e-7
            gui_bounds = gui_projected_bounds(generated_model)
            assert max(gui_bounds[2] - gui_bounds[0], gui_bounds[3] - gui_bounds[1]) <= 16.00001
            assert abs(gui_bounds[0] + gui_bounds[2]) < 1e-5
            assert abs(gui_bounds[1] + gui_bounds[3]) < 1e-5
            assert {view: transform for view, transform in generated_model["display"].items() if view != "gui"} == {
                view: transform for view, transform in source.get("display", {}).items() if view != "gui"
            }, f"Non-GUI display changed: {identifier}"
        if identifier == "jinzai_vehicle_sets_7c":
            reference = load_json(ROOT / "汽车载具" / "jinzai_vehicle_sets_1c.bbmodel")
            assert generated_model["display"]["gui"] == reference["display"]["gui"], (
                "Police pickup GUI must match the other pickup variants' inventory transform"
            )
        raw_elements += len(source.get("elements", []))
        visible = [
            element for element in source.get("elements", [])
            if element.get("type", "cube") == "cube"
            and element.get("export", True) is not False
            and element.get("visibility") is not False
        ]
        visible_elements += len(visible)
        assert len(generated_model["elements"]) == len(visible)
        if entry["collision_mode"] == "bounding":
            expected_box = placed_model_bounds(generated_model)
            assert all(abs(actual - expected) < 1e-5 for actual, expected in
                       zip(entry["collision_boxes"][0], expected_box)), identifier
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
    assert (raw_elements, visible_elements) == (4295, 4293)

    expected_keys: set[str] | None = None
    for locale in LOCALES:
        language = load_json(ASSETS / "lang" / f"{locale}.json")
        assert isinstance(language, dict) and len(language) == 218
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
    assert "213" in readme and "94" in readme and "13" in readme
    assert all(version in readme for version in ("9.0.6", "10.0.0", "9.2.14"))

    fabric_metadata = load_json(ROOT / "fabric" / "src" / "main" / "resources" / "fabric.mod.json")
    assert fabric_metadata["license"] == "MIT"
    assert fabric_metadata["depends"]["architectury"] == FABRIC_ARCHITECTURY_RANGE
    forge_metadata = (
        ROOT / "forge" / "src" / "main" / "resources" / "META-INF" / "mods.toml"
    ).read_text(encoding="utf-8")
    assert 'license = "MIT"' in forge_metadata
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
            assert len(language) == 218 and not any(key.startswith("tooltip.") for key in language)
        assert archive.read("LICENSE") == (ROOT / "LICENSE").read_bytes()

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
            assert metadata["license"] == "MIT"
            assert metadata["authors"] == ["Crzay津仔"]
            assert metadata["depends"]["architectury"] == FABRIC_ARCHITECTURY_RANGE
            assert "fabric-api" in metadata["depends"]
            assert "JINZAI Street Props" in metadata["description"]
            assert metadata["description"].index("JINZAI Street Props") < metadata["description"].index("津仔的街道设施")
        elif "Forge" in path.name:
            text = archive.read("META-INF/mods.toml").decode("utf-8")
            assert re.search(r'modId\s*=\s*"jinzai_street_props"', text)
            assert re.search(rf'version\s*=\s*"{re.escape(VERSION)}"', text)
            assert 'license = "MIT"' in text
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
    parser.add_argument("--legacy-resources", type=Path,
                        help="Optional 1.0.0 common/src/main/resources directory for compatibility checks")
    arguments = parser.parse_args()
    validate_source_resources()
    if arguments.legacy_resources:
        validate_legacy_compatibility(arguments.legacy_resources)
    for jar in arguments.jars:
        assert jar.is_file(), f"Missing JAR: {jar}"
        validate_jar(jar)
    print(
        "VERIFY_PASS: source resources"
        + (f" and {len(arguments.jars)} release JAR(s)" if arguments.jars else "")
    )


if __name__ == "__main__":
    main()
