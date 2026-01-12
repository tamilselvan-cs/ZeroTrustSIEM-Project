# siem_dashboard/views/rules_view.py
import customtkinter as ctk

class RulesView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        
        # Header
        ctk.CTkLabel(self, text="⚙️ Detection Rules Engine", font=("Arial", 20, "bold")).pack(pady=20, anchor="w")
        ctk.CTkLabel(self, text="Configure thresholds for security anomalies.", text_color="#94a3b8").pack(pady=(0, 20), anchor="w")

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        # Rule 1: Brute Force
        self.create_rule_card(
            "Brute Force Detection", 
            "Triggers when failed login attempts exceed the threshold within 1 minute.",
            default_val=5, 
            unit="Attempts"
        )

        # Rule 2: Impossible Travel
        self.create_rule_card(
            "Impossible Travel Speed", 
            "Flags login locations that imply travel speeds faster than commercial flight.",
            default_val=500, 
            unit="mph"
        )

        # Rule 3: High-Risk User Threshold
        self.create_rule_card(
            "Critical Risk Score Threshold", 
            "Users with a calculated risk score above this value are flagged as Critical.",
            default_val=80, 
            unit="Score Points"
        )

    def create_rule_card(self, title, desc, default_val, unit):
        card = ctk.CTkFrame(self.scroll, fg_color="#1e293b", border_color="#334155", border_width=1)
        card.pack(fill="x", pady=10, padx=10)

        # Title & Switch
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(header, text=title, font=("Arial", 16, "bold")).pack(side="left")
        ctk.CTkSwitch(header, text="Active", onvalue=True, offvalue=False).pack(side="right")

        # Description
        ctk.CTkLabel(card, text=desc, text_color="#94a3b8", anchor="w").pack(fill="x", padx=15)

        # Slider / Input Area
        controls = ctk.CTkFrame(card, fg_color="transparent")
        controls.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(controls, text=f"Threshold ({unit}):").pack(side="left", padx=(0, 10))
        
        # Slider
        slider = ctk.CTkSlider(controls, from_=1, to=100 if default_val < 100 else 1000, number_of_steps=100)
        slider.set(default_val)
        slider.pack(side="left", fill="x", expand=True, padx=10)
        
        val_lbl = ctk.CTkLabel(controls, text=str(default_val), width=40)
        val_lbl.pack(side="right")
        
        # Link slider to label
        slider.configure(command=lambda v: val_lbl.configure(text=str(int(v))))
        
        # Save Button
        ctk.CTkButton(card, text="Update Rule", width=100, height=30, fg_color="#2563eb").pack(anchor="e", padx=15, pady=(0, 15))