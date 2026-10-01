"""Generate all JINZAI Street Props resources from the supplied Blockbench sources.

本模组由"Crzay津仔"提供美术与资金支持，"QiZhang"提供技术实现与制作。
发布署名仅为"Crzay津仔"，美术素材版权归 "Crzay津仔"所有，模组代码/配置版权归"QiZhang"所有。
"""

from __future__ import annotations

import argparse
import copy
import itertools
import json
import math
import posixpath
import re
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET

from phase_two_names import ENGLISH_NAMES, EXTRA_GROUPS, EXTRA_TERMS


ROOT = Path(__file__).resolve().parents[1]
MOD_ID = "jinzai_street_props"
RESOURCE_ROOT = ROOT / "common" / "src" / "main" / "resources"
ASSET_ROOT = RESOURCE_ROOT / "assets" / MOD_ID
DATA_ROOT = RESOURCE_ROOT / "data" / MOD_ID

LOCALES = (
    "zh_cn",
    "en_us",
    "ar_sa",
    "de_de",
    "es_es",
    "fr_fr",
    "hi_in",
    "id_id",
    "ja_jp",
    "ko_kr",
    "pt_br",
    "ru_ru",
    "tr_tr",
)

CATEGORY_ORDER = ("street_lights", "road_signs", "bus_stops", "municipal", "vehicles")
EXPECTED_CATEGORY_COUNTS = {
    "street_lights": 117, "road_signs": 30, "bus_stops": 20,
    "municipal": 6, "vehicles": 40,
}
EXPECTED_KIND_COUNTS = {
    "light_head": 41,
    "side_branch": 46,
    "top_assembly": 3,
    "street_pole": 27,
    "sign_pole": 7,
    "decoration": 89,
}

SIDE_BRANCH_IDS = frozenset({
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
})
TOP_ASSEMBLY_IDS = frozenset({
    "jinzai_street_post_11",
    "jinzai_street_post_14",
    "jinzai_street_post_14a",
})
STREET_POLE_IDS = frozenset({
    "jinzai_street_pole_1", "jinzai_street_pole_1a", "jinzai_street_pole_1b",
    "jinzai_street_pole_1c", "jinzai_street_pole_1d", "jinzai_street_pole_2",
    "jinzai_street_pole_2a", "jinzai_street_pole_2b", "jinzai_street_pole_2c",
    "jinzai_street_pole_2d", "jinzai_street_pole_3", "jinzai_street_pole_3a",
    "jinzai_street_pole_3b", "jinzai_street_pole_3c", "jinzai_street_pole_3d",
    "jinzai_street_pole_4", "jinzai_street_pole_4a", "jinzai_street_pole_5",
})
SIGN_POLE_IDS = frozenset({f"signpost_pole_{index}" for index in range(1, 8)})
DETAILED_COLLISION_IDS = STREET_POLE_IDS | SIGN_POLE_IDS
PHASE_TWO_BRANCH_IDS = frozenset(
    f"jinzai_street_post_{suffix}" for suffix in (
        "15", "16", "17", "18", "19", "b1", "b2", "b3", "b3b", "b4",
        "b5", "b6", "b7", "b8", "b9", "b10",
    )
)
PHASE_TWO_POLE_IDS = frozenset(
    f"jinzai_street_pole_{suffix}" for suffix in (
        "6", "6a", "7", "7a", "7b", "7c", "7d", "7e", "b1",
    )
)
SIDE_BRANCH_IDS = SIDE_BRANCH_IDS | PHASE_TWO_BRANCH_IDS
STREET_POLE_IDS = STREET_POLE_IDS | PHASE_TWO_POLE_IDS
DEPRECATED_IDS = frozenset({"jinzai_street_post_5b"})

# The supplied police pickup rear uses a 0.625 GUI scale (2.5 times the
# matching pickup variants), so its inventory icon overlaps adjacent slots.
# Keep the source art and world geometry intact; use the matching rear-view
# inventory transform only when exporting this model. The nine additional
# overrides were checked in-game on 2026-10-01: their GUI projections exceeded
# 20 pixels. Keep their angles, fit the longest projected side to 16 pixels,
# and center the icon without touching held/world transforms or source art.
GUI_DISPLAY_OVERRIDES = {
    "jinzai_vehicle_sets_7c": {
        "rotation": [30, 43, 0],
        "translation": [0.5, -1.75, 0],
        "scale": [0.25, 0.25, 0.25],
    },
    "jinzai_street_pole_6": {
        "rotation": [0, 0, 0],
        "translation": [0, -4, 0],
        "scale": [0.5, 0.5, 0.5],
    },
    "jinzai_bus_stop_3": {
        "rotation": [30, -135, 0],
        "translation": [2.75043857, 0.15027909, 0],
        "scale": [0.35360978, 0.35360978, 0.35360978],
    },
    "jinzai_bus_stop_1": {
        "rotation": [30, -135, 0],
        "translation": [0.7702731, -0.71548282, 0],
        "scale": [0.36311022, 0.36311022, 0.36311022],
    },
    "jinzai_bus_stop_2": {
        "rotation": [30, -135, 0],
        "translation": [0, 0, 0],
        "scale": [0.37101575, 0.37101575, 0.37101575],
    },
    "jinzai_bus_stop_4": {
        "rotation": [30, -135, 0],
        "translation": [-0.14627412, -2.93951265, 0],
        "scale": [0.41372568, 0.41372568, 0.41372568],
    },
    "signpost_12a": {
        "rotation": [30, -135, 0],
        "translation": [0, -3.09760588, 0],
        "scale": [0.42539267, 0.42539267, 0.42539267],
    },
    "jinzai_street_light_14": {
        "rotation": [30, -135, 0],
        "translation": [0, -2.6177753, 0],
        "scale": [0.43182094, 0.43182094, 0.43182094],
    },
    "jinzai_bus_stop_5": {
        "rotation": [30, -135, 0],
        "translation": [0, -3.05031169, 0],
        "scale": [0.44027457, 0.44027457, 0.44027457],
    },
    "jinzai_street_post_14a": {
        "rotation": [30, -135, 0],
        "translation": [0, -3.58763261, 0],
        "scale": [0.45254834, 0.45254834, 0.45254834],
    },
}

_SHEET_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_DOC_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
_RESOURCE_ID_RE = re.compile(r"^[a-z0-9._-]+$")


@dataclass(frozen=True)
class AssetSpec:
    source_folder: str
    source_stem: str
    identifier: str
    category: str
    kind: str
    placement: str
    collision_mode: str
    light_level: int
    zh_cn: str
    en_us: str

    @property
    def source_model(self) -> Path:
        return ROOT / self.source_folder / f"{self.source_stem}.bbmodel"

    @property
    def source_texture(self) -> Path:
        return ROOT / self.source_folder / f"{self.source_stem}.png"


def rounded(value: float, digits: int = 6) -> float | int:
    result = round(float(value), digits)
    if math.isclose(result, round(result), abs_tol=10 ** (-digits)):
        return int(round(result))
    return result


