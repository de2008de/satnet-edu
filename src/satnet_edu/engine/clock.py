"""Pure sample grid; event boundaries are applied before recording their frame."""
import math
from ..config import number, integer


def sample_times(start_s, duration_s, step_s, failures=(), max_samples=10000):
    number(start_s, "start_s")
    number(duration_s, "duration_s")
    number(step_s, "step_s", positive=True)
    integer(max_samples, "max_samples")
    end = start_s + duration_s
    number(end, "end_s")
    count = math.floor(duration_s / step_s)
    if count + 1 > max_samples:
        raise ValueError(f"recording: exceeds max_samples={max_samples}")
    times = {start_s, end}
    times.update(start_s + i * step_s for i in range(1, count + 1) if start_s + i * step_s < end)
    for f in failures:
        times.update(t for t in (f["start_s"], f["end_s"]) if start_s <= t <= end)
    if len(times) > max_samples:
        raise ValueError(f"recording with event boundaries exceeds max_samples={max_samples}")
    return sorted(times)
