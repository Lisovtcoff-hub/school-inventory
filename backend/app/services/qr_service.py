from io import BytesIO
from pathlib import Path

import qrcode
from fastapi import HTTPException, status
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from sqlalchemy.orm import Session

from app.db.models.asset import Asset
from app.db.models.user import User
from app.repositories.asset_repository import (
    get_asset_by_id,
    get_assets_by_ids,
)
from app.schemas.qr import QRLabelsPdfRequest


DEFAULT_FONT_NAME = "Helvetica"
REGISTERED_FONT_NAME = "AppRegularFont"


def _register_pdf_font() -> str:
    """
    Регистрирует шрифт для PDF.

    Почему это нужно:
    стандартный Helvetica в ReportLab плохо подходит для кириллицы.
    Поэтому пытаемся найти системный TTF-шрифт.

    На Windows обычно есть Arial.
    На Linux часто есть DejaVu Sans.

    Если шрифт не найден, останется Helvetica.
    Английский текст и цифры будут работать, но кириллица может отображаться плохо.
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


def build_qr_payload(asset_code: str) -> str:
    """
    Payload, который будет зашит в QR.

    Используем внутренний формат:
    asset:1234567800000001

    Flutter после сканирования достанет asset_code
    и вызовет GET /assets/by-code/{asset_code}.
    """
    return f"asset:{asset_code}"


def generate_qr_png_bytes(payload: str) -> bytes:
    """
    Генерирует QR-код в PNG и возвращает bytes.
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )

    qr.add_data(payload)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    return buffer.getvalue()


def get_asset_qr_png_for_current_user(
    db: Session,
    *,
    current_user: User,
    asset_id: int,
) -> bytes:
    """
    Генерирует PNG QR-код для одной единицы техники.
    """
    asset = get_asset_by_id(
        db,
        organization_id=current_user.organization_id,
        asset_id=asset_id,
    )

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Техника не найдена",
        )

    payload = build_qr_payload(asset.asset_code)

    return generate_qr_png_bytes(payload)


def _draw_centered_text_line(
    pdf: canvas.Canvas,
    *,
    text: str,
    center_x: float,
    y: float,
    max_width: float,
    font_name: str,
    font_size: int,
) -> None:
    """
    Рисует одну строку текста по центру.
    Если строка слишком длинная, аккуратно обрезает её через многоточие.
    """
    if not text:
        return

    text = str(text)
    ellipsis = "..."

    while pdf.stringWidth(text, font_name, font_size) > max_width and len(text) > 3:
        text = text[:-1]

    if text != str(text) and len(text) > 3:
        text = text[:-3] + ellipsis

    pdf.setFont(font_name, font_size)
    pdf.drawCentredString(center_x, y, text)


def _fit_text_to_width(
    pdf: canvas.Canvas,
    *,
    text: str,
    max_width: float,
    font_name: str,
    font_size: int,
) -> str:
    """
    Обрезает текст так, чтобы он поместился в max_width.
    """
    if pdf.stringWidth(text, font_name, font_size) <= max_width:
        return text

    ellipsis = "..."
    result = text

    while result and pdf.stringWidth(result + ellipsis, font_name, font_size) > max_width:
        result = result[:-1]

    return result + ellipsis if result else ellipsis