def _xlsx_text(node: ET.Element) -> str:
    return "".join(text.text or "" for text in node.iter(f"{{{_SHEET_NS}}}t"))


def read_first_sheet_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with zipfile.ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared_strings = [
                _xlsx_text(item)
                for item in shared_root.findall(f"{{{_SHEET_NS}}}si")
            ]
        first_sheet = workbook.find(f"{{{_SHEET_NS}}}sheets/{{{_SHEET_NS}}}sheet")
        if first_sheet is None:
            raise ValueError(f"Workbook has no worksheets: {path}")
        relationship_id = first_sheet.attrib[f"{{{_DOC_REL_NS}}}id"]
        target = next(
            (
                rel.attrib["Target"]
                for rel in relationships.findall(f"{{{_PKG_REL_NS}}}Relationship")
                if rel.attrib.get("Id") == relationship_id
            ),
            None,
        )
        if target is None:
            raise ValueError(f"Cannot resolve first worksheet: {path}")
        sheet_entry = (
            target.lstrip("/")
            if target.startswith("/")
            else posixpath.normpath(posixpath.join("xl", target))
        )
        sheet = ET.fromstring(archive.read(sheet_entry))
        rows: list[dict[str, str]] = []
        for row in sheet.findall(f".//{{{_SHEET_NS}}}sheetData/{{{_SHEET_NS}}}row"):
            values: dict[str, str] = {}
            for cell in row.findall(f"{{{_SHEET_NS}}}c"):
                match = re.match(r"([A-Z]+)", cell.attrib.get("r", ""))
                if not match:
                    continue
                cell_type = cell.attrib.get("t")
                if cell_type == "inlineStr":
                    value = _xlsx_text(cell)
                else:
                    value_node = cell.find(f"{{{_SHEET_NS}}}v")
                    raw = "" if value_node is None else value_node.text or ""
                    value = shared_strings[int(raw)] if cell_type == "s" and raw else raw
                values[match.group(1)] = value.strip()
            rows.append(values)
        return rows


def source_pair_stems(folder: str) -> set[str]:
    directory = ROOT / folder
    models = {path.stem for path in directory.glob("*.bbmodel")}
    textures = {path.stem for path in directory.glob("*.png")}
    if models != textures:
        raise ValueError(
            f"Unpaired assets in {folder}: models-only={sorted(models - textures)}, "
            f"textures-only={sorted(textures - models)}"
        )
    return models


def english_name(zh_cn: str) -> str:
    if zh_cn in ENGLISH_NAMES:
        return ENGLISH_NAMES[zh_cn]
    head = re.fullmatch(r"(LED|钨丝灯|钨丝|花园)路灯头([Bb]?\d+[a-z]?)", zh_cn)
    if head:
        head_type = {"LED": "LED", "钨丝灯": "Incandescent", "钨丝": "Incandescent", "花园": "Garden"}[head.group(1)]
        return f"{head_type} Street Light Head {head.group(2)}"
    branch = re.fullmatch(r"(白色|蓝色|黑色|墨绿色|灰色)路灯(分支|成品)([Bb]?\d+[a-z]?)", zh_cn)
    if branch:
        color = {
            "白色": "White", "蓝色": "Blue", "黑色": "Black", "墨绿色": "Dark Green", "灰色": "Gray",
        }[branch.group(1)]
        noun = "Street Light Branch" if branch.group(2) == "分支" else "Complete Street Light"
        return f"{color} {noun} {branch.group(3)}"
    pole = re.fullmatch(r"(白色|蓝色|黑色|墨绿色)路灯杆(\d+)", zh_cn)
    if pole:
        color = {
            "白色": "White", "蓝色": "Blue", "黑色": "Black", "墨绿色": "Dark Green",
        }[pole.group(1)]
        return f"{color} Street Light Pole {pole.group(2)}"
    crossbar = re.fullmatch(r"(白色|蓝色|黑色)路灯横杆", zh_cn)
    if crossbar:
        color = {"白色": "White", "蓝色": "Blue", "黑色": "Black"}[crossbar.group(1)]
        return f"{color} Street Light Crossbar"
    exact = {
        "墨绿色路灯杆底部": "Dark Green Street Light Pole Bottom",
        "灯杆顶部配件": "Street Light Pole Top Accessory",
        "广州蓝色路牌": "Guangzhou Blue Road Sign",
        "广州绿色路牌": "Guangzhou Green Road Sign",
        "广州蓝绿色路牌": "Guangzhou Teal Road Sign",
        "深圳米色路牌": "Shenzhen Beige Road Sign",
        "深圳抱箍式路牌": "Shenzhen Clamp-Mounted Road Sign",
        "陈旧小区路牌": "Worn Residential Area Road Sign",
        "小区路牌": "Residential Area Road Sign",
        "怀旧型路牌": "Vintage Road Sign",
        "湛江怀旧型路牌": "Zhanjiang Vintage Road Sign",
        "简易蓝色路牌": "Simple Blue Road Sign",
        "简易绿色路牌": "Simple Green Road Sign",
        "路牌灯箱-底部": "Road Sign Lightbox - Bottom",
        "路牌灯箱-中部": "Road Sign Lightbox - Middle",
        "路牌灯箱-顶部": "Road Sign Lightbox - Top",
        "沪式蓝色路牌": "Shanghai-Style Blue Road Sign",
        "沪式绿色路牌": "Shanghai-Style Green Road Sign",
        "沪式棕色路牌": "Shanghai-Style Brown Road Sign",
        "厦门标准蓝色路牌": "Xiamen Standard Blue Road Sign",
        "厦门标准绿色路牌": "Xiamen Standard Green Road Sign",
        "沪式蓝色抱箍式路牌": "Shanghai-Style Blue Clamp-Mounted Road Sign",
        "沪式绿色抱箍式路牌": "Shanghai-Style Green Clamp-Mounted Road Sign",
        "沪式棕色抱箍式路牌": "Shanghai-Style Brown Clamp-Mounted Road Sign",
        "广州路牌杆": "Guangzhou Road Sign Pole",
        "广州蓝色路牌杆": "Guangzhou Blue Road Sign Pole",
        "广州绿色路牌杆": "Guangzhou Green Road Sign Pole",
        "细棕色杆": "Thin Brown Pole",
        "沪式路牌杆顶部": "Shanghai-Style Road Sign Pole Top",
        "苏州路牌杆": "Suzhou Road Sign Pole",
        "苏州路牌杆顶部": "Suzhou Road Sign Pole Top",
        "广州停车场标志牌": "Guangzhou Parking Sign",
        "悬挂式公交站牌": "Hanging Bus Stop Sign",
        "花园小区公交站牌": "Garden Community Bus Stop Sign",
        "不锈钢公交站牌1": "Stainless Steel Bus Stop Sign 1",
        "不锈钢公交站牌2-底部": "Stainless Steel Bus Stop Sign 2 - Bottom",
        "不锈钢公交站牌2-顶部": "Stainless Steel Bus Stop Sign 2 - Top",
        "简易公交站牌": "Simple Bus Stop Sign",
        "贴广告的简易公交站牌": "Simple Bus Stop Sign with Advertisement",
    }
    try:
        return exact[zh_cn]
    except KeyError as exception:
        raise ValueError(f"No English translation rule for {zh_cn!r}") from exception


