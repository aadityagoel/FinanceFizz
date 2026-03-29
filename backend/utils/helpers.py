import uuid
from datetime import datetime
from database import audit_logs_collection

def generate_id(prefix: str = "") -> str:
    """Generate a unique ID"""
    return f"{prefix}{uuid.uuid4().hex}" if prefix else uuid.uuid4().hex

def log_audit(user_id: str, action: str, resource: str, details: dict = None):
    """Log user actions for audit trail"""
    audit_log = {
        "log_id": generate_id("log_"),
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "details": details or {},
        "timestamp": datetime.utcnow()
    }
    audit_logs_collection.insert_one(audit_log)

def calculate_percentage(current: float, total: float) -> float:
    """Calculate percentage"""
    if total == 0:
        return 0.0
    return round((current / total) * 100, 2)