import tkinter as tk
from tkinter import ttk, messagebox
from tvDatafeed import TvDatafeed, Interval
import pandas as pd
from tradingview_ta import TA_Handler, Interval as TA_Interval, Exchange
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Initialize TradingView API (no login needed for public data)
tv = TvDatafeed()

# Available time intervals (mapped to both libraries)
INTERVALS = {
    "1 Minute": (Interval.in_1_minute, TA_Interval.INTERVAL_1_MINUTE),
    "5 Minutes": (Interval.in_5_minute, TA_Interval.INTERVAL_5_MINUTES),
    "1 Hour": (Interval.in_1_hour, TA_Interval.INTERVAL_1_HOUR),
    "1 Day": (Interval.in_daily, TA_Interval.INTERVAL_1_DAY),
}

# Sample list of NSE stock symbols (you can expand this list)
NSE_STOCKS = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN",
    "ICICIBANK", "HINDUNILVR", "KOTAKBANK", "LT", "BAJFINANCE"
]

class TradingViewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NSE Stock Data - TradingView")
        self.root.geometry("900x800")  # Slightly wider for better layout
        self.root.configure(bg="#f0f0f0")  # Light gray background

        # Style configuration
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10, "bold"), padding=5)
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

        # Title Label
        tk.Label(root, text="NSE Stock Data Dashboard", font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#333333").pack(pady=10)

        # Input Frame (Horizontal Layout)
        input_frame = tk.Frame(root, bg="#f0f0f0")
        input_frame.pack(pady=10)

        # Stock Selection
        self.stock_var = tk.StringVar(value="RELIANCE")
        ttk.Label(input_frame, text="Select Stock:").pack(side="left", padx=5)
        self.stock_menu = ttk.Combobox(input_frame, textvariable=self.stock_var, values=NSE_STOCKS, state="readonly", width=20)
        self.stock_menu.pack(side="left", padx=5)

        # Interval Selection
        self.interval_var = tk.StringVar(value="1 Hour")
        ttk.Label(input_frame, text="Select Time Interval:").pack(side="left", padx=5)
        self.interval_menu = ttk.Combobox(input_frame, textvariable=self.interval_var, values=list(INTERVALS.keys()), state="readonly", width=20)
        self.interval_menu.pack(side="left", padx=5)

        # Fetch Data Button
        self.fetch_button = ttk.Button(input_frame, text="Fetch Data", command=self.fetch_data)
        self.fetch_button.pack(side="left", padx=5)

        # Technical Analysis Frame (Left: Text, Right: Horizontal Bar Chart)
        self.ta_frame = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
        self.ta_frame.pack(pady=10, padx=10, fill="x")

        # TA Text (Left)
        tk.Label(self.ta_frame, text="Technical Analysis", font=("Arial", 12, "bold"), bg="#ffffff", fg="#333333").pack(pady=5)
        self.ta_text = tk.Text(self.ta_frame, height=6, width=30, font=("Arial", 10), bg="#ffffff", fg="#333333", bd=0)
        self.ta_text.pack(side="left", padx=10, pady=5)
        self.ta_text.config(state="disabled")

        # TA Graph (Right)
        self.graph_frame = tk.Frame(self.ta_frame, bg="#ffffff")
        self.graph_frame.pack(side="right", padx=10, pady=5)
        self.canvas = None  # Placeholder for the bar chart

        # Table Frame with Scrollbar
        self.table_frame = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
        self.table_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Treeview Table to Show Stock Data with Scrollbar
        self.tree = ttk.Treeview(self.table_frame, columns=("Date", "Open", "High", "Low", "Close", "Volume"), show="headings", height=15)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")
        
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", expand=True, fill="both")

    def fetch_data(self):
        """Fetch stock data and technical analysis for the selected stock, then display"""
        interval_key = self.interval_var.get()
        tv_interval, ta_interval = INTERVALS[interval_key]
        selected_stock = self.stock_var.get()
        
        try:
            # Fetch data for the selected stock from NSE
            data = tv.get_hist(symbol=selected_stock, exchange="NSE", interval=tv_interval, n_bars=100)
            
            if data is None or data.empty:
                messagebox.showerror("Error", f"No data fetched for {selected_stock}. Try another stock or interval.")
                return

            # Clear old data
            self.tree.delete(*self.tree.get_children())

            # Insert new data
            for index, row in data.iterrows():
                self.tree.insert("", "end", values=(index, row.open, row.high, row.low, row.close, row.volume))

            # Fetch Technical Analysis for the selected stock
            stock_ta = TA_Handler(
                symbol=selected_stock,
                screener="india",
                exchange="NSE",
                interval=ta_interval
            )
            analysis = stock_ta.get_analysis().summary

            # Display Technical Analysis Text
            ta_summary = f"Recommendation: {analysis['RECOMMENDATION']}\n"
            ta_summary += f"Buy: {analysis['BUY']}\n"
            ta_summary += f"Neutral: {analysis['NEUTRAL']}\n"
            ta_summary += f"Sell: {analysis['SELL']}"
            
            self.ta_text.config(state="normal")
            self.ta_text.delete(1.0, tk.END)
            self.ta_text.insert(tk.END, ta_summary)
            self.ta_text.config(state="disabled")

            # Plot Technical Analysis Horizontal Bar Chart
            self.plot_ta_bar(analysis)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data for {selected_stock}: {e}")

    def plot_ta_bar(self, analysis):
        """Plot a horizontal bar chart for Technical Analysis"""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()  # Clear previous chart

        # Data for plotting
        categories = ["Sell", "Neutral", "Buy"]  # Reversed order for bottom-to-top
        values = [analysis["SELL"], analysis["NEUTRAL"], analysis["BUY"]]
        colors = ["red", "gray", "green"]

        # Create horizontal bar chart
        fig, ax = plt.subplots(figsize=(4, 2.5))
        ax.barh(categories, values, color=colors)
        ax.set_title("Technical Analysis", fontsize=10)
        ax.set_xlabel("Count", fontsize=8)

        # Customize
        ax.tick_params(axis='both', labelsize=8)
        for i, v in enumerate(values):
            ax.text(v + 0.2, i, str(v), va='center', fontsize=8)

        # Embed in Tkinter
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
        plt.close(fig)

# Run the Tkinter App
if __name__ == "__main__":
    root = tk.Tk()
    app = TradingViewApp(root)
    root.mainloop()