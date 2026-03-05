# flask_server.py
from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
from flask import request
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

CORS(app)

# MongoDB Configuration
# Uses MONGODB_URI environment variable or defaults to a local instance
mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client['afk_guardian_db']
collection = db['employee_data']


@app.route('/employee/<employee_id>', methods=['GET'])
def get_state_times(employee_id):
    """Returns the open, closed, and away times for a specific employee."""
    # Find the employee data in the MongoDB collection
    employee_doc = collection.find_one({"_id": employee_id})
    
    if not employee_doc:
         return jsonify({"status": "error", "message": f"Employee {employee_id} not found"}), 404
         
    # Remove the MongoDB specific '_id' before sending response to frontend
    employee_data = employee_doc.copy()
    employee_data.pop("_id", None)
        
    # Return the employee data. It contains timestamp keys mapping to activity data.
    return jsonify({"status": "success", "data": employee_data})
    
@app.route('/employee/<employee_id>', methods=['POST'])
def update_employee_data(employee_id):
    """Updates the data for a specific employee."""
    data = request.json
    
    # Add timestamp to the data
    current_time = datetime.now().isoformat().replace(".", "_")
    
    # Update document in MongoDB using the employee ID.
    # $set updates/creates the specific timestamp key without overwriting older timestamps.
    collection.update_one(
        {"_id": employee_id},
        {"$set": {current_time: data}},
        upsert=True
    )
        
    return jsonify({"status": "success", "message": f"Data for employee {employee_id} updated"})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)