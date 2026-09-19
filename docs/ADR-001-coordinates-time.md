# ADR 001: UTC, original PyEphem propagation, spherical link geometry

Use the archived synthetic TLE construction and PyEphem `readtle` + `compute` path.
All public times are nonnegative seconds relative to an explicit UTC epoch, default
2000-01-01T00:00:00Z. TLE years are restricted to 1957–2056 and TLE epoch precision
is 1e-8 days. Store actual exported TLE, including its rounded epoch.

PyEphem documents `sublat` as geocentric and `elevation` relative to WGS66, not a
spherical radial height. Do not add that elevation to a different sphere radius.
Instead reconstruct a common ECEF position from un-refracted topocentric azimuth,
altitude and range at observer latitude=longitude=elevation=0 (pressure=0):
`x=6378.16 + range*sin(alt); y=range*cos(alt)*sin(az); z=range*cos(alt)*cos(az)` (km).
The observer origin is the WGS66 equatorial radius used by libastro/PyEphem.
This is a coordinate conversion of original propagated results, not a new orbit.

New education geometry uses a sphere with radius 6378.16 km for GS, horizon and
segment/Earth intersection. Public latitude is geocentric, longitude is Earth-fixed;
altitude is norm(ECEF) minus this spherical radius. Link lengths use Euclidean ECEF.
This simplification is distinct from the WGS72 gravity model used to construct TLEs.
The original period uses Astropy R_earth and G*M_earth; those constants are recorded.

Regression compares actual original topocentric fields and the original separation/
range distance function. Distance tolerance is 0.01 km: topocentric angles and ranges
are exposed with limited precision; empirical errors are recorded in tests/report.
It does not assert full research equivalence or operational orbit accuracy.

References: [PyEphem fields](https://rhodesmill.org/pyephem/quick.html),
[SGP4 API](https://pypi.org/project/sgp4/). Inspected 2026-09-19.
