"""Independent source, export and optional customer/baseline checks for 1.1.4.

Requires Pillow for full PNG decoding. Private customer paths are CLI arguments;
the public repository contains everything needed for generated-source checks.
"""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import io
import itertools
import json
import math
import zipfile
from collections import Counter
from pathlib import Path

from PIL import Image

MOD_ID = "jinzai_street_props"
ROOT = Path(__file__).resolve().parents[1]
LOCALES = {"zh_cn", "en_us", "ar_sa", "de_de", "es_es", "fr_fr", "hi_in",
           "id_id", "ja_jp", "ko_kr", "pt_br", "ru_ru", "tr_tr"}
CATEGORIES = {"street_lights", "road_signs", "bus_stops", "municipal", "vehicles"}
LEGACY_GUI = {"jinzai_vehicle_sets_7c", "jinzai_street_pole_6", "jinzai_bus_stop_1",
              "jinzai_bus_stop_2", "jinzai_bus_stop_3", "jinzai_bus_stop_4", "jinzai_bus_stop_5",
              "signpost_12a", "jinzai_street_light_14", "jinzai_street_post_14a"}
METADATA_NORMALIZED = {"jinzai_street_deco_1", "jinzai_street_deco_1a", "jinzai_guardrail_1",
                       "jinzai_guardrail_1a", "jinzai_street_decoration_6"}
REPLACED_PNGS = {"jinzai_street_decoration_8b", "jinzai_street_decoration_8c", "jinzai_vehicle_sets_27a"}
ACCESSORY_REPLACEMENTS = {f"jinzai_street_deco_{suffix}" for suffix in ("1", "1a", "2", "3", "4", "5", "6", "6a")}
TRUCK = "jinzai_vehicle_sets_27a"
CHANGED_OLD_COLLISION = "jinzai_street_decoration_3a"
RESOURCE_PREFIX = "common/src/main/resources/"
HAND_FIT_IDS = {"jinzai_street_decoration_19", "jinzai_vehicle_sets_28", "jinzai_vehicle_sets_29",
               "jinzai_vehicle_sets_30", "jinzai_vehicle_sets_31", "jinzai_vehicle_sets_g1",
               "jinzai_vehicle_sets_g1a", "jinzai_vehicle_sets_g2", "jinzai_vehicle_sets_g2a",
               "jinzai_vehicle_sets_sd1"}
HAND_VIEWS = {"firstperson_righthand", "firstperson_lefthand", "thirdperson_righthand", "thirdperson_lefthand"}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def same_file_content(original: bytes, current: bytes, text: bool) -> bool:
    # The baseline is an LF git archive; the Windows working tree may use CRLF.
    # Ignore only this transport difference for text, never image bytes.
    return (original.replace(b"\r\n", b"\n") == current.replace(b"\r\n", b"\n")) if text else original == current


def assert_close(actual, expected, context: str) -> None:
    if isinstance(expected, (list, tuple)):
        assert isinstance(actual, (list, tuple)) and len(actual) == len(expected), context
        for a, b in zip(actual, expected, strict=True):
            assert_close(a, b, context)
    else:
        assert isinstance(actual, (int, float)) and math.isfinite(actual), context
        assert abs(actual - expected) <= 1.1e-6, (context, actual, expected)


def decoded_png(data: bytes, context: str) -> Image.Image:
    with Image.open(io.BytesIO(data)) as image:
        assert image.format == "PNG", context
        image.verify()
    with Image.open(io.BytesIO(data)) as image:
        assert getattr(image, "n_frames", 1) == 1, f"Unexpected animation: {context}"
        image.load()
        assert image.width > 0 and image.height > 0, context
        return image.convert("RGBA")


