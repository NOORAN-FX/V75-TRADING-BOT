import tkinter as tk
from tkinter import ttk
import asyncio

class TradingBotGUI:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("V75 Prediction Bot")
        self.root.geometry("800x600")
        
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Time displays
        self.time_frame = ttk.LabelFrame(self.main_frame, text="Time")
        self.time_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.countdown_label = ttk.Label(self.time_frame, text="Time to 12 PM EAT: ")
        self.countdown_label.pack(pady=5)
        
        self.live_clock_label = ttk.Label(self.time_frame, text="Current Time: ")
        self.live_clock_label.pack(pady=5)
        
        # Status logs
        self.log_frame = ttk.LabelFrame(self.main_frame, text="Analysis Logs")
        self.log_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.log_text = tk.Text(self.log_frame, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Alert system
        self.alert_frame = ttk.LabelFrame(self.main_frame, text="Alerts")
        self.alert_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        self.alert_label = ttk.Label(self.alert_frame, text="No active alerts")
        self.alert_label.pack(pady=5)
        
    def update_countdown(self, time_remaining):
        self.countdown_label.config(text=f"Time to 12 PM EAT: {time_remaining}")
        
    def update_clock(self, current_time):
        self.live_clock_label.config(text=f"Current Time: {current_time}")
        
    def show_alert(self, direction, confidence, duration):
        self.alert_label.config(text=f"ALERT: Predicted {direction} (Confidence: {confidence}%)\nRecommended Duration: {duration}")
        
    def add_log_entry(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)


class TradingGUI:
    def setup_ui(self):
        # Analysis Display Section
        self.analysis_frame = ttk.LabelFrame(self.root, text="Live Analysis")
        self.analysis_text = tk.Text(self.analysis_frame, height=10, width=60)
        self.analysis_scroll = ttk.Scrollbar(self.analysis_frame, 
                                           command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=self.analysis_scroll.set)
        
        # Pack components
        self.analysis_frame.pack(pady=10, fill='both', expand=True)
        self.analysis_text.pack(side='left', fill='both', expand=True)
        self.analysis_scroll.pack(side='right', fill='y')

    def update(self, prediction):
        if prediction:
            analysis_output = f"""
            [ {datetime.now().strftime('%H:%M:%S')} ]
            Direction: {prediction['direction']}
            Confidence: {prediction['confidence']}%
            Recommended Duration: {prediction['duration']} mins
            """
            self.analysis_text.config(state='normal')
            self.analysis_text.insert('end', analysis_output)
            self.analysis_text.see('end')
            self.analysis_text.config(state='disabled')