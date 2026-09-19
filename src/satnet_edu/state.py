"""Immutable public data objects. No mutable ephem object escapes the adapter."""

from dataclasses import dataclass
from types import MappingProxyType

from .config import identifier


@dataclass(frozen=True)
class RouteQuery:
    id: str
    source: str
    target: str
    metric: str = "delay"

    def __post_init__(self):
        for field in ("id", "source", "target"):
            identifier(getattr(self, field), field)
        if self.metric not in ("delay", "hops"):
            raise ValueError("metric: expected delay or hops")


@dataclass(frozen=True)
class NodeState:
    id: str
    enabled: bool
    position_ecef_km: tuple
    lat_deg: float
    lon_deg: float
    altitude_km: float


@dataclass(frozen=True)
class LinkState:
    id: str
    source: str
    target: str
    kind: str
    distance_km: float
    propagation_ms: float


@dataclass(frozen=True)
class Route:
    reachable: bool
    path: tuple
    link_ids: tuple
    hops: int | None
    distance_km: float | None
    propagation_ms: float | None
    metric: str
    reason: str | None


@dataclass(frozen=True)
class Snapshot:
    t_s: float
    nodes: object
    links: object
    kinds: object

    def __post_init__(self):
        for field in ("nodes", "links", "kinds"):
            object.__setattr__(
                self, field, MappingProxyType(dict(getattr(self, field)))
            )

    def route(self, source, target, metric="delay"):
        from .engine.routing import route

        return route(self, source, target, metric)
