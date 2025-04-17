import tkinter as tk
from tkinter import ttk, messagebox
from tvDatafeed import TvDatafeed, Interval
import pandas as pd
from tradingview_ta import TA_Handler, Interval as TA_Interval, Exchange
import os
import threading
import time
import shutil
import tempfile

# Initialize TradingView API (no login needed for public data)
tv = TvDatafeed()

# Available time intervals (mapped to both libraries)
INTERVALS = {
    "1 Minute": (Interval.in_1_minute, TA_Interval.INTERVAL_1_MINUTE),
    "15 Minute": (Interval.in_15_minute, TA_Interval.INTERVAL_15_MINUTES),
    "1 Hour": (Interval.in_1_hour, TA_Interval.INTERVAL_1_HOUR),
    "1 Day": (Interval.in_daily, TA_Interval.INTERVAL_1_DAY),
}

# Excel file name
EXCEL_FILE = "stock_data.xlsx"
TEMP_FILE = os.path.join(tempfile.gettempdir(), "stock_data_temp.xlsx")

class TradingViewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NSE Stock Data - TradingView")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f0f0")

        # Style configuration
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10, "bold"), padding=5)
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

        # Define color tags for Technical Analysis
        self.tree_tag_colors = {
            "BUY": "green",
            "SELL": "red",
            "NEUTRAL": "gray",
            "STRONG_BUY": "darkgreen",
            "STRONG_SELL": "darkred"
        }

        # Title Label
        tk.Label(root, text="NSE Stock Data Dashboard", font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#333333").pack(pady=10)

        # Input Frame (Horizontal Layout)
        input_frame = tk.Frame(root, bg="#f0f0f0")
        input_frame.pack(pady=10)

        # Stock Selection (Fetched from Excel)
        self.stock_list = self.load_stocks_from_excel() or ["RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN",
                                                           "ICICIBANK", "HINDUNILVR", "KOTAKBANK", "LT", "BAJFINANCE"]
        self.stock_var = tk.StringVar(value=self.stock_list[0])
        ttk.Label(input_frame, text="Select Stock:").pack(side="left", padx=5)
        self.stock_menu = ttk.Combobox(input_frame, textvariable=self.stock_var, values=self.stock_list, state="readonly", width=20)
        self.stock_menu.pack(side="left", padx=5)

        # Interval Selection
        self.interval_var = tk.StringVar(value="1 Hour")
        ttk.Label(input_frame, text="Select Time Interval:").pack(side="left", padx=5)
        self.interval_menu = ttk.Combobox(input_frame, textvariable=self.interval_var, values=list(INTERVALS.keys()), state="readonly", width=20)
        self.interval_menu.pack(side="left", padx=5)

        # Fetch Data Button
        self.fetch_button = ttk.Button(input_frame, text="Fetch Data", command=self.fetch_data)
        self.fetch_button.pack(side="left", padx=5)

        # Table Frame with Scrollbar
        self.table_frame = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
        self.table_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Treeview Table (Matching Excel Columns)
        self.tree = ttk.Treeview(self.table_frame, columns=("stock", "Open", "High", "Low", "CMP", "Volume", 
                                                            "1 Minute", "15 Minute", "1 Hour", "1 Day"), 
                                 show="headings", height=15)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        
        # Configure tags for color coding
        for status, color in self.tree_tag_colors.items():
            self.tree.tag_configure(status, background=color, foreground="white")

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", expand=True, fill="both")

        # Load initial data from Excel
        self.load_initial_excel_data()

        # Start auto-update thread
        self.running = True
        self.update_thread = threading.Thread(target=self.auto_update_excel, daemon=True)
        self.update_thread.start()

    def load_stocks_from_excel(self):
        """Load stock list from the first column of the Excel file"""
        if os.path.exists(EXCEL_FILE):
            try:
                df = pd.read_excel(EXCEL_FILE)
                if "stock" in df.columns:
                    return list(df["stock"].dropna().unique())
            except Exception as e:
                print(f"Error loading stocks from Excel: {e}")
        return None

    def load_initial_excel_data(self):
        """Load initial data from Excel into Treeview"""
        self.tree.delete(*self.tree.get_children())
        if os.path.exists(EXCEL_FILE):
            try:
                df = pd.read_excel(EXCEL_FILE)
                for _, row in df.iterrows():
                    values = [row[col] for col in self.tree["columns"]]
                    tags = [row[col] for col in ["1 Minute", "15 Minute", "1 Hour", "1 Day"] if row[col] in self.tree_tag_colors]
                    self.tree.insert("", "end", iid=row["stock"], values=values, tags=tags)
            except Exception as e:
                print(f"Error loading initial Excel data into Treeview: {e}")
        else:
            # Populate with default stocks if no Excel file exists
            for stock in self.stock_list:
                self.tree.insert("", "end", iid=stock, values=(stock, "-", "-", "-", "-", "-", "-", "-", "-", "-"))

    def update_treeview_row(self, stock, data):
        """Update a single row in the Treeview"""
        values = [data[col] for col in self.tree["columns"]]
        tags = [data[col] for col in ["1 Minute", "15 Minute", "1 Hour", "1 Day"] if data[col] in self.tree_tag_colors]
        if self.tree.exists(stock):
            self.tree.item(stock, values=values, tags=tags)
        else:
            self.tree.insert("", "end", iid=stock, values=values, tags=tags)

    def fetch_data(self):
        """Fetch stock data for the selected stock and update UI"""
        interval_key = self.interval_var.get()
        tv_interval, _ = INTERVALS[interval_key]
        selected_stock = self.stock_var.get()
        
        try:
            # Fetch data and update Excel and Treeview
            data = self.update_excel(selected_stock)
            if data:
                self.update_treeview_row(selected_stock, data)
            else:
                messagebox.showerror("Error", f"No data fetched for {selected_stock}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data for {selected_stock}: {e}")

    def update_excel(self, stock):
        """Fetch and update Excel data for a single stock, return data for Treeview"""
        try:
            # Fetch latest data (using 1-minute interval for the most recent data point)
            data = tv.get_hist(symbol=stock, exchange="NSE", interval=Interval.in_1_minute, n_bars=1)
            if data is None or data.empty:
                return None

            latest_row = data.iloc[-1]

            # Fetch Technical Analysis for all intervals
            ta_data = {}
            for interval_name, (_, ta_int) in INTERVALS.items():
                stock_ta = TA_Handler(symbol=stock, screener="india", exchange="NSE", interval=ta_int)
                analysis = stock_ta.get_analysis().summary
                ta_data[interval_name] = analysis["RECOMMENDATION"]

            # Prepare data for Excel and Treeview
            excel_data = {
                "stock": stock,
                "Open": latest_row["open"],
                "High": latest_row["high"],
                "Low": latest_row["low"],
                "CMP": latest_row["close"],
                "Volume": latest_row["volume"],
                "1 Minute": ta_data["1 Minute"],
                "15 Minute": ta_data["15 Minute"],
                "1 Hour": ta_data["1 Hour"],
                "1 Day": ta_data["1 Day"]
            }

            # Update Excel file with temp file approach
            columns = ["stock", "Open", "High", "Low", "CMP", "Volume", "1 Minute", "15 Minute", "1 Hour", "1 Day"]
            if os.path.exists(EXCEL_FILE):
                df = pd.read_excel(EXCEL_FILE)
                if stock in df["stock"].values:
                    df.loc[df["stock"] == stock, columns] = [excel_data[col] for col in columns]
                else:
                    df = pd.concat([df, pd.DataFrame([excel_data])], ignore_index=True)
            else:
                df = pd.DataFrame([excel_data], columns=columns)

            # Write to a temporary file first
            with pd.ExcelWriter(TEMP_FILE, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)

            # Attempt to replace the original file
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    shutil.move(TEMP_FILE, EXCEL_FILE)
                    break
                except PermissionError:
                    if attempt == max_retries - 1:
                        self.root.after(0, lambda: messagebox.showwarning(
                            "File Locked",
                            f"Cannot update {EXCEL_FILE} because it is open in another program. Please close it to allow updates."
                        ))
                    time.sleep(2)

            return excel_data

        except Exception as e:
            print(f"Error updating {stock}: {e}")
            return None

    def auto_update_excel(self):
        """Automatically update Excel and Treeview row by row every minute"""
        while self.running:
            for stock in self.stock_list:
                data = self.update_excel(stock)
                if data:
                    self.update_treeview_row(stock, data)
                time.sleep(1)  # Small delay between stocks to avoid overwhelming the API
            time.sleep(60 - len(self.stock_list))  # Adjust sleep to total 60 seconds

    def on_closing(self):
        """Handle window close event"""
        self.running = False
        self.root.destroy()

# Run the Tkinter App
if __name__ == "__main__":
    root = tk.Tk()
    app = TradingViewApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()