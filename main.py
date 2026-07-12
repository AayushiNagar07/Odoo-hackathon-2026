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


@app.route('/dashboard')
def dashboard():
    return render_template("expenses.html")


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
