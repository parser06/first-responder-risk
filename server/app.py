"""
Flask + SQLite demo backend for First Responder dashboard.

Endpoints:
- GET  /api/officers
- GET  /api/officers/<id>
- POST /api/officers/upsert
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timezone
import uuid
import random

DB_PATH = "./server_demo.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS officers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            badge_number TEXT NOT NULL,
            department TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            is_on_duty INTEGER DEFAULT 1,
            risk_level TEXT DEFAULT 'low',
            risk_score REAL DEFAULT 0.0,
            last_seen TEXT,
            heart_rate REAL,
            activity_type TEXT,
            fall_detected INTEGER DEFAULT 0,
            latitude REAL,
            longitude REAL,
            accuracy REAL,
            device_id TEXT,
            app_version TEXT,
            battery_level REAL,
            network_status TEXT
        );
        """
    )
    # Alerts table (demo)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            title TEXT,
            message TEXT,
            created_at TEXT,
            source_officer_id TEXT,
            radius_m REAL,
            center_lat REAL,
            center_lng REAL,
            target_ids TEXT
        );
        """
    )
    conn.commit()
    conn.close()


def row_to_officer(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "badgeNumber": row["badge_number"],
        "department": row["department"],
        "isActive": bool(row["is_active"]),
        "isOnDuty": bool(row["is_on_duty"]),
        "riskLevel": row["risk_level"],
        "riskScore": row["risk_score"] or 0.0,
        "lastSeen": row["last_seen"],
        "heartRate": row["heart_rate"],
        "activityType": row["activity_type"],
        "fallDetected": bool(row["fall_detected"]) if row["fall_detected"] is not None else False,
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "accuracy": row["accuracy"],
        "deviceId": row["device_id"] or "",
        "appVersion": row["app_version"],
        "batteryLevel": row["battery_level"],
        "networkStatus": row["network_status"],
    }


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000", "*"]}})


with app.app_context():
    init_db()

@app.get("/")
def root():
    return jsonify({"message": "Flask demo API running", "status": "ok"})


@app.get("/api/officers")
def list_officers():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM officers ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    officers = [row_to_officer(r) for r in rows]
    return jsonify({"officers": officers, "total_count": len(officers)})


@app.get("/api/officers/<officer_id>")
def get_officer(officer_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM officers WHERE id = ?", (officer_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Officer not found"}), 404
    return jsonify(row_to_officer(row))


@app.post("/api/officers/upsert")
def upsert_officer():
    data = request.get_json(force=True) or {}

    # Defaults
    officer_id = data.get("id") or str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    payload = {
        "id": officer_id,
        "name": data.get("name", "Unknown"),
        "badge_number": data.get("badgeNumber", ""),
        "department": data.get("department", "Unknown"),
        "is_active": 1 if data.get("isActive", True) else 0,
        "is_on_duty": 1 if data.get("isOnDuty", True) else 0,
        "risk_level": data.get("riskLevel", "low"),
        "risk_score": float(data.get("riskScore", 0.0) or 0.0),
        "last_seen": data.get("lastSeen", now_iso),
        "heart_rate": data.get("heartRate"),
        "activity_type": data.get("activityType"),
        "fall_detected": 1 if data.get("fallDetected", False) else 0,
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "accuracy": data.get("accuracy"),
        "device_id": data.get("deviceId"),
        "app_version": data.get("appVersion"),
        "battery_level": data.get("batteryLevel"),
        "network_status": data.get("networkStatus"),
    }

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO officers (
            id, name, badge_number, department,
            is_active, is_on_duty, risk_level, risk_score, last_seen,
            heart_rate, activity_type, fall_detected,
            latitude, longitude, accuracy,
            device_id, app_version, battery_level, network_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            badge_number=excluded.badge_number,
            department=excluded.department,
            is_active=excluded.is_active,
            is_on_duty=excluded.is_on_duty,
            risk_level=excluded.risk_level,
            risk_score=excluded.risk_score,
            last_seen=excluded.last_seen,
            heart_rate=excluded.heart_rate,
            activity_type=excluded.activity_type,
            fall_detected=excluded.fall_detected,
            latitude=excluded.latitude,
            longitude=excluded.longitude,
            accuracy=excluded.accuracy,
            device_id=excluded.device_id,
            app_version=excluded.app_version,
            battery_level=excluded.battery_level,
            network_status=excluded.network_status
        ;
        """,
        (
            payload["id"],
            payload["name"],
            payload["badge_number"],
            payload["department"],
            payload["is_active"],
            payload["is_on_duty"],
            payload["risk_level"],
            payload["risk_score"],
            payload["last_seen"],
            payload["heart_rate"],
            payload["activity_type"],
            payload["fall_detected"],
            payload["latitude"],
            payload["longitude"],
            payload["accuracy"],
            payload["device_id"],
            payload["app_version"],
            payload["battery_level"],
            payload["network_status"],
        ),
    )
    conn.commit()
    conn.close()
    # Echo back in frontend shape
    response = {
        "id": payload["id"],
        "name": payload["name"],
        "badgeNumber": payload["badge_number"],
        "department": payload["department"],
        "isActive": bool(payload["is_active"]),
        "isOnDuty": bool(payload["is_on_duty"]),
        "riskLevel": payload["risk_level"],
        "riskScore": payload["risk_score"],
        "lastSeen": payload["last_seen"],
        "heartRate": payload["heart_rate"],
        "activityType": payload["activity_type"],
        "fallDetected": bool(payload["fall_detected"]),
        "latitude": payload["latitude"],
        "longitude": payload["longitude"],
        "accuracy": payload["accuracy"],
        "deviceId": payload["device_id"],
        "appVersion": payload["app_version"],
        "batteryLevel": payload["battery_level"],
        "networkStatus": payload["network_status"],
    }
    return jsonify({"success": True, "officer": response})