def rotated_points(element):
    points = []
    for point in itertools.product(*zip(element["from"], element["to"])):
        x, y, z = point
        rotation = element.get("rotation")
        if rotation:
            assert not rotation.get("rescale", False), "Explicit rescale bounds support required"
            ox, oy, oz = rotation["origin"]
            x, y, z = x - ox, y - oy, z - oz
            angle = math.radians(rotation["angle"])
            c, s = math.cos(angle), math.sin(angle)
            if rotation["axis"] == "x":
                y, z = y * c - z * s, y * s + z * c
            elif rotation["axis"] == "y":
                x, z = x * c + z * s, -x * s + z * c
            else:
                x, y = x * c - y * s, x * s + y * c
            x, y, z = x + ox, y + oy, z + oz
        points.append((x, y, z))
    return points


def held_model_bounds(model, transform, left_hand):
    """Measure item-space bounds after Minecraft's scale/XYZ/translation stack.

    ItemTransform applies mirrored Y/Z rotation and X translation for the left
    hand. JSON translation is expressed in model units here (16 = one block).
    """
    angles = list(transform.get("rotation", [0, 0, 0]))
    translation = list(transform.get("translation", [0, 0, 0]))
    scale = transform.get("scale", [1, 1, 1])
    if left_hand:
        angles[1], angles[2] = -angles[1], -angles[2]
        translation[0] = -translation[0]
    points = []
    for element in model["elements"]:
        for point in rotated_points(element):
            x, y, z = [(point[axis] - 8) * scale[axis] for axis in range(3)]
            # Quaternion rotationXYZ is Rx*Ry*Rz, so column vectors see Z first.
            for axis in (2, 1, 0):
                angle = math.radians(angles[axis])
                c, s = math.cos(angle), math.sin(angle)
                if axis == 0:
                    y, z = y * c - z * s, y * s + z * c
                elif axis == 1:
                    x, z = x * c + z * s, -x * s + z * c
                else:
                    x, y = x * c - y * s, x * s + y * c
            points.append([x + translation[0], y + translation[1], z + translation[2]])
    return [min(point[i] for point in points) for i in range(3)] + [max(point[i] for point in points) for i in range(3)]


def validate_hand_transforms(identifier, source, generated, transforms):
    assert identifier in HAND_FIT_IDS and set(source.get("display", {})) == {"gui"}, identifier
    assert set(transforms) == HAND_VIEWS, identifier
    measured = {}
    for view, transform in transforms.items():
        assert set(transform) == {"rotation", "translation", "scale"}, (identifier, view)
        assert all(len(transform[key]) == 3 and all(isinstance(value, (int, float)) and math.isfinite(value)
                   for value in transform[key]) for key in transform), (identifier, view)
        first_person = view.startswith("firstperson")
        target_size = 8 if first_person else 6
        target_center = [0, 0, 0] if first_person else [0, 2.5, 0]
        assert transform["rotation"] == ([0, 45, 0] if first_person else [75, 45, 0]), (identifier, view)
        assert min(transform["scale"]) > 0 and max(transform["scale"]) <= 1, (identifier, view)
        assert max(transform["scale"]) - min(transform["scale"]) < 1e-8, (identifier, view)
        assert generated["display"][view] == transform, (identifier, view)
        bounds = held_model_bounds(generated, transform, view.endswith("lefthand"))
        dimensions = [bounds[i + 3] - bounds[i] for i in range(3)]
        assert abs(max(dimensions) - target_size) < 2e-5, (identifier, view, dimensions)
        centers = [(bounds[i] + bounds[i + 3]) / 2 for i in range(3)]
        assert all(abs(a - b) < 2e-5 for a, b in zip(centers, target_center)), (identifier, view, centers)
        assert all(target_center[i] - target_size / 2 - 2e-5 <= bounds[i]
                   and bounds[i + 3] <= target_center[i] + target_size / 2 + 2e-5 for i in range(3)), (identifier, view)
        measured[view] = bounds
    return measured