def _draw_label(
    pdf: canvas.Canvas,
    *,
    asset: Asset,
    x: float,
    y: float,
    label_width: float,
    label_height: float,
    qr_size: float,
    include_asset_code: bool,
    include_asset_name: bool,
    include_room: bool,
) -> None:
    """
    Рисует одну наклейку в координатах PDF.

    x, y - левый нижний угол наклейки.
    Размеры уже передаются в points.
    """
    padding = 0.12 * cm
    center_x = x + label_width / 2

    # Лёгкая рамка помогает резать наклейки после печати.
    pdf.setLineWidth(0.25)
    pdf.rect(x, y, label_width, label_height)

    text_lines: list[str] = []

    if include_asset_code:
        text_lines.append(asset.asset_code)

    if include_asset_name:
        text_lines.append(asset.name)

    if include_room and asset.room:
        text_lines.append(f"Каб. {asset.room}")

    text_font_size = 7
    text_line_height = 0.32 * cm
    text_block_height = len(text_lines) * text_line_height

    qr_x = x + (label_width - qr_size) / 2
    qr_y = y + label_height - padding - qr_size

    # Если подписей много, QR поднимаем, а текст ставим ниже.
    min_qr_y = y + padding + text_block_height
    if qr_y < min_qr_y:
        qr_y = min_qr_y

    payload = build_qr_payload(asset.asset_code)
    qr_png_bytes = generate_qr_png_bytes(payload)

    image = Image.open(BytesIO(qr_png_bytes)).convert("RGB")
    image_reader = ImageReader(image)

    pdf.drawImage(
        image_reader,
        qr_x,
        qr_y,
        width=qr_size,
        height=qr_size,
        preserveAspectRatio=True,
        mask="auto",
    )

    text_y = qr_y - 0.22 * cm
    max_text_width = label_width - padding * 2

    for line in text_lines:
        fitted_line = _fit_text_to_width(
            pdf,
            text=line,
            max_width=max_text_width,
            font_name=PDF_FONT_NAME,
            font_size=text_font_size,
        )
        pdf.setFont(PDF_FONT_NAME, text_font_size)
        pdf.drawCentredString(center_x, text_y, fitted_line)
        text_y -= text_line_height


def generate_qr_labels_pdf_for_current_user(
    db: Session,
    *,
    current_user: User,
    data: QRLabelsPdfRequest,
) -> bytes:
    """
    Генерирует PDF-лист с QR-кодами выбранной техники.

    PDF выбран вместо DOCX, потому что он лучше держит точный физический размер
    наклеек и QR-кодов при печати.
    """
    unique_asset_ids = list(dict.fromkeys(data.asset_ids))

    assets = get_assets_by_ids(
        db,
        organization_id=current_user.organization_id,
        asset_ids=unique_asset_ids,
    )

    if not assets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Выбранная техника не найдена",
        )

    found_ids = {asset.id for asset in assets}
    missing_ids = [asset_id for asset_id in unique_asset_ids if asset_id not in found_ids]

    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некоторые единицы техники не найдены или недоступны: {missing_ids}",
        )

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    page_width, page_height = A4
    margin = 1 * cm
    content_width = page_width - margin * 2
    content_height = page_height - margin * 2

    label_width = data.label_width_cm * cm
    label_height = data.label_height_cm * cm
    qr_size = data.qr_size_cm * cm

    if label_width > content_width:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ширина наклейки больше доступной ширины листа A4",
        )

    if label_height > content_height:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Высота наклейки больше доступной высоты листа A4",
        )

    columns = data.columns or max(1, int(content_width // label_width))
    columns = min(columns, max(1, int(content_width // label_width)))

    rows_per_page = max(1, int(content_height // label_height))
    labels_per_page = columns * rows_per_page

    if labels_per_page <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно разместить наклейки с такими размерами на листе A4",
        )

    asset_index = 0

    while asset_index < len(assets):
        pdf.setFont(PDF_FONT_NAME, 8)

        for row in range(rows_per_page):
            for column in range(columns):
                if asset_index >= len(assets):
                    break

                x = margin + column * label_width
                y = page_height - margin - (row + 1) * label_height

                _draw_label(
                    pdf,
                    asset=assets[asset_index],
                    x=x,
                    y=y,
                    label_width=label_width,
                    label_height=label_height,
                    qr_size=qr_size,
                    include_asset_code=data.include_asset_code,
                    include_asset_name=data.include_asset_name,
                    include_room=data.include_room,
                )

                asset_index += 1

            if asset_index >= len(assets):
                break

        if asset_index < len(assets):
            pdf.showPage()

    pdf.save()
    buffer.seek(0)

    return buffer.getvalue()
