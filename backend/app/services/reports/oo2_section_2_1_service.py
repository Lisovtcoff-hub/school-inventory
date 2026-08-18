from io import BytesIO
from pathlib import Path
from typing import Iterable

from fastapi import HTTPException, status
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import (
    ASSET_TYPE_COMPUTER,
    ASSET_TYPE_INTERACTIVE_BOARD,
    ASSET_TYPE_LAPTOP,
    ASSET_TYPE_MFU,
    ASSET_TYPE_PRINTER,
    ASSET_TYPE_PROJECTOR,
    ASSET_TYPE_TABLET,
    REPORT_CATEGORY_COPIER,
    REPORT_CATEGORY_DESKTOP_PC,
    REPORT_CATEGORY_INFO_TERMINAL,
    REPORT_CATEGORY_INTERACTIVE_BOARD,
    REPORT_CATEGORY_LAPTOP,
    REPORT_CATEGORY_MFU,
    REPORT_CATEGORY_NOT_INCLUDED,
    REPORT_CATEGORY_OTHER,
    REPORT_CATEGORY_PRINTER,
    REPORT_CATEGORY_PROJECTOR,
    REPORT_CATEGORY_SCANNER,
    REPORT_CATEGORY_TABLET,
    REPORT_CATEGORY_TERMINAL,
)
from app.db.models.asset import Asset
from app.db.models.user import User
from app.repositories.organization_repository import get_organization_by_id
from app.schemas.report import OO2Section21Response, OO2Section21Row, ReportWarning


DEFAULT_FONT_NAME = "Helvetica"
REGISTERED_FONT_NAME = "AppReportRegularFont"

PC_REPORT_CATEGORIES = {
    REPORT_CATEGORY_DESKTOP_PC,
    REPORT_CATEGORY_LAPTOP,
    REPORT_CATEGORY_TABLET,
    REPORT_CATEGORY_TERMINAL,
}

TYPE_TO_REPORT_CATEGORY = {
    ASSET_TYPE_COMPUTER: REPORT_CATEGORY_DESKTOP_PC,
    ASSET_TYPE_LAPTOP: REPORT_CATEGORY_LAPTOP,
    ASSET_TYPE_TABLET: REPORT_CATEGORY_TABLET,
    ASSET_TYPE_PROJECTOR: REPORT_CATEGORY_PROJECTOR,
    ASSET_TYPE_INTERACTIVE_BOARD: REPORT_CATEGORY_INTERACTIVE_BOARD,
    ASSET_TYPE_PRINTER: REPORT_CATEGORY_PRINTER,
    ASSET_TYPE_MFU: REPORT_CATEGORY_MFU,
}


def _register_pdf_font() -> str:
    """
    Регистрирует TTF-шрифт для кириллицы в PDF.

    Шрифт не кладём в проект, а ищем системный: Windows Arial или Linux DejaVu.
    """
    possible_font_paths = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    ]

    for font_path in possible_font_paths:
        if font_path.exists():
            try:
                pdfmetrics.registerFont(TTFont(REGISTERED_FONT_NAME, str(font_path)))
                return REGISTERED_FONT_NAME
            except Exception:
                continue

    return DEFAULT_FONT_NAME


PDF_FONT_NAME = _register_pdf_font()


def _get_assets_for_report(db: Session, *, organization_id: int) -> list[Asset]:
    statement = (
        select(Asset)
        .where(
            Asset.organization_id == organization_id,
            Asset.deleted_at.is_(None),
            Asset.include_in_reports.is_(True),
        )
        .order_by(Asset.id.asc())
    )

    return list(db.scalars(statement).all())


def _resolve_report_category(asset: Asset) -> tuple[str | None, bool]:
    """
    Возвращает категорию отчёта и признак, что она была угадана по Asset.type.

    Это нужно, чтобы старые карточки техники не пропали из отчёта сразу после миграции.
    Пользователь сможет позже проставить report_category явно.
    """
    if asset.report_category:
        if asset.report_category == REPORT_CATEGORY_NOT_INCLUDED:
            return None, False

        return asset.report_category, False

    guessed_category = TYPE_TO_REPORT_CATEGORY.get(asset.type)

    if guessed_category:
        return guessed_category, True

    return None, False


def _count_assets(
    assets_with_categories: Iterable[tuple[Asset, str]],
    *,
    categories: set[str],
    condition: str | None = None,
) -> int:
    count = 0

    for asset, category in assets_with_categories:
        if category not in categories:
            continue

        if condition == "has_lan" and not asset.has_lan:
            continue

        if condition == "has_internet" and not asset.has_internet:
            continue

        if condition == "has_intranet" and not asset.has_intranet:
            continue

        if condition == "received_in_current_year" and not asset.received_in_current_year:
            continue

        count += 1

    return count


def _count_education(
    assets_with_categories: Iterable[tuple[Asset, str]],
    *,
    categories: set[str],
    student_available: bool = False,
) -> int:
    count = 0

    for asset, category in assets_with_categories:
        if category not in categories:
            continue

        if student_available:
            if asset.is_available_for_students:
                count += 1
        else:
            if asset.is_used_for_education:
                count += 1

    return count


