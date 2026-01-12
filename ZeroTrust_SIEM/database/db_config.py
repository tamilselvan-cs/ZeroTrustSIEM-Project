# database/db_config.py
from pymongo import MongoClient

def get_db_connection():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['zerotrust_siem_db']
    
    # Init collections
    if 'logs' not in db.list_collection_names(): db.create_collection('logs')
    if 'alerts' not in db.list_collection_names(): db.create_collection('alerts')
    
    # NEW: Collection for Blocked Entities
    if 'blocked_entities' not in db.list_collection_names(): 
        db.create_collection('blocked_entities')
        
    return db
if __name__ == "__main__":
    db = get_db_connection()
    print("--- RESETTING DATABASE FOR CLEAN START ---")
    db.logs.delete_many({})
    db.blocked_entities.delete_many({})
    print("✅ Database Flushed & Indexes Verified.")