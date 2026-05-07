from typing import List, Tuple
from src.model.process import ProcessResult

# ─── Statistics ──────────────────────────────────────────────────────────────

def compute_averages(results: List[ProcessResult]) -> Tuple[float, float, float]:
    """Return (avg_wt, avg_tat, avg_rt) for a list of ProcessResult."""
    if not results:
        return 0.0, 0.0, 0.0
    n = len(results)
    return (
        sum(r.wt for r in results) / n,
        sum(r.tat for r in results) / n,
        sum(r.rt for r in results) / n,
    )


def std_dev(values: List[float]) -> float:
    """Population standard deviation."""
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    return (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5
