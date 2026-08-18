import random
import string


def generate_organization_public_id() -> str:
    """
    Генерирует 8-значный публичный ID организации.

    Пример:
    12345678
    """
    return "".join(random.choices(string.digits, k=8))


def generate_license_code() -> str:
    """
    Генерирует человекочитаемый лицензионный код.

    Пример:
    A7KD-92LA-PQ10-ZX88
    """
    alphabet = string.ascii_uppercase + string.digits

    parts = [
        "".join(random.choices(alphabet, k=4))
        for _ in range(4)
    ]

    return "-".join(parts)