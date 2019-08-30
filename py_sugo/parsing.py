# Standard libs imports
import datetime
from typing import List
from decimal import Decimal


def parse(text: str):
    if input.isdecimal():
        return Decimal(input)
    elif input.isnumeric():
        return int(input)
    elif input in ['True', 'False']:
        return bool(input)
    elif is_date(input):
        return input
    return input


DATE_FORMATS: List[str] = []


def is_date(input: str) -> bool:
    for format in DATE_FORMATS:
        try:
            return datetime.strptime(input, format)
        except ValueError:
            pass
    return None


def parse_date(input: str):
    pass
