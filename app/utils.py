import re


def normalize_whatsapp_number(value):
    """Return a WhatsApp-compatible Turkish number without a leading plus sign."""
    digits = re.sub(r"\D", "", str(value or ""))

    if digits.startswith("00"):
        digits = digits[2:]

    if len(digits) == 12 and digits.startswith("90"):
        return digits
    if len(digits) == 11 and digits.startswith("0"):
        return f"90{digits[1:]}"
    if len(digits) == 10:
        return f"90{digits}"

    return digits
