"""Adapted from UserGS helpers/generate_tle.py, orbital_period.py, mean_motion.py.

Original designator handling attributes Hypatia. See PROVENANCE and notices.
Retains the original near-circle, constants, phase and mean-motion conversion.
"""

import math
from datetime import timedelta

import ephem
from astropy.constants import G, M_earth, R_earth
from sgp4.api import WGS72, Satrec, jday
from sgp4.exporter import export_tle

from .geometry import EARTH_RADIUS_KM, coordinates


def phases(plane, slot, planes, slots):
    shift = 360.0 / (slots * 2.0) if plane % 2 else 0.0
    return plane * 360.0 / planes, shift + slot / slots * 360.0


def generate_tle(satnum, epoch, altitude_km, inclination_deg, raan_deg, phase_deg):
    period = (
        2
        * math.pi
        * math.sqrt(
            (R_earth.value + altitude_km * 1000) ** 3 / (G.value * M_earth.value)
        )
    )
    motion = (86400.0 / period) * 60 / 13750.9870831397
    jd, fr = jday(
        epoch.year,
        epoch.month,
        epoch.day,
        epoch.hour,
        epoch.minute,
        epoch.second + epoch.microsecond / 1e6,
    )
    sat = Satrec()
    sat.sgp4init(
        WGS72,
        "i",
        satnum,
        jd + fr - 2433281.5,
        0.0,
        0.0,
        0.0,
        1e-7,
        0.0,
        math.radians(inclination_deg),
        math.radians(phase_deg),
        motion,
        math.radians(raan_deg),
    )
    line1, line2 = export_tle(sat)
    # Change designator only. UserGS replaced the epoch here too; preserve ours.
    line1 = line1[:7] + "U 00000ABC" + line1[17:68]
    checksum = sum(int(c) if c.isdigit() else 1 if c == "-" else 0 for c in line1) % 10
    return (line1 + str(checksum), line2)


def propagate(tle, epoch, t_s):
    # Fresh ephem object per query prevents shared mutable state and order effects.
    sat = ephem.readtle("SatNet Edu", *tle)
    obs = ephem.Observer()
    obs.lat = obs.lon = "0"
    obs.elevation = obs.pressure = 0
    try:
        obs.date = ephem.Date((epoch + timedelta(seconds=t_s)).replace(tzinfo=None))
    except (OverflowError, ValueError) as exc:
        raise ValueError("t_s: outside supported calendar range") from exc
    try:
        sat.compute(obs)
        r, az, alt = sat.range / 1000.0, float(sat.az), float(sat.alt)
    except (RuntimeError, ValueError) as exc:
        raise ValueError(
            f"orbit at t_s={t_s}: PyEphem could not propagate this TLE ({exc}); no fallback engine is used"
        ) from exc
    p = (
        EARTH_RADIUS_KM + r * math.sin(alt),
        r * math.cos(alt) * math.sin(az),
        r * math.cos(alt) * math.cos(az),
    )
    return p, coordinates(p)
