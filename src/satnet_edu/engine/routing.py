"""Deterministic snapshot shortest paths. Ground stations are endpoints only."""

import heapq

from ..state import Route


def route(snapshot, source, target, metric):
    if metric not in ("delay", "hops"):
        raise ValueError("metric: expected delay or hops")
    for node in (source, target):
        if node not in snapshot.nodes:
            raise ValueError(f"route: unknown node {node}")

    def missing(reason):
        return Route(False, (), (), None, None, None, metric, reason)

    if not snapshot.nodes[source].enabled or not snapshot.nodes[target].enabled:
        return missing("endpoint_disabled")
    adjacency = {n: [] for n in snapshot.nodes}
    for link in snapshot.links.values():
        adjacency[link.source].append((link.target, link))
        adjacency[link.target].append((link.source, link))
    # Exact binary float comparison; no tolerance-based non-transitive ordering.
    # Primary, secondary, full ID sequence provide stable ties.
    queue = [(0, 0, (source,), (), 0.0, 0.0)]
    best = {}
    while queue:
        primary, secondary, path, lids, km, ms = heapq.heappop(queue)
        node = path[-1]
        key = (primary, secondary, path)
        if node in best:
            continue
        best[node] = key
        if node == target:
            return Route(True, path, lids, len(lids), km, ms, metric, None)
        if node != source and snapshot.kinds[node] == "ground_station":
            continue
        for nxt, link in sorted(adjacency[node], key=lambda item: item[0]):
            if nxt in path or not snapshot.nodes[nxt].enabled:
                continue
            dist, delay, hops = (
                km + link.distance_km,
                ms + link.propagation_ms,
                len(lids) + 1,
            )
            a, b = (delay, hops) if metric == "delay" else (hops, delay)
            heapq.heappush(queue, (a, b, path + (nxt,), lids + (link.id,), dist, delay))
    return missing("no_path")
