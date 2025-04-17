import tkinter as tk
from tkinter import ttk
import requests
import pandas as pd
from threading import Thread
import time

class NSEOpenInterestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NSE Futures Open Interest Tracker")
        self.root.geometry("600x400")
        
        self.tree = ttk.Treeview(root, columns=("Symbol", "OI", "Change"), show="headings")
        self.tree.heading("Symbol", text="Symbol")
        self.tree.heading("OI", text="Open Interest")
        self.tree.heading("Change", text="Change (%)")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.prev_data = {}
        self.update_data()
        
    def fetch_nse_oi(self):
        url = "https://www.nseindia.com/api/option-chain-equities?symbol=BANKNIFTY"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            oi_data = []
            
            for record in data.get("records", {}).get("data", []):
                symbol = record.get("CE", {}).get("underlying", "Unknown")
                oi = record.get("CE", {}).get("openInterest", 0)
                oi_data.append((symbol, oi))
            
            return oi_data
        except Exception as e:
            print("Error fetching data:", e)
            return []
    
    def update_data(self):
        data = self.fetch_nse_oi()
        
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        for symbol, oi in data:
            prev_oi = self.prev_data.get(symbol, 0)
            change = ((oi - prev_oi) / prev_oi * 100) if prev_oi else 0
            self.tree.insert("", tk.END, values=(symbol, oi, f"{change:.2f}%"))
            self.prev_data[symbol] = oi
        
        self.root.after(60000, self.update_data)  # Update every 60 seconds

if __name__ == "__main__":
    root = tk.Tk()
    app = NSEOpenInterestApp(root)
    root.mainloop()
