"""Generate ideal circular-orbit teaching data, using only the Python standard library.

This is a geometry calculation for the slides, not a SatNet Edu orbit propagator.
Earth is spherical, precession and drag are omitted, and the prime meridian
coincides with the reference direction at t=0. Ground tracks include Earth
rotation. The overhead contact comparison holds the observer fixed in inertial
space and therefore omits Earth rotation, as stated on that slide.
"""

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
R = 6371.0
MU = 398600.4418
SIDEREAL_S = 86164.0905


def period(h):
    return 2 * math.pi * math.sqrt((R + h) ** 3 / MU)


def footprint_angle(h, elevation):
    e = math.radians(elevation)
    return math.acos(R / (R + h) * math.cos(e)) - e


def write_csv(name, header, rows):
    with (ROOT / name).open('w', encoding='ascii', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(header)
        w.writerows(rows)


def main():
    rows = []
    for angle in range(361):
        u = math.radians(angle)
        rows.append([angle, *(f'{math.degrees(math.asin(math.sin(math.radians(i)) * math.sin(u))):.6f}' for i in (53, 85))])
    write_csv('latitude.csv', ['phase', 'i53', 'i85'], rows)

    T = period(550)
    for orbit in (0, 1):
        rows = []
        last_lon = None
        for k in range(721):
            u = k * 2 * math.pi / 720
            t = T * (orbit + k / 720)
            lat = math.asin(math.sin(math.radians(53)) * math.sin(u))
            lon = math.atan2(math.cos(math.radians(53)) * math.sin(u), math.cos(u)) - 2 * math.pi * t / SIDEREAL_S
            lon = (math.degrees(lon) + 180) % 360 - 180
            if last_lon is not None and abs(lon - last_lon) > 180:
                rows.append(['nan', 'nan'])
            rows.append([f'{lon:.6f}', f'{math.degrees(lat):.6f}'])
            last_lon = lon
        write_csv(f'ground-track-{orbit + 1}.csv', ['lon', 'lat'], rows)

    rows = []
    for j in range(321):
        minutes = -8 + j * 0.05
        elevations = []
        for h in (550, 1200):
            theta = 2 * math.pi / period(h) * minutes * 60
            e = math.degrees(math.atan2((R + h) * math.cos(theta) - R, (R + h) * abs(math.sin(theta))))
            elevations.append(f'{max(0, e):.6f}')
        rows.append([f'{minutes:.2f}', *elevations])
    write_csv('overhead-passes.csv', ['minutes', 'h550', 'h1200'], rows)

    numbers = {
        'earth_radius_km': R,
        'mu_km3_s2': MU,
        'sidereal_day_s': SIDEREAL_S,
        'orbits': {str(h): {'period_min': period(h) / 60, 'speed_km_s': math.sqrt(MU / (R + h)),
                           'contact_minutes_mask25': footprint_angle(h, 25) * period(h) / math.pi / 60}
                   for h in (550, 1200)},
        'footprints_h550': {str(e): {'angle_deg': math.degrees(footprint_angle(550, e)),
                                    'surface_radius_km': R * footprint_angle(550, e)}
                           for e in (10, 25, 40)},
        'ground_track_west_shift_deg': 360 * T / SIDEREAL_S,
        'latitude_envelope_i53_mask25': 53 + math.degrees(footprint_angle(550, 25)),
    }
    (ROOT / 'geometry-values.json').write_text(json.dumps(numbers, indent=2) + '\n', encoding='ascii')
    print(json.dumps(numbers, indent=2))


if __name__ == '__main__':
    main()
