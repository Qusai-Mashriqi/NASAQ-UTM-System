# 🚁 NASAQ | UTM System (Unmanned Traffic Management)

![NASAQ Banner](https://img.shields.io/badge/System-Active-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Framework-Flask-lightgrey?style=for-the-badge&logo=flask)
![Leaflet](https://img.shields.io/badge/Maps-Leaflet.js-green?style=for-the-badge&logo=leaflet)

> **"The Future of Organized Airspace"**
> An advanced Unmanned Traffic Management (UTM) system designed to integrate UAVs safely into the national airspace through real-time tracking, dynamic geofencing, and automated flight authorization protocols.

---

## 📌 Project Overview
**NASAQ** is a capstone engineering project aimed at solving the chaos of unregulated drone flights. It provides a centralized platform for:
1.  **Authorities (Controllers):** To define No-Fly Zones, monitor airspace, and approve flight plans.
2.  **Operators (Pilots):** To register drones, file flight requests, and simulate missions before takeoff.

Built with a focus on **Clean Architecture**, **Security**, and **Scalability**.

---

## 🚀 Key Features

### 🛡️ For Controllers (Admins)
* **Dynamic Geofencing:** Draw and manage restricted zones (Red/Yellow/Green) directly on the map using Leaflet.js.
* **Flight Control Board:** Review pending flight requests with conflict detection algorithms.
* **Live Surveillance:** Real-time simulation and monitoring of active drone missions.
* **User Management:** Verify pilot licenses and approve official access.

### 🎮 For Pilots (Operators)
* **Fleet Management:** Register and manage UAVs (Serial No, Weight, Usage Type).
* **Interactive Flight Planning:** Draw flight paths on the map and validate against No-Fly Zones.
* **Mission Simulation:** Pre-flight visualization of altitude, speed, and battery estimates.
* **Dashboard:** Track flight history and approval status.

---

## 🛠️ Tech Stack & Architecture

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python (Flask) | RESTful APIs, Blueprints Modular Architecture |
| **Database** | SQLAlchemy | ORM for relational data management |
| **Frontend** | HTML5, Jinja2 | Server-side rendering with dynamic templates |
| **Styling** | CSS3 (Glassmorphism) | Custom responsive UI with Dark/Light mode |
| **Mapping** | Leaflet.js | Interactive maps, Geofencing, and Path drawing |
| **Security** | Flask-Bcrypt, Flask-Login | Password hashing and session management |

---

## ⚙️ Installation & Setup

Follow these steps to run the system locally:

```bash
1. Clone the Repository
git clone [https://github.com/Qusai-Mashriqi/NASAQ-UTM-System.git](https://github.com/Qusai-Mashriqi/NASAQ-UTM-System.git)
cd NASAQ-UTM-System


2. Set Up Virtual Environment
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

3. Install Dependencies
pip install -r requirements.txt


4. Initialize Database
# This will create the database and the first Super Admin account
python create_super_admin.py


5. Run the Application
python run.py
The system will start at http://127.0.0.1:5000/
```

```bash
🔐 Default Credentials
To access the Controller Dashboard immediately:

Email: admin@nasaq.jo

Password: admin123

To test the Pilot features, please register a new account via the "Join Network" page.
```


📂 Project Structure
Plaintext

```bash
NASAQ-UTM-System/
├── app/
│   ├── admin/       # Controller logic & routes
│   ├── auth/        # Authentication system
│   ├── pilot/       # Operator logic & routes
│   ├── static/      # CSS, JS, Images (Assets)
│   ├── templates/   # HTML Jinja2 Templates
│   ├── models.py    # Database Schema
│   └── __init__.py  # App Factory
├── instance/        # SQLite Database
├── config.py        # Environment Configuration
├── run.py           # Entry Point
└── requirements.txt # Python Dependencies
```

🔮 Future Roadmap
[ ] Integration with hardware (DJI SDK) for telemetry.

[ ] AI-based conflict detection for overlapping flight paths.

[ ] Mobile App for field operators.

👨‍💻 Author
Qusai Mashriqi Computer Engineering Student | Yarmouk University