def validate_geometry(identifier, source, generated):
    visible = [element for element in source["elements"] if element.get("type", "cube") == "cube"
               and element.get("visibility", True) is not False and element.get("export", True) is not False]
    assert len(visible) == len(generated["elements"]), identifier
    width, height = source["resolution"]["width"], source["resolution"]["height"]
    assert generated["texture_size"] == [width, height], identifier
    references = set()
    face_count = 0
    for index, (old, new) in enumerate(zip(visible, generated["elements"], strict=True)):
        context = f"{identifier} element {index}"
        inflate = old.get("inflate", 0) or 0
        assert_close(new["from"], [coordinate - inflate for coordinate in old["from"]], context)
        assert_close(new["to"], [coordinate + inflate for coordinate in old["to"]], context)
        assert new["shade"] == bool(old.get("shade", True)), context
        rotations = [(axis, angle) for axis, angle in zip("xyz", old.get("rotation", [0, 0, 0])) if abs(angle) > 1e-9]
        assert len(rotations) <= 1, context
        if rotations:
            axis, angle = rotations[0]
            assert angle in (-45, -22.5, 22.5, 45), context
            assert new["rotation"]["axis"] == axis and new["rotation"]["angle"] == angle, context
            assert_close(new["rotation"]["origin"], old.get("origin", [8, 8, 8]), context)
            assert new["rotation"]["rescale"] == bool(old.get("rescale", False)), context
        else:
            assert "rotation" not in new, context
        faces = {side: face for side, face in old["faces"].items() if face is not None and face.get("enabled", True) is not False}
        assert set(faces) == set(new["faces"]), context
        for side, face in faces.items():
            exported = new["faces"][side]
            assert face.get("texture") is not None, (context, side)
            references.add(int(face["texture"]))
            expected_uv = [coordinate * 16 / (width if position % 2 == 0 else height)
                           for position, coordinate in enumerate(face["uv"])]
            assert_close(exported["uv"], expected_uv, f"{context} {side} UV")
            assert all(0 <= value <= 16 for value in exported["uv"]), context
            assert exported["texture"] == "#0", context
            extras = {}
            if "rotation" in face:
                extras["rotation"] = int(face["rotation"])
            if face.get("cullface"):
                extras["cullface"] = str(face["cullface"])
            tint = face.get("tint", face.get("tintindex"))
            if tint is not None and int(tint) >= 0:
                extras["tintindex"] = int(tint)
            assert {key: value for key, value in exported.items() if key not in ("uv", "texture")} == extras, context
            face_count += 1
    assert len(references) == 1, (identifier, references)
    texture = source["textures"][next(iter(references))]
    assert texture["name"] == texture["relative_path"] == f"{identifier}.png", identifier
    assert generated["textures"] == {"0": f"{MOD_ID}:block/{identifier}", "particle": f"{MOD_ID}:block/{identifier}"}, identifier
    assert generated["ambientocclusion"] == bool(source.get("ambientocclusion", True)), identifier
    assert generated["gui_light"] == ("front" if source.get("front_gui_light", False) else "side"), identifier
    return len(visible), face_count


