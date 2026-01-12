# siem_dashboard/analytics_engine.py
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_config import get_db_connection

class AnalyticsEngine:
    def __init__(self):
        self.db = get_db_connection()
        self.logs_col = self.db['logs']
        self.alerts_col = self.db['alerts']

    def run_analysis(self):
        """Runs rule-based detection on recent logs."""
        self.detect_brute_force()
        self.calculate_risk_scores()

    def detect_brute_force(self):
        # Rule: More than 5 failed logins in 1 minute
        pipeline = [
            {"$match": {"event_type": "Failed Login"}},
            {"$group": {"_id": "$user", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 5}}}
        ]
        results = list(self.logs_col.aggregate(pipeline))
        for res in results:
            self._create_alert(res['_id'], "Brute Force Detected", "Critical")

    def calculate_risk_scores(self):
        # Simple heuristic: Start at 0, add points for bad events
        users = self.logs_col.distinct("user")
        for user in users:
            score = 20 # Base Score
            # Count high severity logs
            crit_count = self.logs_col.count_documents({"user": user, "severity": "Critical"})
            high_count = self.logs_col.count_documents({"user": user, "severity": "High"})
            
            score += (crit_count * 30) + (high_count * 15)
            if score > 100: score = 100
            
            # Update latest log with this score for visualization
            self.logs_col.update_many({"user": user}, {"$set": {"risk_score": score}})

    def _create_alert(self, user, alert_type, severity):
        # Avoid duplicate alerts in last minute
        exists = self.alerts_col.find_one({
            "user": user, 
            "alert_type": alert_type,
            "timestamp": {"$gt": datetime.now() - timedelta(minutes=1)}
        })
        if not exists:
            self.alerts_col.insert_one({
                "timestamp": datetime.now(),
                "user": user,
                "alert_type": alert_type,
                "severity": severity,
                "status": "New"
            })