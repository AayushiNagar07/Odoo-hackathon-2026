# TransitOps 🚛

**Smart Transport Operations Platform**

TransitOps is an all-in-one management system built to streamline fleet operations, trip logistics, and maintenance tracking with secure, role-based access.

---

### 🚀 Key Features
* **Role-Based Access (RBAC):** Customized dashboards for Fleet Managers, Dispatchers, Safety Officers, and Financial Analysts.
* **Smart Dispatching:** Real-time trip tracking and capacity management.
* **Maintenance & Expenses:** Automated vehicle service logs and fuel cost tracking.
* **Secure Login:** Encrypted authentication with "Remember Me" support.

---

### 🛠 Quick Start

1. **Clone & Setup:**
   ```bash
   git clone <your-repo-url>
   cd transitops


2. **Configure Environment:**
```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

```


3. **Install Requirements:**
```bash
pip install flask flask-sqlalchemy flask-login

```


4. **Launch:**
```bash
# Make sure you are in the 'transitops' folder
python app.py

```


5. **Visit:**
Open your browser at `http://127.0.0.1:5000/login`

---

### 📂 Project Structure

* `app.py` — The engine; handles routes and business logic.
* `models.py` — Database structure and user roles.
* `templates/` — HTML views for the login and dashboards.
* `static/` — CSS styles for a modern, clean look.

---

### 🔐 Roles & Access

| Role | Primary Responsibility |
| --- | --- |
| **Fleet Manager** | Fleet & Maintenance |
| **Dispatcher** | Trips & Live Dashboard |
| **Safety Officer** | Drivers & Compliance |
| **Financial Analyst** | Fuel & Analytics |

---

*Built for the 2026 Odoo Hackathon.*

```

```