def validate_generated_sources(root: Path) -> dict:
    resources = root / RESOURCE_PREFIX
    assets = resources / "assets" / MOD_ID
    manifest_document = read_json(root / "tools/block_manifest.json")
    assert manifest_document["schema"] == 1 and len(manifest_document["blocks"]) == 370
    manifest = {entry["id"]: entry for entry in manifest_document["blocks"]}
    assert len(manifest) == 370
    catalog = {entry["id"]: entry for entry in read_json(assets / "block_catalog.json")["blocks"]}
    assert set(manifest) == set(catalog)
    assert not list(assets.rglob("*.mcmeta")), "This release has no animated textures"
    gui_path = root / "tools/phase_three_gui.json"
    gui = read_json(gui_path) if gui_path.exists() else {}
    assert set(gui) <= set(manifest)
    hand = read_json(root / "tools/phase_three_hand.json")
    assert set(hand) == HAND_FIT_IDS, "Only the ten newly supplied GUI-only models may receive hand transforms"
    source_folders = {entry["source_folder"] for entry in manifest.values()}
    assert all(not list((root / folder).glob("*.mcmeta")) for folder in source_folders)
    elements = faces = 0
    for identifier, spec in manifest.items():
        assert spec["source_stem"] == identifier and identifier == identifier.lower(), identifier
        assert set(spec["names"]) == LOCALES, identifier
        assert all(isinstance(value, str) and value.strip() for value in spec["names"].values())
        assert {key: value for key, value in catalog[identifier].items() if key != "collision_boxes"} == {
            key: value for key, value in spec.items() if key != "names"}, identifier
        source = read_json(root / spec["source_folder"] / f"{identifier}.bbmodel")
        assert source["name"].lower() == identifier and source["meta"]["model_format"] == "java_block", identifier
        assert not source.get("animations"), f"Unexpected model animation: {identifier}"
        generated = read_json(assets / "models/block" / f"{identifier}.json")
        count, face_count = validate_geometry(identifier, source, generated)
        elements += count
        faces += face_count
        source_png = (root / spec["source_folder"] / f"{identifier}.png").read_bytes()
        assert source_png == (assets / "textures/block" / f"{identifier}.png").read_bytes(), identifier
        decoded_png(source_png, identifier)
        old_display, new_display = source.get("display", {}), generated.get("display", {})
        expected_non_gui = {key: value for key, value in old_display.items() if key != "gui"}
        if identifier in hand:
            validate_hand_transforms(identifier, source, generated, hand[identifier])
            expected_non_gui.update(hand[identifier])
        assert expected_non_gui == {
            key: value for key, value in new_display.items() if key != "gui"}, f"Non-GUI transform changed: {identifier}"
        if identifier in gui:
            assert new_display["gui"] == gui[identifier]
            before, after = old_display.get("gui", {}), gui[identifier]
            assert after.get("rotation", [0, 0, 0]) == before.get("rotation", [0, 0, 0]), identifier
            assert after.get("translation", [0, 0, 0])[2] == before.get("translation", [0, 0, 0])[2], identifier
            old_scale, new_scale = before.get("scale", [1, 1, 1]), after.get("scale", [1, 1, 1])
            assert all(old > 0 and new > 0 for old, new in zip(old_scale, new_scale)), identifier
            factors = [new / old for old, new in zip(old_scale, new_scale)]
            assert max(factors) - min(factors) < 1e-6 and max(factors) <= 1.000001, identifier
            from verify_release import gui_projected_bounds
            bounds = gui_projected_bounds(generated)
            assert max(bounds[2] - bounds[0], bounds[3] - bounds[1]) <= 16.0001, identifier
            assert abs(bounds[0] + bounds[2]) < 1e-4 and abs(bounds[1] + bounds[3]) < 1e-4, identifier
        elif identifier not in LEGACY_GUI:
            assert old_display.get("gui") == new_display.get("gui"), f"Unapproved GUI change: {identifier}"
        boxes = catalog[identifier]["collision_boxes"]
        points = [point for element in generated["elements"] for point in rotated_points(element)]
        expected_bounds = [min(point[i] for point in points) for i in range(3)] + [max(point[i] for point in points) for i in range(3)]
        actual_bounds = [min(box[i] for box in boxes) for i in range(3)] + [max(box[i + 3] for box in boxes) for i in range(3)]
        assert_close(actual_bounds, expected_bounds, f"Collision overall bounds: {identifier}")
        if catalog[identifier]["collision_mode"] == "detailed":
            assert all(any(all(box[i] - 1.1e-6 <= point[i] <= box[i + 3] + 1.1e-6 for i in range(3)) for box in boxes)
                       for point in points), f"Collision misses model corners: {identifier}"
        state = read_json(assets / "blockstates" / f"{identifier}.json")
        expected_states = {f"facing={facing}": dict({"model": f"{MOD_ID}:block/{identifier}"}, **({"y": angle} if angle else {}))
                           for facing, angle in (("north", 0), ("east", 90), ("south", 180), ("west", 270))}
        assert state == {"variants": expected_states}, identifier
        loot = read_json(resources / "data" / MOD_ID / "loot_tables/blocks" / f"{identifier}.json")
        assert loot == {"type": "minecraft:block", "pools": [{"rolls": 1, "bonus_rolls": 0,
            "entries": [{"type": "minecraft:item", "name": f"{MOD_ID}:{identifier}"}],
            "conditions": [{"condition": "minecraft:survives_explosion"}]}]}, identifier
    assert elements == 9257
    expected_keys = {f"block.{MOD_ID}.{identifier}" for identifier in manifest} | {f"itemGroup.{MOD_ID}.{category}" for category in CATEGORIES}
    for locale in LOCALES:
        language = read_json(assets / "lang" / f"{locale}.json")
        assert set(language) == expected_keys and len(language) == 375, locale
        assert all(language[f"block.{MOD_ID}.{identifier}"] == spec["names"][locale] for identifier, spec in manifest.items()), locale
    for category in CATEGORIES | {"all_blocks"}:
        tag = read_json(resources / "data" / MOD_ID / "tags/blocks" / f"{category}.json")
        expected = sorted(f"{MOD_ID}:{identifier}" for identifier, spec in manifest.items()
                          if category == "all_blocks" or spec["category"] == category)
        assert tag == {"replace": False, "values": expected}, category
    result = {"result": "PASS", "blocks": 370, "visible_elements": elements, "textured_faces": faces,
              "decoded_pngs": 370, "animated_pngs": 0, "locales": 13, "keys_per_locale": 375,
              "collision_boxes": sum(len(entry["collision_boxes"]) for entry in catalog.values()),
              "hand_fitted_models": len(hand), "hand_transforms": sum(len(views) for views in hand.values())}
    print("INDEPENDENT_EXPORT_PASS: " + json.dumps(result))
    return result


