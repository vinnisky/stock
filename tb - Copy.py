import tkinter as tk
from tkinter import ttk, messagebox
from tvDatafeed import TvDatafeed, Interval
import pandas as pd

# Initialize TradingView API (no login needed for public data)
tv = TvDatafeed()

# Available time intervals
INTERVALS = {
    "1 Minute": Interval.in_1_minute,
    "5 Minutes": Interval.in_5_minute,
    "1 Hour": Interval.in_1_hour,
    "1 Day": Interval.in_daily,
}

class TradingViewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reliance Stock Data - TradingView")
        self.root.geometry("800x500")

        # Title Label
        tk.Label(root, text="Reliance Stock Data (NSE)", font=("Arial", 16, "bold")).pack(pady=10)

        # Interval Selection
        self.interval_var = tk.StringVar(value="1 Hour")
        ttk.Label(root, text="Select Time Interval:").pack()
        self.interval_menu = ttk.Combobox(root, textvariable=self.interval_var, values=list(INTERVALS.keys()), state="readonly")
        self.interval_menu.pack(pady=5)

        # Fetch Data Button
        self.fetch_button = ttk.Button(root, text="Fetch Data", command=self.fetch_data)
        self.fetch_button.pack(pady=10)

        # Treeview Table to Show Data
        self.tree = ttk.Treeview(root, columns=("Date", "Open", "High", "Low", "Close", "Volume"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

    def fetch_data(self):
        """Fetch stock data and display in table"""
        interval = INTERVALS[self.interval_var.get()]
        
        try:
            # Fetch data for Reliance from NSE
            data = tv.get_hist(symbol="RELIANCE", exchange="NSE", interval=interval, n_bars=100)
            
            if data is None or data.empty:
                messagebox.showerror("Error", "No data fetched. Try another interval.")
                return

            # Clear old data
            self.tree.delete(*self.tree.get_children())

            # Insert new data
            for index, row in data.iterrows():
                self.tree.insert("", "end", values=(index, row.open, row.high, row.low, row.close, row.volume))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data: {e}")

# Run the Tkinter App
if __name__ == "__main__":
    root = tk.Tk()
    app = TradingViewApp(root)
    root.mainloop()
