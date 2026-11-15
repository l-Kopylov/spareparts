# Единая точка правды по значениям для форм и будущей выгрузки.
# Категории деталей, марки/модели техники — в БД (Category, CarModel, MotoModel),
# а вот эти перечни — кодовые константы.

# ---------- Тип техники ----------
SCOPE_CHOICES = [
    ("auto", "Авто"),
    ("moto", "Мото"),
]


PART_TYPES_AUTO = [
    "Двигатель", "Кузов", "Подвеска", "Трансмиссия", "Тормозная система",
    "Электрика", "Электроника (блоки управления)", "Оптика", "Салон",
    "Охлаждение", "Выхлоп", "Топливная система", "Прочее",
]

PART_TYPES_MOTO = [
    "Двигатель",
    "ЦПГ",
    "Трансмиссия / вариатор",
    "Рама",
    "Подвеска",
    "Тормозная система",
    "Электрика",
    "Пластик / обвес",
    "Топливная и выхлопная системы",    
    "Система охлаждения",              
    "Прочее",
]

# ---------- Состояние ----------
CONDITIONS = [
    ("new", "Новое"),
    ("used", "Б/у"),
]

# ---------- Колёса: общее ----------
VEHICLE_KINDS = [
    ("car", "Легковые"),
    ("moto", "Мото"),
]

PRODUCT_FORMS = [
    ("tire", "Шины"),
    ("rim", "Диски"),
    ("set", "Комплект"),
]

SEASONS = [
    ("summer", "Лето"),
    ("winter_stud", "Зима шипованная"),
    ("winter_studless", "Зима нешипованная"),
    ("allseason", "Всесезонные"),
]

RIM_TYPES = [
    ("steel", "Штампованные"),
    ("alloy", "Литые"),
    ("forged", "Кованые"),
]

# ---------- Авто: шины ----------
CAR_TIRE_WIDTHS = [
    "125", "135", "145", "155", "165", "175", "185", "195",
    "205", "215", "225", "235", "245", "255", "265", "275",
    "285", "295", "305", "315", "325", "335", "355",
]

CAR_TIRE_PROFILES = [
    "20", "25", "30", "35", "40", "45", "50", "55",
    "60", "65", "70", "75", "80", "85", "90",
]

CAR_TIRE_DIAMETERS = [
    "12", "13", "14", "15", "16", "17", "18", "19",
    "20", "21", "22", "23", "24",
]

# ---------- Авто: диски ----------
RIM_WIDTHS = [
    "4", "4.5", "5", "5.5", "6", "6.5", "7", "7.5", "8",
    "8.5", "9", "9.5", "10", "10.5", "11", "11.5", "12", "13", "14",
]

RIM_DIAMETERS = [
    "10", "11", "12", "13", "14", "15", "16", "17", "18",
    "19", "20", "21", "22", "23", "24",
]

# ---------- Разболтовка (только авто) ----------
BOLT_COUNTS = [3, 4, 5, 6, 8, 10]

PCD_DIAMETERS = [
    "98", "100", "108", "110", "112", "114.3", "115", "118",
    "120", "127", "130", "139.7", "150", "165.1", "180",
]

# ---------- Мото: шины ----------
MOTO_TIRE_WIDTHS = [
    "60", "70", "80", "90", "100", "110", "120", "130",
    "140", "150", "160", "170", "180", "190", "200",
]

MOTO_TIRE_PROFILES = [
    "35", "40", "45", "50", "55", "60", "65", "70", "80", "90", "100",
]

MOTO_TIRE_DIAMETERS = [
    "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "21",
]

MOTO_RIM_DIAMETERS = [
    "10", "12", "13", "14", "15", "16", "17", "18", "19", "21",
]

DESCRIPTION_LIMIT = 3000

# ---------- Колёса: какие поля показывать/требовать по типу товара ----------
# Ключ — значение product_form из PRODUCT_FORMS.
# show    — поля, которые видны в форме для этого типа.
# required — из них обязательные.

WHEEL_FORM_FIELDS = {
    "tire": {
        "show": [
            "tire_width", "tire_profile", "tire_diameter",
            "season", "tread_remain",
        ],
        "required": [
            "tire_width", "tire_profile", "tire_diameter", "season",
        ],
    },
    "rim": {
        "show": [
            "rim_width", "rim_diameter", "rim_type",
            "pcd_bolt_count", "pcd_diameter", "offset_et", "center_bore",
        ],
        "required": [
            "rim_diameter", "rim_type",
            "pcd_bolt_count", "pcd_diameter", "offset_et",
        ],
    },
    "set": {
        "show": [
            "tire_width", "tire_profile", "tire_diameter",
            "season", "tread_remain",
            "rim_width", "rim_diameter", "rim_type",
            "pcd_bolt_count", "pcd_diameter", "offset_et", "center_bore",
        ],
        "required": [
            "tire_width", "tire_profile", "tire_diameter", "season",
            "rim_diameter", "rim_type",
            "pcd_bolt_count", "pcd_diameter", "offset_et",
        ],
    },
}

# Какие категории допустимы для каждого kind (для импорта Авито)
ALLOWED_CATEGORIES = {
    "wheel": ["Колёса и шины", "Шины", "Диски", "Колёса"],  # + то, что Авито может прислать
    "auto": PART_TYPES_AUTO,
    "moto": PART_TYPES_MOTO,
}

# ---------- Проверка целостности ----------
for _pair in (CONDITIONS + VEHICLE_KINDS + PRODUCT_FORMS + SEASONS + RIM_TYPES):
    assert _pair[0], f"Пустое value в choices: {_pair}"
assert len(set(PART_TYPES_AUTO)) == len(PART_TYPES_AUTO), "Дубли в PART_TYPES_AUTO"
assert len(set(PART_TYPES_MOTO)) == len(PART_TYPES_MOTO), "Дубли в PART_TYPES_MOTO"
# проверка WHEEL_FORM_FIELDS: ключи = значения product_form, show ⊆ required
_pf_values = {v for v, _ in PRODUCT_FORMS}
assert set(WHEEL_FORM_FIELDS) == _pf_values, (
    f"WHEEL_FORM_FIELDS должен покрывать все product_form: {_pf_values}"
)
for _pf, _conf in WHEEL_FORM_FIELDS.items():
    assert set(_conf["required"]).issubset(set(_conf["show"])), (
        f"В {_pf}: required содержит поля не из show"
    )