def validate_baseline(root: Path, baseline: Path) -> set[str]:
    from verify_release import LEGACY_POLE_IDS
    resources = root / RESOURCE_PREFIX
    assets = resources / "assets" / MOD_ID
    current = {entry["id"]: entry for entry in read_json(assets / "block_catalog.json")["blocks"]}
    with zipfile.ZipFile(baseline) as archive:
        assert archive.testzip() is None
        suffix = RESOURCE_PREFIX + f"assets/{MOD_ID}/block_catalog.json"
        entries = [name for name in archive.namelist() if name.endswith(suffix)]
        assert len(entries) == 1, "Baseline must contain one complete source tree"
        prefix = entries[0][:-len(suffix)]
        old_catalog = json.loads(archive.read(entries[0]))["blocks"]
        old_ids = {entry["id"] for entry in old_catalog}
        assert len(old_ids) == 213 and len(set(current) - old_ids) == 157, "Wrong baseline or additions"
        for old in old_catalog:
            identifier = old["id"]
            new = current[identifier]
            if identifier == CHANGED_OLD_COLLISION or identifier in LEGACY_POLE_IDS:
                ignored = {"collision_mode", "collision_boxes"}
                assert {k: v for k, v in old.items() if k not in ignored} == {k: v for k, v in new.items() if k not in ignored}
                if identifier == CHANGED_OLD_COLLISION:
                    assert old["collision_mode"] == "bounding" and new["collision_mode"] == "detailed"
                    assert old["collision_boxes"] != new["collision_boxes"]
                else:
                    assert old["collision_mode"] == "detailed" and new["collision_mode"] == "bounding"
                    assert len(new["collision_boxes"]) == 1
            else:
                assert old == new, f"Existing registration/collision changed: {identifier}"
            for directory, extension in (("models/block", "json"), ("models/item", "json"), ("blockstates", "json"), ("textures/block", "png")):
                relative = f"assets/{MOD_ID}/{directory}/{identifier}.{extension}"
                assert same_file_content(archive.read(prefix + RESOURCE_PREFIX + relative), (resources / relative).read_bytes(), extension == "json"), f"Existing generated asset changed: {relative}"
            relative = f"data/{MOD_ID}/loot_tables/blocks/{identifier}.json"
            assert same_file_content(archive.read(prefix + RESOURCE_PREFIX + relative), (resources / relative).read_bytes(), True), relative
            for extension in ("bbmodel", "png"):
                relative = f"{old['source_folder']}/{old['source_stem']}.{extension}"
                assert same_file_content(archive.read(prefix + relative), (root / relative).read_bytes(), extension == "bbmodel"), f"Existing source changed: {relative}"
        for locale in LOCALES:
            relative = f"assets/{MOD_ID}/lang/{locale}.json"
            old_language = json.loads(archive.read(prefix + RESOURCE_PREFIX + relative))
            language = read_json(resources / relative)
            assert all(language.get(key) == value for key, value in old_language.items()), f"Existing translation changed: {locale}"
        for relative in ("pack.mcmeta",):
            assert same_file_content(archive.read(prefix + RESOURCE_PREFIX + relative), (resources / relative).read_bytes(), relative.endswith(".mcmeta")), relative
    gui_path = root / "tools/phase_three_gui.json"
    if gui_path.exists():
        assert set(read_json(gui_path)).isdisjoint(old_ids), "Phase-three GUI overrides must only target new blocks"
    assert set(read_json(root / "tools/phase_three_hand.json")).isdisjoint(old_ids), "Hand overrides must not change any old block"
    print("BASELINE_PASS: all 213 existing IDs, source art, world/GUI geometry, textures and translations retained; cone corner and 25 pole collisions changed under the approved corner-only rule; icon validated separately")
    return old_ids


