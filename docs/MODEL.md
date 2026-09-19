# Model and limits

The actual source path is UserGS synthetic TLE → sgp4 export → PyEphem readtle and
compute. See PROVENANCE and ADR-001. This is not the earlier UI's circular-orbit engine.
Default epoch is 2000-01-01 UTC, synthetic data, not a live satellite catalogue.

Retained assumptions: WGS72 TLE initialization, zero drag, eccentricity 1e-7,
argument of perigee zero, Astropy orbital-period constants, original mean-motion
conversion, evenly spaced RAAN and alternating half-slot mean-anomaly phases.
The phase rule is named `usergs_alternating_half_slot`, not a general Walker rule.
Actual TLE strings and dependency versions accompany every run. TLE epoch has
1e-8-day resolution; very fine epochs are rounded by the original format.

New link geometry: Earth-fixed three-dimensional positions reconstructed from
PyEphem's un-refracted azimuth/altitude/range at a fixed equatorial observer.
Reference observer origin and educational sphere radius: 6378.16 km. This matches
the [PyEphem libastro source](https://github.com/brandon-rhodes/pyephem/blob/master/libastro/earthsat.c)
equatorial radius. Ground stations use geocentric spherical latitude. Satellite
altitude is radius minus this sphere, not the original ellipsoidal elevation field.
No mixing TEME/ECI coordinates with stationary ground positions.

Neighbor candidates retain UserGS wraparound plane/slot rules, without orbital seams,
self loops or duplicate pairs. New filters require both enabled endpoints, maximum
ISL distance and a segment strictly outside the sphere (tangency is blocked). Ground
links require minimum elevation 0–90 degrees; actual slant range sets the distance.
All passing ground contacts are available. Links are undirected; GS have no terrestrial
shortcuts and cannot relay between satellites. Distance policy considers every pair
and does not model finite terminal counts, pointing schedules or interference.

Delay = sum of link distances / 299792.458 km/s × 1000 ms. The metric is **one-way
propagation delay** only. No traffic queues, serialization, processing, packet loss,
congestion, batteries, bids, cooperative offload or routing convergence are modeled.
Shortest path uses (primary objective, secondary objective, full stable ID sequence).
Delay's secondary objective is hops; hops' secondary objective is delay. Binary float
values compare exactly for ordering; validators use 1e-6 absolute / 1e-9 relative
tolerances for recorded metric sums. No arbitrary epsilon changes optimization.

Known inherited limitation: PyEphem 4.2.1 fails to propagate the synthetic 35786 km,
exactly 0° inclination example at the default epoch. The API reports the propagator
error; it never switches to a fake orbit. The near-geostationary 0.1° test validates
Earth-fixed rotation. Other extreme configurations may also expose upstream limits.
No claim is made of flight-grade accuracy or agreement with real operators.

Sampling includes event boundaries. The player displays discrete frames, never
interpolated link/path results. A lack of service between samples can be missed;
no continuous availability guarantee or challenge score is provided. A `no_path`
sample is a valid result, distinct from an unrecorded query capability.

Original regression checks six satellites at 0/60/600 s. TLE text matches exactly;
latitude/longitude tolerance 1e-4 degrees and distance tolerance 0.01 km account for
float PyEphem fields and independent angular-distance conversion. Measured errors
are in TEST_REPORT; paper experiments and figures have not been reproduced.
