import customtkinter as ctk
import tkinter as tk
import sys
import os
from PIL import Image, ImageTk

# Import Views
from views.dashboard_view import DashboardView
from views.logs_view import LogsView
from views.alerts_view import AlertsView
from views.users_view import UsersView
from views.rules_view import RulesView
from views.settings_view import SettingsView

# Database Setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_config import get_db_connection

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

def get_asset_path(filename):
    return os.path.join(os.path.dirname(__file__), "assets", filename)

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Zero-Trust SIEM | Enterprise Security Monitor")
        self.geometry("1500x900")
        self.db = get_db_connection()
        self.current_user_role = None
        self.bg_image = None 

        self.role_passwords = {
            "CISO": "ciso_secure",
            "Manager": "manager_ops",
            "Admin": "admin_tech"
        }

        self.show_login_screen()

    # =================================================
    # 1. THEMED LOGIN SCREEN (HUD STYLE)
    # =================================================
    def show_login_screen(self):
        for widget in self.winfo_children(): widget.destroy()

        # 1. Background Image
        self.setup_background()

        # 2. Main HUD Container (The Glowing Box)
        # Using a Frame with a border to simulate the HUD
        self.hud_frame = ctk.CTkFrame(self, width=500, height=650, 
                                      corner_radius=20, border_width=3, border_color="#00E5FF", 
                                      fg_color="#050a14") # Deep dark blue/black
        self.hud_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.hud_frame.pack_propagate(False)

        # 3. Inner Decorative Border (Optional, for that 'double line' look)
        self.inner_hud = ctk.CTkFrame(self.hud_frame, width=480, height=630,
                                      corner_radius=15, border_width=1, border_color="#005577",
                                      fg_color="transparent")
        self.inner_hud.place(relx=0.5, rely=0.5, anchor="center")

        # 4. Header Content
        ctk.CTkLabel(self.inner_hud, text="SIEM GUARD", font=("Segoe UI", 42, "bold"), text_color="#00E5FF").pack(pady=(50, 5))
        ctk.CTkLabel(self.inner_hud, text="ENTERPRISE DEFENSE SYSTEM", font=("Consolas", 12), text_color="#AACCFF").pack(pady=(0, 50))

        # 5. Role Selection Area (This will change content when clicked)
        self.content_area = ctk.CTkFrame(self.inner_hud, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=20)
        
        self.show_role_buttons()

    def show_role_buttons(self):
        # Clear area
        for widget in self.content_area.winfo_children(): widget.destroy()

        # Create Buttons matching the mockup style
        self.create_hud_btn("1. CISO ACCESS", "♔", lambda: self.show_password_input("CISO"))
        self.create_hud_btn("2. SOC MANAGER", "♀", lambda: self.show_password_input("Manager")) # Using symbol from image
        self.create_hud_btn("3. SOC ADMIN", "♖", lambda: self.show_password_input("Admin"))

    def create_hud_btn(self, text, icon, cmd):
        btn = ctk.CTkButton(self.content_area, text=f"{text}   {icon}", command=cmd,
                            width=380, height=65, corner_radius=10,
                            fg_color="transparent", border_width=2, border_color="#00E5FF",
                            text_color="#00E5FF", hover_color="#002233",
                            font=("Segoe UI", 18, "bold"))
        btn.pack(pady=15)

    # =================================================
    # 2. PASSWORD INPUT (INTEGRATED INTO HUD)
    # =================================================
    def show_password_input(self, role):
        # Clear buttons
        for widget in self.content_area.winfo_children(): widget.destroy()

        # Show "Selected Role" Header
        ctk.CTkLabel(self.content_area, text=f"// AUTHENTICATING: {role.upper()} //", 
                     font=("Courier New", 14, "bold"), text_color="#00E5FF").pack(pady=(20, 20))

        # Password Box (Styled like the bottom slot in mockup)
        self.pass_entry = ctk.CTkEntry(self.content_area, width=380, height=60, show="●",
                                       font=("Arial", 24), justify="center",
                                       border_color="#00E5FF", border_width=2, corner_radius=10,
                                       fg_color="#001122", text_color="white")
        self.pass_entry.pack(pady=20)
        self.pass_entry.focus()

        # "AUTHENTICATE" Button
        ctk.CTkButton(self.content_area, text="AUTHENTICATE", width=380, height=50,
                      fg_color="#00E5FF", text_color="#000000", font=("Segoe UI", 16, "bold"),
                      hover_color="#FFFFFF", corner_radius=10,
                      command=lambda: self.verify_password(role)).pack(pady=20)

        # Back Button
        ctk.CTkButton(self.content_area, text="< RETURN", width=100, fg_color="transparent", 
                      text_color="#6688AA", hover_color="#111",
                      command=self.show_role_buttons).pack()

        # Error Label
        self.error_lbl = ctk.CTkLabel(self.content_area, text="", text_color="#FF3333", font=("Consolas", 14))
        self.error_lbl.pack(pady=10)

        self.pass_entry.bind("<Return>", lambda event: self.verify_password(role))

    def verify_password(self, role):
        if self.pass_entry.get() == self.role_passwords.get(role):
            self.start_login_sequence(role)
        else:
            self.error_lbl.configure(text="> ACCESS DENIED <")
            self.pass_entry.delete(0, 'end')
            self.pass_entry.configure(border_color="#FF3333")

    # =================================================
    # 3. ANIMATION PAGE (EXACT MATCH)
    # =================================================
    def start_login_sequence(self, role):
        self.current_user_role = role
        
        greeting = f"WELCOME, {role.upper()}"
        if role == "CISO": greeting = "WELCOME, CHIEF"
        if role == "Manager": greeting = "WELCOME, COMMANDER"
        if role == "Admin": greeting = "WELCOME, SOLDIER"

        for widget in self.winfo_children(): widget.destroy()

        # 1. Background
        self.setup_background()
        
        # 2. Main Frame for alignment
        self.anim_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.anim_frame.place(relx=0.5, rely=0.5, anchor="center")

        # 3. Titles (Top)
        ctk.CTkLabel(self.anim_frame, text="ZERO TRUST SIEM", font=("Segoe UI", 56, "bold"), text_color="#00E5FF").pack(pady=(0, 10))
        ctk.CTkLabel(self.anim_frame, text="INITIALIZING SECURE ENVIRONMENT...", font=("Consolas", 18), text_color="#AACCFF").pack(pady=(0, 40))

        # 4. Bear Character
        try:
            image_path = get_asset_path("bear_soldier.png")
            pil_image = Image.open(image_path)
            bear_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(400, 400))
            ctk.CTkLabel(self.anim_frame, image=bear_img, text="").pack(pady=(0, 30))
        except:
            ctk.CTkLabel(self.anim_frame, text="🐻", font=("Arial", 150)).pack(pady=(0, 30))

        # 5. Glowing Progress Bar
        self.progress = ctk.CTkProgressBar(self.anim_frame, width=600, height=25, progress_color="#00E5FF", border_color="#005577")
        self.progress.pack(pady=(20, 20))
        self.progress.set(0)

        # 6. Typewriter Text
        self.welcome_lbl = ctk.CTkLabel(self.anim_frame, text="", font=("Courier New", 32, "bold"), text_color="#FFFFFF")
        self.welcome_lbl.pack()

        self.animate_text(greeting, 0)

    def setup_background(self):
        try:
            bg_path = get_asset_path("login_bg.png")
            pil_bg = Image.open(bg_path)
            # Resize logic to cover screen
            self.bg_image = ctk.CTkImage(light_image=pil_bg, dark_image=pil_bg, size=(1920, 1080))
            bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            bg_label.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
        except Exception:
            self.configure(fg_color="#000000") # Fallback black

    def animate_text(self, text, index):
        if index < len(text):
            self.welcome_lbl.configure(text=text[:index+1]) 
            self.progress.set((index + 1) / len(text))
            self.after(80, lambda: self.animate_text(text, index + 1))
        else:
            self.welcome_lbl.configure(text=text)
            self.after(2000, self.load_main_interface)

    # =================================================
    # 4. DASHBOARD
    # =================================================
    def load_main_interface(self):
        for widget in self.winfo_children(): widget.destroy()
        self.bg_image = None 

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#0f172a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="🛡 SIEM GUARD", font=ctk.CTkFont(size=22, weight="bold"), text_color="#38bdf8").pack(pady=30)
        ctk.CTkLabel(self.sidebar, text=f"OPERATOR:\n{self.current_user_role.upper()}", 
                     font=("Consolas", 12, "bold"), text_color="#00E5FF").pack(pady=(0, 30))

        self.nav_btns = {}
        self.create_nav_btn("📊  Dashboard", self.show_dashboard)
        self.create_nav_btn("📝  Live Logs", self.show_logs)
        self.create_nav_btn("🚨  Alerts", self.show_alerts)
        self.create_nav_btn("👥  User Risk", self.show_users)
        
        ctk.CTkLabel(self.sidebar, text="Configuration", text_color="#64748b", anchor="w").pack(fill="x", padx=20, pady=(20, 5))
        self.create_nav_btn("⚙️  Rules Engine", self.show_rules)
        self.create_nav_btn("🔧  Settings", self.show_settings)
        
        ctk.CTkButton(self.sidebar, text="🔒 LOGOUT", fg_color="#450a0a", hover_color="#7f1d1d", 
                      command=self.show_login_screen).pack(side="bottom", pady=20, padx=10, fill="x")

        self.container = ctk.CTkFrame(self, fg_color="#1e293b")
        self.container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.views = {}
        self.current_view = None
        self.show_dashboard()

    def create_nav_btn(self, text, command):
        btn = ctk.CTkButton(self.sidebar, text=text, command=command, 
                            fg_color="transparent", text_color="#e2e8f0", 
                            hover_color="#334155", anchor="w", height=40, font=("Segoe UI", 16))
        btn.pack(fill="x", padx=10, pady=5)
        self.nav_btns[text] = btn

    def switch_view(self, view_class):
        if self.current_view: self.current_view.pack_forget()
        if view_class not in self.views: self.views[view_class] = view_class(self.container, self.db)
        self.current_view = self.views[view_class]
        self.current_view.pack(fill="both", expand=True)

    def show_dashboard(self): self.switch_view(DashboardView)
    def show_logs(self): self.switch_view(LogsView)
    def show_alerts(self): self.switch_view(AlertsView)
    def show_users(self): self.switch_view(UsersView)
    def show_rules(self): self.switch_view(RulesView)
    def show_settings(self): self.switch_view(SettingsView)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()