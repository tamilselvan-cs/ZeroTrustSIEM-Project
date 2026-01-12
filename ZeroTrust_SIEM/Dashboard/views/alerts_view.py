# siem_dashboard/views/alerts_view.py
import customtkinter as ctk
import threading
import time
from datetime import datetime

class AlertsView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.running = True
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=20)
        ctk.CTkLabel(header, text="🚨 Critical Incidents & Threats", font=("Segoe UI", 20, "bold")).pack(side="left")
        ctk.CTkButton(header, text="Resolve All", fg_color="#10b981", width=100, command=self.resolve_all).pack(side="right")

        # Scrollable Alert Feed
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        # Start Auto-Update
        self.update_thread = threading.Thread(target=self.auto_refresh)
        self.update_thread.start()

    def auto_refresh(self):
        last_count = 0
        while self.running:
            try:
                # Count current High/Critical logs
                current_count = self.db.logs.count_documents({"severity": {"$in": ["High", "Critical"]}})
                
                # Only redraw if count changed
                if current_count != last_count:
                    last_count = current_count
                    self.load_alerts()
            except:
                pass
            time.sleep(3)

    def load_alerts(self):
        # Clear existing
        for widget in self.scroll.winfo_children(): widget.destroy()
        
        # Fetch High/Critical Logs
        alerts = self.db.logs.find({"severity": {"$in": ["High", "Critical"]}}).sort("timestamp", -1)
        
        for alert in alerts:
            # Card Styling
            color = "#ef4444" if alert.get('severity') == "Critical" else "#f59e0b"
            bg_color = "#450a0a" if alert.get('severity') == "Critical" else "#451a03"
            
            card = ctk.CTkFrame(self.scroll, fg_color=bg_color, border_color=color, border_width=2)
            card.pack(fill="x", pady=5, padx=10)
            
            # Top Row: Badge + Event
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(top, text=f" {alert.get('severity')} ", fg_color=color, text_color="white", corner_radius=6).pack(side="left")
            ctk.CTkLabel(top, text=f"  {alert.get('event_type')}", font=("Segoe UI", 16, "bold"), text_color="white").pack(side="left")
            ctk.CTkLabel(top, text=alert.get('timestamp').strftime('%H:%M:%S'), text_color="#cbd5e1").pack(side="right")
            
            # Bottom Row: User + Desc
            btm = ctk.CTkFrame(card, fg_color="transparent")
            btm.pack(fill="x", padx=10, pady=(0, 10))
            
            ctk.CTkLabel(btm, text=f"User: {alert.get('user')}  |  IP: {alert.get('source_ip')}", text_color="#cbd5e1").pack(anchor="w")
            ctk.CTkLabel(btm, text=f"Details: {alert.get('description')}", text_color="white", font=("Segoe UI", 12)).pack(anchor="w", pady=(5,0))

    def resolve_all(self):
        # In a real app, you'd archive these. Here we just flush for demo.
        self.db.logs.delete_many({"severity": {"$in": ["High", "Critical"]}})
        self.load_alerts()