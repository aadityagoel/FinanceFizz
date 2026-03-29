from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/financial_vault")
client = MongoClient(MONGO_URL)
db = client.get_database()

# Collections
users_collection = db["users"]
accounts_collection = db["accounts"]
investments_collection = db["investments"]
sips_collection = db["sips"]
expenses_collection = db["expenses"]
loans_collection = db["loans"]
insurance_collection = db["insurance"]
documents_collection = db["documents"]
goals_collection = db["goals"]
emergency_vault_collection = db["emergency_vault"]
nominees_collection = db["nominees"]
audit_logs_collection = db["audit_logs"]

# Create indexes
def create_indexes():
    """Create necessary indexes for better query performance"""
    users_collection.create_index("email", unique=True)
    users_collection.create_index("user_id", unique=True)
    accounts_collection.create_index("user_id")
    investments_collection.create_index("user_id")
    expenses_collection.create_index("user_id")
    loans_collection.create_index("user_id")
    insurance_collection.create_index("user_id")
    documents_collection.create_index("user_id")
    goals_collection.create_index("user_id")
    audit_logs_collection.create_index("user_id")
    audit_logs_collection.create_index("timestamp")
    print("✅ Database indexes created")

# Initialize indexes
try:
    create_indexes()
except Exception as e:
    print(f"⚠️  Index creation warning: {e}")