GROUP_TRANSLATIONS = {
    "zh_cn": ("路灯", "路牌", "公交站牌"),
    "en_us": ("Street Lights", "Road Signs", "Bus Stop Signs"),
    "ar_sa": ("مصابيح الشوارع", "لافتات الطرق", "لافتات محطات الحافلات"),
    "de_de": ("Straßenlaternen", "Straßenschilder", "Bushaltestellenschilder"),
    "es_es": ("Farolas", "Señales de calle", "Señales de parada de autobús"),
    "fr_fr": ("Lampadaires", "Plaques de rue", "Panneaux d'arrêt de bus"),
    "hi_in": ("सड़क लाइटें", "सड़क संकेत", "बस स्टॉप संकेत"),
    "id_id": ("Lampu Jalan", "Rambu Jalan", "Rambu Halte Bus"),
    "ja_jp": ("街路灯", "道路標識", "バス停標識"),
    "ko_kr": ("가로등", "도로 표지판", "버스 정류장 표지판"),
    "pt_br": ("Iluminação Pública", "Placas de Rua", "Placas de Ponto de Ônibus"),
    "ru_ru": ("Уличные фонари", "Дорожные указатели", "Таблички автобусных остановок"),
    "tr_tr": ("Sokak Lambaları", "Yol Tabelaları", "Otobüs Durağı Tabelaları"),
}


