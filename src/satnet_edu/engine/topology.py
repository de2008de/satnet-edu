"""UserGS neighbor rules with explicit membership, plus new physical filters."""

import json
from itertools import combinations

from ..state import LinkState
from .geometry import C_KM_S, distance, elevation_deg, visible_isl


def candidate_pairs(objects, constellations, topology):
    sats = [o for o in objects if o["kind"] == "satellite"]
    if topology == "distance":
        return sorted(
            tuple(sorted((a["id"], b["id"]))) for a, b in combinations(sats, 2)
        )
    manual = [o["id"] for o in sats if "constellation_id" not in o]
    if manual:
        raise ValueError("topology: manual satellites require topology='distance'")
    pairs = set()
    for c in constellations:
        slots, planes = c["sats_per_plane"], c["planes"]
        members = {
            (o["plane"], o["slot"]): o["id"]
            for o in sats
            if o["constellation_id"] == c["id"]
        }
        for (p, s), sid in members.items():
            # Forward edges represent both directions in this undirected graph.
            for target in (
                members[(p, (s + 1) % slots)],
                members[((p + 1) % planes, s)],
            ):
                if target != sid:
                    pairs.add(tuple(sorted((sid, target))))
    return sorted(pairs)


def build_links(objects, constellations, states, policy):
    links = {}

    def add(a, b, kind):
        a, b = sorted((a, b))
        length = distance(states[a].position_ecef_km, states[b].position_ecef_km)
        # JSON pair encoding is unambiguous even for IDs containing punctuation.
        lid = json.dumps([a, b], ensure_ascii=False, separators=(",", ":"))
        links[lid] = LinkState(lid, a, b, kind, length, length / C_KM_S * 1000)

    for a, b in candidate_pairs(objects, constellations, policy["topology"]):
        sa, sb = states[a], states[b]
        if (
            sa.enabled
            and sb.enabled
            and distance(sa.position_ecef_km, sb.position_ecef_km)
            <= policy["max_isl_km"]
            and visible_isl(sa.position_ecef_km, sb.position_ecef_km)
        ):
            add(a, b, "isl")
    for gs in (o for o in objects if o["kind"] == "ground_station"):
        g = states[gs["id"]]
        for sat in (o for o in objects if o["kind"] == "satellite"):
            s = states[sat["id"]]
            if (
                g.enabled
                and s.enabled
                and elevation_deg(g.position_ecef_km, s.position_ecef_km)
                >= policy["min_elevation_deg"]
            ):
                add(g.id, s.id, "gsl")
    return dict(sorted(links.items()))
