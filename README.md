# AI-BASED ACADEMIC RISK PREDICTION AND INTERVENTION SYSTEM
## RiskGuard — Academic Risk Intelligence

A full-stack, responsive, and explainable AI-powered academic risk prediction and intervention system designed for higher education institutions.

The user interface matches the reference visual language:
- Clean, minimal university/academic SaaS design
- Two-column authentication panel with collegiate campus imagery and dark green overlay
- Fixed 235px dark green sidebar (`#16382C`) with active pills (`#285743`)
- Real-time stat cards, responsive tables, risk badges, doughnut charts, and department bar charts
- Transparent, truthful integration states (Email SMTP & Google Classroom API)

---

## 🌟 Key Highlights & Roles

### 1. Faculty
- **Faculty Dashboard**: Real-time institutional overview: Total Students, Low Risk, Medium Risk, High Risk stat cards, Doughnut Risk Distribution chart, and Department Bar Chart.
- **Students Management**: Search by name/ID, filter by risk level (All, Low, Medium, High).
- **Add Student & Predict**: Enter academic parameters (Attendance, CGPA, CIA Marks, Assignment Score, Lab Performance, Subject Marks) with real-time ML prediction, risk classification, risk probability, and targeted intervention recommendations.
- **Alert History**: Expandable audit log of student email alerts with delivery status (`SENT`, `FAILED`, `NOT_CONFIGURED`).
- **Model Insights**: Feature importance weights, SHAP-based factors, and institutional academic health drivers.
- **Google Classroom**: Direct intervention launcher or OAuth connection.

### 2. Student
- **Student Dashboard**: Welcome personal greeting, overall performance score, attendance benchmark, current risk badge, and pending alerts.
- **Performance Breakdown**: Metric-by-metric comparison against university benchmarks.
- **My Alerts**: Student-isolated alerts and targeted study recommendations.
- **Google Classroom Access**: Direct portal to view course assignments.

### 3. Admin
- **Institutional Overview**: Institutional metrics (Total Students, Total Faculty, Low/Med/High risk counts, Average Attendance, Average Performance, Average CGPA).
- **Faculty Directory**: Monitor faculty mentors, assigned departments, student counts, and add faculty members.
- **Risk Monitoring**: Department-wise breakdowns and real-time prediction history.
- **Alert Audit**: System-wide automated alert dispatch log.

---

## 🚀 How to Run in VS Code

### Step 1: Open the Project
Open the `academic-risk-system` folder in Visual Studio Code:
```bash
cd academic-risk-system
```

### Step 2: Install Dependencies
Ensure Python 3.10+ is installed:
```bash
pip install -r requirements.txt
```

### Step 3: Start the Application
Run the Flask server:
```bash
python backend/app.py
```
*(Or simply double click `run.bat` on Windows or run `./run.sh` on macOS/Linux)*

### Step 4: Open in Your Browser
Navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Pre-Seeded Test Credentials

| Role | Username / Email | Password | Description |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` *(or `admin@university.edu`)* | `admin@123` *(or `admin123`)* | Full institutional administration |
| **Faculty** | `raji` *(or `raji@university.edu`)* | `raji@123` | Faculty mentor from screenshot |
| **Student (High Risk)** | `thanushya` *(or `thanushya@student.edu`)* | `thanushya@123` | High Risk student from screenshot (59.8% / 3.4 CGPA) |
| **Student (Medium Risk)** | `anitha` *(or `anitha@student.edu`)* | `anitha@123` | Medium Risk student from screenshot (80% / 7.0 CGPA) |
| **Student (Low Risk)** | `malathi` *(or `malathi@student.edu`)* | `malathi@123` | Low Risk student from screenshot (98.1% / 9.8 CGPA) |
| **Student (Medium Risk)** | `swe` *(or `swe@student.edu`)* | `swe@123` | Medium Risk student from screenshot (80% / 7.0 CGPA) |

---

## 🧪 Functional Verification Checklist

- [x] **TEST 1**: Register a new Student account &rarr; Login &rarr; Student Dashboard displays personal academic profile.
- [x] **TEST 2**: Register a new Faculty account &rarr; Login &rarr; Faculty Dashboard loads institutional metrics.
- [x] **TEST 3**: Faculty &rarr; Add Student &rarr; Enter academic parameters &rarr; Save & Predict &rarr; Real ML prediction card displayed.
- [x] **TEST 4**: High/Medium Risk student added &rarr; Alert record automatically generated in database.
- [x] **TEST 5**: Student login &rarr; View personal alerts with targeted recommendations.
- [x] **TEST 6**: Live dashboard statistics and chart counts update dynamically on every student addition.
- [x] **TEST 7**: Admin &rarr; Login using `admin / admin@123` &rarr; Admin Dashboard, Faculty management and Risk Monitoring active.
- [x] **TEST 8**: Google Classroom button launches portal (`classroom.google.com`) or initiates OAuth.
- [x] **TEST 9**: Invalid credentials trigger `"Invalid Username or Password"` error.
- [x] **TEST 10**: Email status displays honest state: `NOT CONFIGURED` when SMTP credentials are not in `.env`, `FAILED` on transmission failure, and `SENT` only upon true SMTP server confirmation.

---

## ⚙️ Environment Configuration (`.env`)

Copy `.env.example` to `.env` to configure optional external services:
```ini
# Database (defaults to zero-config SQLite if omitted)
# DATABASE_URL=postgresql://postgres:password@localhost:5432/academic_risk

# SMTP Mail Dispatch
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SENDER_EMAIL=your_email@gmail.com

# Google Classroom OAuth 2.0
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
```

---

## 🗄️ PostgreSQL Setup (Optional)
If running with a dedicated PostgreSQL database:
1. Create database: `createdb academic_risk`
2. Run schema: `psql -d academic_risk -f database/schema.sql`
3. Set `DATABASE_URL=postgresql://postgres:your_password@localhost:5432/academic_risk` in `.env`