TERM_TRANSLATIONS: dict[str, dict[str, str]] = {
    "ar_sa": {
        "Street Light Pole Top Accessory": "ملحق علوي لعمود إنارة الشارع",
        "Street Light Pole Bottom": "قاعدة عمود إنارة الشارع",
        "Street Light Crossbar": "عارضة إنارة الشارع",
        "Street Light Branch": "ذراع إنارة الشارع",
        "Complete Street Light": "مصباح شارع كامل",
        "Street Light Head": "رأس مصباح الشارع",
        "Clamp-Mounted Road Sign": "لافتة طريق مثبتة بمشبك",
        "Road Sign Pole Top": "قمة عمود لافتة الطريق",
        "Road Sign Lightbox": "صندوق إضاءة لافتة الطريق",
        "Road Sign Pole": "عمود لافتة الطريق",
        "Road Sign": "لافتة طريق",
        "Parking Sign": "لافتة موقف سيارات",
        "Bus Stop Sign": "لافتة محطة حافلات",
        "with Advertisement": "مع إعلان", "Stainless Steel": "فولاذ مقاوم للصدأ",
        "Garden Community": "مجمع الحدائق", "Residential Area": "منطقة سكنية",
        "Shanghai-Style": "طراز شنغهاي", "Incandescent": "متوهج", "Garden": "حديقة",
        "Hanging": "معلق", "Simple": "بسيط", "Vintage": "تراثي", "Worn": "قديم",
        "Standard": "قياسي", "Thin": "رفيع", "Dark Green": "أخضر داكن",
        "White": "أبيض", "Blue": "أزرق", "Green": "أخضر", "Teal": "أزرق مخضر",
        "Beige": "بيج", "Brown": "بني", "Black": "أسود", "Pole": "عمود",
        "Bottom": "سفلي", "Middle": "أوسط", "Top": "علوي",
    },
    "de_de": {
        "Street Light Pole Top Accessory": "Zubehör für Laternenmastspitze",
        "Street Light Pole Bottom": "Laternenmastsockel", "Street Light Crossbar": "Laternenquerträger",
        "Street Light Branch": "Laternenausleger", "Complete Street Light": "Komplette Straßenlaterne",
        "Street Light Head": "Leuchtenkopf", "Clamp-Mounted Road Sign": "Straßenschild mit Schellenhalterung",
        "Road Sign Pole Top": "Straßenschildmastspitze", "Road Sign Lightbox": "Straßenschild-Leuchtkasten",
        "Road Sign Pole": "Straßenschildmast", "Road Sign": "Straßenschild", "Parking Sign": "Parkplatzschild",
        "Bus Stop Sign": "Bushaltestellenschild", "with Advertisement": "mit Werbung",
        "Stainless Steel": "Edelstahl", "Garden Community": "Gartensiedlung", "Residential Area": "Wohngebiet",
        "Shanghai-Style": "Shanghai-Stil", "Incandescent": "Glühlampen", "Garden": "Garten",
        "Hanging": "Hängend", "Simple": "Einfach", "Vintage": "Nostalgisch", "Worn": "Verwittert",
        "Standard": "Standard", "Thin": "Dünn", "Dark Green": "Dunkelgrün", "White": "Weiß",
        "Blue": "Blau", "Green": "Grün", "Teal": "Blaugrün", "Beige": "Beige", "Brown": "Braun",
        "Black": "Schwarz", "Pole": "Mast", "Bottom": "Unterteil", "Middle": "Mittelteil", "Top": "Oberteil",
    },
    "es_es": {
        "Street Light Pole Top Accessory": "Accesorio superior de poste de farola", "Street Light Pole Bottom": "Base de poste de farola",
        "Street Light Crossbar": "Travesaño de farola", "Street Light Branch": "Brazo de farola",
        "Complete Street Light": "Farola completa", "Street Light Head": "Cabezal de farola",
        "Clamp-Mounted Road Sign": "Señal de calle con abrazadera", "Road Sign Pole Top": "Parte superior del poste de señal",
        "Road Sign Lightbox": "Caja luminosa de señal", "Road Sign Pole": "Poste de señal de calle",
        "Road Sign": "Señal de calle", "Parking Sign": "Señal de aparcamiento", "Bus Stop Sign": "Señal de parada de autobús",
        "with Advertisement": "con anuncio", "Stainless Steel": "Acero inoxidable", "Garden Community": "Urbanización jardín",
        "Residential Area": "Zona residencial", "Shanghai-Style": "Estilo Shanghái", "Incandescent": "Incandescente",
        "Garden": "Jardín", "Hanging": "Colgante", "Simple": "Sencillo", "Vintage": "Antiguo", "Worn": "Desgastado",
        "Standard": "Estándar", "Thin": "Fino", "Dark Green": "Verde oscuro", "White": "Blanco", "Blue": "Azul",
        "Green": "Verde", "Teal": "Verde azulado", "Beige": "Beis", "Brown": "Marrón", "Black": "Negro",
        "Pole": "Poste", "Bottom": "Parte inferior", "Middle": "Parte central", "Top": "Parte superior",
    },
    "fr_fr": {
        "Street Light Pole Top Accessory": "Accessoire supérieur de mât", "Street Light Pole Bottom": "Base de mât de lampadaire",
        "Street Light Crossbar": "Traverse de lampadaire", "Street Light Branch": "Bras de lampadaire",
        "Complete Street Light": "Lampadaire complet", "Street Light Head": "Tête de lampadaire",
        "Clamp-Mounted Road Sign": "Plaque de rue à collier", "Road Sign Pole Top": "Sommet de poteau de plaque",
        "Road Sign Lightbox": "Caisson lumineux de plaque", "Road Sign Pole": "Poteau de plaque de rue",
        "Road Sign": "Plaque de rue", "Parking Sign": "Panneau de parking", "Bus Stop Sign": "Panneau d'arrêt de bus",
        "with Advertisement": "avec publicité", "Stainless Steel": "Acier inoxydable", "Garden Community": "Résidence jardin",
        "Residential Area": "Zone résidentielle", "Shanghai-Style": "Style Shanghai", "Incandescent": "Incandescent",
        "Garden": "Jardin", "Hanging": "Suspendu", "Simple": "Simple", "Vintage": "Rétro", "Worn": "Usé",
        "Standard": "Standard", "Thin": "Fin", "Dark Green": "Vert foncé", "White": "Blanc", "Blue": "Bleu",
        "Green": "Vert", "Teal": "Bleu-vert", "Beige": "Beige", "Brown": "Marron", "Black": "Noir",
        "Pole": "Poteau", "Bottom": "Partie basse", "Middle": "Partie centrale", "Top": "Partie haute",
    },
    "hi_in": {
        "Street Light Pole Top Accessory": "स्ट्रीट लाइट खंभे का ऊपरी सहायक", "Street Light Pole Bottom": "स्ट्रीट लाइट खंभे का आधार",
        "Street Light Crossbar": "स्ट्रीट लाइट क्रॉसबार", "Street Light Branch": "स्ट्रीट लाइट शाखा",
        "Complete Street Light": "पूर्ण स्ट्रीट लाइट", "Street Light Head": "स्ट्रीट लाइट हेड",
        "Clamp-Mounted Road Sign": "क्लैंप लगा सड़क संकेत", "Road Sign Pole Top": "सड़क संकेत खंभे का शीर्ष",
        "Road Sign Lightbox": "सड़क संकेत लाइटबॉक्स", "Road Sign Pole": "सड़क संकेत खंभा", "Road Sign": "सड़क संकेत",
        "Parking Sign": "पार्किंग संकेत", "Bus Stop Sign": "बस स्टॉप संकेत", "with Advertisement": "विज्ञापन सहित",
        "Stainless Steel": "स्टेनलेस स्टील", "Garden Community": "गार्डन कॉलोनी", "Residential Area": "आवासीय क्षेत्र",
        "Shanghai-Style": "शंघाई शैली", "Incandescent": "तापदीप्त", "Garden": "उद्यान", "Hanging": "लटकता",
        "Simple": "सरल", "Vintage": "पुराना", "Worn": "जीर्ण", "Standard": "मानक", "Thin": "पतला",
        "Dark Green": "गहरा हरा", "White": "सफेद", "Blue": "नीला", "Green": "हरा", "Teal": "नीलहरित",
        "Beige": "बेज", "Brown": "भूरा", "Black": "काला", "Pole": "खंभा", "Bottom": "निचला",
        "Middle": "मध्य", "Top": "ऊपरी",
    },
    "id_id": {
        "Street Light Pole Top Accessory": "Aksesori Puncak Tiang Lampu Jalan", "Street Light Pole Bottom": "Dasar Tiang Lampu Jalan",
        "Street Light Crossbar": "Palang Lampu Jalan", "Street Light Branch": "Lengan Lampu Jalan",
        "Complete Street Light": "Lampu Jalan Lengkap", "Street Light Head": "Kepala Lampu Jalan",
        "Clamp-Mounted Road Sign": "Rambu Jalan Berpenjepit", "Road Sign Pole Top": "Puncak Tiang Rambu Jalan",
        "Road Sign Lightbox": "Kotak Lampu Rambu Jalan", "Road Sign Pole": "Tiang Rambu Jalan", "Road Sign": "Rambu Jalan",
        "Parking Sign": "Rambu Parkir", "Bus Stop Sign": "Rambu Halte Bus", "with Advertisement": "dengan Iklan",
        "Stainless Steel": "Baja Tahan Karat", "Garden Community": "Kompleks Taman", "Residential Area": "Permukiman",
        "Shanghai-Style": "Gaya Shanghai", "Incandescent": "Pijar", "Garden": "Taman", "Hanging": "Gantung",
        "Simple": "Sederhana", "Vintage": "Klasik", "Worn": "Usang", "Standard": "Standar", "Thin": "Tipis",
        "Dark Green": "Hijau Tua", "White": "Putih", "Blue": "Biru", "Green": "Hijau", "Teal": "Biru Kehijauan",
        "Beige": "Krem", "Brown": "Cokelat", "Black": "Hitam", "Pole": "Tiang", "Bottom": "Bawah",
        "Middle": "Tengah", "Top": "Atas",
    },
    "ja_jp": {
        "Street Light Pole Top Accessory": "街路灯ポール上部付属品", "Street Light Pole Bottom": "街路灯ポール下部",
        "Street Light Crossbar": "街路灯横棒", "Street Light Branch": "街路灯アーム", "Complete Street Light": "完成街路灯",
        "Street Light Head": "街路灯ヘッド", "Clamp-Mounted Road Sign": "クランプ式道路標識",
        "Road Sign Pole Top": "道路標識ポール上部", "Road Sign Lightbox": "道路標識ライトボックス",
        "Road Sign Pole": "道路標識ポール", "Road Sign": "道路標識", "Parking Sign": "駐車場標識",
        "Bus Stop Sign": "バス停標識", "with Advertisement": "広告付き", "Stainless Steel": "ステンレス",
        "Garden Community": "ガーデン住宅地", "Residential Area": "住宅地", "Shanghai-Style": "上海式",
        "Incandescent": "白熱灯", "Garden": "庭園", "Hanging": "吊り下げ式", "Simple": "簡易",
        "Vintage": "レトロ", "Worn": "古びた", "Standard": "標準", "Thin": "細型", "Dark Green": "深緑",
        "White": "白", "Blue": "青", "Green": "緑", "Teal": "青緑", "Beige": "ベージュ", "Brown": "茶",
        "Black": "黒", "Pole": "ポール", "Bottom": "下部", "Middle": "中部", "Top": "上部",
    },
    "ko_kr": {
        "Street Light Pole Top Accessory": "가로등 기둥 상단 부속", "Street Light Pole Bottom": "가로등 기둥 하단",
        "Street Light Crossbar": "가로등 가로대", "Street Light Branch": "가로등 지지대", "Complete Street Light": "완성형 가로등",
        "Street Light Head": "가로등 헤드", "Clamp-Mounted Road Sign": "클램프형 도로 표지판",
        "Road Sign Pole Top": "도로 표지판 기둥 상단", "Road Sign Lightbox": "도로 표지판 라이트박스",
        "Road Sign Pole": "도로 표지판 기둥", "Road Sign": "도로 표지판", "Parking Sign": "주차장 표지판",
        "Bus Stop Sign": "버스 정류장 표지판", "with Advertisement": "광고 부착", "Stainless Steel": "스테인리스",
        "Garden Community": "정원 단지", "Residential Area": "주거 지역", "Shanghai-Style": "상하이식",
        "Incandescent": "백열등", "Garden": "정원", "Hanging": "매달림형", "Simple": "간이형", "Vintage": "복고형",
        "Worn": "낡은", "Standard": "표준", "Thin": "얇은", "Dark Green": "진녹색", "White": "흰색",
        "Blue": "파란색", "Green": "초록색", "Teal": "청록색", "Beige": "베이지색", "Brown": "갈색",
        "Black": "검은색", "Pole": "기둥", "Bottom": "하단", "Middle": "중단", "Top": "상단",
    },
    "pt_br": {
        "Street Light Pole Top Accessory": "Acessório Superior do Poste de Luz", "Street Light Pole Bottom": "Base do Poste de Luz",
        "Street Light Crossbar": "Travessa de Iluminação", "Street Light Branch": "Braço de Iluminação",
        "Complete Street Light": "Luminária Completa", "Street Light Head": "Cabeça de Luminária",
        "Clamp-Mounted Road Sign": "Placa de Rua com Abraçadeira", "Road Sign Pole Top": "Topo do Poste de Placa",
        "Road Sign Lightbox": "Caixa Iluminada de Placa", "Road Sign Pole": "Poste de Placa de Rua", "Road Sign": "Placa de Rua",
        "Parking Sign": "Placa de Estacionamento", "Bus Stop Sign": "Placa de Ponto de Ônibus", "with Advertisement": "com Anúncio",
        "Stainless Steel": "Aço Inoxidável", "Garden Community": "Condomínio Jardim", "Residential Area": "Área Residencial",
        "Shanghai-Style": "Estilo Xangai", "Incandescent": "Incandescente", "Garden": "Jardim", "Hanging": "Suspensa",
        "Simple": "Simples", "Vintage": "Retrô", "Worn": "Desgastada", "Standard": "Padrão", "Thin": "Fino",
        "Dark Green": "Verde-Escuro", "White": "Branco", "Blue": "Azul", "Green": "Verde", "Teal": "Verde-Azulado",
        "Beige": "Bege", "Brown": "Marrom", "Black": "Preto", "Pole": "Poste", "Bottom": "Parte Inferior",
        "Middle": "Parte Central", "Top": "Parte Superior",
    },
    "ru_ru": {
        "Street Light Pole Top Accessory": "Верхняя деталь фонарного столба", "Street Light Pole Bottom": "Основание фонарного столба",
        "Street Light Crossbar": "Перекладина фонаря", "Street Light Branch": "Кронштейн фонаря",
        "Complete Street Light": "Готовый уличный фонарь", "Street Light Head": "Светильник уличного фонаря",
        "Clamp-Mounted Road Sign": "Дорожный указатель с хомутом", "Road Sign Pole Top": "Верх стойки указателя",
        "Road Sign Lightbox": "Световой короб указателя", "Road Sign Pole": "Стойка дорожного указателя",
        "Road Sign": "Дорожный указатель", "Parking Sign": "Знак парковки", "Bus Stop Sign": "Табличка автобусной остановки",
        "with Advertisement": "с рекламой", "Stainless Steel": "Нержавеющая сталь", "Garden Community": "Садовый жилой комплекс",
        "Residential Area": "Жилой район", "Shanghai-Style": "Шанхайский стиль", "Incandescent": "Лампа накаливания",
        "Garden": "Садовый", "Hanging": "Подвесная", "Simple": "Простой", "Vintage": "Винтажный", "Worn": "Старый",
        "Standard": "Стандартный", "Thin": "Тонкий", "Dark Green": "Тёмно-зелёный", "White": "Белый",
        "Blue": "Синий", "Green": "Зелёный", "Teal": "Сине-зелёный", "Beige": "Бежевый", "Brown": "Коричневый",
        "Black": "Чёрный", "Pole": "Столб", "Bottom": "Нижняя часть", "Middle": "Средняя часть", "Top": "Верхняя часть",
    },
    "tr_tr": {
        "Street Light Pole Top Accessory": "Sokak Lambası Direği Üst Aksesuarı", "Street Light Pole Bottom": "Sokak Lambası Direği Altlığı",
        "Street Light Crossbar": "Sokak Lambası Traversı", "Street Light Branch": "Sokak Lambası Kolu",
        "Complete Street Light": "Tam Sokak Lambası", "Street Light Head": "Sokak Lambası Başlığı",
        "Clamp-Mounted Road Sign": "Kelepçeli Yol Tabelası", "Road Sign Pole Top": "Yol Tabelası Direği Üstü",
        "Road Sign Lightbox": "Işıklı Yol Tabelası Kutusu", "Road Sign Pole": "Yol Tabelası Direği", "Road Sign": "Yol Tabelası",
        "Parking Sign": "Otopark Tabelası", "Bus Stop Sign": "Otobüs Durağı Tabelası", "with Advertisement": "Reklamlı",
        "Stainless Steel": "Paslanmaz Çelik", "Garden Community": "Bahçeli Site", "Residential Area": "Yerleşim Alanı",
        "Shanghai-Style": "Şanghay Tarzı", "Incandescent": "Akkor", "Garden": "Bahçe", "Hanging": "Asılı",
        "Simple": "Basit", "Vintage": "Nostaljik", "Worn": "Eskimiş", "Standard": "Standart", "Thin": "İnce",
        "Dark Green": "Koyu Yeşil", "White": "Beyaz", "Blue": "Mavi", "Green": "Yeşil", "Teal": "Turkuaz",
        "Beige": "Bej", "Brown": "Kahverengi", "Black": "Siyah", "Pole": "Direk", "Bottom": "Alt",
        "Middle": "Orta", "Top": "Üst",
    },
}


