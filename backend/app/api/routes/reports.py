from datetime import datetime
from io import BytesIO
from urllib.parse import quote

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.utils.datetime import utc_now
from app.api.deps import CurrentUser, DbSession
from app.schemas.report import (
    CabinetPassportResponse,
    OO2Section21Response,
    ReportCatalogItem,
)
from app.services.reports.cabinet_passport_service import (
    calculate_cabinet_passport_for_current_user,
    generate_cabinet_passport_pdf_for_current_user,
    get_cabinet_passport_locations_for_current_user,
)
from app.services.reports.oo2_section_2_1_service import (
    calculate_oo2_section_2_1_for_current_user,
    generate_oo2_section_2_1_pdf_for_current_user,
)
from app.services.reports.registry import get_available_reports


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=list[ReportCatalogItem])
def get_reports(
    current_user: CurrentUser,
) -> list[ReportCatalogItem]:
    """Получить список доступных отчётов приложения."""
    return get_available_reports()


@router.get("/cabinet-passport/locations", response_model=list[str])
def get_cabinet_passport_locations(
    db: DbSession,
    current_user: CurrentUser,
) -> list[str]:
    """Получить список кабинетов/локаций по технике текущей организации."""
    return get_cabinet_passport_locations_for_current_user(
        db,
        current_user=current_user,
    )


@router.get("/cabinet-passport", response_model=CabinetPassportResponse)
def get_cabinet_passport(
    db: DbSession,
    current_user: CurrentUser,
    location: str = Query(min_length=1, max_length=100),
) -> CabinetPassportResponse:
    """JSON-предпросмотр паспорта выбранного учебного кабинета."""
    return calculate_cabinet_passport_for_current_user(
        db,
        current_user=current_user,
        location=location,
    )


@router.get("/cabinet-passport.pdf")
def get_cabinet_passport_pdf(
    db: DbSession,
    current_user: CurrentUser,
    location: str = Query(min_length=1, max_length=100),
) -> StreamingResponse:
    """PDF-экспорт паспорта выбранного учебного кабинета."""
    pdf_bytes = generate_cabinet_passport_pdf_for_current_user(
        db,
        current_user=current_user,
        location=location,
    )
    safe_location = quote(location.strip().replace(" ", "_")) or "cabinet"

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="cabinet_passport.pdf"; '
                f"filename*=UTF-8''cabinet_passport_{safe_location}.pdf"
            )
        },
    )


@router.get("/oo2/section-2-1", response_model=OO2Section21Response)
def get_oo2_section_2_1_report(
    db: DbSession,
    current_user: CurrentUser,
    year: int | None = Query(default=None, ge=2000, le=2100),
) -> OO2Section21Response:
    """
    JSON-предпросмотр ОО-2, раздел 2.1.

    Его удобно показывать во Flutter перед скачиванием PDF:
    пользователь видит рассчитанные строки и предупреждения по данным.
    """
    report_year = year or utc_now().year

    return calculate_oo2_section_2_1_for_current_user(
        db,
        current_user=current_user,
        year=report_year,
    )


@router.get("/oo2/section-2-1.pdf")
def get_oo2_section_2_1_pdf(
    db: DbSession,
    current_user: CurrentUser,
    year: int | None = Query(default=None, ge=2000, le=2100),
) -> StreamingResponse:
    """
    PDF-помощник по ОО-2, раздел 2.1.

    Это не официальный бланк, а расчётная таблица для проверки и переноса
    данных в форму. Официальный шаблон можно подключить позже.
    """
    report_year = year or utc_now().year

    pdf_bytes = generate_oo2_section_2_1_pdf_for_current_user(
        db,
        current_user=current_user,
        year=report_year,
    )

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="oo2_section_2_1_{report_year}.pdf"'
            )
        },
    )