# --- Development utilities ---

@app.post("/api/dev/seed")
def dev_seed():
    """Insert sample officers for demo purposes."""
    init_db()
    # MIT Campus (approx): 42.3586, -71.0949
    base_lat, base_lng = 42.3586, -71.0949
    samples = [
        {
            "name": "Officer Sarah Lee",
            "badgeNumber": "MIT-1021",
            "department": "MIT",
            "riskLevel": "low",
            "riskScore": 0.12,
            "heartRate": 72,
            "activityType": "walking",
            "fallDetected": False,
        },
        {
            "name": "Officer Miguel Alvarez",
            "badgeNumber": "MIT-2087",
            "department": "MIT",
            "riskLevel": "medium",
            "riskScore": 0.48,
            "heartRate": 102,
            "activityType": "running",
            "fallDetected": False,
        },
        {
            "name": "Officer Priya Singh",
            "badgeNumber": "MIT-3345",
            "department": "MIT",
            "riskLevel": "low",
            "riskScore": 0.20,
            "heartRate": 88,
            "activityType": "walking",
            "fallDetected": False,
        },
        {
            "name": "Officer Jake Thompson",
            "badgeNumber": "MIT-4512",
            "department": "MIT",
            "riskLevel": "high",
            "riskScore": 0.82,
            "heartRate": 132,
            "activityType": "running",
            "fallDetected": True,
        },
        {
            "name": "Officer Aiko Tanaka",
            "badgeNumber": "MIT-5879",
            "department": "MIT",
            "riskLevel": "medium",
            "riskScore": 0.55,
            "heartRate": 96,
            "activityType": "walking",
            "fallDetected": False,
        },
    ]

    conn = get_conn()
    cur = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    for s in samples:
        # Keep them tightly clustered around MIT (~300m radius)
        lat = base_lat + random.uniform(-0.003, 0.003)
        lng = base_lng + random.uniform(-0.003, 0.003)
        oid = str(uuid.uuid4())
        payload = {
            "id": oid,
            "name": s["name"],
            "badge_number": s["badgeNumber"],
            "department": s["department"],
            "is_active": 1,
            "is_on_duty": 1,
            "risk_level": s["riskLevel"],
            "risk_score": s["riskScore"],
            "last_seen": now_iso,
            "heart_rate": s["heartRate"],
            "activity_type": s["activityType"],
            "fall_detected": 1 if s["fallDetected"] else 0,
            "latitude": lat,
            "longitude": lng,
            "accuracy": 10.0,
            "device_id": "demo-device",
            "app_version": "1.0.0",
            "battery_level": round(random.uniform(0.2, 0.95), 2),
            "network_status": random.choice(["wifi", "cellular"]),
        }
        cur.execute(
            """
            INSERT INTO officers (
                id, name, badge_number, department,
                is_active, is_on_duty, risk_level, risk_score, last_seen,
                heart_rate, activity_type, fall_detected,
                latitude, longitude, accuracy,
                device_id, app_version, battery_level, network_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                badge_number=excluded.badge_number,
                department=excluded.department,
                is_active=excluded.is_active,
                is_on_duty=excluded.is_on_duty,
                risk_level=excluded.risk_level,
                risk_score=excluded.risk_score,
                last_seen=excluded.last_seen,
                heart_rate=excluded.heart_rate,
                activity_type=excluded.activity_type,
                fall_detected=excluded.fall_detected,
                latitude=excluded.latitude,
                longitude=excluded.longitude,
                accuracy=excluded.accuracy,
                device_id=excluded.device_id,
                app_version=excluded.app_version,
                battery_level=excluded.battery_level,
                network_status=excluded.network_status
            ;
            """,
            (
                payload["id"],
                payload["name"],
                payload["badge_number"],
                payload["department"],
                payload["is_active"],
                payload["is_on_duty"],
                payload["risk_level"],
                payload["risk_score"],
                payload["last_seen"],
                payload["heart_rate"],
                payload["activity_type"],
                payload["fall_detected"],
                payload["latitude"],
                payload["longitude"],
                payload["accuracy"],
                payload["device_id"],
                payload["app_version"],
                payload["battery_level"],
                payload["network_status"],
            ),
        )

    conn.commit()
    conn.close()
    return jsonify({"inserted": len(samples)})