def localized_name(spec: AssetSpec, locale: str) -> str:
    if locale == "zh_cn":
        return spec.zh_cn
    if locale == "en_us":
        return spec.en_us
    result = spec.en_us
    new_content = (
        spec.identifier in PHASE_TWO_BRANCH_IDS | PHASE_TWO_POLE_IDS
        or spec.identifier.startswith(("jinzai_street_light_b", "jinzai_vehicle_sets_", "jinzai_street_decoration_"))
        or spec.identifier.startswith(tuple(f"jinzai_bus_stop_{number}" for number in (6, 7, 8)))
    )
    terms = {**TERM_TRANSLATIONS[locale], **EXTRA_TERMS[locale]} if new_content else TERM_TRANSLATIONS[locale]
    for source in sorted(terms, key=len, reverse=True):
        result = result.replace(source, terms[source])
    return result


def classify(identifier: str, category: str) -> tuple[str, str, str, int]:
    if identifier.startswith("jinzai_street_light_"):
        return "light_head", "horizontal", "bounding", 15
    if identifier in SIDE_BRANCH_IDS:
        return "side_branch", "side_only", "bounding", 0
    if identifier in TOP_ASSEMBLY_IDS:
        return "top_assembly", "top_only", "bounding", 0
    if identifier in STREET_POLE_IDS:
        mode = "detailed" if identifier in DETAILED_COLLISION_IDS else "bounding"
        return "street_pole", "horizontal", mode, 0
    if identifier in SIGN_POLE_IDS:
        return "sign_pole", "horizontal", "detailed", 0
    return "decoration", "horizontal", "bounding", 0


