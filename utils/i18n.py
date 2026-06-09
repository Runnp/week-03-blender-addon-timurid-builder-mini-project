"""
i18n.py
Multi-language UI label system for the Registan Generator.

Languages: EN (default), UZ (O'zbek), RU (Русский)

Usage:
    from .utils.i18n import t, set_lang, current_lang
    t("Generate Building")
"""

_LANG = "EN"

TRANSLATIONS: dict[str, dict[str, str]] = {

    # =========================================================
    # UZBEK
    # =========================================================
    "UZ": {
        # Panel titles
        "Registan Generator":           "Registon Generatori",
        "Style Preset":                 "Uslub Shabloni",
        "Detail Level":                 "Detal Darajasi",
        "Material Palette":             "Material Palitrasi",
        "Snapshots":                    "Saqlab Qo'yish",
        "Developer Tools":              "Ishlab Chiqaruvchi Vositalari",

        # Preset & LOD
        "Load":                         "Yuklash",
        "Apply LOD":                    "LOD Qo'llash",
        "Language":                     "Til",

        # Randomizer
        "Randomizer":                   "Tasodiflashtirish",
        "Full Roll":                    "To'liq Aylanish",
        "Tweak":                        "Sozlash",
        "Tweak %":                      "Sozlash %",
        "Seed":                         "Urug'",

        # Building base
        "Building Base":                "Bino Asosi",
        "Building Width":               "Bino Kengligi",
        "Building Depth":               "Bino Chuqurligi",
        "Building Height":              "Bino Balandligi",

        # Dome
        "Dome":                         "Gumbaz",
        "Dome Size":                    "Gumbaz O'lchami",
        "Dome Segments":                "Gumbaz Segmentlari",
        "Dome Band":                    "Gumbaz Lentasi",

        # Minarets
        "Minarets":                     "Minaralar",
        "Minaret Count":                "Minara Soni",
        "Minaret Height":               "Minara Balandligi",
        "Minaret Radius":               "Minara Radiusi",
        "Minaret Segments":             "Minara Segmentlari",
        "Serefe Balcony":               "Serefe Balkoni",

        # Arch & sub-features
        "Arch Entrance":                "Ravoq Kirishi",
        "Arch Count":                   "Ravoq Soni",
        "Arch Height":                  "Ravoq Balandligi",
        "Arch Width":                   "Ravoq Kengligi",
        "Muqarnas Vault":               "Muqarnas Gumbazi",
        "Muqarnas Tiers":               "Muqarnas Qavatlar",
        "Pishtaq Portal":               "Pishtaq Darvozasi",
        "Portal Height":                "Darvoza Balandligi",
        "Portal Width":                 "Darvoza Kengligi",
        "Crown Steps":                  "Toj Zinapoyalari",
        "Iwan Hall":                    "Ayvon Zali",
        "Iwan Depth":                   "Ayvon Chuqurligi",
        "Side Niches":                  "Yon Toq Nishlar",
        "Niches Per Side":              "Har Tomonda Nish",

        # Courtyard
        "Courtyard":                    "Hovli",
        "Courtyard Size":               "Hovli O'lchami",
        "Hauz Fountain":                "Hovuz",
        "Rim Spouts":                   "Chetki Oqimlar",

        # Girih
        "Girih Relief":                 "Girih Naqshi",
        "Cell Size":                    "Katak O'lchami",
        "Extrusion":                    "Chiqish",

        # Arcade
        "Wall Arcade":                  "Devor Arkalari",
        "Arcade Bays":                  "Arkada Boylari",
        "Arcade Height":                "Arkada Balandligi",
        "Back Wall Too":                "Orqa Devor Ham",
        "Apex Roundels":                "Tepa Medalyonlar",

        # Symmetry
        "Symmetry":                     "Simmetriya",

        # Complex
        "Full Complex (3 Buildings)":   "To'liq Majmua (3 Bino)",
        "Building Gap":                 "Binolar Orasidagi Masofa",
        "Auto Tile Materials":          "Avtomatik Kafel Materiallari",
        "Generate Complex":             "Majmua Yaratish",
        "Remove Complex":               "Majmuani O'chirish",

        # Action buttons
        "Generate Building":            "Bino Yaratish",
        "Apply Tile Materials":         "Kafel Materiallarini Qo'llash",
        "Apply Advanced Shaders":       "Kengaytirilgan Sheyderlar",
        "Weather":                      "Ob-Havo Effekti",
        "Apply":                        "Qo'llash",
        "Remove":                       "O'chirish",
        "Frames":                       "Kadrlar",
        "Animate":                      "Animatsiya",
        "Setup Scene":                  "Sahna Sozlash",
        "Export OBJ…":                  "OBJ Eksport…",
        "Export Floor Plan SVG…":       "Qavat Rejasi SVG…",
        "Remove Scene Setup":           "Sahna Sozlamalarini O'chirish",
        "Clear Scene":                  "Sahnani Tozalash",

        # Weathering
        "Weathering":                   "Eski Ko'rinish",
        "Build Frames":                 "Qurilish Kadrlari",

        # Dev panel
        "Scene Stats":                  "Sahna Statistikasi",
        "Generate History":             "Yaratish Tarixi",
        "Dev Actions":                  "Ishlab Chiqish Amallari",
        "Reload Addon":                 "Plaginni Qayta Yuklash",
        "Reload config.json":           "Konfigni Qayta Yuklash",
        "Write Default config.json":    "Standart Konfig Yozish",
        "Print Stats Report":           "Statistika Hisobotini Chop Etish",
        "Print Props to Console":       "Xususiyatlarni Konsolga Chiqarish",
        "Changelog":                    "O'zgarishlar Jurnali",

        # Snapshots panel
        "Slot Name":                    "Slot Nomi",
        "Save":                         "Saqlash",
        "Load Snapshot":                "Yuklash",
        "Delete":                       "O'chirish",
        "Snapshot Name":                "Saqlash Nomi",
        "Saved Snapshots":              "Saqlangan Snapshotlar",
        "No snapshots saved yet.":      "Hali snapshot saqlanmagan.",

        # Palette panel
        "Live colour editors":          "Jonli Rang Muharrirlari",
        "Reset to Timurid Defaults":    "Temuriy Standartlariga Qaytarish",
        "Terracotta (Walls)":           "Terrakota (Devorlar)",
        "Azure Tile (Dome)":            "Ko'k Kafel (Gumbaz)",
        "White Marble (Fountain)":      "Oq Marmar (Hovuz)",
        "Gold (Trim)":                  "Oltin (Bezak)",
        "Sand (Ground)":                "Qum (Er)",
        "Dark Brick (Frames)":          "To'q G'isht (Ramkalar)",

        # History
        "◀  Back":                      "◀  Orqaga",
        "Forward  ▶":                   "Oldinga  ▶",

        # LOD labels
        "LOW":                          "PAST",
        "MID":                          "O'RTA",
        "HIGH":                         "YUQORI",
    },

    # =========================================================
    # RUSSIAN
    # =========================================================
    "RU": {
        # Panel titles
        "Registan Generator":           "Генератор Регистана",
        "Style Preset":                 "Стиль Пресета",
        "Detail Level":                 "Уровень Детализации",
        "Material Palette":             "Палитра Материалов",
        "Snapshots":                    "Снимки Состояния",
        "Developer Tools":              "Инструменты Разработчика",

        # Preset & LOD
        "Load":                         "Загрузить",
        "Apply LOD":                    "Применить LOD",
        "Language":                     "Язык",

        # Randomizer
        "Randomizer":                   "Рандомизатор",
        "Full Roll":                    "Полный Рандом",
        "Tweak":                        "Подстройка",
        "Tweak %":                      "Подстройка %",
        "Seed":                         "Зерно",

        # Building base
        "Building Base":                "Основание Здания",
        "Building Width":               "Ширина Здания",
        "Building Depth":               "Глубина Здания",
        "Building Height":              "Высота Здания",

        # Dome
        "Dome":                         "Купол",
        "Dome Size":                    "Размер Купола",
        "Dome Segments":                "Сегменты Купола",
        "Dome Band":                    "Пояс Купола",

        # Minarets
        "Minarets":                     "Минареты",
        "Minaret Count":                "Количество Минаретов",
        "Minaret Height":               "Высота Минарета",
        "Minaret Radius":               "Радиус Минарета",
        "Minaret Segments":             "Сегменты Минарета",
        "Serefe Balcony":               "Балкон Шерефе",

        # Arch & sub-features
        "Arch Entrance":                "Арочный Вход",
        "Arch Count":                   "Количество Арок",
        "Arch Height":                  "Высота Арки",
        "Arch Width":                   "Ширина Арки",
        "Muqarnas Vault":               "Мукарнас Свод",
        "Muqarnas Tiers":               "Ярусы Мукарнаса",
        "Pishtaq Portal":               "Пештак Портал",
        "Portal Height":                "Высота Портала",
        "Portal Width":                 "Ширина Портала",
        "Crown Steps":                  "Ступени Короны",
        "Iwan Hall":                    "Зал Айвана",
        "Iwan Depth":                   "Глубина Айвана",
        "Side Niches":                  "Боковые Ниши",
        "Niches Per Side":              "Ниш на Сторону",

        # Courtyard
        "Courtyard":                    "Двор",
        "Courtyard Size":               "Размер Двора",
        "Hauz Fountain":                "Хауз Фонтан",
        "Rim Spouts":                   "Бортовые Струи",

        # Girih
        "Girih Relief":                 "Рельеф Гириха",
        "Cell Size":                    "Размер Ячейки",
        "Extrusion":                    "Выдавливание",

        # Arcade
        "Wall Arcade":                  "Стенная Аркада",
        "Arcade Bays":                  "Пролёты Аркады",
        "Arcade Height":                "Высота Аркады",
        "Back Wall Too":                "Также Задняя Стена",
        "Apex Roundels":                "Вершинные Медальоны",

        # Symmetry
        "Symmetry":                     "Симметрия",

        # Complex
        "Full Complex (3 Buildings)":   "Полный Комплекс (3 Здания)",
        "Building Gap":                 "Расстояние Между Зданиями",
        "Auto Tile Materials":          "Авто Плиточные Материалы",
        "Generate Complex":             "Создать Комплекс",
        "Remove Complex":               "Удалить Комплекс",

        # Action buttons
        "Generate Building":            "Создать Здание",
        "Apply Tile Materials":         "Применить Плиточные Материалы",
        "Apply Advanced Shaders":       "Применить Продвинутые Шейдеры",
        "Weather":                      "Состаривание",
        "Apply":                        "Применить",
        "Remove":                       "Удалить",
        "Frames":                       "Кадры",
        "Animate":                      "Анимировать",
        "Setup Scene":                  "Настроить Сцену",
        "Export OBJ…":                  "Экспорт OBJ…",
        "Export Floor Plan SVG…":       "Экспорт Плана SVG…",
        "Remove Scene Setup":           "Удалить Настройки Сцены",
        "Clear Scene":                  "Очистить Сцену",

        # Weathering
        "Weathering":                   "Состаривание",
        "Build Frames":                 "Кадры Анимации",

        # Dev panel
        "Scene Stats":                  "Статистика Сцены",
        "Generate History":             "История Генерации",
        "Dev Actions":                  "Действия Разработчика",
        "Reload Addon":                 "Перезагрузить Аддон",
        "Reload config.json":           "Перезагрузить Конфиг",
        "Write Default config.json":    "Записать Конфиг по Умолчанию",
        "Print Stats Report":           "Вывести Отчёт Статистики",
        "Print Props to Console":       "Вывести Параметры в Консоль",
        "Changelog":                    "История Изменений",

        # Snapshots panel
        "Slot Name":                    "Имя Слота",
        "Save":                         "Сохранить",
        "Load Snapshot":                "Загрузить",
        "Delete":                       "Удалить",
        "Snapshot Name":                "Имя Снимка",
        "Saved Snapshots":              "Сохранённые Снимки",
        "No snapshots saved yet.":      "Снимки ещё не сохранены.",

        # Palette panel
        "Live colour editors":          "Редакторы Цвета в Реальном Времени",
        "Reset to Timurid Defaults":    "Сбросить к Тимуридским Настройкам",
        "Terracotta (Walls)":           "Терракота (Стены)",
        "Azure Tile (Dome)":            "Лазурная Плитка (Купол)",
        "White Marble (Fountain)":      "Белый Мрамор (Фонтан)",
        "Gold (Trim)":                  "Золото (Отделка)",
        "Sand (Ground)":                "Песок (Земля)",
        "Dark Brick (Frames)":          "Тёмный Кирпич (Рамки)",

        # History
        "◀  Back":                      "◀  Назад",
        "Forward  ▶":                   "Вперёд  ▶",

        # LOD labels
        "LOW":                          "НИЗКИЙ",
        "MID":                          "СРЕДНИЙ",
        "HIGH":                         "ВЫСОКИЙ",
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
