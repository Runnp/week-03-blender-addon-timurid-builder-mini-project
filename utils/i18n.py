"""
i18n.py
Multi-language UI label system for the Registan Generator.

Supported languages:
  EN  — English (default)
  UZ  — Uzbek (O'zbek)
  RU  — Russian (Русский)

Usage:
    from utils.i18n import t, set_lang, current_lang
    t("Generate Building")   # returns translated string

The translation table covers all UI-facing strings in panels.py and
the dev_panel. Keys are English strings. Fallback: if a key isn't
translated, the English key is returned unchanged.
"""

_LANG = "EN"   # module-level active language

TRANSLATIONS: dict[str, dict[str, str]] = {
    # ------------------------------------------------------------------ EN
    # (English is the key — no entry needed)

    # ------------------------------------------------------------------ UZ
    "UZ": {
        "Registan Generator":     "Registon Generatori",
        "Style Preset":           "Uslub Shabloni",
        "Load":                   "Yuklash",
        "Apply LOD":              "LOD Qo'llash",
        "Detail Level":           "Detal Darajasi",
        "Randomizer":             "Tasodiflashtirish",
        "Full Roll":              "To'liq Aylanish",
        "Tweak":                  "Sozlash",
        "Tweak %":                "Sozlash %",
        "Building Base":          "Bino Asosi",
        "Building Width":         "Bino Kengligi",
        "Building Depth":         "Bino Chuqurligi",
        "Building Height":        "Bino Balandligi",
        "Dome":                   "Gumbaz",
        "Dome Size":              "Gumbaz O'lchami",
        "Dome Segments":          "Gumbaz Segmentlari",
        "Minarets":               "Minaralar",
        "Minaret Count":          "Minara Soni",
        "Minaret Height":         "Minara Balandligi",
        "Minaret Radius":         "Minara Radiusi",
        "Serefe Balcony":         "Serefe Balkoni",
        "Arch Entrance":          "Ravoq Kirishi",
        "Arch Count":             "Ravoq Soni",
        "Arch Height":            "Ravoq Balandligi",
        "Arch Width":             "Ravoq Kengligi",
        "Muqarnas Vault":         "Muqarnas Gumbazi",
        "Muqarnas Tiers":         "Muqarnas Qavatlar",
        "Pishtaq Portal":         "Pishtaq Darvozasi",
        "Portal Height":          "Darvoza Balandligi",
        "Portal Width":           "Darvoza Kengligi",
        "Crown Steps":            "Toj Zinapoyalari",
        "Courtyard":              "Hovli",
        "Courtyard Size":         "Hovli O'lchami",
        "Hauz Fountain":          "Hovuz",
        "Rim Spouts":             "Chetki Oqimlar",
        "Girih Relief":           "Girih Naqshi",
        "Cell Size":              "Katak O'lchami",
        "Extrusion":              "Chiqish",
        "Dome Band":              "Gumbaz Lentasi",
        "Symmetry":               "Simmetriya",
        "Full Complex (3 Buildings)": "To'liq Majmua (3 Bino)",
        "Building Gap":           "Binolar Orasidagi Masofa",
        "Auto Tile Materials":    "Avtomatik Kafel Materiallari",
        "Generate Complex":       "Majmua Yaratish",
        "Generate Building":      "Bino Yaratish",
        "Apply Tile Materials":   "Kafel Materiallarini Qo'llash",
        "Weather":                "Ob-Havo Effekti",
        "Apply":                  "Qo'llash",
        "Frames":                 "Kadrlar",
        "Animate":                "Animatsiya",
        "Setup Scene":            "Sahna Sozlash",
        "Export OBJ…":            "OBJ Eksport…",
        "Export Floor Plan SVG…": "Qavat Rejasi SVG…",
        "Remove Scene Setup":     "Sahna Sozlamalarini O'chirish",
        "Clear Scene":            "Sahnani Tozalash",
        "Developer Tools":        "Ishlab Chiqaruvchi Vositalari",
        "Scene Stats":            "Sahna Statistikasi",
        "Generate History":       "Yaratish Tarixi",
        "Snapshots":              "Saqlab Qo'yish",
        "Save":                   "Saqlash",
        "Delete":                 "O'chirish",
        "Snapshot Name":          "Saqlash Nomi",
        "Build Frames":           "Qurilish Kadrlari",
        "Weathering":             "Eski Ko'rinish",
        "Seed":                   "Urug'",
    },

    # ------------------------------------------------------------------ RU
    "RU": {
        "Registan Generator":     "Генератор Регистана",
        "Style Preset":           "Стиль Пресета",
        "Load":                   "Загрузить",
        "Apply LOD":              "Применить LOD",
        "Detail Level":           "Уровень Детали",
        "Randomizer":             "Рандомизатор",
        "Full Roll":              "Полный Рандом",
        "Tweak":                  "Подстройка",
        "Tweak %":                "Подстройка %",
        "Building Base":          "Основание Здания",
        "Building Width":         "Ширина Здания",
        "Building Depth":         "Глубина Здания",
        "Building Height":        "Высота Здания",
        "Dome":                   "Купол",
        "Dome Size":              "Размер Купола",
        "Dome Segments":          "Сегменты Купола",
        "Minarets":               "Минареты",
        "Minaret Count":          "Количество Минаретов",
        "Minaret Height":         "Высота Минарета",
        "Minaret Radius":         "Радиус Минарета",
        "Serefe Balcony":         "Балкон Шерефе",
        "Arch Entrance":          "Арочный Вход",
        "Arch Count":             "Количество Арок",
        "Arch Height":            "Высота Арки",
        "Arch Width":             "Ширина Арки",
        "Muqarnas Vault":         "Мукарнас Свод",
        "Muqarnas Tiers":         "Ярусы Мукарнаса",
        "Pishtaq Portal":         "Пештак Портал",
        "Portal Height":          "Высота Портала",
        "Portal Width":           "Ширина Портала",
        "Crown Steps":            "Ступени Короны",
        "Courtyard":              "Двор",
        "Courtyard Size":         "Размер Двора",
        "Hauz Fountain":          "Хауз Фонтан",
        "Rim Spouts":             "Бортовые Струи",
        "Girih Relief":           "Рельеф Гириха",
        "Cell Size":              "Размер Ячейки",
        "Extrusion":              "Выдавливание",
        "Dome Band":              "Пояс Купола",
        "Symmetry":               "Симметрия",
        "Full Complex (3 Buildings)": "Полный Комплекс (3 Здания)",
        "Building Gap":           "Расстояние Между Зданиями",
        "Auto Tile Materials":    "Авто Плиточные Материалы",
        "Generate Complex":       "Создать Комплекс",
        "Generate Building":      "Создать Здание",
        "Apply Tile Materials":   "Применить Плиточные Материалы",
        "Weather":                "Состаривание",
        "Apply":                  "Применить",
        "Frames":                 "Кадры",
        "Animate":                "Анимировать",
        "Setup Scene":            "Настроить Сцену",
        "Export OBJ…":            "Экспорт OBJ…",
        "Export Floor Plan SVG…": "Экспорт Плана SVG…",
        "Remove Scene Setup":     "Удалить Настройки Сцены",
        "Clear Scene":            "Очистить Сцену",
        "Developer Tools":        "Инструменты Разработчика",
        "Scene Stats":            "Статистика Сцены",
        "Generate History":       "История Генерации",
        "Snapshots":              "Снимки Состояния",
        "Save":                   "Сохранить",
        "Delete":                 "Удалить",
        "Snapshot Name":          "Имя Снимка",
        "Build Frames":           "Кадры Анимации",
        "Weathering":             "Состаривание",
        "Seed":                   "Зерно",
    },
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def t(key: str) -> str:
    """Return the translated string for *key* in the current language."""
    if _LANG == "EN":
        return key
    return TRANSLATIONS.get(_LANG, {}).get(key, key)


def set_lang(lang_code: str):
    """Set active language. Accepts: 'EN', 'UZ', 'RU'."""
    global _LANG
    if lang_code in ("EN", "UZ", "RU"):
        _LANG = lang_code


def current_lang() -> str:
    return _LANG


def available_langs() -> list[tuple[str, str, str]]:
    """Return Blender EnumProperty items list."""
    return [
        ("EN", "English",  "English UI labels"),
        ("UZ", "O'zbek",   "Oʻzbekcha teglari"),
        ("RU", "Русский",  "Русские ярлыки"),
    ]