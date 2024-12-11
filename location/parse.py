import re

from .location_api import Location

directions = ["N", "S", "E", "W"]


def parse_coordinates(raw: str) -> Location | None:
    """
    Parse coordinates from a string.
    Accepted formats:
    - decimal: "lat lon" or "lat,lon"
    - dms: "dd°mm'ss"[N|S] dd°mm'ss"[E|W]"
    """
    try:
        if any(c in directions for c in raw.upper()):
            return parse_degrees_coordinates(raw)

        return parse_decimal_coordinates(raw)
    except ValueError:
        return None


def parse_decimal_coordinates(raw: str) -> Location:
    parts = raw.split(" ") if " " in raw else raw.split(",")
    lat, lon = map(float, parts)
    return {"lat": lat, "lon": lon}


def parse_degrees_coordinates(raw: str) -> Location:
    p1, p2 = sorted(
        map(parse_dms, raw.upper().split(" ")),
        key=lambda p: directions.index(p[3]),
    )
    return {
        "lat": dms_to_decimal_coordinate(*p1),
        "lon": dms_to_decimal_coordinate(*p2),
    }


def parse_dms(raw: str):
    pattern = r"(\d+)°(\d+)'([\d.]+)\"?([NSEW])"
    match = re.match(pattern, raw)

    if not match:
        raise ValueError("Invalid DMS format")

    degrees = int(match.group(1))
    minutes = int(match.group(2))
    seconds = float(match.group(3))
    direction = match.group(4)

    return degrees, minutes, seconds, direction


def dms_to_decimal_coordinate(degrees: int, minutes: int, seconds: float, direction: str) -> float:
    dd = degrees + (minutes / 60) + (seconds / 3600)
    if direction in ["S", "W"]:
        dd *= -1
    return dd
