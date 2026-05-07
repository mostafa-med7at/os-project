from typing import List, Tuple
from src.model.process import Process, ProcessResult, GanttEntry

# ─── Round Robin ─────────────────────────────────────────────────────────────

def round_robin(processes: List[Process], quantum: int
                ) -> Tuple[List[GanttEntry], List[ProcessResult]]:
    """
    Round Robin Scheduling.

    Rules:
      - Processes are sorted by arrival time initially.
      - A ready queue rotates: after each time quantum, the running process
        is re-added to the back of the queue (if not finished).
      - Processes that arrive DURING a time slice are added to the ready queue
        AFTER the current slice finishes (standard FIFO queue behavior).
      - If the ready queue is empty, CPU is idle until the next arrival.

    Returns:
      gantt  : list of (pid, start, end) execution segments
      results: list of ProcessResult for each process
    """
    if not processes:
        return [], []

    # Sort by arrival, break ties by pid
    procs = sorted(processes, key=lambda p: (p.arrival, p.pid))
    n = len(procs)

    remaining = {p.pid: p.burst for p in procs}
    first_run = {p.pid: -1 for p in procs}
    completion = {p.pid: 0 for p in procs}
    proc_map = {p.pid: p for p in procs}

    gantt: List[GanttEntry] = []
    ready_queue: List[str] = []
    in_queue: set = set()
    time = 0
    idx = 0  # pointer into sorted procs for new arrivals
    completed = 0

    # Seed queue with t=0 arrivals
    while idx < n and procs[idx].arrival <= time:
        ready_queue.append(procs[idx].pid)
        in_queue.add(procs[idx].pid)
        idx += 1

    while completed < n:
        # If queue empty, jump forward to next arrival
        if not ready_queue:
            if idx < n:
                time = procs[idx].arrival
                while idx < n and procs[idx].arrival <= time:
                    ready_queue.append(procs[idx].pid)
                    in_queue.add(procs[idx].pid)
                    idx += 1
            continue

        pid = ready_queue.pop(0)
        in_queue.discard(pid)

        # Record first-run for response time
        if first_run[pid] == -1:
            first_run[pid] = time

        # Execute for min(quantum, remaining_burst)
        run_time = min(quantum, remaining[pid])
        start = time
        time += run_time
        remaining[pid] -= run_time

        gantt.append((pid, start, time))

        # Admit processes that arrived DURING this slice (before appending current)
        while idx < n and procs[idx].arrival <= time:
            new_pid = procs[idx].pid
            if new_pid not in in_queue and remaining[new_pid] > 0:
                ready_queue.append(new_pid)
                in_queue.add(new_pid)
            idx += 1

        if remaining[pid] == 0:
            completed += 1
            completion[pid] = time
        else:
            # Not finished — go back to end of queue
            ready_queue.append(pid)
            in_queue.add(pid)

    # Build results
    results = []
    for p in procs:
        tat = completion[p.pid] - p.arrival
        wt = tat - p.burst
        rt = first_run[p.pid] - p.arrival
        results.append(ProcessResult(
            pid=p.pid, arrival=p.arrival, burst=p.burst, priority=p.priority,
            completion=completion[p.pid], wt=wt, tat=tat, rt=rt
        ))

    return gantt, results


# ─── Priority Scheduling ─────────────────────────────────────────────────────

def priority_scheduling(processes: List[Process]
                        ) -> Tuple[List[GanttEntry], List[ProcessResult]]:

    if not processes:
        return [], []

    procs = sorted(processes, key=lambda p: p.arrival)
    n = len(procs)
    done = set()
    time = 0
    gantt: List[GanttEntry] = []
    completion = {}
    first_run = {}

    while len(done) < n:
        # All processes that have arrived and not yet completed
        available = [p for p in procs if p.arrival <= time and p.pid not in done]

        if not available:
            # CPU idle — jump to next arrival
            next_t = min(p.arrival for p in procs if p.pid not in done)
            time = next_t
            continue

        # Select: lowest priority number → earliest arrival → smallest pid
        selected = min(available, key=lambda p: (p.priority, p.arrival, p.pid))

        pid = selected.pid
        first_run[pid] = time
        start = time
        time += selected.burst
        gantt.append((pid, start, time))
        done.add(pid)
        completion[pid] = time

    # Build results
    results = []
    for p in procs:
        tat = completion[p.pid] - p.arrival
        wt = tat - p.burst
        rt = first_run[p.pid] - p.arrival
        results.append(ProcessResult(
            pid=p.pid, arrival=p.arrival, burst=p.burst, priority=p.priority,
            completion=completion[p.pid], wt=wt, tat=tat, rt=rt
        ))

    return gantt, results
