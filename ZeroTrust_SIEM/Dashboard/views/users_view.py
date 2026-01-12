# siem_dashboard/views/users_view.py
import customtkinter as ctk

class UsersView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        
        # Header
        ctk.CTkLabel(self, text="👥 User Risk Profiles", font=("Segoe UI", 20, "bold")).pack(pady=20, anchor="w")

        # Container for User Cards
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        self.load_users()

    def load_users(self):
        # Group logs by user and calculate a mock "Risk Score"
        users = self.db.logs.distinct("user")
        
        for user in users:
            # Simple Risk Calculation Logic
            high_sev = self.db.logs.count_documents({"user": user, "severity": "High"})
            crit_sev = self.db.logs.count_documents({"user": user, "severity": "Critical"})
            risk_score = (high_sev * 20) + (crit_sev * 40)
            if risk_score > 100: risk_score = 100

            # Card Color based on Risk
            border_col = "#ef4444" if risk_score > 80 else ("#f59e0b" if risk_score > 40 else "#10b981")
            
            # User Card UI
            card = ctk.CTkFrame(self.scroll, fg_color="#1e293b", border_color=border_col, border_width=2)
            card.pack(fill="x", pady=10, padx=20)
            
            # Layout
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", padx=20, pady=15)
            
            ctk.CTkLabel(info_frame, text=user, font=("Segoe UI", 18, "bold")).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Role: Standard User", text_color="#94a3b8").pack(anchor="w")

            score_frame = ctk.CTkFrame(card, fg_color="transparent")
            score_frame.pack(side="right", padx=30)
            
            ctk.CTkLabel(score_frame, text="Risk Score", text_color="#94a3b8").pack()
            ctk.CTkLabel(score_frame, text=str(risk_score), font=("Segoe UI", 30, "bold"), text_color=border_col).pack()