"""Single source for contracts; generated schemas ship in the wheel."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = {"type": "string", "maxLength": 4096}
ID = {"type": "string", "minLength": 1, "maxLength": 256}
N = {"type": "number"}
POS = {"type": "number", "minimum": 0}
I = {"type": "integer", "minimum": 0}
B = {"type": "boolean"}


def enum(*v):
    return {"enum": list(v)}


def arr(item, **kw):
    return dict(type="array", items=item, **kw)


def obj(props, optional=()):
    return dict(
        type="object",
        properties=props,
        required=[k for k in props if k not in optional],
        additionalProperties=False,
    )


def ref(n):
    return {"$ref": "#/$defs/" + n}


def nullable(s):
    return {"anyOf": [s, {"type": "null"}]}


def ranged(lo, hi, typ="number"):
    return dict(type=typ, minimum=lo, maximum=hi)


defs = {}
defs["orbit"] = obj(
    dict(
        altitude_km=ranged(100, 36000),
        inclination_deg=ranged(0, 180),
        raan_deg=ranged(0, 360),
        phase_deg=ranged(0, 360),
    )
)
defs["object"] = obj(
    dict(
        id=ID,
        label=S,
        kind=enum("satellite", "ground_station"),
        tle=arr(S, minItems=2, maxItems=2),
        orbit=ref("orbit"),
        constellation_id=ID,
        plane=I,
        slot=I,
        lat_deg=ranged(-90, 90),
        lon_deg=ranged(-180, 180),
    ),
    ("tle", "orbit", "constellation_id", "plane", "slot", "lat_deg", "lon_deg"),
)
defs["constellation"] = obj(
    dict(
        id=ID,
        planes=ranged(1, 10000, "integer"),
        sats_per_plane=ranged(1, 10000, "integer"),
        altitude_km=ranged(100, 36000),
        inclination_deg=ranged(0, 180),
        phase_rule=enum("usergs_alternating_half_slot"),
    )
)
defs["policy"] = obj(
    dict(
        topology=enum("orbital_neighbors", "distance"),
        max_isl_km=dict(type="number", exclusiveMinimum=0),
        min_elevation_deg=ranged(0, 90),
    )
)
defs["failure"] = obj(dict(node_id=ID, start_s=POS, end_s=POS))
defs["scenario"] = obj(
    dict(
        format={"const": "satnet-edu.scenario"},
        schema_version={"const": "1.0.0"},
        name=S,
        epoch_utc=S,
        seed=ranged(0, 9007199254740991, "integer"),
        limits=obj(
            dict(
                max_nodes=ranged(1, 10000, "integer"),
                max_samples=ranged(1, 100000, "integer"),
            )
        ),
        constellations=arr(ref("constellation")),
        objects=arr(ref("object")),
        link_policy=ref("policy"),
        failures=arr(ref("failure")),
    )
)
defs["query"] = obj(dict(id=ID, source=ID, target=ID, metric=enum("hops", "delay")))
defs["state"] = obj(
    dict(
        id=ID,
        enabled=B,
        position_ecef_km=arr(N, minItems=3, maxItems=3),
        lat_deg=ranged(-90, 90),
        lon_deg=ranged(-180, 180),
        altitude_km=N,
    )
)
defs["link"] = obj(
    dict(
        id=S,
        source=ID,
        target=ID,
        kind=enum("isl", "gsl"),
        distance_km=POS,
        propagation_ms=POS,
    )
)
defs["route"] = obj(
    dict(
        query_id=ID,
        status=enum("reachable", "unreachable"),
        node_ids=arr(ID),
        link_ids=arr(S),
        hops=nullable(I),
        distance_km=nullable(POS),
        propagation_ms=nullable(POS),
        reason=nullable(enum("no_path", "endpoint_disabled")),
    )
)
defs["frame"] = obj(
    dict(
        t_s=POS,
        node_states=arr(ref("state")),
        links=arr(ref("link")),
        routes=arr(ref("route")),
    )
)
trace = obj(
    dict(
        format={"const": "satnet-edu.trace"},
        schema_version={"const": "1.0.0"},
        producer=obj(
            dict(
                name={"const": "satnet-edu"},
                version=S,
                source_zip_sha256=S,
                dependencies={"type": "object", "additionalProperties": S},
            )
        ),
        experiment=obj(
            dict(id=ID, name=S, epoch_utc=S, seed=I, scenario=ref("scenario"))
        ),
        model=obj(
            dict(
                propagator=S,
                earth_model={"const": "sphere"},
                earth_radius_km=dict(type="number", exclusiveMinimum=0),
                latitude_kind={"const": "geocentric"},
                coordinate_frame={"const": "ECEF"},
                units=obj(
                    dict(
                        length={"const": "km"},
                        angle={"const": "deg"},
                        time={"const": "s"},
                        delay={"const": "ms"},
                    )
                ),
                c_km_s=dict(type="number", exclusiveMinimum=0),
                tle_gravity_model=S,
                orbit_radius_constant_m=POS,
                orbit_mu_m3_s2=POS,
                link_policy=ref("policy"),
                delay_model={"const": "one-way propagation only"},
                limitations=arr(S),
            )
        ),
        recording=obj(
            dict(
                start_s=POS,
                end_s=POS,
                step_s=dict(type="number", exclusiveMinimum=0),
                sample_count=ranged(1, 100000, "integer"),
                route_queries=arr(ref("query")),
                capabilities=obj(
                    dict(
                        routes=B,
                        energy={"const": False},
                        packet_events={"const": False},
                    )
                ),
            )
        ),
        objects=arr(ref("object")),
        frames=arr(ref("frame"), minItems=1),
        events=arr(
            obj(
                dict(
                    t_s=POS,
                    node_id=ID,
                    kind=enum("failure_start", "failure_end"),
                    timing={"const": "scheduled"},
                )
            )
        ),
        extensions={"type": "object"},
    ),
    ("extensions",),
)
for name, schema in [("scenario", ref("scenario")), ("trace", trace)]:
    full = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"urn:satnet-edu:{name}:1.0.0",
        **schema,
        "$defs": defs,
    }
    for folder in [ROOT / "schemas", ROOT / "src/satnet_edu/assets"]:
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{name}.schema.json").write_text(
            json.dumps(full, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
print("Built scenario and trace schemas")
