"""Schema and semantic validation. Recorded paths are checked, never re-routed."""

import json
import math
from functools import lru_cache
from importlib.resources import files

from jsonschema import Draft202012Validator

from ..config import utc_epoch
from ..engine.clock import sample_times
from ..engine.orbit import phases


@lru_cache(maxsize=2)
def _validator(kind):
    return Draft202012Validator(
        json.loads(
            files("satnet_edu")
            .joinpath(f"assets/{kind}.schema.json")
            .read_text(encoding="utf-8")
        )
    )


def _finite(v, path="$"):
    if isinstance(v, float) and not math.isfinite(v):
        raise ValueError(f"{path}: expected finite number")
    if isinstance(v, dict):
        for k, x in v.items():
            _finite(x, f"{path}.{k}")
    if isinstance(v, (list, tuple)):
        for i, x in enumerate(v):
            _finite(x, f"{path}[{i}]")


def _schema(data, kind):
    _finite(data)
    error = next(_validator(kind).iter_errors(data), None)
    if error:
        raise ValueError(
            f"{kind}.{'.'.join(map(str, error.absolute_path))}: {error.message}"
        )


def _unique(items, key, path):
    result = {}
    for item in items:
        if item[key] in result:
            raise ValueError(f"{path}: duplicate {key} {item[key]}")
        result[item[key]] = item
    return result


def _require(ok, path, message):
    if not ok:
        raise ValueError(f"{path}: {message}")


def _close(a, b, path):
    _require(
        a is not None and math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-6),
        path,
        f"expected {b}, got {a}",
    )


def validate_scenario(data, *, structural=True):
    if structural:
        _schema(data, "scenario")
    utc_epoch(data["epoch_utc"])
    objects = _unique(data["objects"], "id", "objects")
    constellations = _unique(data["constellations"], "id", "constellations")
    _require(
        len(objects) <= data["limits"]["max_nodes"], "objects", "exceeds max_nodes"
    )
    occupied = set()
    for sid, o in objects.items():
        path = f"objects.{sid}"
        fields = (
            ("tle", "orbit") if o["kind"] == "satellite" else ("lat_deg", "lon_deg")
        )
        _require(all(k in o for k in fields), path, f"requires {fields}")
        forbidden = (
            ("tle", "orbit", "constellation_id", "plane", "slot")
            if o["kind"] == "ground_station"
            else ("lat_deg", "lon_deg")
        )
        _require(not any(k in o for k in forbidden), path, "incompatible object fields")
        if "constellation_id" in o:
            c = constellations.get(o["constellation_id"])
            _require(
                c is not None and "plane" in o and "slot" in o,
                path,
                "invalid membership",
            )
            m = (c["id"], o["plane"], o["slot"])
            _require(
                o["plane"] < c["planes"]
                and o["slot"] < c["sats_per_plane"]
                and m not in occupied,
                path,
                "invalid or duplicate slot",
            )
            occupied.add(m)
            expected_raan, expected_phase = phases(
                o["plane"], o["slot"], c["planes"], c["sats_per_plane"]
            )
            _require(
                o["orbit"]
                == dict(
                    altitude_km=c["altitude_km"],
                    inclination_deg=c["inclination_deg"],
                    raan_deg=expected_raan,
                    phase_deg=expected_phase,
                ),
                path,
                "orbit differs from constellation definition",
            )
        else:
            _require(
                "plane" not in o and "slot" not in o,
                path,
                "slot requires constellation",
            )
    for cid, c in constellations.items():
        _require(
            sum(m[0] == cid for m in occupied) == c["planes"] * c["sats_per_plane"],
            f"constellations.{cid}",
            "missing slots",
        )
    for f in data["failures"]:
        _require(
            f["node_id"] in objects and f["end_s"] > f["start_s"],
            "failures",
            "unknown node or empty/reversed interval",
        )
    return data


