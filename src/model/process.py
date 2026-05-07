from dataclasses import dataclass, field
from typing import List, Tuple, Dict

@dataclass
class Process:
    """Represents a process submitted to the scheduler."""
    pid: str
    arrival: int  # Arrival time
    burst: int  # CPU burst time needed
    priority: int  # Lower number = higher urgency


@dataclass
class ProcessResult:
    """Metrics for one process after scheduling."""
    pid: str
    arrival: int
    burst: int
    priority: int
    completion: int = 0
    wt: float = 0.0  # Waiting Time
    tat: float = 0.0  # Turnaround Time
    rt: float = 0.0  # Response Time (first execution - arrival)


# (process_id, start_time, end_time)
GanttEntry = Tuple[str, int, int]
