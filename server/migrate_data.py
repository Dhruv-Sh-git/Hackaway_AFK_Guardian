import json
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client['afk_guardian_db']
collection = db['employee_data']

# Wipe existing data to prevent corrupted schema
collection.delete_many({})

if os.path.exists('employee_data.json'):
    with open('employee_data.json', 'r') as f:
        data = json.load(f)
        
    for emp_id, emp_data in data.items():
        print(f"Migrating employee {emp_id} with {len(emp_data)} records...")
        
        sanitized_data = {}
        for k, v in emp_data.items():
            sanitized_key = k.replace(".", "_")
            sanitized_data[sanitized_key] = v
            
        collection.update_one(
            {"_id": emp_id},
            {"$set": sanitized_data},
            upsert=True
        )
    print("Migration complete!")
else:
    print("No employee_data.json found.")
