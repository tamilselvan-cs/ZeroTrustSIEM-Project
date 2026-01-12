# siem_dashboard/views/logs_view.py
import customtkinter as ctk
from datetime import datetime

class LogsView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db

        # Header
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=10)
        ctk.CTkLabel(top_bar, text="🗄️ Full System Logs", font=("Arial", 20, "bold")).pack(side="left")
        
        ctk.CTkButton(top_bar, text="🔄 Refresh", command=self.load_logs, width=100).pack(side="right")

        # Table Area
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="#1e293b")
        self.scroll.pack(fill="both", expand=True)
        
        self.load_logs()

    def load_logs(self):
        for widget in self.scroll.winfo_children(): widget.destroy()
        
        logs = self.db.logs.find().sort("timestamp", -1).limit(50)
        
        for i, log in enumerate(logs):
            bg = "#334155" if i % 2 == 0 else "#1e293b"
            row = ctk.CTkFrame(self.scroll, fg_color=bg)
            row.pack(fill="x", pady=1)
            
            # Format text
            txt = f"[{log.get('timestamp', '')}] {log.get('severity','')} | {log.get('user','')} | {log.get('event_type','')} | {log.get('description','')}"
            ctk.CTkLabel(row, text=txt, anchor="w").pack(fill="x", padx=10, pady=5)