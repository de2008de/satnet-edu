"""New educational spherical geometry; distances are always 3-D ECEF km."""
import math

EARTH_RADIUS_KM = 6378.16
C_KM_S = 299792.458


def coordinates(p):
    r = math.sqrt(sum(v * v for v in p))
    return math.degrees(math.atan2(p[2], math.hypot(p[0], p[1]))), math.degrees(math.atan2(p[1], p[0])), r - EARTH_RADIUS_KM


def ground_position(lat, lon):
    lat, lon = math.radians(lat), math.radians(lon)
    return (EARTH_RADIUS_KM * math.cos(lat) * math.cos(lon),
            EARTH_RADIUS_KM * math.cos(lat) * math.sin(lon), EARTH_RADIUS_KM * math.sin(lat))


def distance(a, b):
    return math.dist(a, b)


def visible_isl(a, b):
    d = tuple(y - x for x, y in zip(a, b))
    dd = sum(x * x for x in d)
    if dd == 0:
        return False
    f = max(0, min(1, -sum(x * y for x, y in zip(a, d)) / dd))
    return sum((x + f * y) ** 2 for x, y in zip(a, d)) > EARTH_RADIUS_KM ** 2


def elevation_deg(ground, satellite):
    delta = tuple(s - g for s, g in zip(satellite, ground))
    norm = math.sqrt(sum(v * v for v in delta))
    if norm == 0:
        return -90.0
    sine = sum(a * b for a, b in zip(delta, ground)) / (norm * EARTH_RADIUS_KM)
    return math.degrees(math.asin(max(-1, min(1, sine))))