@app.post("/api/dev/reset")
def dev_reset():
    """Clear all officers (demo reset)."""
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM officers")
    conn.commit()
    conn.close()
    return jsonify({"reset": True})

@app.post("/api/dev/delete_officer/<officer_id>")
def delete_officer(officer_id: str):
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM officers WHERE id = ?", (officer_id,))
    conn.commit()
    conn.close()
    return jsonify({"reset": True})

# --- Alerts ---

def haversine_m(lat1, lon1, lat2, lon2):
    from math import radians, cos, sin, asin, sqrt
    R = 6371000.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


@app.post("/api/alerts/nearby")
def create_nearby_alert():
    data = request.get_json(force=True) or {}
    source_id = data.get("sourceOfficerId")
    radius_m = float(data.get("radiusMeters", 300))
    title = data.get("title", "Officer Down")
    message = data.get("message", "Assist needed nearby")

    if not source_id:
        return jsonify({"error": "sourceOfficerId required"}), 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM officers WHERE id = ?", (source_id,))
    src = cur.fetchone()
    if not src:
        conn.close()
        return jsonify({"error": "Source officer not found"}), 404
    if src["latitude"] is None or src["longitude"] is None:
        conn.close()
        return jsonify({"error": "Source officer has no location"}), 400

    center_lat, center_lng = float(src["latitude"]), float(src["longitude"])

    # Find nearby officers
    cur.execute("SELECT * FROM officers")
    rows = cur.fetchall()
    targets = []
    for r in rows:
        if r["id"] == source_id:
            continue
        if r["latitude"] is None or r["longitude"] is None:
            continue
        d = haversine_m(center_lat, center_lng, float(r["latitude"]), float(r["longitude"]))
        if d <= radius_m:
            targets.append(r["id"])

    alert_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    targets_str = ",".join(targets)
    cur.execute(
        """
        INSERT INTO alerts (id, title, message, created_at, source_officer_id, radius_m, center_lat, center_lng, target_ids)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (alert_id, title, message, now_iso, source_id, radius_m, center_lat, center_lng, targets_str),
    )
    conn.commit()
    conn.close()

    return jsonify({
        "id": alert_id,
        "title": title,
        "message": message,
        "createdAt": now_iso,
        "sourceOfficerId": source_id,
        "radiusMeters": radius_m,
        "center": {"lat": center_lat, "lng": center_lng},
        "targets": targets,
        "count": len(targets),
    })


@app.get("/api/alerts")
def list_alerts():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM alerts ORDER BY datetime(created_at) DESC LIMIT 50")
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "title": r["title"],
            "message": r["message"],
            "createdAt": r["created_at"],
            "sourceOfficerId": r["source_officer_id"],
            "radiusMeters": r["radius_m"],
            "center": {"lat": r["center_lat"], "lng": r["center_lng"]},
            "targets": r["target_ids"].split(",") if r["target_ids"] else [],
        })
    return jsonify({"alerts": out})

if __name__ == "__main__":
    # Change port here if desired
    app.run(host="0.0.0.0", port=5001, debug=True)
