🛡️ Zero-Trust SIEM \& User Behavior Analytics Suite

A deployable Zero-Trust security monitoring platform that detects, analyzes, and responds to cyber threats in real time using continuous identity verification and behavioral analytics.



This project simulates how modern Security Operations Centers (SOC) detect compromised accounts after login, not just at the perimeter.



📖 Abstract

Traditional perimeter-based security fails once an attacker gains valid credentials.

This project implements a Zero Trust Architecture based on the principle:



(Never Trust, Always Verify)



The system continuously monitors user behavior even after successful authentication to detect anomalies such as brute-force attacks, impossible travel, and privilege escalation.



Unlike simple scripts or isolated demos, this solution is engineered as a unified, standalone Windows application.

With one click, it launches:



* A simulated Enterprise Web Application (Victim)
* A centralized SIEM Dashboard (Defender)



Together, they form a complete, realistic testbed for demonstrating real-time detection and response workflows used in modern SOC environments.



🎯 Key Security Use Cases Demonstrated

* 🔐 Brute Force Attack Detection
* 🌍 Impossible Travel (VPN / Geo-Velocity Anomalies)
* 🛡️ Privilege Escalation Attempts
* ⛔ Manual \& Automated User Blocking
* 📊 Dynamic User Risk Scoring



🏗️ System Architecture Overview



The system follows a decoupled Producer–Consumer architecture optimized for speed, modularity, and real-time analysis.



1️⃣ Victim – Enterprise Web Application (Flask)



* Simulated corporate login portal



* Generates security logs for:

* &nbsp;   Login attempts
* &nbsp;   Failed authentications
* &nbsp;   Page access events
* &nbsp;   Role changes



* Acts as the log producer





2️⃣ Brain – Central Log Store (MongoDB)



* High-performance NoSQL database



* Stores:
* Authentication events
* Behavioral logs
* Risk scores
* Blocked user rules



* Serves as the synchronization layer



3️⃣ Defender – SIEM Dashboard (CustomTkinter)



* Desktop SOC interface



* Continuously polls MongoDB



* Provides:
* Live event monitoring
* Global threat map visualization
* User risk score tracking
* Manual \& automated response controls





🛠️ Technology Stack

Core

* Python 3.10+ – Backend logic \& orchestration



SIEM Dashboard

* CustomTkinter – Modern dark-mode UI
* TkinterMapView – Global threat map visualization
* Matplotlib – Risk score trend analysis



Web Application

* Flask
* HTML5 / Bootstrap



Database

* MongoDB (Local Instance)



Packaging \& Deployment

* PyInstaller – Python to Windows executable
* Inno Setup – Professional Windows installer



🚀 Installation \& Usage

✅ Option 1: One-Click Installer (Recommended)





1. Go to the Releases section of this repository
2. Download SIEM\_Guard\_Setup.exe
3. Install the application
4. Launch Zero-Trust SIEM from the desktop



ℹ️ The installer automatically starts:

The Flask Web Server

The SIEM Dashboard

No manual setup required.





🧪Option 2: Running from Source(Developer Mode)

1.Clone this repository:    

&nbsp;     git clone https://github.com/YOUR\_USERNAME/ZeroTrust-SIEM.git

&nbsp;     cd ZeroTrust-SIEM



2.Install dependencies:

&nbsp;      pip install -r requirements.txt



3.Ensure MongoDB is running locally.



4.Run the main application:

&nbsp;     python Dashboard/main\_ui.py



⚡ How to Simulate Attacks (Demo Guide)

Once the application is running, follow these steps to demonstrate the security features:



1\. 🔐 Brute Force Detection

* Open the Web App (http://127.0.0.1:5000).
* Enter a valid username (e.g., bob) but a wrong password 3 times in a row.
* Result: The Web App will lock the account temporarily.
* Dashboard: A "Brute Force Detected" alert will appear in the Live Logs.



2\. 🌍 Impossible Travel (VPN Hopping)

* Login as alice with the VPN dropdown set to "USA".
* Logout immediately.
* Login as alice again, but change the VPN dropdown to "Russia" From (http://127.0.0.1:5000/vpn).
* Result: The system detects that traveling from USA to Russia in <1 minute is physically impossible.
* Dashboard: A Red Arrow appears on the Global Threat Map, and the User Risk Score spikes.



3\.🔐Privilege Escalation

* Open the Web App (http://127.0.0.1:5000).
* Login: Log in as alice (Password: password123).
* Navigate: Click on the "Profile" or "Settings" tab in the navigation bar.
* Inspect:

&nbsp;     Right-click on the "Update Profile" button (or anywhere on the form).

&nbsp;     Select Inspect (or Inspect Element).

* The Hack:

1. &nbsp;	In the Developer Tools window, look for a hidden input field: <input type="hidden" name="role" value="user">
2. &nbsp;	Double-click on value="user".
3. &nbsp;	Change it to value="admin".
4. &nbsp;	Press Enter.

* Execute:

1. &nbsp;	Close the Developer Tools.
2. &nbsp;	Click the "Update Profile" button on the web page.



4\. 🛡️ Active Response (Blocking a User)

* On the SIEM Dashboard, identify a high-risk user.
* Click the "⛔ Block" button next to their name.
* Result: The user is permanently banned. If they try to click anything on the Web App, they are instantly logged out and denied access.



📊 SIEM Capabilities


* Live event ingestion
* Global threat visualization
* Risk score trend analysis
* Manual SOC response controls
* Automated high-risk user blocking





🔮 Future Scope


* Integration of Machine Learning (Random Forest) for predictive threat analysis.
* Cloud deployment using AWS/Azure for remote log ingestion.
* Mobile App notification integration for SOC admins.



👨‍💻 Author



Tamilselvan C



* LinkedIn: https://www.linkedin.com/in/tamilselvanc-cs/



⚠️ Disclaimer



This project is developed strictly for educational and defensive security research purposes.

All attack simulations are performed in a controlled environment.

No real systems or users are targeted.