def without_allowed_metadata(model):
    result = copy.deepcopy(model)
    result.pop("name")
    for texture in result["textures"]:
        texture.pop("name", None)
        texture.pop("relative_path", None)
    return result


def validate_truck_pixels(old, new, new_png: bytes):
    old_images = [decoded_png(base64.b64decode(texture["source"].split(",", 1)[1]), "truck embedded") for texture in old["textures"]]
    image = decoded_png(new_png, "truck replacement")
    assert len(new["textures"]) == 1 and base64.b64decode(new["textures"][0]["source"].split(",", 1)[1]) == new_png
    old_rest, new_rest = copy.deepcopy(old), copy.deepcopy(new)
    for model in (old_rest, new_rest):
        model.pop("textures")
        for element in model["elements"]:
            for face in element["faces"].values():
                face.pop("uv")
                face.pop("texture")
    assert old_rest == new_rest, "Truck change extends beyond texture references and UVs"
    count = 0
    for old_element, new_element in zip(old["elements"], new["elements"], strict=True):
        for side, face in old_element["faces"].items():
            changed = new_element["faces"][side]
            assert changed["texture"] == 0
            source_image = old_images[face["texture"]]
            for iy in range(37):
                for ix in range(41):
                    colors = []
                    for model, texture, current in ((old, source_image, face), (new, image, changed)):
                        u, v = (ix + 0.371) / 41, (iy + 0.617) / 37
                        uv = current["uv"]
                        x = math.floor((uv[0] + u * (uv[2] - uv[0])) / model["resolution"]["width"] * texture.width)
                        y = math.floor((uv[1] + v * (uv[3] - uv[1])) / model["resolution"]["height"] * texture.height)
                        pixel = texture.getpixel((x, y))
                        colors.append(pixel if pixel[3] else (0, 0, 0, 0))
                    assert colors[0] == colors[1], ("Truck texture sampling changed", old_element["uuid"], side, ix, iy)
                    count += 1
    assert count == 709956
    return count


