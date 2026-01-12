from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta  # <--- Added timedelta
import re
import sys
import os
import math

# Database Configuration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_config import get_db_connection

app = Flask(__name__)
app.secret_key = 'enterprise_secret_key'
db = get_db_connection()

# --- MOCK DATA ---
# Default Users
USERS = {
    "admin": {"password": "adminpass", "role": "admin", "dept": "IT Security"},
    "alice": {"password": "alicepass", "role": "user", "dept": "HR"},
    "bob": {"password": "bobpass", "role": "user", "dept": "Finance"},
    "dave": {"password": "davepass", "role": "user", "dept": "Engineering"}
}

# 1. ADMIN MODULE DATA (Projects & Payments)
PROJECTS = [
    {"id": "PROJ-101", "name": "Zero-Trust Firewall", "deadline": "2025-12-01", "budget": "$150,000", "expenses": "$45,000", "status": "In Progress"},
    {"id": "PROJ-102", "name": "Legacy Server Migration", "deadline": "2025-10-15", "budget": "$80,000", "expenses": "$78,000", "status": "Completed"},
    {"id": "PROJ-103", "name": "AI Threat Detection", "deadline": "2026-03-30", "budget": "$300,000", "expenses": "$12,000", "status": "Planning"},
]

PAYMENTS = [
    {"id": "INV-9001", "project": "Zero-Trust Firewall", "vendor": "Cisco", "amount": "$45,000", "date": "2025-09-01", "status": "Paid"},
    {"id": "INV-9002", "project": "Cloud Hosting", "vendor": "AWS", "amount": "$12,500", "date": "2025-09-15", "status": "Pending"},
    {"id": "INV-9003", "project": "Hardware Refresh", "vendor": "Dell", "amount": "$22,000", "date": "2025-08-20", "status": "Overdue"},
]

# 2. EMPLOYEE MODULE DATA (Resources)
RESOURCES = [
    {"id": "hr", "name": "Workday HR", "icon": "👥", "desc": "Payroll & Benefits Portal"},
    {"id": "cloud", "name": "Cloud Drive", "icon": "☁️", "desc": "Project Files Storage"},
    {"id": "jira", "name": "Jira Tickets", "icon": "🎫", "desc": "Engineering Tasks"},
]

# VPN Locations
LOCATIONS = {
    "USA": {"ip": "192.168.1.50", "country": "USA", "lat": 37.77, "lon": -122.41},
    "Russia": {"ip": "185.12.13.1", "country": "Russia", "lat": 55.75, "lon": 37.61},
    "China": {"ip": "101.12.33.1", "country": "China", "lat": 39.90, "lon": 116.40},
    "Nigeria": {"ip": "197.210.1.1", "country": "Nigeria", "lat": 9.08, "lon": 8.67},
    "India": {"ip": "103.45.1.1", "country": "India", "lat": 20.59, "lon": 78.96}
}

CURRENT_VPN_IP = "USA"

# --- HELPER FUNCTIONS ---
def calculate_distance(lat1, lon1, lat2, lon2):
    if lat1 is None or lat2 is None: return 0
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return int(R * c)

def log_event(event_type, user, severity, desc):
    try:
        loc = LOCATIONS.get(CURRENT_VPN_IP, LOCATIONS["USA"])
        db.logs.insert_one({
            "timestamp": datetime.now(),
            "event_type": event_type,
            "user": user,
            "severity": severity,
            "description": desc,
            "source_ip": loc["ip"],
            "location": loc["country"],
            "lat": loc["lat"],
            "lon": loc["lon"],
            "risk_score": 0,
            "action_taken": "none"
        })
        print(f"--> [LOGGED] {event_type}")
    except Exception as e:
        print(f"Log Error: {e}")

def auto_block_user(user, reason):
    """Adds user to MongoDB blocked list immediately."""
    if not db.blocked_entities.find_one({"value": user}):
        db.blocked_entities.insert_one({
            "type": "user",
            "value": user,
            "timestamp": datetime.now(),
            "reason": reason
        })
        print(f"!!! AUTO-BLOCKED USER: {user} | Reason: {reason}")

# --- ROUTES ---