def discover_specs(private_input_root: Path, phase_two_input_root: Path) -> list[AssetSpec]:
    labels: dict[str, tuple[str, str]] = {}

    def add(folder: str, identifier: str, label: str) -> None:
        identifier = identifier.lower()
        if not _RESOURCE_ID_RE.fullmatch(identifier):
            raise ValueError(f"Invalid resource id {identifier!r}")
        if identifier in DEPRECATED_IDS:
            return
        if identifier in labels:
            if identifier == "jinzai_street_post_4":
                identifier = "jinzai_street_post_4c"
            else:
                raise ValueError(f"Duplicate workbook id: {identifier}")
        if identifier in labels:
            raise ValueError(f"Corrected workbook id is still duplicated: {identifier}")
        labels[identifier] = (folder, label)

    light_folder = "路灯杆与支架"
    light_rows = read_first_sheet_rows(private_input_root / light_folder / "路灯杆与支架模型名称.xlsx")
    for row in light_rows:
        for id_column, name_column in (("A", "B"), ("D", "E"), ("G", "H")):
            identifier = row.get(id_column, "")
            label = row.get(name_column, "")
            if _RESOURCE_ID_RE.fullmatch(identifier) and label:
                add(light_folder, identifier, label)

    sign_folder = "路牌"
    sign_rows = read_first_sheet_rows(private_input_root / sign_folder / "路牌模型名称.xlsx")
    for row in sign_rows:
        for id_column, name_column in (("A", "B"), ("D", "E"), ("G", "H")):
            identifier = row.get(id_column, "")
            label = row.get(name_column, "")
            if _RESOURCE_ID_RE.fullmatch(identifier) and label:
                add(sign_folder, identifier, label)

    bus_folder = "公交站"
    for row in read_first_sheet_rows(private_input_root / bus_folder / "公交站方块模型名称.xlsx"):
        identifier = row.get("A", "")
        label = row.get("B", "")
        if _RESOURCE_ID_RE.fullmatch(identifier) and label:
            add(bus_folder, identifier, label)

    legacy_ids = set(labels)
    if len(legacy_ids) != 119:
        raise ValueError("The private phase-one workbooks must preserve all 119 legacy IDs")

    new_workbooks = (
        (light_folder, "路灯（新增）/路灯新增模型名称.xlsx", (("A", "B"), ("D", "E"), ("G", "H"))),
        (bus_folder, "公交站（新增）/公交站方块新增名称.xlsx", (("A", "B"),)),
        ("市政设施", "市政设施/市政设施方块名称.xlsx", (("A", "B"),)),
        ("汽车载具", "汽车载具/普通载具新增方块.xlsx", (("A", "B"),)),
    )
    for folder, workbook, columns in new_workbooks:
        for row in read_first_sheet_rows(phase_two_input_root / workbook):
            for id_column, name_column in columns:
                identifier, label = row.get(id_column, "").lower(), row.get(name_column, "")
                if _RESOURCE_ID_RE.fullmatch(identifier) and label:
                    if identifier in labels:
                        raise ValueError(f"Phase-two ID already exists: {identifier}")
                    add(folder, identifier, label)
    if len(set(labels) - legacy_ids) != 94:
        raise ValueError("Expected 94 named phase-two additions")

    disk_by_folder = {
        light_folder: source_pair_stems(light_folder),
        sign_folder: source_pair_stems(sign_folder),
        bus_folder: source_pair_stems(bus_folder),
        "市政设施": source_pair_stems("市政设施"),
        "汽车载具": source_pair_stems("汽车载具"),
    }
    all_disk = set().union(*disk_by_folder.values())
    if set(labels) != all_disk:
        raise ValueError(
            f"Workbook/source mismatch: workbook-only={sorted(set(labels) - all_disk)}, "
            f"source-only={sorted(all_disk - set(labels))}"
        )
    if len(labels) != 213 or "jinzai_street_post_5b" in labels or "jinzai_street_post_4c" not in labels:
        raise ValueError("Corrected 213-model inventory assertion failed")

    specs: list[AssetSpec] = []
    for identifier, (folder, zh_cn) in labels.items():
        category = (
            "street_lights" if folder == light_folder
            else "road_signs" if folder == sign_folder
            else "bus_stops" if folder == bus_folder
            else "municipal" if folder == "市政设施"
            else "vehicles"
        )
        kind, placement, collision_mode, light_level = classify(identifier, category)
        specs.append(AssetSpec(
            source_folder=folder,
            source_stem=identifier,
            identifier=identifier,
            category=category,
            kind=kind,
            placement=placement,
            collision_mode=collision_mode,
            light_level=light_level,
            zh_cn=zh_cn,
            en_us=english_name(zh_cn),
        ))

    specs.sort(key=lambda spec: (
        CATEGORY_ORDER.index(spec.category),
        spec.kind,
        spec.identifier,
    ))
    ids = {spec.identifier for spec in specs}
    if ids & DEPRECATED_IDS or not (SIDE_BRANCH_IDS | TOP_ASSEMBLY_IDS | DETAILED_COLLISION_IDS) <= ids:
        raise ValueError("Strict placement/collision id sets do not match the inventory")
    return specs


def _inflated_bounds(element: dict[str, Any]) -> tuple[list[float], list[float]]:
    inflate = float(element.get("inflate", 0) or 0)
    return (
        [float(value) - inflate for value in element["from"]],
        [float(value) + inflate for value in element["to"]],
    )


def _rotation_parts(element: dict[str, Any]) -> tuple[str, float, list[float]] | None:
    rotation = element.get("rotation")
    if not rotation or not any(abs(float(value)) > 1e-9 for value in rotation):
        return None
    non_zero = [
        (axis, float(angle))
        for axis, angle in zip("xyz", rotation)
        if abs(float(angle)) > 1e-9
    ]
    if len(non_zero) != 1:
        raise ValueError(f"Unsupported multi-axis rotation: {rotation}")
    axis, angle = non_zero[0]
    if angle not in (-45.0, -22.5, 22.5, 45.0):
        raise ValueError(f"Unsupported Minecraft element angle: {angle}")
    return axis, angle, [float(value) for value in element.get("origin", [8, 8, 8])]


