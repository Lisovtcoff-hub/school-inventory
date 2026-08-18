from app.schemas.report import ReportCatalogItem


REPORT_OO2_SECTION_2_1 = "OO2_SECTION_2_1"
REPORT_CABINET_PASSPORT = "CABINET_PASSPORT"


def get_available_reports() -> list[ReportCatalogItem]:
    """Список отчётов, доступных в приложении.

    Небольшой registry нужен, чтобы новые отчёты добавлялись в один понятный
    список, а не зашивались только во Flutter-меню.
    """
    return [
        ReportCatalogItem(
            code=REPORT_OO2_SECTION_2_1,
            title="ОО-2. Раздел 2.1",
            description="Сведения о технических средствах обучения и оборудовании",
        ),
        ReportCatalogItem(
            code=REPORT_CABINET_PASSPORT,
            title="Паспорт учебного кабинета",
            description="Автоматическое формирование паспорта кабинета на основе техники",
        ),
    ]