@app.route('/')
def index():
    if 'user' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('employee_dashboard'))
    return render_template('login.html', vpn_loc=CURRENT_VPN_IP)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # 1. CHECK IF BLOCKED
    blocked_user = db.blocked_entities.find_one({"type": "user", "value": username})
    if blocked_user:
        reason = blocked_user.get('reason', 'Security Violation')
        if "Privilege Escalation" in reason:
             flash("Privilege escalation notice: please wait until our team has reviewed", "danger")
        else:
             flash(f"⛔ ACCOUNT LOCKED: {reason}", "danger")
        log_event("Blocked Access Attempt", username, "High", f"Blocked user tried login ({reason})")
        return redirect(url_for('index'))

    # 2. VALIDATE CREDENTIALS
    if username in USERS and USERS[username]['password'] == password:
        
        # 3. IMPOSSIBLE TRAVEL CHECK
        last_login = db.logs.find_one({"user": username, "event_type": "Login Success"}, sort=[("timestamp", -1)])
        if last_login:
            last_country = last_login['location']
            curr_country = LOCATIONS[CURRENT_VPN_IP]['country']
            time_diff = (datetime.now() - last_login['timestamp']).total_seconds() / 60
            
            if last_country != curr_country and time_diff < 5:
                dist_km = calculate_distance(last_login.get('lat', 0), last_login.get('lon', 0), 
                                             LOCATIONS[CURRENT_VPN_IP]['lat'], LOCATIONS[CURRENT_VPN_IP]['lon'])
                
                desc = f"Jumped {last_country}->{curr_country} ({dist_km} km) in {int(time_diff)}m"
                log_event("Impossible Travel", username, "Critical", desc)
                auto_block_user(username, "Impossible Travel Detection")
                
                flash("Impossible travel notice: please be patient buddy", "danger")
                return redirect(url_for('index'))

        # SUCCESS LOGIN
        session['user'] = username
        session['role'] = USERS[username]['role']
        session['dept'] = USERS[username]['dept']
        log_event("Login Success", username, "Low", "Authenticated via SSO")
        
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('employee_dashboard'))
    
    else:
        # === BRUTE FORCE LOGIC START ===
        log_event("Failed Login", username, "Medium", "Invalid credentials")
        
        # Count failed logins in the last 1 minute
        one_min_ago = datetime.now() - timedelta(minutes=1)
        failed_count = db.logs.count_documents({
            "event_type": "Failed Login",
            "user": username,
            "timestamp": {"$gt": one_min_ago}
        })

        if failed_count >= 3:
            log_event("Brute Force Detected", username, "Critical", f"Detected {failed_count} failures in <1min")
            auto_block_user(username, "Brute Force Detection")
            flash("⛔ ACCOUNT LOCKED: Too many failed attempts.", "danger")
        else:
            flash("Invalid ID or Password.", "danger")
        # === BRUTE FORCE LOGIC END ===

        return redirect(url_for('index'))

# --- SEPARATE DASHBOARDS ---

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    return render_template('admin_dashboard.html', user=session['user'], projects=PROJECTS, payments=PAYMENTS, users_list=USERS)

@app.route('/employee_dashboard')
def employee_dashboard():
    if 'user' not in session: return redirect(url_for('index'))
    if session.get('role') == 'admin': return redirect(url_for('admin_dashboard'))
    return render_template('employee_dashboard.html', user=session['user'], dept=session.get('dept'), resources=RESOURCES)

# --- ADMIN ACTIONS ---

@app.route('/add_user', methods=['POST'])
def add_user():
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    new_user = request.form.get('new_username')
    new_pass = request.form.get('new_password')
    new_dept = request.form.get('new_dept')
    if new_user and new_pass:
        USERS[new_user] = {"password": new_pass, "role": "user", "dept": new_dept}
        flash("user created successfully", "success")
        log_event("Admin Action", session['user'], "Low", f"Created new user: {new_user}")
    return redirect(url_for('admin_dashboard'))

# --- PROFILE & ATTACK VECTOR ---

@app.route('/profile')
def profile():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('profile.html', user=session['user'], dept=session.get('dept'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user' not in session: return redirect(url_for('index'))
    user = session['user']
    new_pass = request.form.get('password')
    
    # === PRIVILEGE ESCALATION TRAP ===
    hack_role = request.form.get('role') 
    if hack_role and hack_role == 'admin':
        log_event("Privilege Escalation", user, "High", "Unauthorized IT Admin Access")
        auto_block_user(user, "Privilege Escalation Attempt")
        session.clear()
        flash("Privilege escalation notice: please wait until our team has reviewed", "danger")
        return redirect(url_for('index'))
    
    if new_pass:
        USERS[user]['password'] = new_pass
        flash("Password updated successfully.", "success")
    else:
        flash("Profile information updated.", "success")
    
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('employee_dashboard'))

# --- VPN & UTILS ---

@app.route('/vpn')
def vpn_panel():
    return render_template('vpn.html', current_loc=CURRENT_VPN_IP, locations=LOCATIONS)

@app.route('/set_vpn', methods=['POST'])
def set_vpn():
    global CURRENT_VPN_IP
    new_loc = request.form.get('location')
    if new_loc in LOCATIONS:
        CURRENT_VPN_IP = new_loc
        return jsonify({"status": "success", "location": LOCATIONS[new_loc]['country'], "ip": LOCATIONS[new_loc]['ip']})
    return jsonify({"status": "error"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)