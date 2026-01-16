from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Retrieve MongoDB connection string from environment variables
MONGO_URI = os.getenv("MONGO_URI")

# --- Database Connection Setup ---
try:
    # Initialize MongoDB Client
    client = MongoClient(MONGO_URI)
    
    # Verify connection (Ping the server)
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {e}")

# Select Database and Collection
# Note: MongoDB creates the DB and Collection automatically if they don't exist
db = client['analytics_db']       # Database Name
collection = db['events']         # Collection (Table) Name


# --- API Endpoints ---

@app.route('/analytics', methods=['POST'])
def collect_data():
    """
    Endpoint to receive analytics events from the client (Android SDK)
    and store them in MongoDB.
    """
    try:
        # 1. Parse JSON data from the request
        events_list = request.json
        
        # Validate received data
        if not events_list:
            return jsonify({"error": "No data received"}), 400

        print(f"📥 Received {len(events_list)} events...")

        # 2. Add Server Timestamp (Metadata)
        # This adds the exact time the event was processed by the server
        current_time = datetime.datetime.now()
        for event in events_list:
            event['server_timestamp'] = current_time

        # 3. Save to MongoDB
        # Using 'insert_many' for efficient batch insertion
        result = collection.insert_many(events_list)
        
        print(f"✅ Saved {len(result.inserted_ids)} events to MongoDB Atlas.")
        
        # 4. Send Success Response
        return jsonify({
            "status": "success", 
            "message": "Events saved to DB",
            "saved_count": len(result.inserted_ids)
        }), 200
        
    except Exception as e:
        # Handle errors gracefully
        print(f"❌ Error processing data: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask server
    # host='0.0.0.0' allows access from external sources (like Android Emulator)
    print("Server is running on port 5000...")
    app.run(host='0.0.0.0', port=5000)