import re


def is_phone_number(phone_number):
    # Шаблон для номера телефона +7XXXXXXXXXX
    pattern = r'^\+7\d{10}$'

    if re.match(pattern, phone_number):
        return True
    else:
        return False


