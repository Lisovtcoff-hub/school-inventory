from pydantic import BaseModel


class ReportCatalogItem(BaseModel):
    code: str
    title: str
    description: str


class ReportWarning(BaseModel):
    asset_id: int | None = None
    asset_code: str | None = None
    message: str


class OO2Section21Row(BaseModel):
    row_code: str
    name: str
    total: int
    used_for_education: int | None = None
    available_for_students: int | None = None


class OO2Section21Response(BaseModel):
    report_code: str = "OO-2"
    section: str = "2.1"
    title: str = "Количество персональных компьютеров и информационного оборудования"
    report_year: int
    organization_id: int
    organization_name: str
    rows: list[OO2Section21Row]
    warnings: list[ReportWarning]


class CabinetPassportOrganization(BaseModel):
    name: str
    short_name: str | None = None


class CabinetPassportSummary(BaseModel):
    total_assets: int
    working_assets: int
    needs_repair: int
    written_off: int


class CabinetPassportAsset(BaseModel):
    asset_code: str
    name: str
    type: str
    model: str | None = None
    serial_number: str | None = None
    inventory_number: str | None = None
    status: str
    responsible_person: str | None = None
    is_used_for_education: bool


class CabinetPassportSection(BaseModel):
    title: str
    items: list[CabinetPassportAsset]


class CabinetPassportResponse(BaseModel):
    report_code: str = "CABINET_PASSPORT"
    title: str = "Паспорт учебного кабинета"
    location: str
    organization: CabinetPassportOrganization
    summary: CabinetPassportSummary
    assets: list[CabinetPassportAsset]
    sections: list[CabinetPassportSection]
    warnings: list[ReportWarning]
