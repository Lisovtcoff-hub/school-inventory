from app.core.constants import LICENSE_STATUS_NEW
from app.db.session import SessionLocal
from app.repositories.license_repository import create_license_code
from app.utils.code_generator import generate_license_code


def main() -> None:
    db = SessionLocal()

    try:
        code = generate_license_code()

        license_code = create_license_code(
            db,
            code=code,
            status=LICENSE_STATUS_NEW,
            max_users=10,
            max_assets=1000,
        )

        db.commit()
        db.refresh(license_code)

        print("Создан тестовый лицензионный код:")
        print(license_code.code)

    finally:
        db.close()


if __name__ == "__main__":
    main()