def validate_customer_sources(root: Path, old_ids: set[str], customer: Path, replacements: Path,
                              truck_proof: Path, accessory_overrides: Path | None = None) -> dict:
    catalog = read_json(root / RESOURCE_PREFIX / "assets" / MOD_ID / "block_catalog.json")["blocks"]
    model_paths, png_paths = {}, {}
    for suffix, destination in (("bbmodel", model_paths), ("png", png_paths)):
        for path in customer.rglob(f"*.{suffix}"):
            identifier = path.stem.lower()
            assert identifier not in destination, f"Duplicate customer asset: {identifier}"
            destination[identifier] = path
    assert set(model_paths) == set(png_paths) and len(model_paths) == 158
    new_ids = {entry["id"] for entry in catalog} - old_ids
    assert set(model_paths) == new_ids | {CHANGED_OLD_COLLISION}
    assert METADATA_NORMALIZED <= new_ids and REPLACED_PNGS <= new_ids
    if accessory_overrides is not None:
        expected_files = {identifier + suffix for identifier in ACCESSORY_REPLACEMENTS for suffix in (".bbmodel", ".png")}
        assert {path.name for path in accessory_overrides.iterdir()} == expected_files, "Expected exactly eight approved accessory pairs"
        assert ACCESSORY_REPLACEMENTS <= new_ids
    proof = read_json(truck_proof)
    compared = 0
    for entry in catalog:
        identifier = entry["id"]
        if identifier not in model_paths:
            continue
        source_bytes = model_paths[identifier].read_bytes()
        current_bytes = (root / entry["source_folder"] / f"{identifier}.bbmodel").read_bytes()
        source_model, current_model = json.loads(source_bytes), json.loads(current_bytes)
        if accessory_overrides is not None and identifier in ACCESSORY_REPLACEMENTS:
            assert current_bytes == (accessory_overrides / f"{identifier}.bbmodel").read_bytes(), f"Replacement model changed: {identifier}"
        elif identifier == TRUCK:
            assert proof["original_model_sha256"] == sha(source_bytes)
            assert proof["output_model_sha256"] == sha(current_bytes)
            assert len(proof["faces"]) == 468
        elif identifier in METADATA_NORMALIZED:
            assert without_allowed_metadata(source_model) == without_allowed_metadata(current_model), identifier
            assert current_model["name"] == identifier
            assert all(texture["name"] == texture["relative_path"] == f"{identifier}.png" for texture in current_model["textures"]), identifier
        else:
            assert source_bytes == current_bytes, f"Customer model changed: {identifier}"
        expected_png = replacements / f"{identifier}.png" if identifier in REPLACED_PNGS else png_paths[identifier]
        if accessory_overrides is not None and identifier in ACCESSORY_REPLACEMENTS:
            expected_png = accessory_overrides / f"{identifier}.png"
        actual_png = (root / entry["source_folder"] / f"{identifier}.png").read_bytes()
        assert actual_png == expected_png.read_bytes(), f"Customer PNG changed: {identifier}"
        if identifier == TRUCK:
            assert proof["replacement_png_sha256"] == sha(actual_png)
            validate_truck_pixels(source_model, current_model, actual_png)
        compared += 1
    assert compared == 158
    result = {"result": "PASS", "customer_pairs": compared, "new_ids": len(new_ids),
              "metadata_only_normalizations": len(METADATA_NORMALIZED - (ACCESSORY_REPLACEMENTS if accessory_overrides else set())),
              "accessory_replacement_pairs": len(ACCESSORY_REPLACEMENTS) if accessory_overrides else 0,
              "replacement_pngs": len(REPLACED_PNGS),
              "truck_uv_samples": 709956, "truck_uv_mismatches": 0}
    print("CUSTOMER_SOURCE_PASS: " + json.dumps(result))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--baseline-source", type=Path)
    parser.add_argument("--phase-three-source", type=Path)
    parser.add_argument("--texture-overrides", type=Path)
    parser.add_argument("--truck-proof", type=Path)
    parser.add_argument("--accessory-overrides", type=Path, help="Optional approved eight accessory BBMODEL/PNG pairs")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.accessory_overrides and not args.phase_three_source:
        parser.error("--accessory-overrides requires --phase-three-source")
    result = {"generated_sources": validate_generated_sources(args.root)}
    if args.baseline_source:
        old_ids = validate_baseline(args.root, args.baseline_source)
        result["baseline"] = {"result": "PASS", "existing_ids": len(old_ids)}
        if args.phase_three_source:
            assert args.texture_overrides and args.truck_proof
            result["customer_sources"] = validate_customer_sources(args.root, old_ids, args.phase_three_source,
                                                                   args.texture_overrides, args.truck_proof, args.accessory_overrides)
    elif args.phase_three_source:
        parser.error("--phase-three-source requires --baseline-source, --texture-overrides and --truck-proof")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
