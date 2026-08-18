from datetime import datetime
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, status
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from app.utils.datetime import utc_now
from app.core.constants import (
    ASSET_STATUS_IN_REPAIR,
    ASSET_STATUS_IN_USE,
    ASSET_STATUS_LOST,
    ASSET_STATUS_NEEDS_REPAIR,
    ASSET_STATUS_WRITTEN_OFF,
    ASSET_TYPE_COMPUTER,
    ASSET_TYPE_INTERACTIVE_BOARD,
    ASSET_TYPE_LAPTOP,
    ASSET_TYPE_MFU,
    ASSET_TYPE_MONITOR,
    ASSET_TYPE_NETWORK_DEVICE,
    ASSET_TYPE_PRINTER,
    ASSET_TYPE_PROJECTOR,
    ASSET_TYPE_SERVER,
    ASSET_TYPE_TABLET,
    ASSET_TYPE_UPS,
    REPORT_CATEGORY_COPIER,
    REPORT_CATEGORY_DESKTOP_PC,
    REPORT_CATEGORY_INFO_TERMINAL,
    REPORT_CATEGORY_INTERACTIVE_BOARD,
    REPORT_CATEGORY_LAPTOP,
    REPORT_CATEGORY_MFU,
    REPORT_CATEGORY_PRINTER,
    REPORT_CATEGORY_PROJECTOR,
    REPORT_CATEGORY_SCANNER,
    REPORT_CATEGORY_TABLET,
    REPORT_CATEGORY_TERMINAL,
)
from app.db.models.asset import Asset
from app.db.models.user import User
from app.repositories.asset_repository import list_asset_rooms_by_organization, list_assets_by_room
from app.repositories.organization_repository import get_organization_by_id
from app.schemas.report import (
    CabinetPassportAsset,
    CabinetPassportOrganization,
    CabinetPassportResponse,
    CabinetPassportSection,
    CabinetPassportSummary,
    ReportWarning,
)


DEFAULT_FONT_NAME = "Helvetica"
REGISTERED_FONT_NAME = "AppCabinetReportRegularFont"

TECHNICAL_TEACHING_TYPES = {
    ASSET_TYPE_PROJECTOR,
    ASSET_TYPE_INTERACTIVE_BOARD,
}
TECHNICAL_TEACHING_CATEGORIES = {
    REPORT_CATEGORY_PROJECTOR,
    REPORT_CATEGORY_INTERACTIVE_BOARD,
    REPORT_CATEGORY_INFO_TERMINAL,
}

COMPUTER_TYPES = {
    ASSET_TYPE_COMPUTER,
    ASSET_TYPE_LAPTOP,
    ASSET_TYPE_TABLET,
    ASSET_TYPE_SERVER,
    ASSET_TYPE_MONITOR,
}
COMPUTER_CATEGORIES = {
    REPORT_CATEGORY_DESKTOP_PC,
    REPORT_CATEGORY_LAPTOP,
    REPORT_CATEGORY_TABLET,
    REPORT_CATEGORY_TERMINAL,
}

PERIPHERAL_TYPES = {
    ASSET_TYPE_PRINTER,
    ASSET_TYPE_MFU,
    ASSET_TYPE_NETWORK_DEVICE,
    ASSET_TYPE_UPS,
}
PERIPHERAL_CATEGORIES = {
    REPORT_CATEGORY_PRINTER,
    REPORT_CATEGORY_MFU,
    REPORT_CATEGORY_SCANNER,
    REPORT_CATEGORY_COPIER,
}


def _register_pdf_font() -> str:
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


def get_cabinet_passport_locations_for_current_user(
    db: Session,
    *,
    current_user: User,
) -> list[str]:
    return list_asset_rooms_by_organization(
        db,
        organization_id=current_user.organization_id,
    )


