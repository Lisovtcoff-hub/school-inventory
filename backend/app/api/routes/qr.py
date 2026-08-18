from datetime import datetime
from io import BytesIO

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.utils.datetime import utc_now
from app.api.deps import CurrentUser, DbSession
from app.schemas.qr import QRLabelsPdfRequest
from app.services.qr_service import (
    generate_qr_labels_pdf_for_current_user,
    get_asset_qr_png_for_current_user,
)


router = APIRouter(tags=["qr"])


@router.get("/assets/{asset_id}/qr.png")
def get_asset_qr_png(
    asset_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> StreamingResponse:
    """
    Получить PNG QR-код для одной единицы техники.
    """
    qr_png_bytes = get_asset_qr_png_for_current_user(
        db,
        current_user=current_user,
        asset_id=asset_id,
    )

    return StreamingResponse(
        BytesIO(qr_png_bytes),
        media_type="image/png",
        headers={
            "Content-Disposition": f'inline; filename="asset_{asset_id}_qr.png"'
        },
    )


@router.post("/qr/labels.pdf")
def generate_qr_labels_pdf(
    data: QRLabelsPdfRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> StreamingResponse:
    """
    Сформировать PDF-лист с QR-кодами выбранной техники.

    Сценарий для Flutter:
    1. пользователь выбирает галочками несколько единиц техники;
    2. выбирает размер наклейки в сантиметрах;
    3. выбирает размер QR-кода в сантиметрах;
    4. backend возвращает PDF-файл для печати.
    """
    pdf_bytes = generate_qr_labels_pdf_for_current_user(
        db,
        current_user=current_user,
        data=data,
    )

    date_str = utc_now().strftime("%Y_%m_%d_%H_%M")

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="qr_labels_{date_str}.pdf"'
            )
        },
    )