def _build_row(
    assets_with_categories: list[tuple[Asset, str]],
    *,
    row_code: str,
    name: str,
    categories: set[str],
    condition: str | None = None,
    with_education_columns: bool = False,
) -> OO2Section21Row:
    filtered_total = _count_assets(
        assets_with_categories,
        categories=categories,
        condition=condition,
    )

    if not with_education_columns:
        return OO2Section21Row(
            row_code=row_code,
            name=name,
            total=filtered_total,
            used_for_education=None,
            available_for_students=None,
        )

    if condition is None:
        education_source = [
            item for item in assets_with_categories if item[1] in categories
        ]
    else:
        education_source = []
        for asset, category in assets_with_categories:
            if category not in categories:
                continue
            if condition == "has_lan" and not asset.has_lan:
                continue
            if condition == "has_internet" and not asset.has_internet:
                continue
            if condition == "has_intranet" and not asset.has_intranet:
                continue
            if condition == "received_in_current_year" and not asset.received_in_current_year:
                continue
            education_source.append((asset, category))

    return OO2Section21Row(
        row_code=row_code,
        name=name,
        total=filtered_total,
        used_for_education=_count_education(
            education_source,
            categories=categories,
            student_available=False,
        ),
        available_for_students=_count_education(
            education_source,
            categories=categories,
            student_available=True,
        ),
    )


def calculate_oo2_section_2_1_for_current_user(
    db: Session,
    *,
    current_user: User,
    year: int,
) -> OO2Section21Response:
    """
    Считает ОО-2, раздел 2.1 по активной технике организации.

    Этот расчёт не претендует на заполнение всего официального бланка ОО-2.
    Он формирует расчётную таблицу по подразделу 2.1 на основе базы assets.
    """
    organization = get_organization_by_id(db, current_user.organization_id)

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Организация не найдена",
        )

    assets = _get_assets_for_report(
        db,
        organization_id=current_user.organization_id,
    )

    warnings: list[ReportWarning] = []
    assets_with_categories: list[tuple[Asset, str]] = []

    for asset in assets:
        category, was_guessed = _resolve_report_category(asset)

        if category is None:
            warnings.append(
                ReportWarning(
                    asset_id=asset.id,
                    asset_code=asset.asset_code,
                    message=(
                        "Техника не попала в ОО-2 раздел 2.1: "
                        "не указана report_category и невозможно определить её по type"
                    ),
                )
            )
            continue

        if category == REPORT_CATEGORY_OTHER:
            warnings.append(
                ReportWarning(
                    asset_id=asset.id,
                    asset_code=asset.asset_code,
                    message=(
                        "Есть оборудование с категорией 'Другое', которое не включено "
                        "в строки ОО-2 раздела 2.1. Проверьте корректность категории."
                    ),
                )
            )
            continue

        if was_guessed:
            warnings.append(
                ReportWarning(
                    asset_id=asset.id,
                    asset_code=asset.asset_code,
                    message=(
                        "report_category не указана явно; "
                        f"для расчёта использована категория '{category}' по полю type"
                    ),
                )
            )

        assets_with_categories.append((asset, category))

    rows = [
        _build_row(
            assets_with_categories,
            row_code="01",
            name="Персональные компьютеры - всего",
            categories=PC_REPORT_CATEGORIES,
            with_education_columns=True,
        ),
        _build_row(
            assets_with_categories,
            row_code="02",
            name="Ноутбуки, нетбуки и другие портативные компьютеры",
            categories={REPORT_CATEGORY_LAPTOP},
            with_education_columns=True,
        ),
        _build_row(
            assets_with_categories,
            row_code="03",
            name="Планшетные компьютеры",
            categories={REPORT_CATEGORY_TABLET},
            with_education_columns=True,
        ),
        _build_row(
            assets_with_categories,
            row_code="04",
            name="ПК в составе локальных вычислительных сетей",
            categories=PC_REPORT_CATEGORIES,
            condition="has_lan",
            with_education_columns=True,
        ),
        _build_row(
            assets_with_categories,
            row_code="05",
            name="ПК с доступом к Интернету",
            categories=PC_REPORT_CATEGORIES,
            condition="has_internet",
            with_education_columns=True,
        ),
        _build_row(
            assets_with_categories,
            row_code="06",
            name="ПК с доступом к Интранет-порталу организации",
            categories=PC_REPORT_CATEGORIES,
            condition="has_intranet",
            with_education_columns=True,
        ),
        _build_row(
            assets_with_categories,
            row_code="07",
            name="Вычислительная техника, полученная в отчётном году",
            categories=PC_REPORT_CATEGORIES,
            condition="received_in_current_year",
            with_education_columns=True,
        ),
        _build_row(
            assets_with_categories,
            row_code="08",
            name="Электронные терминалы / инфоматы / информационные киоски",
            categories={REPORT_CATEGORY_INFO_TERMINAL},
        ),
        _build_row(
            assets_with_categories,
            row_code="09",
            name="Электронные терминалы с доступом к Интернету",
            categories={REPORT_CATEGORY_INFO_TERMINAL},
            condition="has_internet",
        ),
        _build_row(
            assets_with_categories,
            row_code="10",
            name="Мультимедийные проекторы",
            categories={REPORT_CATEGORY_PROJECTOR},
        ),
        _build_row(
            assets_with_categories,
            row_code="11",
            name="Интерактивные доски",
            categories={REPORT_CATEGORY_INTERACTIVE_BOARD},
        ),
        _build_row(
            assets_with_categories,
            row_code="12",
            name="Принтеры",
            categories={REPORT_CATEGORY_PRINTER},
        ),
        _build_row(
            assets_with_categories,
            row_code="13",
            name="Сканеры",
            categories={REPORT_CATEGORY_SCANNER},
        ),
        _build_row(
            assets_with_categories,
            row_code="14",
            name="Многофункциональные устройства",
            categories={REPORT_CATEGORY_MFU},
        ),
        _build_row(
            assets_with_categories,
            row_code="15",
            name="Ксероксы",
            categories={REPORT_CATEGORY_COPIER},
        ),
    ]

    return OO2Section21Response(
        report_year=year,
        organization_id=organization.id,
        organization_name=organization.name,
        rows=rows,
        warnings=warnings,
    )


