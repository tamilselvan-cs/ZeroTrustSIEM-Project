import customtkinter as ctk
import tkintermapview
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import threading
import time
import math
import re

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.running = True
        
        # --- MAP COORDINATES ---
        self.loc_coords = {
            "USA": (37.0902, -95.7129),
            "Russia": (61.5240, 105.3188),
            "China": (35.8617, 104.1954),
            "Nigeria": (9.0820, 8.6753),
            "India": (20.5937, 78.9629),
            "Unknown": (0, 0)
        }

        # --- LAYOUT ---
        self.grid_columnconfigure((0, 1, 2, 3), weight=1) 
        self.grid_rowconfigure(2, weight=1) 

        # 1. HEADER
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(title_frame, text="Zero-Trust User Behaviour Analytics & SIEM Log Monitoring Application", 
                     font=("Segoe UI", 20, "bold"), text_color="white", anchor="w").pack(side="left")
        

        # 2. KPI CARDS
        self.create_kpi_card(0, "Total Logs Processed", "0", "#10b981") 
        self.create_kpi_card(1, "Active Threats", "0", "#ef4444")       
        self.create_kpi_card(2, "User Risk Score > 80", "0", "#f59e0b") 
        self.create_kpi_card(3, "Failed Login Bursts", "0", "#ef4444")        

        # 3. MIDDLE (MAP + CHART)
        self.mid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mid_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=10)
        self.mid_frame.grid_columnconfigure(0, weight=1) 
        self.mid_frame.grid_columnconfigure(1, weight=1) 

        # Map
        self.map_panel = ctk.CTkFrame(self.mid_frame, fg_color="#1e293b", corner_radius=10)
        self.map_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        ctk.CTkLabel(self.map_panel, text="Global Access Threat Map", font=("Segoe UI", 14, "bold"), anchor="w").pack(fill="x", padx=15, pady=10)
        self.map_widget = tkintermapview.TkinterMapView(self.map_panel, corner_radius=10)
        self.map_widget.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga") 
        self.map_widget.set_position(20, 0)
        self.map_widget.set_zoom(1)

        # Chart
        self.chart_panel = ctk.CTkFrame(self.mid_frame, fg_color="#1e293b", corner_radius=10)
        self.chart_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        ctk.CTkLabel(self.chart_panel, text="User Behaviour Analytics - Risk Score Trend", font=("Segoe UI", 14, "bold"), anchor="w").pack(fill="x", padx=15, pady=10)
        self.setup_chart()

        # 4. LOGS TABLE
        self.table_panel = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=10)
        self.table_panel.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=(10, 0))
        ctk.CTkLabel(self.table_panel, text="Live Security Alerts & Anomalies", font=("Segoe UI", 14, "bold"), anchor="w").pack(fill="x", padx=15, pady=10)

        header = ctk.CTkFrame(self.table_panel, fg_color="#0f172a", height=35)
        header.pack(fill="x", padx=10)
        columns = [("Time", 100), ("Severity", 100), ("Event Type", 150), ("User", 100), ("Source IP & Location", 200), ("Description", 300)]
        for col, width in columns:
            ctk.CTkLabel(header, text=col, width=width, font=("Segoe UI", 12, "bold"), anchor="w").pack(side="left", padx=5)

        self.log_scroll = ctk.CTkScrollableFrame(self.table_panel, fg_color="transparent")
        self.log_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        # START WORKER
        self.update_thread = threading.Thread(target=self.refresh_data)
        self.update_thread.daemon = True 
        self.update_thread.start()

    def create_kpi_card(self, col, title, value, color):
        if not hasattr(self, 'kpi_container'):
            self.kpi_container = ctk.CTkFrame(self, fg_color="transparent")
            self.kpi_container.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(40, 5)) 
            self.kpi_container.grid_columnconfigure((0,1,2,3), weight=1)

        card = ctk.CTkFrame(self.kpi_container, fg_color="#1e293b", border_color=color, border_width=2)
        card.grid(row=0, column=col, sticky="ew", padx=5)
        ctk.CTkLabel(card, text=title, text_color="#94a3b8", font=("Segoe UI", 12)).pack(anchor="w", padx=15, pady=(10, 0))
        val_lbl = ctk.CTkLabel(card, text=value, text_color="white", font=("Segoe UI", 24, "bold"))
        val_lbl.pack(anchor="w", padx=15, pady=(0, 10))
        setattr(self, f"kpi_lbl_{col}", val_lbl)

    def setup_chart(self):
        self.fig = Figure(figsize=(5, 3), dpi=100, facecolor="#1e293b")
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_panel)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def create_curved_path(self, start_lat, start_lon, end_lat, end_lon):
        points = []
        steps = 20
        for i in range(steps + 1):
            t = i / steps
            lat = start_lat + (end_lat - start_lat) * t
            lon = start_lon + (end_lon - start_lon) * t
            arch_height = 15 * math.sin(t * math.pi) 
            points.append((lat + arch_height, lon))
        return points

    # --- MAIN REFRESH LOOP ---
    def refresh_data(self):
        while self.running:
            try:
                # 1. FETCH LOGS (Simple: Always get last 25)
                # This guarantees sync with DB
                logs_cursor = self.db.logs.find().sort("timestamp", -1).limit(25)
                logs = list(logs_cursor)
                
                # Send to UI
                self.after(0, lambda: self.render_logs_table(logs))

                # 2. UPDATE STATS
                total_logs = self.db.logs.count_documents({})
                active = self.db.logs.count_documents({"severity": {"$in": ["High", "Critical"]}})
                bursts = self.db.logs.count_documents({"event_type": "Brute Force Detected"})
                risky = len(self.db.logs.distinct("user", {"severity": {"$in": ["High", "Critical"]}}))
                
                chart_data = list(self.db.logs.find().sort("timestamp", 1).limit(20))
                self.after(0, lambda: self.update_stats(total_logs, active, risky, bursts, chart_data))

                # 3. UPDATE MAP
                threats = list(self.db.logs.find({"severity": {"$in": ["High", "Critical"]}}).sort("timestamp", -1).limit(5))
                self.after(0, lambda: self.update_map(threats))

            except Exception as e:
                print(f"Loop Error: {e}")
            
            time.sleep(3) # Update every 2 seconds

    # --- UI RENDERERS ---

    def render_logs_table(self, logs):
        # Clear existing rows
        for widget in self.log_scroll.winfo_children(): widget.destroy()

        # Add new rows
        for log in logs:
            row = ctk.CTkFrame(self.log_scroll, fg_color="transparent", height=35)
            row.pack(fill="x", pady=2)

            sev = log.get('severity', 'Info')
            sev_color = "#ef4444" if sev == "Critical" else ("#f59e0b" if sev == "High" else "#3b82f6")

            # Timestamp parsing
            ts = log.get('timestamp', datetime.now())
            if isinstance(ts, datetime): ts_str = ts.strftime('%H:%M:%S')
            else: ts_str = str(ts)[11:19]

            self._add_col(row, ts_str, 100)
            ctk.CTkLabel(row, text=sev, width=100, fg_color=sev_color, text_color="white", corner_radius=5).pack(side="left", padx=5)
            self._add_col(row, log.get('event_type'), 150)
            self._add_col(row, log.get('user'), 100)
            self._add_col(row, f"{log.get('source_ip')} ({log.get('location')})", 200)
            self._add_col(row, log.get('description'), 250)
            
            # --- ACTION BUTTON LOGIC ---
            if sev in ['High', 'Critical']:
                action = log.get("action_taken") # Check if already handled
                
                btn_frame = ctk.CTkFrame(row, fg_color="transparent")
                btn_frame.pack(side="right", padx=5)

                if action == "allowed":
                    ctk.CTkLabel(btn_frame, text="✅ ALLOWED", text_color="#10b981", font=("Segoe UI", 10, "bold")).pack()
                elif action == "blocked":
                    ctk.CTkLabel(btn_frame, text="⛔ BLOCKED", text_color="#ef4444", font=("Segoe UI", 10, "bold")).pack()
                else:
                    # Show Buttons if no action taken yet
                    ctk.CTkButton(btn_frame, text="✔", width=30, height=20, fg_color="#064e3b", 
                                  command=lambda l=log, f=btn_frame: self.allow_user(l, f)).pack(side="left", padx=2)
                    ctk.CTkButton(btn_frame, text="⛔", width=30, height=20, fg_color="#450a0a",
                                  command=lambda l=log, f=btn_frame: self.block_user(l, f)).pack(side="left", padx=2)

    def update_map(self, threats):
        self.map_widget.delete_all_marker()
        self.map_widget.delete_all_path()
        
        # 1. Group Events by Location to prevent text overlap
        location_groups = {} # Key: (lat, lon), Value: { "name": "USA", "events": [] }

        for threat in threats:
            event = threat.get("event_type")
            desc = threat.get("description", "")
            loc_name = threat.get("location", "Unknown")
            
            # Default location
            dest_lat = threat.get("lat", 20)
            dest_lon = threat.get("lon", 0)
            coord_key = (dest_lat, dest_lon)

            # Add to group for marker listing
            if coord_key not in location_groups:
                location_groups[coord_key] = {"name": loc_name, "events": []}
            
            # Avoid duplicate event names in the list for the same location
            if event not in location_groups[coord_key]["events"]:
                location_groups[coord_key]["events"].append(event)

            # --- DRAW PATHS (Keep separate so arrows still appear) ---
            if event == "Impossible Travel":
                start_lat, start_lon = dest_lat, dest_lon # Fallback
                
                origin_name = None
                for name in self.loc_coords:
                    if name in desc and name != loc_name:
                         origin_name = name
                         break
                
                if origin_name:
                    start_lat, start_lon = self.loc_coords[origin_name]
                    
                path = self.create_curved_path(start_lat, start_lon, dest_lat, dest_lon)
                self.map_widget.set_path(path, color="#ef4444")

        # 2. Draw ONE Marker per Location with a Clean List
        for coord, data in location_groups.items():
            # Format: "USA\n• Brute Force\n• Impossible Travel"
            event_list = "\n".join([f"• {e}" for e in data["events"]])
            marker_text = f"{data['name']}\n{event_list}"
            
            self.map_widget.set_marker(coord[0], coord[1], text=marker_text)

    def update_stats(self, total, active, risky, bursts, chart_logs):
        getattr(self, "kpi_lbl_0").configure(text=f"⬆ {total}")
        getattr(self, "kpi_lbl_1").configure(text=f"((●)) {active}")
        getattr(self, "kpi_lbl_2").configure(text=f"⚠ {risky} Users")
        getattr(self, "kpi_lbl_3").configure(text=f"⛔ {bursts}")
        
        self.ax.clear()
        self.ax.set_facecolor("#1e293b")
        self.ax.spines['bottom'].set_color('#94a3b8')
        self.ax.spines['left'].set_color('#94a3b8')
        self.ax.spines['top'].set_color('none')
        self.ax.spines['right'].set_color('none')
        self.ax.tick_params(axis='x', colors='#94a3b8')
        self.ax.tick_params(axis='y', colors='#94a3b8')
        self.ax.grid(True, color='#334155', linestyle='--', alpha=0.5)
        self.ax.set_ylim(0, 100)
        
        y_vals, x_vals = [], []
        if not chart_logs:
            x_vals = list(range(10)); y_vals = [10] * 10
        else:
            padding = 20 - len(chart_logs)
            for i in range(padding): y_vals.append(10); x_vals.append(i)
            for i, log in enumerate(chart_logs):
                idx = padding + i
                x_vals.append(idx)
                score = log.get('risk_score', 0)
                if score == 0:
                    sev = log.get('severity', 'Low')
                    score = 95 if sev == 'Critical' else (75 if sev == 'High' else 15)
                y_vals.append(score)
                if score > 60:
                    self.ax.text(idx, score+5, log.get('event_type','!'), color="white", fontsize=8, backgroundcolor="#ef4444", ha='center')

        self.ax.plot(x_vals, y_vals, color="#38bdf8", linewidth=2, marker='o')
        self.ax.axhline(y=80, color='#ef4444', linestyle='--', label='Critical')
        self.canvas.draw()

    # --- ACTION HANDLERS (PERSISTENT STATE) ---

    def allow_user(self, log, btn_frame):
        user = log.get('user')
        log_id = log.get('_id')
        
        # 1. Update Database (Persistent)
        self.db.blocked_entities.delete_many({"type": "user", "value": user})
        self.db.logs.update_one({"_id": log_id}, {"$set": {"action_taken": "allowed"}})
        
        # 2. Update UI Immediately
        for widget in btn_frame.winfo_children(): widget.destroy()
        ctk.CTkLabel(btn_frame, text="✅ ALLOWED", text_color="#10b981", font=("Segoe UI", 10, "bold")).pack()

    def block_user(self, log, btn_frame):
        user = log.get('user')
        log_id = log.get('_id')
        
        # 1. Update Database (Persistent)
        self.db.blocked_entities.update_one(
            {"type": "user", "value": user}, 
            {"$set": {"timestamp": datetime.now(), "reason": "Admin Confirmed"}}, 
            upsert=True
        )
        self.db.logs.update_one({"_id": log_id}, {"$set": {"action_taken": "blocked"}})
        
        # 2. Update UI Immediately
        for widget in btn_frame.winfo_children(): widget.destroy()
        ctk.CTkLabel(btn_frame, text="⛔ BLOCKED", text_color="#ef4444", font=("Segoe UI", 10, "bold")).pack()

    def _add_col(self, parent, text, width):
        ctk.CTkLabel(parent, text=str(text), width=width, anchor="w", text_color="#cbd5e1").pack(side="left", padx=5)