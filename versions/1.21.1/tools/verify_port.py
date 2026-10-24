"""Verify final Street Props 1.21.1 JARs against the shared source resources.

Run with Python 3.11 or later. This is an archive/source check, not a client
rendering or gameplay test. Art/funding: Crzay津仔. Implementation: QiZhang. MIT.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import struct
import tomllib
import zipfile

PORT = Path(__file__).resolve().parents[1]
REPOSITORY = PORT.parents[1]
SHARED = REPOSITORY / "common/src/main/resources"
MOD = "jinzai_street_props"
VERSION = "1.1.4"
EXPECTED_CATEGORIES = {
    "street_lights": 149, "road_signs": 30, "bus_stops": 21,
    "municipal": 71, "vehicles": 99,
}
EXPECTED_LOCALES = {
    "ar_sa", "de_de", "en_us", "es_es", "fr_fr", "hi_in", "id_id",
    "ja_jp", "ko_kr", "pt_br", "ru_ru", "tr_tr", "zh_cn",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def adapted_path(relative: str) -> str:
    """Apply only the Minecraft 1.21 data-registry folder rename."""
    parts = relative.split("/")
    if parts[0] != "data" or len(parts) < 3:
        return relative
    singular = {
        "advancements": "advancement", "functions": "function",
        "item_modifiers": "item_modifier", "loot_tables": "loot_table",
        "predicates": "predicate", "recipes": "recipe", "structures": "structure",
    }
    tag_names = {
        "blocks": "block", "items": "item", "fluids": "fluid",
        "entity_types": "entity_type", "game_events": "game_event", "functions": "function",
    }
    if parts[2] in singular:
        parts[2] = singular[parts[2]]
    elif parts[2] == "tags" and len(parts) > 3 and parts[3] in tag_names:
        parts[3] = tag_names[parts[3]]
    return "/".join(parts)


def verify_metadata(jar: zipfile.ZipFile, entries: set[str]) -> str:
    has_fabric = "fabric.mod.json" in entries
    has_neo = "META-INF/neoforge.mods.toml" in entries
    require(has_fabric != has_neo, "Exactly one loader descriptor is required")
    require("META-INF/mods.toml" not in entries, "Legacy Forge descriptor in 1.21.1 JAR")
    if has_fabric:
        metadata = json.loads(jar.read("fabric.mod.json"))
        require(metadata["id"] == MOD and metadata["version"] == VERSION, "Fabric mod id/version")
        require(metadata["license"] == "MIT", "Fabric license")
        require(metadata["authors"] == ["Crzay津仔"], "Fabric authors")
        require(metadata["icon"] == "icon.png" and metadata["environment"] == "*", "Fabric icon/environment")
        require(metadata["depends"] == {
            "fabricloader": ">=0.17.2", "minecraft": "1.21.1", "java": ">=21",
            "fabric-api": ">=0.116.15+1.21.1", "architectury": ">=13.0.8 <14.0.0",
        }, "Fabric dependencies")
        require(metadata["entrypoints"] == {
            "main": ["cn.crazyjinzai.streetprops.fabric.JinzaiStreetPropsFabric"],
            "client": ["cn.crazyjinzai.streetprops.fabric.JinzaiStreetPropsFabricClient"],
        }, "Fabric entrypoints")
        return "Fabric"
    metadata = tomllib.loads(jar.read("META-INF/neoforge.mods.toml").decode("utf-8"))
    require(metadata["modLoader"] == "javafml" and metadata["loaderVersion"] == "[4,)", "NeoForge loader")
    require(metadata["license"] == "MIT", "NeoForge license")
    require(len(metadata["mods"]) == 1, "Unexpected NeoForge mod entry")
    mod = metadata["mods"][0]
    require(mod["modId"] == MOD and mod["version"] == VERSION, "NeoForge mod id/version")
    require(mod["authors"] == "Crzay津仔" and mod["logoFile"] == "icon.png", "NeoForge authors/icon")
    deps = metadata["dependencies"][MOD]
    require(len(deps) == 3, "Unexpected NeoForge dependency count")
    dependencies = {dependency["modId"]: dependency for dependency in deps}
    expected = {
        "minecraft": ("[1.21.1,1.21.2)", "NONE"),
        "neoforge": ("[21.1.248,21.2)", "NONE"),
        "architectury": ("[13.0.8,14.0.0)", "AFTER"),
    }
    require(set(dependencies) == set(expected), "NeoForge dependency ids")
    for identifier, (version_range, ordering) in expected.items():
        dependency = dependencies[identifier]
        require(dependency["versionRange"] == version_range, f"NeoForge dependency range: {identifier}")
        require(dependency["ordering"] == ordering and dependency["side"] == "BOTH"
                and dependency["type"] == "required", f"NeoForge dependency flags: {identifier}")
    require(metadata["features"][MOD]["javaVersion"] == "[21,)", "NeoForge Java requirement")
    return "NeoForge"


def verify(path: Path) -> dict:
    path = path.resolve()
    shared_files = sorted(source for source in SHARED.rglob("*") if source.is_file())
    require(bool(shared_files), "Shared source resources are unavailable")
    expected_resources = {adapted_path(source.relative_to(SHARED).as_posix()) for source in shared_files}
    with zipfile.ZipFile(path) as jar:
        require(jar.testzip() is None, "Corrupt archive CRC")
        names = jar.namelist()
        require(len(names) == len(set(names)), "Duplicate archive paths")
        require(all(not name.startswith(("/", "\\")) and ".." not in PurePosixPath(name).parts
                    and "\\" not in name for name in names), "Unsafe archive path")
        entries = {name for name in names if not name.endswith("/")}
        for source in shared_files:
            relative = source.relative_to(SHARED).as_posix()
            expected = adapted_path(relative)
            require(expected in entries, f"Missing shared resource: {expected}")
            if relative != "pack.mcmeta":
                require(jar.read(expected) == source.read_bytes(), f"Shared content differs: {expected}")
            if expected != relative:
                require(relative not in entries, f"Legacy data path retained: {relative}")
        actual_resources = {name for name in entries if name.startswith(("assets/", "data/"))
                            or name in {"icon.png", "pack.mcmeta"}}
        require(actual_resources == expected_resources, "Extra or missing shared resources")
        for name in entries:
            if name.startswith("data/"):
                require(adapted_path(name) == name, f"Plural Minecraft 1.20 data path: {name}")
        pack = json.loads(jar.read("pack.mcmeta"))["pack"]
        require(pack["pack_format"] == 34, "Resource pack format")
        require(pack["supported_formats"] == {"min_inclusive": 34, "max_inclusive": 48}, "Data/resource format support")
        source_pack = json.loads((SHARED / "pack.mcmeta").read_text(encoding="utf-8"))["pack"]
        require(pack["description"] == source_pack["description"], "Pack description changed")
        for name in ("LICENSE", "COPYRIGHT.txt"):
            require(jar.read(name) == (REPOSITORY / name).read_bytes(), f"Source document differs: {name}")
        require(jar.read("README.md") == (PORT / "README.md").read_bytes(), "Port README differs")

        catalog = json.loads(jar.read(f"assets/{MOD}/block_catalog.json"))
        require(catalog["schema"] == 1, "Catalog schema")
        blocks = catalog["blocks"]
        require(len(blocks) == 370, "Block count")
        require(Counter(entry["category"] for entry in blocks) == EXPECTED_CATEGORIES, "Creative category counts")
        identifiers = {entry["id"] for entry in blocks}
        require(len(identifiers) == len(blocks), "Duplicate block ids")
        for folder, extension in (("models/block", "json"), ("models/item", "json"),
                                  ("blockstates", "json"), ("textures/block", "png")):
            expected = {f"assets/{MOD}/{folder}/{identifier}.{extension}" for identifier in identifiers}
            actual = {name for name in entries if name.startswith(f"assets/{MOD}/{folder}/") and name.endswith(f".{extension}")}
            require(actual == expected, f"Incomplete block resource coverage: {folder}")
        loot_prefix = f"data/{MOD}/loot_table/blocks/"
        expected_loots = {f"{loot_prefix}{identifier}.json" for identifier in identifiers}
        require({name for name in entries if name.startswith(loot_prefix)} == expected_loots, "Loot table coverage")
        for identifier in identifiers:
            loot = json.loads(jar.read(f"{loot_prefix}{identifier}.json"))
            require(loot["type"] == "minecraft:block", f"Loot type: {identifier}")
            drops = [entry["name"] for pool in loot["pools"] for entry in pool["entries"]
                     if entry["type"] == "minecraft:item"]
            require(drops == [f"{MOD}:{identifier}"], f"Loot item id: {identifier}")
        tag_prefix = f"data/{MOD}/tags/block/"
        expected_tags = {f"{tag_prefix}{category}.json" for category in EXPECTED_CATEGORIES} | {f"{tag_prefix}all_blocks.json"}
        require({name for name in entries if name.startswith(tag_prefix)} == expected_tags, "Block tag coverage")
        for category in [*EXPECTED_CATEGORIES, "all_blocks"]:
            tag = json.loads(jar.read(f"{tag_prefix}{category}.json"))
            expected = {f"{MOD}:{entry['id']}" for entry in blocks if category == "all_blocks" or entry["category"] == category}
            require(tag["replace"] is False and set(tag["values"]) == expected
                    and len(tag["values"]) == len(expected), f"Block tag membership: {category}")

        language_files = {name for name in entries if name.startswith(f"assets/{MOD}/lang/") and name.endswith(".json")}
        require({Path(name).stem for name in language_files} == EXPECTED_LOCALES, "Locale coverage")
        expected_keys = {f"block.{MOD}.{identifier}" for identifier in identifiers} | {
            f"itemGroup.{MOD}.{category}" for category in EXPECTED_CATEGORIES}
        for name in language_files:
            values = json.loads(jar.read(name))
            require(set(values) == expected_keys, f"Translation coverage: {name}")
            require(all(isinstance(value, str) and value.strip() for value in values.values()), f"Empty translation: {name}")

        loader = verify_metadata(jar, entries)
        require(path.name == f"JINZAI_Street_props-{loader}-1.21.1-{VERSION}.jar", "Not a final release JAR name")
        loader_package = "fabric" if loader == "Fabric" else "neoforge"
        loader_class = "Fabric" if loader == "Fabric" else "NeoForge"
        package = "cn/crazyjinzai/streetprops/"
        expected_classes = {
            f"{package}JinzaiStreetProps.class", f"{package}block/CatalogFacingBlock.class",
            f"{package}client/JinzaiStreetPropsClient.class",
            f"{package}{loader_package}/JinzaiStreetProps{loader_class}.class",
            f"{package}{loader_package}/JinzaiStreetProps{loader_class}Client.class",
        } | {f"{package}JinzaiStreetProps${nested}.class" for nested in (
            "BlockDefinition", "CatalogDocument", "CatalogEntry", "Category", "CollisionMode", "Kind", "ModelBox", "PlacementMode")}
        classes = {name for name in entries if name.endswith(".class")}
        mod_classes = {name for name in classes if name.startswith(package)}
        require(mod_classes == expected_classes, "Unexpected or missing mod classes")
        injected = classes - mod_classes
        require(len(injected) == 1 and all(re.fullmatch(r"architectury_inject_jinzaistreetprops1211_[^/]+/PlatformMethods\.class", name)
                                          for name in injected), "Unexpected bundled/helper classes")
        for name in mod_classes:
            data = jar.read(name)
            require(data[:4] == b"\xca\xfe\xba\xbe" and struct.unpack(">H", data[6:8])[0] == 65, f"Not Java 21 bytecode: {name}")
            require(b"tooltip." not in data, f"Unexpected custom tooltip: {name}")
            for marker in (b"java/lang/instrument", b"-javaagent", b"qzqa", b"QAAgent", b"qa_output"):
                require(marker not in data, f"QA/instrumentation marker: {name}")
        injected_majors = {name: struct.unpack(">H", jar.read(name)[6:8])[0] for name in injected}
        require(all(major <= 65 for major in injected_majors.values()), "Incompatible Architectury helper bytecode")
        manifest = jar.read("META-INF/MANIFEST.MF").decode("utf-8")
        for attribute in ("Premain-Class", "Agent-Class", "Launcher-Agent-Class"):
            require(attribute not in manifest, "Agent manifest attributes")
        descriptor = "fabric.mod.json" if loader == "Fabric" else "META-INF/neoforge.mods.toml"
        allowed = expected_resources | classes | {"META-INF/MANIFEST.MF", "LICENSE", "COPYRIGHT.txt", "README.md", descriptor}
        require(entries == allowed, f"Unexpected packaged files: {sorted(entries - allowed)}")
    return {
        "result": "PASS", "scope": "archive/source verification; not a runtime test",
        "jar": str(path), "sha256": sha256(path), "bytes": path.stat().st_size,
        "loader": loader, "version": VERSION, "blocks": len(blocks), "categories": EXPECTED_CATEGORIES,
        "shared_resources_identical": len(shared_files) - 1, "pack_metadata_adapted": 1,
        "loot_tables": len(expected_loots), "block_tags": len(expected_tags),
        "languages": len(language_files), "translation_keys_per_language": len(expected_keys),
        "mod_classes": len(mod_classes), "mod_class_java_major": 65,
        "architectury_helper_class_major": list(injected_majors.values()),
        "resource_pack_format": 34, "data_pack_format": 48, "qa_instrumentation_packaged": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jars", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    reports = []
    for candidate in args.jars:
        try:
            reports.append(verify(candidate))
        except (ValueError, KeyError, OSError, zipfile.BadZipFile, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
            reports.append({"result": "FAIL", "jar": str(candidate), "error": str(error)})
    text = json.dumps(reports, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text)
    raise SystemExit(0 if all(report["result"] == "PASS" for report in reports) else 1)