def _paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(str(text).replace("\n", "<br/>"), style)


def generate_oo2_section_2_1_pdf_for_current_user(
    db: Session,
    *,
    current_user: User,
    year: int,
) -> bytes:
    """
    Генерирует PDF-помощник для заполнения ОО-2, раздел 2.1.
    """
    report = calculate_oo2_section_2_1_for_current_user(
        db,
        current_user=current_user,
        year=year,
    )

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1 * cm,
        rightMargin=1 * cm,
        topMargin=1 * cm,
        bottomMargin=1 * cm,
        title="OO-2 section 2.1",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "AppTitle",
        parent=styles["Title"],
        fontName=PDF_FONT_NAME,
        fontSize=14,
        leading=17,
        alignment=1,
        spaceAfter=8,
    )
    normal_style = ParagraphStyle(
        "AppNormal",
        parent=styles["Normal"],
        fontName=PDF_FONT_NAME,
        fontSize=8,
        leading=10,
    )
    small_style = ParagraphStyle(
        "AppSmall",
        parent=styles["Normal"],
        fontName=PDF_FONT_NAME,
        fontSize=7,
        leading=9,
    )

    story = [
        _paragraph("ОО-2. Раздел 2.1", title_style),
        _paragraph(report.title, title_style),
        _paragraph(f"Организация: {report.organization_name}", normal_style),
        _paragraph(f"Отчётный год: {report.report_year}", normal_style),
        Spacer(1, 0.25 * cm),
    ]

    table_data = [
        [
            _paragraph("Строка", small_style),
            _paragraph("Показатель", small_style),
            _paragraph("Всего", small_style),
            _paragraph("В учебных целях", small_style),
            _paragraph("Доступно обучающимся", small_style),
        ]
    ]

    for row in report.rows:
        table_data.append(
            [
                _paragraph(row.row_code, small_style),
                _paragraph(row.name, small_style),
                _paragraph(str(row.total), small_style),
                _paragraph("-" if row.used_for_education is None else str(row.used_for_education), small_style),
                _paragraph("-" if row.available_for_students is None else str(row.available_for_students), small_style),
            ]
        )

    table = Table(
        table_data,
        colWidths=[1.7 * cm, 13.2 * cm, 2.1 * cm, 3.2 * cm, 3.8 * cm],
        repeatRows=1,
    )
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), PDF_FONT_NAME),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (2, 0), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    story.append(table)

    story.append(Spacer(1, 0.35 * cm))
    story.append(_paragraph("Примечание", normal_style))
    story.append(
        _paragraph(
            "PDF является внутренним помощником для проверки расчёта. "
            "Официальный шаблон ОО-2 можно будет подключить позже отдельным экспортёром.",
            small_style,
        )
    )

    if report.warnings:
        story.append(Spacer(1, 0.35 * cm))
        story.append(_paragraph("Предупреждения по данным", normal_style))

        warning_data = [[_paragraph("ID", small_style), _paragraph("Код", small_style), _paragraph("Сообщение", small_style)]]
        for warning in report.warnings:
            warning_data.append(
                [
                    _paragraph("-" if warning.asset_id is None else str(warning.asset_id), small_style),
                    _paragraph(warning.asset_code or "-", small_style),
                    _paragraph(warning.message, small_style),
                ]
            )

        warning_table = Table(
            warning_data,
            colWidths=[1.5 * cm, 4.2 * cm, 18.3 * cm],
            repeatRows=1,
        )
        warning_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), PDF_FONT_NAME),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(warning_table)

    document.build(story)
    buffer.seek(0)

    return buffer.getvalue()
