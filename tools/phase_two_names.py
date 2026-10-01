"""Public localization rules for the 1.1.2 decorative additions (MIT)."""

ENGLISH_NAMES = {
    "公交站-路线牌（右侧）": "Bus Stop Route Sign (Right)",
    "公交站-路线牌（左侧）": "Bus Stop Route Sign (Left)",
    "公交站-雨棚": "Bus Stop Shelter 1",
    "公交站-雨棚2": "Bus Stop Shelter 2",
    "公交站-双雨棚": "Bus Stop Double Shelter 1",
    "公交站-双雨棚2": "Bus Stop Double Shelter 2",
    "公交站-凳子": "Bus Stop Bench",
    "灯箱公交牌-底部": "Lightbox Bus Stop Sign - Bottom",
    "灯箱公交牌-顶部": "Lightbox Bus Stop Sign - Top",
    "交通锥1": "Traffic Cone 1", "交通锥2": "Traffic Cone 2",
    "交通锥横杆": "Traffic Cone Crossbar",
    "交通锥横杆-拐角": "Traffic Cone Crossbar - Corner",
    "施工栅栏1": "Construction Barrier 1", "施工栅栏2": "Construction Barrier 2",
    "灰色路灯杆底部": "Gray Street Light Pole Bottom",
    "灰色路灯杆": "Gray Street Light Pole",
    "白色路灯杆（B类路灯分支专用）": "White Street Light Pole (B-Series Branches)",
    "警车警灯": "Police Light Bar",
    "出租车标志": "Taxi Sign", "出租车标志-带LED": "Taxi Sign with LED",
}
for number in range(1, 5):
    ENGLISH_NAMES[f"公交站-广告牌{number}"] = f"Bus Stop Advertising Panel {number}"
for chinese, english in (("白色", "White"), ("蓝色", "Blue"), ("黑色", "Black")):
    ENGLISH_NAMES[f"{chinese}路灯杆底部"] = f"{english} Street Light Pole Bottom"
    ENGLISH_NAMES[f"{chinese}路灯杆底部-半砖"] = f"{english} Street Light Pole Bottom - Half Slab"
for chinese, english in (
    ("橙色轿车", "Orange Sedan"), ("黑色轿车", "Black Sedan"),
    ("白色轿车", "White Sedan"), ("红色轿车", "Red Sedan"),
    ("蓝色轿车", "Blue Sedan"), ("绿色轿车", "Green Sedan"),
    ("警车", "Police Car"), ("出租车", "Taxi"),
    ("白色面包车", "White Van"), ("邮政面包车", "Postal Van"), ("救护车", "Ambulance"),
):
    for part, translated in (("车头", "Front"), ("车尾", "Rear"),
                             ("车尾2", "Rear 2"), ("车尾3-皮卡", "Rear 3 - Pickup")):
        ENGLISH_NAMES[f"{chinese}（{part}）"] = f"{english} ({translated})"

EXTRA_GROUPS = {
    "zh_cn": ("市政设施", "汽车载具"), "en_us": ("Municipal Facilities", "Vehicles"),
    "ar_sa": ("المرافق البلدية", "المركبات"), "de_de": ("Stadtausstattung", "Fahrzeuge"),
    "es_es": ("Mobiliario urbano", "Vehículos"), "fr_fr": ("Mobilier urbain", "Véhicules"),
    "hi_in": ("नगर सुविधाएँ", "वाहन"), "id_id": ("Fasilitas Kota", "Kendaraan"),
    "ja_jp": ("都市設備", "車両"), "ko_kr": ("도시 시설", "차량"),
    "pt_br": ("Mobiliário Urbano", "Veículos"), "ru_ru": ("Городская инфраструктура", "Транспорт"),
    "tr_tr": ("Kent Donatıları", "Araçlar"),
}

