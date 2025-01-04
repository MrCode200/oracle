import re

unit_mapping: dict[str, int] = {
    "s": 1,
    "m": 60,
    "h": 24 * 60,
    "d": 7 * 24 * 60,
    "w": 30 * 24 * 60,
    "M": 12 * 30 * 24 * 60
}


def parse_interval(interval: str) -> int:
    match = re.findall(r"(\d+)(s|m|h|d|w|M)", interval)

    return int(match[0][0]) * unit_mapping[match[0][1]]