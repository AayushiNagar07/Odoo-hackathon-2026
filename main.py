from datetime import date
import sqlite3

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
DATABASE_NAME = "my_database.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_db_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS fleet_manager (
                employee_id TEXT PRIMARY KEY,
                email_id TEXT NOT NULL,
                current_password TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS dispatcher (
                employee_id TEXT PRIMARY KEY,
                email_id TEXT NOT NULL,
                current_password TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS safety_officer (
                employee_id TEXT PRIMARY KEY,
                email_id TEXT NOT NULL,
                current_password TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS financial_analyst (
                employee_id TEXT PRIMARY KEY,
                email_id TEXT NOT NULL,
                current_password TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS fuel_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle TEXT NOT NULL,
                date TEXT NOT NULL,
                liters REAL NOT NULL,
                cost REAL NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_type TEXT NOT NULL,
                vehicle TEXT NOT NULL,
                toll REAL NOT NULL DEFAULT 0,
                other REAL NOT NULL DEFAULT 0
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS fleet_vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_code TEXT NOT NULL UNIQUE,
                vehicle_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'available',
                last_service TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS fleet_trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_code TEXT NOT NULL UNIQUE,
                vehicle_code TEXT NOT NULL,
                driver_name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                eta_minutes INTEGER DEFAULT 0,
                route TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS fleet_drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_name TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'on_duty',
                shift TEXT NOT NULL DEFAULT 'day'
            )
            """
        )
        connection.commit()

        fuel_count = connection.execute("SELECT COUNT(*) AS count FROM fuel_logs").fetchone()["count"]
        if fuel_count == 0:
            connection.execute(
                "INSERT INTO fuel_logs (vehicle, date, liters, cost) VALUES (?, ?, ?, ?)",
                ("VAN-05", "2024-07-06", 42, 3500),
            )
            connection.execute(
                "INSERT INTO fuel_logs (vehicle, date, liters, cost) VALUES (?, ?, ?, ?)",
                ("TRUCK-11", "2024-07-06", 110, 9400),
            )
            connection.execute(
                "INSERT INTO fuel_logs (vehicle, date, liters, cost) VALUES (?, ?, ?, ?)",
                ("MINI-08", "2024-07-06", 28, 2050),
            )

        expense_count = connection.execute("SELECT COUNT(*) AS count FROM expenses").fetchone()["count"]
        if expense_count == 0:
            connection.execute(
                "INSERT INTO expenses (expense_type, vehicle, toll, other) VALUES (?, ?, ?, ?)",
                ("TOLL", "VAN-05", 30, 0),
            )
            connection.execute(
                "INSERT INTO expenses (expense_type, vehicle, toll, other) VALUES (?, ?, ?, ?)",
                ("MISC", "TRUCK-12", 80, 40),
            )

        vehicle_count = connection.execute("SELECT COUNT(*) AS count FROM fleet_vehicles").fetchone()["count"]
        if vehicle_count == 0:
            connection.executemany(
                "INSERT INTO fleet_vehicles (vehicle_code, vehicle_type, status, last_service) VALUES (?, ?, ?, ?)",
                [
                    ("VAN-05", "Van", "on_trip", "2026-06-20"),
                    ("TRK-12", "Truck", "available", "2026-06-18"),
                    ("ALT-08", "Alt", "in_maintenance", "2026-06-10"),
                    ("MINI-17", "Mini", "available", "2026-06-24"),
                    ("BOX-22", "Box", "available", "2026-06-15"),
                    ("TANK-33", "Tank", "on_trip", "2026-06-22"),
                ],
            )

        trip_count = connection.execute("SELECT COUNT(*) AS count FROM fleet_trips").fetchone()["count"]
        if trip_count == 0:
            connection.executemany(
                "INSERT INTO fleet_trips (trip_code, vehicle_code, driver_name, status, eta_minutes, route) VALUES (?, ?, ?, ?, ?, ?)",
                [
                    ("TR001", "VAN-05", "Alex", "on_trip", 45, "North Hub → Port"),
                    ("TR002", "TRK-12", "John", "completed", 0, "Central Depot → Warehouse"),
                    ("TR003", "ALT-08", "Priya", "dispatched", 60, "Airport → Cold Chain"),
                    ("TR004", "MINI-17", "Mina", "draft", 0, "City Loop → Retail"),
                    ("TR005", "BOX-22", "Dinesh", "pending", 120, "Industrial Park → Dock"),
                ],
            )

        driver_count = connection.execute("SELECT COUNT(*) AS count FROM fleet_drivers").fetchone()["count"]
        if driver_count == 0:
            connection.executemany(
                "INSERT INTO fleet_drivers (driver_name, status, shift) VALUES (?, ?, ?)",
                [
                    ("Alex", "on_duty", "day"),
                    ("John", "on_duty", "day"),
                    ("Priya", "on_duty", "night"),
                    ("Mina", "off_duty", "day"),
                    ("Dinesh", "on_duty", "night"),
                ],
            )

        connection.commit()


initialize_database()


@app.route('/')
def index():
    return render_template("login.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', '').strip()

    if not email or not password or not role:
        return jsonify({"success": False, "message": "All fields are required."}), 400

    table_name_map = {
        "fleet_manager": "fleet_manager",
        "dispatcher": "dispatcher",
        "safety_officer": "safety_officer",
        "financial_analyst": "financial_analyst",
    }
    table_name = table_name_map.get(role)
    if not table_name:
        return jsonify({"success": False, "message": "Invalid role selected."}), 400

    with get_db_connection() as connection:
        user = connection.execute(
            f"SELECT email_id, current_password FROM {table_name} WHERE email_id = ? AND current_password = ?",
            (email, password),
        ).fetchone()

    if user:
        return jsonify({"success": True, "redirect": "/dashboard"})

    return jsonify({"success": False, "message": "Invalid email or password for the selected role."}), 401


@app.route('/expenses')
def expenses():
    return render_template("expenses.html")


@app.route('/dashboard')
def dashboard():
    with get_db_connection() as connection:
        vehicles = connection.execute(
            "SELECT vehicle_code, status FROM fleet_vehicles ORDER BY id"
        ).fetchall()
        trips = connection.execute(
            "SELECT trip_code, vehicle_code, driver_name, status, eta_minutes, route FROM fleet_trips ORDER BY id DESC"
        ).fetchall()
        drivers = connection.execute(
            "SELECT driver_name, status FROM fleet_drivers ORDER BY id"
        ).fetchall()

    total_vehicles = len(vehicles)
    active_vehicles = sum(1 for vehicle in vehicles if vehicle["status"] != "in_maintenance")
    available_vehicles = sum(1 for vehicle in vehicles if vehicle["status"] == "available")
    maintenance_vehicles = sum(1 for vehicle in vehicles if vehicle["status"] == "in_maintenance")
    active_trips = sum(1 for trip in trips if trip["status"] in {"on_trip", "dispatched"})
    pending_trips = sum(1 for trip in trips if trip["status"] in {"pending", "draft"})
    drivers_on_duty = sum(1 for driver in drivers if driver["status"] == "on_duty")
    fleet_utilization = round((active_vehicles / total_vehicles * 100) if total_vehicles else 0)

    metric_cards = [
        {"title": "Active Vehicles", "value": active_vehicles, "subtitle": "Currently in service", "icon": "🚚", "css_class": "metric-card-blue"},
        {"title": "Available Vehicles", "value": available_vehicles, "subtitle": "Ready for dispatch", "icon": "✅", "css_class": "metric-card-green"},
        {"title": "Vehicles in Maintenance", "value": maintenance_vehicles, "subtitle": "Out for servicing", "icon": "🛠️", "css_class": "metric-card-amber"},
        {"title": "Active Trips", "value": active_trips, "subtitle": "Trips in motion", "icon": "🛣️", "css_class": "metric-card-sky"},
        {"title": "Pending Trips", "value": pending_trips, "subtitle": "Awaiting dispatch", "icon": "⏳", "css_class": "metric-card-violet"},
        {"title": "Drivers on Duty", "value": drivers_on_duty, "subtitle": "Available crew", "icon": "👤", "css_class": "metric-card-coral"},
        {"title": "Fleet Utilization", "value": f"{fleet_utilization}%", "subtitle": "Capacity used", "icon": "📈", "css_class": "metric-card-dark"},
    ]

    status_labels = {
        "on_trip": "On Trip",
        "dispatched": "Dispatched",
        "completed": "Completed",
        "pending": "Pending",
        "draft": "Draft",
    }
    status_classes = {
        "on_trip": "status-active",
        "dispatched": "status-dispatched",
        "completed": "status-complete",
        "pending": "status-pending",
        "draft": "status-draft",
    }
    recent_trips = []
    for trip in trips[:6]:
        recent_trips.append(
            {
                "trip_code": trip["trip_code"],
                "vehicle_code": trip["vehicle_code"],
                "driver_name": trip["driver_name"],
                "status": trip["status"],
                "status_label": status_labels.get(trip["status"], trip["status"].replace("_", " ").title()),
                "status_class": status_classes.get(trip["status"], "status-pending"),
                "eta_minutes": trip["eta_minutes"],
                "route": trip["route"],
            }
        )

    max_bar_value = max(1, available_vehicles, maintenance_vehicles, active_trips, pending_trips, drivers_on_duty, fleet_utilization)
    visual_metrics = [
        {"label": "Available Vehicles", "value": available_vehicles, "percent": min(100, round((available_vehicles / max_bar_value) * 100)), "color": "success"},
        {"label": "Active Trips", "value": active_trips, "percent": min(100, round((active_trips / max_bar_value) * 100)), "color": "primary"},
        {"label": "Drivers on Duty", "value": drivers_on_duty, "percent": min(100, round((drivers_on_duty / max_bar_value) * 100)), "color": "warning"},
        {"label": "Fleet Utilization", "value": fleet_utilization, "percent": min(100, round((fleet_utilization / max_bar_value) * 100)), "color": "info"},
    ]

    return render_template(
        "dashboard.html",
        metric_cards=metric_cards,
        recent_trips=recent_trips,
        visual_metrics=visual_metrics,
    )


@app.route('/api/fuel_logs', methods=['GET', 'POST'])
def fuel_logs_api():
    if request.method == 'GET':
        with get_db_connection() as connection:
            rows = connection.execute(
                "SELECT id, vehicle, date, liters, cost FROM fuel_logs ORDER BY date DESC, id DESC"
            ).fetchall()
        return jsonify([dict(row) for row in rows])

    payload = request.get_json(silent=True) or request.form.to_dict()
    vehicle = (payload.get('vehicle') or '').strip()
    entry_date = (payload.get('date') or '').strip() or date.today().isoformat()
    liters = float(payload.get('liters') or 0)
    cost = float(payload.get('cost') or 0)

    if not vehicle:
        return jsonify({"success": False, "message": "Vehicle is required."}), 400

    with get_db_connection() as connection:
        connection.execute(
            "INSERT INTO fuel_logs (vehicle, date, liters, cost) VALUES (?, ?, ?, ?)",
            (vehicle, entry_date, liters, cost),
        )
        connection.commit()

    return jsonify({"success": True, "message": "Fuel log added successfully."})


@app.route('/api/expenses', methods=['GET', 'POST'])
def expenses_api():
    if request.method == 'GET':
        with get_db_connection() as connection:
            rows = connection.execute(
                "SELECT id, expense_type, vehicle, toll, other FROM expenses ORDER BY id DESC"
            ).fetchall()
        return jsonify([dict(row) for row in rows])

    payload = request.get_json(silent=True) or request.form.to_dict()
    expense_type = (payload.get('type') or payload.get('expense_type') or '').strip()
    vehicle = (payload.get('vehicle') or '').strip()
    toll = float(payload.get('toll') or 0)
    other = float(payload.get('other') or 0)

    if not expense_type or not vehicle:
        return jsonify({"success": False, "message": "Expense type and vehicle are required."}), 400

    with get_db_connection() as connection:
        connection.execute(
            "INSERT INTO expenses (expense_type, vehicle, toll, other) VALUES (?, ?, ?, ?)",
            (expense_type, vehicle, toll, other),
        )
        connection.commit()

    return jsonify({"success": True, "message": "Expense added successfully."})


@app.route('/api/trips', methods=['GET', 'POST'])
def trips_api():
    if request.method == 'GET':
        with get_db_connection() as connection:
            rows = connection.execute("SELECT * FROM trips ORDER BY id DESC").fetchall()
        return jsonify([dict(row) for row in rows])

    data = request.get_json()
    with get_db_connection() as connection:
        connection.execute(
            "INSERT INTO trips (vehicle, driver, source, destination) VALUES (?, ?, ?, ?)",
            (data['vehicle'], data['driver'], data['source'], data['destination'])
        )
        connection.commit()
    return jsonify({"success": True})

@app.route('/trips')
def trips_page():
    return render_template("trips.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