# Ordered phrases are replaced longest first by the main generator, together
# with its existing color, light, pole and bus-sign vocabulary.
_TERMS = (
    "Bus Stop Route Sign", "Bus Stop Double Shelter", "Bus Stop Shelter", "Bus Stop Bench",
    "Bus Stop Advertising Panel", "Traffic Cone Crossbar", "Traffic Cone", "Construction Barrier",
    "Street Light Pole", "B-Series Branches", "Half Slab", "Police Light Bar", "Taxi Sign with LED",
    "Taxi Sign", "Police Car", "Postal Van", "Ambulance", "Sedan", "Van", "Taxi", "Pickup",
    "Front", "Rear", "Right", "Left", "Corner", "Lightbox", "Orange", "Red", "Gray",
)
_VALUES = {
    "ar_sa": (
        "لوحة خطوط محطة الحافلات", "مظلة مزدوجة لمحطة الحافلات", "مظلة محطة الحافلات", "مقعد محطة الحافلات",
        "لوحة إعلانات محطة الحافلات", "عارضة مخروط المرور", "مخروط المرور", "حاجز أعمال البناء",
        "عمود إنارة الشارع", "أذرع الفئة B", "نصف بلاطة", "شريط أضواء الشرطة", "لافتة سيارة أجرة بإضاءة LED",
        "لافتة سيارة أجرة", "سيارة شرطة", "شاحنة بريد صغيرة", "سيارة إسعاف", "سيارة سيدان", "شاحنة صغيرة", "سيارة أجرة", "بيك أب",
        "مقدمة", "مؤخرة", "يمين", "يسار", "زاوية", "صندوق مضيء", "برتقالي", "أحمر", "رمادي",
    ),
    "de_de": (
        "Buslinienanzeige", "Doppeltes Buswartehäuschen", "Buswartehäuschen", "Haltestellenbank",
        "Haltestellen-Werbetafel", "Leitkegel-Querträger", "Leitkegel", "Baustellenabsperrung",
        "Laternenmast", "Ausleger der B-Serie", "Halbe Stufe", "Polizei-Lichtbalken", "Taxischild mit LED",
        "Taxischild", "Polizeiauto", "Posttransporter", "Krankenwagen", "Limousine", "Kleintransporter", "Taxi", "Pickup",
        "Vorderteil", "Heck", "Rechts", "Links", "Ecke", "Leuchtkasten", "Orange", "Rot", "Grau",
    ),
    "es_es": (
        "Panel de rutas de autobús", "Marquesina doble de autobús", "Marquesina de autobús", "Banco de parada de autobús",
        "Panel publicitario de parada", "Travesaño de cono de tráfico", "Cono de tráfico", "Barrera de obras",
        "Poste de farola", "Brazos de la serie B", "Media losa", "Barra de luces policial", "Letrero de taxi con LED",
        "Letrero de taxi", "Coche de policía", "Furgoneta postal", "Ambulancia", "Sedán", "Furgoneta", "Taxi", "Camioneta",
        "Parte delantera", "Parte trasera", "Derecha", "Izquierda", "Esquina", "Caja luminosa", "Naranja", "Rojo", "Gris",
    ),
    "fr_fr": (
        "Panneau des lignes de bus", "Abribus double", "Abribus", "Banc d'arrêt de bus",
        "Panneau publicitaire d'arrêt de bus", "Traverse de cône de chantier", "Cône de chantier", "Barrière de chantier",
        "Poteau de lampadaire", "Bras de série B", "Demi-dalle", "Rampe lumineuse de police", "Enseigne de taxi à LED",
        "Enseigne de taxi", "Voiture de police", "Fourgon postal", "Ambulance", "Berline", "Fourgonnette", "Taxi", "Pick-up",
        "Avant", "Arrière", "Droite", "Gauche", "Angle", "Caisson lumineux", "Orange", "Rouge", "Gris",
    ),
    "hi_in": (
        "बस स्टॉप मार्ग पट्ट", "बस स्टॉप दोहरा शेड", "बस स्टॉप शेड", "बस स्टॉप बेंच",
        "बस स्टॉप विज्ञापन पट्ट", "यातायात शंकु आड़ी छड़", "यातायात शंकु", "निर्माण अवरोधक",
        "स्ट्रीट लाइट खंभा", "B-श्रृंखला शाखाएँ", "आधा स्लैब", "पुलिस लाइट बार", "LED वाला टैक्सी संकेत",
        "टैक्सी संकेत", "पुलिस कार", "डाक वैन", "एम्बुलेंस", "सेडान", "वैन", "टैक्सी", "पिकअप",
        "अगला भाग", "पिछला भाग", "दायाँ", "बायाँ", "कोना", "लाइटबॉक्स", "नारंगी", "लाल", "धूसर",
    ),
    "id_id": (
        "Papan Rute Halte Bus", "Atap Ganda Halte Bus", "Atap Halte Bus", "Bangku Halte Bus",
        "Papan Iklan Halte Bus", "Palang Kerucut Lalu Lintas", "Kerucut Lalu Lintas", "Pagar Konstruksi",
        "Tiang Lampu Jalan", "Lengan Seri B", "Setengah Lempeng", "Lampu Rotator Polisi", "Papan Taksi dengan LED",
        "Papan Taksi", "Mobil Polisi", "Van Pos", "Ambulans", "Sedan", "Van", "Taksi", "Pikap",
        "Depan", "Belakang", "Kanan", "Kiri", "Sudut", "Kotak Lampu", "Oranye", "Merah", "Abu-abu",
    ),
    "ja_jp": (
        "バス停路線案内板", "バス停ダブルシェルター", "バス停シェルター", "バス停ベンチ",
        "バス停広告パネル", "カラーコーンバー", "カラーコーン", "工事用フェンス",
        "街路灯ポール", "B型アーム用", "ハーフブロック", "パトカー警光灯", "LED付きタクシー表示灯",
        "タクシー表示灯", "パトカー", "郵便バン", "救急車", "セダン", "バン", "タクシー", "ピックアップ",
        "前部", "後部", "右側", "左側", "コーナー", "電照式", "オレンジ", "赤", "灰色",
    ),
    "ko_kr": (
        "버스 정류장 노선 안내판", "버스 정류장 이중 쉼터", "버스 정류장 쉼터", "버스 정류장 벤치",
        "버스 정류장 광고판", "안전 고깔 연결봉", "안전 고깔", "공사장 울타리",
        "가로등 기둥", "B형 가로등 암용", "반 블록", "경찰차 경광등", "LED 택시 표시등",
        "택시 표시등", "경찰차", "우편 밴", "구급차", "세단", "밴", "택시", "픽업",
        "앞부분", "뒷부분", "오른쪽", "왼쪽", "모서리", "라이트박스", "주황", "빨강", "회색",
    ),
    "pt_br": (
        "Placa de Linhas de Ônibus", "Abrigo Duplo de Ônibus", "Abrigo de Ônibus", "Banco de Ponto de Ônibus",
        "Painel Publicitário de Ponto de Ônibus", "Travessa de Cone de Trânsito", "Cone de Trânsito", "Barreira de Obras",
        "Poste de Iluminação Pública", "Braços da Série B", "Meia Laje", "Giroflex Policial", "Letreiro de Táxi com LED",
        "Letreiro de Táxi", "Carro de Polícia", "Van Postal", "Ambulância", "Sedã", "Van", "Táxi", "Picape",
        "Frente", "Traseira", "Direita", "Esquerda", "Canto", "Caixa Luminosa", "Laranja", "Vermelho", "Cinza",
    ),
    "ru_ru": (
        "Указатель автобусных маршрутов", "Двойной навес автобусной остановки", "Навес автобусной остановки", "Скамейка автобусной остановки",
        "Рекламный щит автобусной остановки", "Перекладина дорожного конуса", "Дорожный конус", "Строительное ограждение",
        "Столб уличного фонаря", "Кронштейны серии B", "Полуплита", "Полицейская световая балка", "Знак такси с LED",
        "Знак такси", "Полицейский автомобиль", "Почтовый фургон", "Скорая помощь", "Седан", "Фургон", "Такси", "Пикап",
        "Передняя часть", "Задняя часть", "Справа", "Слева", "Угол", "Световой короб", "Оранжевый", "Красный", "Серый",
    ),
    "tr_tr": (
        "Otobüs Hattı Tabelası", "Çift Otobüs Durağı Sığınağı", "Otobüs Durağı Sığınağı", "Otobüs Durağı Bankı",
        "Otobüs Durağı Reklam Panosu", "Trafik Konisi Çapraz Çubuğu", "Trafik Konisi", "İnşaat Bariyeri",
        "Sokak Lambası Direği", "B Serisi Kollar", "Yarım Basamak", "Polis Tepe Lambası", "LED Taksi Tabelası",
        "Taksi Tabelası", "Polis Arabası", "Posta Minibüsü", "Ambulans", "Sedan", "Minibüs", "Taksi", "Pikap",
        "Ön", "Arka", "Sağ", "Sol", "Köşe", "Işıklı Kutu", "Turuncu", "Kırmızı", "Gri",
    ),
}
EXTRA_TERMS = {locale: dict(zip(_TERMS, values, strict=True)) for locale, values in _VALUES.items()}
