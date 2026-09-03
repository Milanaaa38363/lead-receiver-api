import re

class InvalidPhoneError(ValueError):
    pass

def normalize_phone(raw_phone: str) -> str:
    if not raw_phone or not raw_phone.strip():
        raise InvalidPhoneError("Номер телефона не может быть пустым")

    digits = re.sub(r"[^\d]", "", raw_phone)

    if len(digits) == 11:
        if digits.startswith("8") or digits.startswith("7"):
            digits = "7" + digits[1:]
        else:
            raise InvalidPhoneError("Неверный код страны")
    elif len(digits) == 10:
        digits = "7" + digits
    else:
        raise InvalidPhoneError("Номер должен содержать 10 или 11 цифр")

    normalized = f"+{digits}"
    
    if not re.match(r"^\+7\d{10}$", normalized):
        raise InvalidPhoneError("Формат должен быть +7XXXXXXXXXX")

    return normalized