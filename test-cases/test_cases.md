# OS Scheduling Algorithm Test Scenarios

This document outlines several test scenarios designed to verify the correctness of the scheduling algorithms implemented in this project (Round Robin and Non-Preemptive Priority Scheduling). Each scenario includes the input process details, the expected Gantt chart execution order, and the final calculated metrics.

## Scenario 1: Round Robin with small quantum

This scenario tests the standard Round Robin algorithm, focusing on how it handles processes arriving at different times and getting preempted after a short time quantum.

#### Input Processes
| Process ID | Arrival Time | Burst Time | Priority |
|---|---|---|---|
| P1 | 0 | 5 | 1 |
| P2 | 1 | 4 | 1 |
| P3 | 2 | 2 | 1 |
| P4 | 4 | 1 | 1 |

**Algorithm:** Round Robin (Quantum = 2)

#### Gantt Chart
`| P1 (0-2) | P2 (2-4) | P3 (4-6) | P1 (6-8) | P4 (8-9) | P2 (9-11) | P1 (11-12) |`

#### Output Metrics
| Process ID | Completion Time | Turnaround Time | Waiting Time | Response Time |
|---|---|---|---|---|
| P1 | 12 | 12 | 7 | 0 |
| P2 | 11 | 10 | 6 | 1 |
| P3 | 6 | 4 | 2 | 2 |
| P4 | 9 | 5 | 4 | 4 |

---

## Scenario 2: Priority Scheduling with CPU Idle Time

This scenario tests the Non-Preemptive Priority Scheduling algorithm and verifies that the system correctly handles idle time when the ready queue is completely empty before the next process arrives.

#### Input Processes
| Process ID | Arrival Time | Burst Time | Priority |
|---|---|---|---|
| P1 | 0 | 3 | 3 |
| P2 | 2 | 4 | 1 |
| P3 | 8 | 2 | 2 |
| P4 | 9 | 1 | 1 |

**Algorithm:** Non-Preemptive Priority Scheduling
*(Note: Lower number means higher priority)*

#### Gantt Chart
`| P1 (0-3) | P2 (3-7) | CPU Idle (7-8) | P3 (8-10) | P4 (10-11) |`

#### Output Metrics
| Process ID | Completion Time | Turnaround Time | Waiting Time | Response Time |
|---|---|---|---|---|
| P1 | 3 | 3 | 0 | 0 |
| P2 | 7 | 5 | 1 | 1 |
| P3 | 10 | 2 | 0 | 0 |
| P4 | 11 | 2 | 1 | 1 |


---

## Scenario 3: Round Robin with Simultaneous Arrivals

This scenario verifies the Round Robin algorithm's behavior when multiple processes arrive at the exact same time, checking that it correctly processes them in order of their Process IDs before moving through the queue.

#### Input Processes
| Process ID | Arrival Time | Burst Time | Priority |
|---|---|---|---|
| P1 | 0 | 4 | 1 |
| P2 | 0 | 5 | 1 |
| P3 | 0 | 2 | 1 |
| P4 | 0 | 1 | 1 |

**Algorithm:** Round Robin (Quantum = 3)

#### Gantt Chart
`| P1 (0-3) | P2 (3-6) | P3 (6-8) | P4 (8-9) | P1 (9-10) | P2 (10-12) |`

#### Output Metrics
| Process ID | Completion Time | Turnaround Time | Waiting Time | Response Time |
|---|---|---|---|---|
| P1 | 10 | 10 | 6 | 0 |
| P2 | 12 | 12 | 7 | 3 |
| P3 | 8 | 8 | 6 | 6 |
| P4 | 9 | 9 | 8 | 8 |
