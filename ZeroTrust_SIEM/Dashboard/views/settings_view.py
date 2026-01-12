import customtkinter as ctk
import tkinter.messagebox as msg
from tkinter import filedialog
import csv
from datetime import datetime

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        
        ctk.CTkLabel(self, text="🔧 System Settings", font=("Segoe UI", 20, "bold")).pack(pady=20, anchor="w")
        
        # --- SECTION 1: APPEARANCE ---
        self.create_section("Appearance")
        theme_frame = ctk.CTkFrame(self, fg_color="#1e293b")
        theme_frame.pack(fill="x", pady=5, padx=10)
        ctk.CTkLabel(theme_frame, text="Interface Theme").pack(side="left", padx=20, pady=20)
        ctk.CTkOptionMenu(theme_frame, values=["Dark", "Light", "System"], command=self.change_theme).pack(side="right", padx=20)

        # --- SECTION 2: DATA MANAGEMENT ---
        self.create_section("Data Management")
        data_frame = ctk.CTkFrame(self, fg_color="#1e293b")
        data_frame.pack(fill="x", pady=5, padx=10)
        
        # Log Stats
        count = self.db.logs.count_documents({})
        self.lbl_count = ctk.CTkLabel(data_frame, text=f"Current Log Volume: {count} records")
        self.lbl_count.pack(pady=10)
        
        # Flush Button
        btn_flush = ctk.CTkButton(data_frame, text="🗑 Flush All Data (Logs + Blocks)", 
                                  fg_color="#ef4444", hover_color="#b91c1c", 
                                  command=self.flush_db)
        btn_flush.pack(pady=(0, 20))

        # --- SECTION 3: EXPORT ---
        self.create_section("Reporting")
        export_frame = ctk.CTkFrame(self, fg_color="#1e293b")
        export_frame.pack(fill="x", pady=5, padx=10)
        
        # Export Button
        ctk.CTkButton(export_frame, text="📄 Export Audit Report (CSV)", 
                      fg_color="#10b981", hover_color="#059669",
                      command=self.export_csv).pack(pady=20)

    def create_section(self, title):
        ctk.CTkLabel(self, text=title, text_color="#38bdf8", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=10, pady=(20, 5))

    def change_theme(self, new_theme):
        ctk.set_appearance_mode(new_theme)

    def flush_db(self):
        confirm = msg.askyesno("Confirm System Reset", 
                               "WARNING: This will delete ALL:\n- Security Logs\n- Alerts\n- Blocked Users\n\nAre you sure?")
        if confirm:
            # 1. Delete ALL Data Collections
            self.db.logs.delete_many({})
            self.db.alerts.delete_many({})
            self.db.blocked_entities.delete_many({}) # <--- IMPORTANT: Unblocks everyone
            
            # 2. Update UI Logic
            self.lbl_count.configure(text="Current Log Volume: 0 records")
            
            msg.showinfo("System Reset", "✅ All data has been flushed.\nDashboard and sub-modules will refresh automatically.")

    def export_csv(self):
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Audit Report",
                initialfile=f"SIEM_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            )

            if not filename:
                return

            logs = list(self.db.logs.find().sort("timestamp", -1))
            
            if not logs:
                msg.showwarning("No Data", "There are no logs to export.")
                return

            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                headers = ["Timestamp", "Severity", "Event Type", "User", "Source IP", "Location", "Risk Score", "Description"]
                writer.writerow(headers)

                for log in logs:
                    writer.writerow([
                        log.get('timestamp', ''),
                        log.get('severity', ''),
                        log.get('event_type', ''),
                        log.get('user', ''),
                        log.get('source_ip', ''),
                        log.get('location', ''),
                        log.get('risk_score', 0),
                        log.get('description', '')
                    ])

            msg.showinfo("Export Successful", f"Report saved successfully to:\n{filename}")

        except Exception as e:
            msg.showerror("Export Error", f"Failed to save file:\n{str(e)}")