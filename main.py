import tkinter as tk
from src.gui.app import SimpleSchedulerApp


def main():
    root = tk.Tk()
    root.title("CPU Scheduling Simulator")


    w, h = 700, 500
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    app = SimpleSchedulerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()