def _rotate_point(
    point: Iterable[float], axis: str, angle: float, origin: Iterable[float]
) -> list[float]:
    x, y, z = (float(value) for value in point)
    ox, oy, oz = (float(value) for value in origin)
    x -= ox
    y -= oy
    z -= oz
    radians = math.radians(angle)
    cosine, sine = math.cos(radians), math.sin(radians)
    if axis == "x":
        y, z = y * cosine - z * sine, y * sine + z * cosine
    elif axis == "y":
        x, z = x * cosine + z * sine, -x * sine + z * cosine
    elif axis == "z":
        x, y = x * cosine - y * sine, x * sine + y * cosine
    else:
        raise ValueError(axis)
    return [x + ox, y + oy, z + oz]


def element_collision_box(element: dict[str, Any]) -> list[float | int]:
    from_pos, to_pos = _inflated_bounds(element)
    corners = [list(point) for point in itertools.product(*zip(from_pos, to_pos))]
    rotation = _rotation_parts(element)
    if rotation is not None:
        axis, angle, origin = rotation
        corners = [_rotate_point(point, axis, angle, origin) for point in corners]
    minimum = [min(point[index] for point in corners) for index in range(3)]
    maximum = [max(point[index] for point in corners) for index in range(3)]
    return [rounded(value) for value in minimum + maximum]


def _split_interval(
    start: float,
    end: float,
    maximum_size: float = 1.0,
) -> list[tuple[float, float]]:
    length = end - start
    if length <= 0:
        raise ValueError(f"Cannot split a non-positive interval: {start}..{end}")
    segment_count = max(1, math.ceil(length / maximum_size - 1e-9))
    segment_size = length / segment_count
    return [
        (
            start + segment_size * index,
            end if index + 1 == segment_count else start + segment_size * (index + 1),
        )
        for index in range(segment_count)
    ]


def detailed_collision_boxes(element: dict[str, Any]) -> list[list[float | int]]:
    """Approximate a rotated model cuboid with <=1-unit cells in its rotation plane."""
    from_pos, to_pos = _inflated_bounds(element)
    rotation = _rotation_parts(element)
    if rotation is None:
        return [element_collision_box(element)]
    axis, _, _ = rotation
    plane_axes = {"x": (1, 2), "y": (0, 2), "z": (0, 1)}[axis]
    intervals = [
        _split_interval(from_pos[index], to_pos[index])
        for index in plane_axes
    ]
    boxes: list[list[float | int]] = []
    for first, second in itertools.product(*intervals):
        sub_element = dict(element)
        sub_from = list(from_pos)
        sub_to = list(to_pos)
        sub_from[plane_axes[0]], sub_to[plane_axes[0]] = first
        sub_from[plane_axes[1]], sub_to[plane_axes[1]] = second
        sub_element["from"] = sub_from
        sub_element["to"] = sub_to
        sub_element["inflate"] = 0
        boxes.append(element_collision_box(sub_element))
    return boxes


def enclosing_box(boxes: list[list[float | int]]) -> list[list[float | int]]:
    if not boxes:
        raise ValueError("Cannot enclose an empty model")
    minimum = [min(float(box[index]) for box in boxes) for index in range(3)]
    maximum = [max(float(box[index + 3]) for box in boxes) for index in range(3)]
    return [[rounded(value) for value in minimum + maximum]]


def scaled_uv(uv: list[float], width: int, height: int) -> list[float | int]:
    if len(uv) != 4:
        raise ValueError(f"Invalid UV: {uv}")
    result = [
        rounded(float(uv[0]) * 16 / width), rounded(float(uv[1]) * 16 / height),
        rounded(float(uv[2]) * 16 / width), rounded(float(uv[3]) * 16 / height),
    ]
    if any(float(value) < -1e-6 or float(value) > 16.000001 for value in result):
        raise ValueError(f"Normalized UV outside 0..16: {result}")
    return result


def referenced_texture_index(source: dict[str, Any], stem: str) -> int:
    references: set[int] = set()
    for element in source.get("elements", []):
        for face in element.get("faces", {}).values():
            if face is not None and face.get("enabled") is not False and face.get("texture") is not None:
                references.add(int(face["texture"]))
    if len(references) != 1:
        raise ValueError(f"{stem} must reference exactly one texture: {sorted(references)}")
    index = next(iter(references))
    texture = source.get("textures", [])[index]
    expected = f"{stem}.png"
    if texture.get("name") != expected or texture.get("relative_path") != expected:
        raise ValueError(f"Texture metadata mismatch in {stem}")
    return index


def export_element(
    element: dict[str, Any], width: int, height: int, texture_index: int
) -> dict[str, Any]:
    from_pos, to_pos = _inflated_bounds(element)
    output: dict[str, Any] = {
        "from": [rounded(value) for value in from_pos],
        "to": [rounded(value) for value in to_pos],
        "shade": bool(element.get("shade", True)),
        "faces": {},
    }
    rotation = _rotation_parts(element)
    if rotation is not None:
        axis, angle, origin = rotation
        output["rotation"] = {
            "origin": [rounded(value) for value in origin],
            "axis": axis,
            "angle": rounded(angle),
            "rescale": bool(element.get("rescale", False)),
        }
    for direction, face in element.get("faces", {}).items():
        if face is None or face.get("enabled") is False:
            continue
        if int(face["texture"]) != texture_index:
            raise ValueError("A face references an unexpected texture")
        exported: dict[str, Any] = {
            "uv": scaled_uv(face["uv"], width, height),
            "texture": "#0",
        }
        if "rotation" in face:
            exported["rotation"] = int(face["rotation"])
        if face.get("cullface"):
            exported["cullface"] = str(face["cullface"])
        tint = face.get("tint", face.get("tintindex"))
        if tint is not None and int(tint) >= 0:
            exported["tintindex"] = int(tint)
        output["faces"][direction] = exported
    if not output["faces"]:
        raise ValueError("Visible cube has no textured faces")
    return output