def _to_report_asset(asset: Asset) -> CabinetPassportAsset:
    return CabinetPassportAsset(
        asset_code=asset.asset_code,
        name=asset.name,
        type=asset.type,
        model=asset.model,
        serial_number=asset.serial_number,
        inventory_number=asset.inventory_number,
        status=asset.status,
        responsible_person=asset.responsible_person,
        is_used_for_education=asset.is_used_for_education,
    )


def _is_technical_teaching_asset(asset: Asset) -> bool:
    return (
        asset.type in TECHNICAL_TEACHING_TYPES
        or asset.report_category in TECHNICAL_TEACHING_CATEGORIES
    )


def _is_computer_asset(asset: Asset) -> bool:
    return asset.type in COMPUTER_TYPES or asset.report_category in COMPUTER_CATEGORIES


def _is_peripheral_asset(asset: Asset) -> bool:
    return asset.type in PERIPHERAL_TYPES or asset.report_category in PERIPHERAL_CATEGORIES


def _build_sections(assets: list[Asset]) -> list[CabinetPassportSection]:
    technical: list[CabinetPassportAsset] = []
    computers: list[CabinetPassportAsset] = []
    peripherals: list[CabinetPassportAsset] = []
    other: list[CabinetPassportAsset] = []

    for asset in assets:
        report_asset = _to_report_asset(asset)

        if _is_technical_teaching_asset(asset):
            technical.append(report_asset)
        elif _is_computer_asset(asset):
            computers.append(report_asset)
        elif _is_peripheral_asset(asset):
            peripherals.append(report_asset)
        else:
            other.append(report_asset)

    return [
        CabinetPassportSection(title="Технические средства обучения", items=technical),
        CabinetPassportSection(title="Компьютерная техника", items=computers),
        CabinetPassportSection(title="Периферийное оборудование", items=peripherals),
        CabinetPassportSection(title="Другое оборудование", items=other),
    ]


def _build_warnings(assets: list[Asset], *, location: str) -> list[ReportWarning]:
    warnings: list[ReportWarning] = []

    if not assets:
        warnings.append(
            ReportWarning(
                message="В выбранном кабинете не найдено оборудование.",
            )
        )
        return warnings

    has_written_off_or_lost = any(
        asset.status in {ASSET_STATUS_WRITTEN_OFF, ASSET_STATUS_LOST}
        for asset in assets
    )
    if has_written_off_or_lost:
        warnings.append(
            ReportWarning(
                message=(
                    "В кабинете есть оборудование со статусом списано/утеряно. "
                    "Проверьте, нужно ли включать его в паспорт."
                ),
            )
        )

    has_missing_inventory_number = any(
        not (asset.inventory_number or "").strip()
        for asset in assets
    )
    if has_missing_inventory_number:
        warnings.append(
            ReportWarning(
                message="У части оборудования не заполнен инвентарный номер.",
            )
        )

    return warnings


def calculate_cabinet_passport_for_current_user(
    db: Session,
    *,
    current_user: User,
    location: str,
) -> CabinetPassportResponse:
    location = location.strip()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Нужно выбрать кабинет/локацию",
        )

    organization = get_organization_by_id(db, current_user.organization_id)
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Организация не найдена",
        )

    assets = list_assets_by_room(
        db,
        organization_id=current_user.organization_id,
        room=location,
    )

    summary = CabinetPassportSummary(
        total_assets=len(assets),
        working_assets=sum(1 for asset in assets if asset.status == ASSET_STATUS_IN_USE),
        needs_repair=sum(
            1
            for asset in assets
            if asset.status in {ASSET_STATUS_IN_REPAIR, ASSET_STATUS_NEEDS_REPAIR}
        ),
        written_off=sum(1 for asset in assets if asset.status == ASSET_STATUS_WRITTEN_OFF),
    )

    return CabinetPassportResponse(
        location=location,
        organization=CabinetPassportOrganization(
            name=organization.name,
            short_name=None,
        ),
        summary=summary,
        assets=[_to_report_asset(asset) for asset in assets],
        sections=_build_sections(assets),
        warnings=_build_warnings(assets, location=location),
    )


