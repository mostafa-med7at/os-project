import tkinter as tk
from tkinter import ttk, messagebox
from src.model.process import Process
from src.scheduler.algorithms import round_robin, priority_scheduling, preemptive_priority_scheduling
from src.metrics.statistics import compute_averages


class SimpleSchedulerApp:

    def __init__(self, root):
        self.root = root
        self.processes = []
        self.build_ui()

    # =========================================================
    def build_ui(self):
    # =========================================================
        # ===== Input Frame =====
        frame = ttk.LabelFrame(self.root, text="Input Panel")
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text="PID").grid(row=0, column=0)
        ttk.Label(frame, text="Arrival").grid(row=0, column=1)
        ttk.Label(frame, text="Burst").grid(row=0, column=2)
        ttk.Label(frame, text="Priority").grid(row=0, column=3)

        self.pid      = ttk.Entry(frame, width=8)
        self.arrival  = ttk.Entry(frame, width=8)
        self.burst    = ttk.Entry(frame, width=8)
        self.priority = ttk.Entry(frame, width=8)

        self.pid.grid(row=1, column=0)
        self.arrival.grid(row=1, column=1)
        self.burst.grid(row=1, column=2)
        self.priority.grid(row=1, column=3)

        ttk.Button(frame, text="Add Process",
                   command=self.add_process).grid(row=1, column=4, padx=5)

        # Quantum
        ttk.Label(frame, text="Quantum").grid(row=0, column=5)
        self.quantum = ttk.Entry(frame, width=8)
        self.quantum.grid(row=1, column=5)

        # ===== Table =====
        self.table = ttk.Treeview(
            self.root,
            columns=("PID", "A", "B", "P"),
            show="headings",
            height=5
        )
        for col in ("PID", "A", "B", "P"):
            self.table.heading(col, text=col)
        self.table.pack(fill="x", padx=10, pady=5)

        # ===== Buttons =====
        btn_frame = tk.Frame(self.root)
        btn_frame.pack()

        ttk.Button(btn_frame, text="Run Simulation",
                   command=self.run).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear",
                   command=self.clear).pack(side="left", padx=5)

        # ===== Scenario Buttons =====
        sc_frame = ttk.LabelFrame(self.root, text="Test Scenarios")
        sc_frame.pack(fill="x", padx=10, pady=5)

        scenarios = [
            ("A - Mixed",      self.scenario_a),
            ("B - Urgency",    self.scenario_b),
            ("C - Fairness",   self.scenario_c),
            ("D - Starvation", self.scenario_d),
            ("E - Validation", self.scenario_e),
        ]
        for i, (label, cmd) in enumerate(scenarios):
            ttk.Button(sc_frame, text=label, command=cmd,
                       width=18).grid(row=0, column=i, padx=6, pady=6)

        # ===== Notebook (Tabs) =====
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Tab 1: Gantt Charts
        self.tab_gantt = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_gantt, text="Gantt Charts")
        self.gantt_text = tk.Text(self.tab_gantt, height=10, font=("Courier", 10))
        self.gantt_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Tab 2: RR Results
        self.tab_rr = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_rr, text="RR Results")
        self.rr_tree = ttk.Treeview(self.tab_rr, columns=("PID", "WT", "TAT", "RT"), show="headings", height=8)
        for col in ("PID", "WT", "TAT", "RT"):
            self.rr_tree.heading(col, text=col)
        self.rr_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.rr_summary = ttk.Label(self.tab_rr, text="", font=("TkDefaultFont", 10, "bold"))
        self.rr_summary.pack(pady=5)

        # Tab 3: Priority Results
        self.tab_pr = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pr, text="Non-Preempt Priority")
        self.pr_tree = ttk.Treeview(self.tab_pr, columns=("PID", "WT", "TAT", "RT"), show="headings", height=8)
        for col in ("PID", "WT", "TAT", "RT"):
            self.pr_tree.heading(col, text=col)
        self.pr_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.pr_summary = ttk.Label(self.tab_pr, text="", font=("TkDefaultFont", 10, "bold"))
        self.pr_summary.pack(pady=5)

        # Tab 4: Preemptive Priority Results
        self.tab_ppr = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_ppr, text="Preempt Priority")
        self.ppr_tree = ttk.Treeview(self.tab_ppr, columns=("PID", "WT", "TAT", "RT"), show="headings", height=8)
        for col in ("PID", "WT", "TAT", "RT"):
            self.ppr_tree.heading(col, text=col)
        self.ppr_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.ppr_summary = ttk.Label(self.tab_ppr, text="", font=("TkDefaultFont", 10, "bold"))
        self.ppr_summary.pack(pady=5)

        # Tab 5: Analysis & Conclusion
        self.tab_analysis = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_analysis, text="Analysis & Conclusion")
        self.analysis_text = tk.Text(self.tab_analysis, height=15, wrap="word")
        self.analysis_text.pack(fill="both", expand=True, padx=5, pady=5)

    # =========================================================
    # VALIDATION
    # =========================================================

    def validate_process_fields(self, pid, arrival_s, burst_s, priority_s):
        errors = []

        if not pid.strip():
            errors.append("• PID cannot be empty.")
        elif any(p.pid == pid.strip() for p in self.processes):
            errors.append(f"• PID '{pid.strip()}' already exists.")

        arrival = None
        try:
            arrival = int(arrival_s)
            if arrival < 0:
                errors.append("• Arrival Time must be >= 0.")
        except ValueError:
            errors.append(f"• Arrival Time must be a whole number.")

        burst = None
        try:
            burst = int(burst_s)
            if burst <= 0:
                errors.append("• Burst Time must be > 0.")
        except ValueError:
            errors.append(f"• Burst Time must be a whole number.")

        priority = None
        try:
            priority = int(priority_s)
            if priority < 1:
                errors.append("• Priority must be >= 1.")
        except ValueError:
            errors.append(f"• Priority must be a whole number.")

        if errors:
            raise ValueError("\n".join(errors))

        return arrival, burst, priority

    def validate_quantum(self, quantum_s):
        try:
            q = int(quantum_s)
            if q <= 0:
                raise ValueError("Time Quantum must be > 0.")
            return q
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"Time Quantum must be a whole number.")
            raise

    # =========================================================
    # HELPER — load scenario data into table
    # =========================================================

    def _load_scenario(self, rows, quantum):
        self.clear()
        self.quantum.delete(0, tk.END)
        self.quantum.insert(0, str(quantum))
        for pid, arr, bst, pri in rows:
            p = Process(pid=pid, arrival=arr, burst=bst, priority=pri)
            self.processes.append(p)
            self.table.insert("", "end", values=(pid, arr, bst, pri))

    # =========================================================
    # SCENARIOS
    # =========================================================

    def scenario_a(self):
        self._load_scenario([
            ("P1", 0, 5, 3), ("P2", 1, 3, 1), ("P3", 2, 8, 4),
            ("P4", 3, 6, 2), ("P5", 4, 2, 5),
        ], quantum=3)

    def scenario_b(self):
        self._load_scenario([
            ("P1", 0, 8, 4), ("P2", 0, 6, 5), ("P3", 0, 4, 1),
            ("P4", 1, 7, 3), ("P5", 2, 5, 2),
        ], quantum=3)

    def scenario_c(self):
        self._load_scenario([
            ("P1", 0, 10, 3), ("P2", 0, 10, 1),
            ("P3", 0, 10, 2), ("P4", 0, 10, 4),
        ], quantum=4)

    def scenario_d(self):
        self._load_scenario([
            ("P1", 0, 3, 1), ("P2", 0, 3, 1), ("P3", 0, 3, 1),
            ("P4", 0, 3, 1), ("P5", 0, 3, 5), ("P6", 1, 3, 1),
            ("P7", 2, 3, 1),
        ], quantum=2)

    def scenario_e(self):
        self.clear()
        for field, val in [(self.pid, "P_BAD"), (self.arrival, "-1"),
                           (self.burst, "0"), (self.priority, "0"),
                           (self.quantum, "abc")]:
            field.delete(0, tk.END)
            field.insert(0, val)
        messagebox.showwarning("Validation", "Invalid values loaded. Click 'Add Process'.")

    # =========================================================
    # ADD / CLEAR
    # =========================================================

    def add_process(self):
        pid_val = self.pid.get().strip()
        try:
            arrival, burst, priority = self.validate_process_fields(
                pid_val, self.arrival.get(), self.burst.get(), self.priority.get()
            )
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return

        p = Process(pid=pid_val, arrival=arrival, burst=burst, priority=priority)
        self.processes.append(p)
        self.table.insert("", "end", values=(p.pid, p.arrival, p.burst, p.priority))

    def clear(self):
        self.processes.clear()
        for i in self.table.get_children():
            self.table.delete(i)
        for i in self.rr_tree.get_children():
            self.rr_tree.delete(i)
        for i in self.pr_tree.get_children():
            self.pr_tree.delete(i)
        for i in self.ppr_tree.get_children():
            self.ppr_tree.delete(i)
        self.gantt_text.delete("1.0", tk.END)
        self.analysis_text.delete("1.0", tk.END)
        self.rr_summary.config(text="")
        self.pr_summary.config(text="")
        self.ppr_summary.config(text="")

    # =========================================================
    # CONCLUSION GENERATOR
    # =========================================================

    def format_gantt(self, gantt_data):
        if not gantt_data:
            return "Idle"
        parts = []
        for pid, start, end in gantt_data:
            parts.append(f"[{start}]--{pid}--[{end}]")
        return " -> ".join(parts)

    def show_conclusion(self, rr_res, rr_avg, pr_res, pr_avg, ppr_res, ppr_avg):
        rr_wt, rr_tat, rr_rt = rr_avg
        pr_wt, pr_tat, pr_rt = pr_avg
        ppr_wt, ppr_tat, ppr_rt = ppr_avg

        # Determine best algorithm based on WT
        wt_scores = {"Round Robin": rr_wt, "Non-Preempt Priority": pr_wt, "Preempt Priority": ppr_wt}
        rt_scores = {"Round Robin": rr_rt, "Non-Preempt Priority": pr_rt, "Preempt Priority": ppr_rt}
        
        better_wt = min(wt_scores, key=wt_scores.get)
        better_rt = min(rt_scores, key=rt_scores.get)
        
        # Calculate WT standard deviations for fairness
        rr_wts  = [r.wt for r in rr_res]
        pr_wts  = [r.wt for r in pr_res]
        ppr_wts = [r.wt for r in ppr_res]
        
        rr_mean = sum(rr_wts) / len(rr_wts) if rr_wts else 0
        pr_mean = sum(pr_wts) / len(pr_wts) if pr_wts else 0
        ppr_mean = sum(ppr_wts) / len(ppr_wts) if ppr_wts else 0
        
        rr_std  = (sum((v - rr_mean) ** 2 for v in rr_wts) / len(rr_wts)) ** 0.5 if len(rr_wts) > 0 else 0
        pr_std  = (sum((v - pr_mean) ** 2 for v in pr_wts) / len(pr_wts)) ** 0.5 if len(pr_wts) > 0 else 0
        ppr_std  = (sum((v - ppr_mean) ** 2 for v in ppr_wts) / len(ppr_wts)) ** 0.5 if len(ppr_wts) > 0 else 0

        # High priority check
        rr_map   = {r.pid: r for r in rr_res}
        pr_map   = {r.pid: r for r in pr_res}
        ppr_map  = {r.pid: r for r in ppr_res}
        
        top_n    = max(1, len(self.processes) // 3)
        top_pids = {p.pid for p in sorted(self.processes, key=lambda p: p.priority)[:top_n]}
        
        hp_rr    = sum(rr_map[p].wt for p in top_pids) / len(top_pids) if top_pids else 0
        hp_pr    = sum(pr_map[p].wt for p in top_pids) / len(top_pids) if top_pids else 0
        hp_ppr   = sum(ppr_map[p].wt for p in top_pids) / len(top_pids) if top_pids else 0
        
        urgent   = hp_pr < hp_rr * 0.9 or hp_ppr < hp_rr * 0.9

        # Starvation check (checking both priority algorithms)
        max_pri   = max(r.priority for r in pr_res) if pr_res else 0
        low_procs_pr = [r for r in pr_res if r.priority == max_pri]
        low_procs_ppr = [r for r in ppr_res if r.priority == max_pri]
        
        starved   = any(r.wt > pr_wt * 2.0 for r in low_procs_pr) or any(r.wt > ppr_wt * 2.0 for r in low_procs_ppr)
        low_names = ", ".join(r.pid for r in low_procs_pr)

        recommend = better_wt

        analysis = "=== REQUIRED ANALYSIS QUESTIONS ===\n\n"
        analysis += f"1. Which algorithm gave better average waiting time?\n   -> {better_wt} (RR: {rr_wt:.2f}, NP-PR: {pr_wt:.2f}, P-PR: {ppr_wt:.2f})\n\n"
        analysis += f"2. Which algorithm gave better response time?\n   -> {better_rt} (RR: {rr_rt:.2f}, NP-PR: {pr_rt:.2f}, P-PR: {ppr_rt:.2f})\n\n"
        analysis += f"3. Did higher-priority processes gain significant advantage?\n   -> {'Yes' if urgent else 'No'}. High-priority avg WT -> NP-PR: {hp_pr:.2f}, P-PR: {hp_ppr:.2f} vs RR: {hp_rr:.2f}\n\n"
        
        fairest = "Round Robin"
        if pr_std < rr_std and pr_std <= ppr_std:
            fairest = "Non-Preempt Priority"
        elif ppr_std < rr_std and ppr_std < pr_std:
            fairest = "Preempt Priority"
            
        analysis += f"4. Did Round Robin appear more balanced across all processes?\n   -> {'Yes' if fairest == 'Round Robin' else 'No'}. WT Std Dev -> RR: {rr_std:.2f}, NP-PR: {pr_std:.2f}, P-PR: {ppr_std:.2f}\n\n"
        analysis += f"5. Was starvation observed or likely in Priority Scheduling?\n   -> {'Yes' if starved else 'No'}. Lowest priority process(es) [{low_names}] waited significantly.\n\n"
        analysis += f"6. Which algorithm would you recommend for the tested workload, and why?\n   -> {recommend}, because it provided the most optimal overall waiting time.\n\n"
        
        analysis += "=" * 50 + "\n"
        analysis += "=== REQUIRED CONCLUSION ===\n\n"
        analysis += f"- {better_wt} performed better on the selected dataset in terms of average waiting time.\n"
        analysis += f"- Priority-based service {'DID' if urgent else 'DID NOT'} improve urgent-task treatment.\n"
        analysis += f"- Round Robin {'DID' if fairest == 'Round Robin' else 'DID NOT'} improve fairness.\n"
        analysis += f"- Starvation risk {'APPEARED' if starved else 'DID NOT appear'} for lowest priority processes."

        self.analysis_text.delete("1.0", tk.END)
        self.analysis_text.insert(tk.END, analysis)

    # =========================================================
    # RUN SIMULATION
    # =========================================================

    def run(self):
        if not self.processes:
            messagebox.showwarning("Warning", "No Processes")
            return

        try:
            q = self.validate_quantum(self.quantum.get())
        except ValueError as e:
            messagebox.showerror("Invalid Quantum", str(e))
            return

        # Run all algorithms
        rr_gantt, rr_res = round_robin(self.processes, q)
        pr_gantt, pr_res = priority_scheduling(self.processes)
        ppr_gantt, ppr_res = preemptive_priority_scheduling(self.processes)

        rr_avg = compute_averages(rr_res)
        pr_avg = compute_averages(pr_res)
        ppr_avg = compute_averages(ppr_res)

        # Clear previous UI state
        for i in self.rr_tree.get_children(): self.rr_tree.delete(i)
        for i in self.pr_tree.get_children(): self.pr_tree.delete(i)
        for i in self.ppr_tree.get_children(): self.ppr_tree.delete(i)
        self.gantt_text.delete("1.0", tk.END)

        # Update Gantt Tab
        self.gantt_text.insert(tk.END, "=== Round Robin Gantt Chart ===\n\n")
        self.gantt_text.insert(tk.END, self.format_gantt(rr_gantt) + "\n\n\n")
        self.gantt_text.insert(tk.END, "=== Non-Preemptive Priority Gantt Chart ===\n\n")
        self.gantt_text.insert(tk.END, self.format_gantt(pr_gantt) + "\n\n\n")
        self.gantt_text.insert(tk.END, "=== Preemptive Priority Gantt Chart ===\n\n")
        self.gantt_text.insert(tk.END, self.format_gantt(ppr_gantt) + "\n")

        # Update RR Results Tab
        for r in rr_res:
            self.rr_tree.insert("", "end", values=(r.pid, r.wt, r.tat, r.rt))
        self.rr_summary.config(text=f"Averages -> WT: {rr_avg[0]:.2f} | TAT: {rr_avg[1]:.2f} | RT: {rr_avg[2]:.2f}")

        # Update Non-Preemptive Priority Results Tab
        for r in pr_res:
            self.pr_tree.insert("", "end", values=(r.pid, r.wt, r.tat, r.rt))
        self.pr_summary.config(text=f"Averages -> WT: {pr_avg[0]:.2f} | TAT: {pr_avg[1]:.2f} | RT: {pr_avg[2]:.2f}")

        # Update Preemptive Priority Results Tab
        for r in ppr_res:
            self.ppr_tree.insert("", "end", values=(r.pid, r.wt, r.tat, r.rt))
        self.ppr_summary.config(text=f"Averages -> WT: {ppr_avg[0]:.2f} | TAT: {ppr_avg[1]:.2f} | RT: {ppr_avg[2]:.2f}")

        # Update Analysis & Conclusion Tab
        self.show_conclusion(rr_res, rr_avg, pr_res, pr_avg, ppr_res, ppr_avg)

        # Switch to Gantt tab so the user sees results immediately
        self.notebook.select(self.tab_gantt)
