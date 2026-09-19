"""Shared input guards; bool is never accepted as a numeric parameter."""
import math
from datetime import datetime, timezone

DEFAULT_EPOCH = "2000-01-01T00:00:00Z"


def number(value, field, low=0, high=None, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{field}: expected a finite number")
    if value < low or (positive and value == low) or (high is not None and value > high):
        raise ValueError(f"{field}: expected {'>' if positive else '>='} {low}" + (f" and <= {high}" if high is not None else ""))
    return value


def integer(value, field, low=1, high=100000):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{field}: expected integer in [{low}, {high}]")
    return value


def identifier(value, field="id"):
    if not isinstance(value, str) or not value or len(value) > 256:
        raise ValueError(f"{field}: expected nonempty string, at most 256 characters")
    return value


def text(value, field="label"):
    if not isinstance(value, str) or len(value) > 4096:
        raise ValueError(f"{field}: expected string, at most 4096 characters")
    return value


def utc_epoch(value):
    if not isinstance(value, str):
        raise ValueError("epoch: expected ISO-8601 UTC string")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("epoch: expected ISO-8601 UTC string") from exc
    if dt.tzinfo is None or dt.utcoffset().total_seconds() != 0 or not 1957 <= dt.year <= 2056:
        raise ValueError("epoch: UTC offset required; TLE year must be 1957–2056")
    return dt.astimezone(timezone.utc)