def _paragraph(text: str | None, style: ParagraphStyle) -> Paragraph:
    safe_text = "—" if text is None else str(text)
    return Paragraph(safe_text.replace("\n", "<br/>"), style)


def generate_cabinet_passport_pdf_for_current_user(
    db: Session,
    *,
    current_user: User,
    location: str,
) -> bytes:
    report = calculate_cabinet_passport_for_current_user(
        db,
        current_user=current_user,
        location=location,
    )

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1 * cm,
        rightMargin=1 * cm,
        topMargin=1 * cm,
        bottomMargin=1 * cm,
        title="Cabinet passport",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CabinetTitle",
        parent=styles["Title"],
        fontName=PDF_FONT_NAME,
        fontSize=14,
        leading=17,
        alignment=1,
        spaceAfter=8,
    )
    normal_style = ParagraphStyle(
        "CabinetNormal",
        parent=styles["Normal"],
        fontName=PDF_FONT_NAME,
        fontSize=8,
        leading=10,
    )
    small_style = ParagraphStyle(
        "CabinetSmall",
        parent=styles["Normal"],
        fontName=PDF_FONT_NAME,
        fontSize=7,
        leading=9,
    )

    story = [
        _paragraph(report.title, title_style),
        _paragraph(f"Организация: {report.organization.name}", normal_style),
        _paragraph(f"Кабинет/локация: {report.location}", normal_style),
        _paragraph(f"Дата формирования: {utc_now().strftime('%d.%m.%Y')}", normal_style),
        Spacer(1, 0.25 * cm),
    ]

    summary_table = Table(
        [
            [
                _paragraph("Всего", small_style),
                _paragraph("В работе", small_style),
                _paragraph("В ремонте / требует ремонта", small_style),
                _paragraph("Списано", small_style),
            ],
            [
                _paragraph(str(report.summary.total_assets), small_style),
                _paragraph(str(report.summary.working_assets), small_style),
                _paragraph(str(report.summary.needs_repair), small_style),
                _paragraph(str(report.summary.written_off), small_style),
            ],
        ],
        colWidths=[3 * cm, 3 * cm, 5.5 * cm, 3 * cm],
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), PDF_FONT_NAME),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 0.35 * cm))

    story.append(_paragraph("Оборудование кабинета", normal_style))
    table_data = [
        [
            _paragraph("Код", small_style),
            _paragraph("Название", small_style),
            _paragraph("Тип", small_style),
            _paragraph("Модель", small_style),
            _paragraph("Серийный №", small_style),
            _paragraph("Инв. №", small_style),
            _paragraph("Статус", small_style),
            _paragraph("Ответственный", small_style),
            _paragraph("Учебное", small_style),
        ]
    ]

    for asset in report.assets:
        table_data.append(
            [
                _paragraph(asset.asset_code, small_style),
                _paragraph(asset.name, small_style),
                _paragraph(asset.type, small_style),
                _paragraph(asset.model or "—", small_style),
                _paragraph(asset.serial_number or "—", small_style),
                _paragraph(asset.inventory_number or "—", small_style),
                _paragraph(asset.status, small_style),
                _paragraph(asset.responsible_person or "—", small_style),
                _paragraph("Да" if asset.is_used_for_education else "Нет", small_style),
            ]
        )

    equipment_table = Table(
        table_data,
        colWidths=[3.1 * cm, 4.4 * cm, 2.5 * cm, 3 * cm, 3 * cm, 2.5 * cm, 2.4 * cm, 3.2 * cm, 1.6 * cm],
        repeatRows=1,
    )
    equipment_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), PDF_FONT_NAME),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(equipment_table)

    if report.warnings:
        story.append(Spacer(1, 0.35 * cm))
        story.append(_paragraph("Предупреждения", normal_style))
        warning_data = [[_paragraph("Сообщение", small_style)]]
        for warning in report.warnings:
            warning_data.append([_paragraph(warning.message, small_style)])

        warning_table = Table(warning_data, colWidths=[25.7 * cm], repeatRows=1)
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