def validate_trace(data):
    if (
        not isinstance(data, dict)
        or data.get("format") != "satnet-edu.trace"
        or data.get("schema_version") != "1.0.0"
    ):
        raise ValueError(
            "trace: supported format satnet-edu.trace, schema_version 1.0.0"
        )
    _schema(data, "trace")
    s = data["experiment"]["scenario"]
    validate_scenario(s, structural=False)
    for key in ("epoch_utc", "name", "seed"):
        _require(
            data["experiment"][key] == s[key], f"experiment.{key}", "scenario mismatch"
        )
    _require(
        data["model"]["link_policy"] == s["link_policy"],
        "model.link_policy",
        "scenario mismatch",
    )
    objects = _unique(data["objects"], "id", "objects")
    _require(
        objects == {o["id"]: o for o in s["objects"]}, "objects", "scenario mismatch"
    )
    recording = data["recording"]
    queries = _unique(recording["route_queries"], "id", "route_queries")
    _require(
        recording["capabilities"]["routes"] == bool(queries),
        "capabilities.routes",
        "query mismatch",
    )
    for q in queries.values():
        _require(
            q["source"] in objects and q["target"] in objects,
            "route_queries",
            "unknown endpoint",
        )
    times = sample_times(
        recording["start_s"],
        recording["end_s"] - recording["start_s"],
        recording["step_s"],
        s["failures"],
        s["limits"]["max_samples"],
    )
    _require(
        [f["t_s"] for f in data["frames"]] == times,
        "frames.t_s",
        "must match full sample grid including event boundaries",
    )
    _require(
        len(data["frames"]) == recording["sample_count"],
        "recording.sample_count",
        "frame count mismatch",
    )
    for i, f in enumerate(data["frames"]):
        p = f"frames[{i}]"
        states = _unique(f["node_states"], "id", p + ".node_states")
        links = _unique(f["links"], "id", p + ".links")
        routes = _unique(f["routes"], "query_id", p + ".routes")
        _require(states.keys() == objects.keys(), p, "missing/unknown node state")
        _require(routes.keys() == queries.keys(), p, "missing/unknown query result")
        for sid, state in states.items():
            scheduled = any(
                failure["node_id"] == sid
                and failure["start_s"] <= f["t_s"] < failure["end_s"]
                for failure in s["failures"]
            )
            _require(
                state["enabled"] != scheduled,
                p + ".node_states." + sid,
                "scheduled failure state mismatch",
            )
            xyz = state["position_ecef_km"]
            radius = math.sqrt(sum(v * v for v in xyz))
            _require(radius > 0, p + ".node_states." + sid, "zero ECEF position")
            _close(
                state["altitude_km"],
                radius - data["model"]["earth_radius_km"],
                p + ".altitude_km",
            )
            _close(
                state["lat_deg"],
                math.degrees(math.atan2(xyz[2], math.hypot(xyz[0], xyz[1]))),
                p + ".lat_deg",
            )
            longitude = math.degrees(math.atan2(xyz[1], xyz[0]))
            _require(
                abs((state["lon_deg"] - longitude + 180) % 360 - 180) < 1e-6,
                p + ".lon_deg",
                "ECEF mismatch",
            )
        pairs = set()
        for lid, l in links.items():
            a, b = l["source"], l["target"]
            _require(
                a in states and b in states and a != b,
                p + ".links",
                "unknown endpoint or self loop",
            )
            pair = tuple(sorted((a, b)))
            _require(pair not in pairs, p + ".links", "duplicate pair")
            pairs.add(pair)
            _require(
                states[a]["enabled"] and states[b]["enabled"],
                p + ".links",
                "disabled endpoint",
            )
            kinds = [objects[a]["kind"], objects[b]["kind"]]
            _require(
                kinds.count("ground_station") == (1 if l["kind"] == "gsl" else 0),
                p + ".links",
                "invalid link kind",
            )
            _close(
                l["propagation_ms"],
                l["distance_km"] / data["model"]["c_km_s"] * 1000,
                p + ".links." + lid,
            )
            _close(
                l["distance_km"],
                math.dist(states[a]["position_ecef_km"], states[b]["position_ecef_km"]),
                p + ".links." + lid + ".distance_km",
            )
        for qid, r in routes.items():
            rp = p + ".routes." + qid
            q = queries[qid]
            disabled = (
                not states[q["source"]]["enabled"] or not states[q["target"]]["enabled"]
            )
            nodes, lids = r["node_ids"], r["link_ids"]
            if r["status"] == "unreachable":
                _require(
                    not nodes
                    and not lids
                    and all(
                        r[k] is None for k in ("hops", "distance_km", "propagation_ms")
                    ),
                    rp,
                    "unreachable requires empty path and null metrics",
                )
                _require(
                    r["reason"] == ("endpoint_disabled" if disabled else "no_path"),
                    rp,
                    "invalid reason",
                )
                continue
            _require(
                not disabled and r["reason"] is None,
                rp,
                "reachable has disabled endpoint or reason",
            )
            _require(
                bool(nodes)
                and nodes[0] == q["source"]
                and nodes[-1] == q["target"]
                and len(set(nodes)) == len(nodes),
                rp,
                "invalid endpoints/cycle",
            )
            _require(
                len(lids) == len(nodes) - 1 and r["hops"] == len(lids),
                rp,
                "invalid hop count",
            )
            _require(
                all(n in states and states[n]["enabled"] for n in nodes),
                rp,
                "unknown/disabled path node",
            )
            _require(
                all(objects[n]["kind"] == "satellite" for n in nodes[1:-1]),
                rp,
                "GS cannot relay",
            )
            for j, lid in enumerate(lids):
                _require(
                    lid in links
                    and {links[lid]["source"], links[lid]["target"]}
                    == {nodes[j], nodes[j + 1]},
                    rp,
                    "missing/mismatched path edge",
                )
            _close(
                r["distance_km"],
                sum(links[l]["distance_km"] for l in lids),
                rp + ".distance_km",
            )
            _close(
                r["propagation_ms"],
                sum(links[l]["propagation_ms"] for l in lids),
                rp + ".propagation_ms",
            )
    expected = sorted(
        (f[k], f["node_id"], kind)
        for f in s["failures"]
        for k, kind in [("start_s", "failure_start"), ("end_s", "failure_end")]
        if recording["start_s"] <= f[k] <= recording["end_s"]
    )
    _require(
        sorted((e["t_s"], e["node_id"], e["kind"]) for e in data["events"]) == expected,
        "events",
        "scheduled events mismatch",
    )
    return data