def export_model(spec: AssetSpec) -> tuple[dict[str, Any], list[list[float | int]], int, int]:
    source = json.loads(spec.source_model.read_text(encoding="utf-8"))
    if source.get("meta", {}).get("model_format") != "java_block":
        raise ValueError(f"Not a java_block model: {spec.source_model}")
    if str(source.get("name", "")).lower() != spec.source_stem:
        raise ValueError(f"Model name/file mismatch: {spec.source_model}")
    width = int(source["resolution"]["width"])
    height = int(source["resolution"]["height"])
    texture_index = referenced_texture_index(source, spec.source_stem)
    raw_elements = source.get("elements", [])
    visible = [
        element for element in raw_elements
        if element.get("type", "cube") == "cube"
        and element.get("export", True) is not False
        and element.get("visibility") is not False
    ]
    elements = [export_element(element, width, height, texture_index) for element in visible]
    # Only legacy poles retain the detailed shape policy. Every new block gets
    # one AABB around the placed model, without generating tiny intermediate cells.
    box_exporter = detailed_collision_boxes if spec.collision_mode == "detailed" else lambda element: [element_collision_box(element)]
    detailed_boxes = [
        box
        for element in visible
        for box in box_exporter(element)
    ]
    boxes = detailed_boxes if spec.collision_mode == "detailed" else enclosing_box(detailed_boxes)
    model: dict[str, Any] = {
        "credit": "Crzay津仔 / Made with Blockbench",
        "ambientocclusion": bool(source.get("ambientocclusion", True)),
        "gui_light": "front" if source.get("front_gui_light", False) else "side",
        "texture_size": [width, height],
        "textures": {
            "0": f"{MOD_ID}:block/{spec.identifier}",
            "particle": f"{MOD_ID}:block/{spec.identifier}",
        },
        "elements": elements,
    }
    if "display" in source:
        model["display"] = copy.deepcopy(source["display"])
    if spec.identifier in GUI_DISPLAY_OVERRIDES:
        model.setdefault("display", {})["gui"] = copy.deepcopy(GUI_DISPLAY_OVERRIDES[spec.identifier])
    return model, boxes, len(raw_elements), len(raw_elements) - len(visible)


def blockstate(identifier: str) -> dict[str, Any]:
    model = f"{MOD_ID}:block/{identifier}"
    return {"variants": {
        "facing=north": {"model": model},
        "facing=east": {"model": model, "y": 90},
        "facing=south": {"model": model, "y": 180},
        "facing=west": {"model": model, "y": 270},
    }}


def loot_table(identifier: str) -> dict[str, Any]:
    return {
        "type": "minecraft:block",
        "pools": [{
            "rolls": 1,
            "bonus_rolls": 0,
            "entries": [{"type": "minecraft:item", "name": f"{MOD_ID}:{identifier}"}],
            "conditions": [{"condition": "minecraft:survives_explosion"}],
        }],
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-input-root", type=Path, required=True,
                        help="Private phase-one folder containing the three naming workbooks")
    parser.add_argument("--phase-two-input-root", type=Path, required=True,
                        help="Private phase-two folder containing the supplied naming workbooks")
    arguments = parser.parse_args()
    specs = discover_specs(arguments.private_input_root, arguments.phase_two_input_root)
    for generated_root in (ASSET_ROOT, DATA_ROOT):
        resolved = generated_root.resolve()
        if resolved != generated_root.absolute() or not resolved.is_relative_to(ROOT.resolve()):
            raise ValueError(f"Refusing to replace a redirected resource directory: {generated_root}")
        if generated_root.exists():
            shutil.rmtree(generated_root)

    models = ASSET_ROOT / "models" / "block"
    items = ASSET_ROOT / "models" / "item"
    states = ASSET_ROOT / "blockstates"
    textures = ASSET_ROOT / "textures" / "block"
    loot = DATA_ROOT / "loot_tables" / "blocks"

    languages: dict[str, dict[str, str]] = {locale: {} for locale in LOCALES}
    for locale, names in GROUP_TRANSLATIONS.items():
        names = names + EXTRA_GROUPS[locale]
        languages[locale].update({
            f"itemGroup.{MOD_ID}.{category}": name
            for category, name in zip(CATEGORY_ORDER, names, strict=True)
        })

    catalog: list[dict[str, Any]] = []
    category_values: dict[str, list[str]] = {category: [] for category in CATEGORY_ORDER}
    raw_count = visible_count = excluded_count = collision_count = 0

    for spec in specs:
        model, boxes, raw, excluded = export_model(spec)
        raw_count += raw
        excluded_count += excluded
        visible_count += len(model["elements"])
        collision_count += len(boxes)
        write_json(models / f"{spec.identifier}.json", model)
        write_json(items / f"{spec.identifier}.json", {"parent": f"{MOD_ID}:block/{spec.identifier}"})
        write_json(states / f"{spec.identifier}.json", blockstate(spec.identifier))
        write_json(loot / f"{spec.identifier}.json", loot_table(spec.identifier))
        textures.mkdir(parents=True, exist_ok=True)
        shutil.copy2(spec.source_texture, textures / f"{spec.identifier}.png")

        key = f"block.{MOD_ID}.{spec.identifier}"
        for locale in LOCALES:
            languages[locale][key] = localized_name(spec, locale)
        category_values[spec.category].append(f"{MOD_ID}:{spec.identifier}")
        catalog.append({
            "id": spec.identifier,
            "category": spec.category,
            "kind": spec.kind,
            "placement": spec.placement,
            "collision_mode": spec.collision_mode,
            "light_level": spec.light_level,
            "source_folder": spec.source_folder,
            "source_stem": spec.source_stem,
            "collision_boxes": boxes,
        })

    category_counts = {
        category: sum(spec.category == category for spec in specs)
        for category in CATEGORY_ORDER
    }
    kind_counts = {
        kind: sum(spec.kind == kind for spec in specs)
        for kind in EXPECTED_KIND_COUNTS
    }
    if category_counts != EXPECTED_CATEGORY_COUNTS or kind_counts != EXPECTED_KIND_COUNTS:
        raise ValueError(f"Generated inventory mismatch: {category_counts}, {kind_counts}")
    if collision_count != 351:
        raise ValueError(f"Expected 351 collision boxes, generated {collision_count}")
    if raw_count != visible_count + excluded_count:
        raise ValueError("Element accounting mismatch")

    expected_keys = None
    for locale, values in languages.items():
        if len(values) != 218 or any(not value.strip() for value in values.values()):
            raise ValueError(f"Incomplete language {locale}: {len(values)} keys")
        keys = set(values)
        if expected_keys is None:
            expected_keys = keys
        elif keys != expected_keys:
            raise ValueError(f"Language key mismatch in {locale}")
        if any(key.startswith("tooltip.") for key in keys):
            raise ValueError("Street Props must not add item tooltip notes")
        write_json(ASSET_ROOT / "lang" / f"{locale}.json", dict(sorted(values.items())))

    write_json(ASSET_ROOT / "block_catalog.json", {"schema": 1, "blocks": catalog})
    all_values: list[str] = []
    tag_names = {category: category for category in CATEGORY_ORDER}
    for category, values in category_values.items():
        sorted_values = sorted(values)
        all_values.extend(sorted_values)
        write_json(
            DATA_ROOT / "tags" / "blocks" / f"{tag_names[category]}.json",
            {"replace": False, "values": sorted_values},
        )
    write_json(
        DATA_ROOT / "tags" / "blocks" / "all_blocks.json",
        {"replace": False, "values": sorted(all_values)},
    )
    write_json(
        RESOURCE_ROOT / "pack.mcmeta",
        {"pack": {"pack_format": 15, "description": "JINZAI Street Props resources"}},
    )
    print(
        f"Generated {len(specs)} blocks ({category_counts}), {visible_count} visible elements, "
        f"{collision_count} collision boxes, and {len(languages)} languages."
    )


if __name__ == "__main__":
    main()
