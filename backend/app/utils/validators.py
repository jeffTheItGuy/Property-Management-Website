import re


def is_valid_zim_phone(phone: str) -> bool:
    """Basic check for Zimbabwe mobile numbers."""
    cleaned = re.sub(r"\D", "", phone)
    return bool(re.match(r"^(0|263|\+263)?7[1-9]\d{7,8}$", cleaned))


def is_valid_national_id(nid: str) -> bool:
    """Zimbabwe national ID format: 63-1234567A89 or similar."""
    return bool(re.match(r"^\d{2}-\d{6,7}[A-Z]\d{2}$", nid.strip().upper()))


def clean_phone(phone: str) -> str:
    """Normalize to +263... format."""
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("0"):
        digits = "263" + digits[1:]
    if not digits.startswith("+"):
        digits = "+" + digits
    return digits
