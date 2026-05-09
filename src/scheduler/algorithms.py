from typing import List, Tuple
from src.model.process import Process, ProcessResult, GanttEntry

# ─── Round Robin ─────────────────────────────────────────────────────────────

def round_robin(processes: List[Process], quantum: int
                ) -> Tuple[List[GanttEntry], List[ProcessResult]]:
   
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


# ─── Preemptive Priority Scheduling ──────────────────────────────────────────

def preemptive_priority_scheduling(processes: List[Process]
                                   ) -> Tuple[List[GanttEntry], List[ProcessResult]]:

    if not processes:
        return [], []

    # Sort processes by arrival
    procs = sorted(processes, key=lambda p: p.arrival)
    n = len(procs)
    
    remaining = {p.pid: p.burst for p in procs}
    first_run = {p.pid: -1 for p in procs}
    completion = {p.pid: 0 for p in procs}
    
    gantt: List[GanttEntry] = []
    time = 0
    completed = 0
    
    current_pid = None
    start_time = 0

    while completed < n:
        # Get all arrived processes that are not yet completed
        available = [p for p in procs if p.arrival <= time and remaining[p.pid] > 0]
        
        if not available:
            # If no process is available, jump time to the next arrival
            if current_pid is not None:
                gantt.append((current_pid, start_time, time))
                current_pid = None
            next_arrivals = [p.arrival for p in procs if remaining[p.pid] > 0 and p.arrival > time]
            if next_arrivals:
                time = min(next_arrivals)
            continue
            
        # Select highest priority (lowest number), break ties by earliest arrival then pid
        selected = min(available, key=lambda p: (p.priority, p.arrival, p.pid))
        
        # If CPU was idle or a new process preempted the current one
        if current_pid != selected.pid:
            # Save previous gantt segment
            if current_pid is not None:
                gantt.append((current_pid, start_time, time))
            
            # Record first run time for response time
            if first_run[selected.pid] == -1:
                first_run[selected.pid] = time
                
            current_pid = selected.pid
            start_time = time
            
        # Execute for 1 unit of time
        # Alternatively, execute until the next process arrives or the current finishes
        # Find time until next arrival or completion
        next_arr_time = min([p.arrival for p in procs if p.arrival > time] + [float('inf')])
        time_to_run = min(remaining[current_pid], next_arr_time - time)
        if time_to_run <= 0:
            time_to_run = 1 # Fallback just in case
            
        time += time_to_run
        remaining[current_pid] -= time_to_run
        
        if remaining[current_pid] == 0:
            completed += 1
            completion[current_pid] = time
            gantt.append((current_pid, start_time, time))
            current_pid = None

    # Complete the last running process if any
    if current_pid is not None:
        gantt.append((current_pid, start_time, time))

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
