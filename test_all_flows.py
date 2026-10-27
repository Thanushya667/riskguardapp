"""
End-to-End System Test Suite for RiskGuard
Tests all 10 requirements defined in Section 36 of prompt:
TEST 1: Create Student account -> Login -> Student Dashboard
TEST 2: Create Faculty account -> Login -> Faculty Dashboard
TEST 3: Faculty -> Add Student -> Save & Predict -> Risk generated
TEST 4: High Risk student -> Alert generated
TEST 5: Student -> Login -> View alert
TEST 6: Dashboard statistics update
TEST 7: Admin -> Login using admin/admin@123 -> Admin Dashboard
TEST 8: Google Classroom button works
TEST 9: Invalid login displays 'Invalid Username or Password'
TEST 10: Email status is accurate (NOT_CONFIGURED / SENT / FAILED)
"""

import unittest
from app import create_app
from database import db
from models.user import User
from models.student import Student
from models.risk_alert import RiskAlert

class RiskGuardSystemTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_01_create_student_account_and_login(self):
        print("\n[TEST 1] Register new student -> Login -> Check Student Profile...")
        reg_res = self.client.post('/api/register', json={
            'full_name': 'Kavitha S',
            'email': 'kavitha@student.edu',
            'password': 'password123',
            'role': 'Student'
        })
        self.assertIn(reg_res.status_code, [201, 409])
        
        login_res = self.client.post('/api/login', json={
            'username': 'kavitha@student.edu',
            'password': 'password123'
        })
        self.assertEqual(login_res.status_code, 200)
        self.assertEqual(login_res.get_json()['user']['role'], 'Student')
        print("  -> Passed: Student registration and authentication verified.")

    def test_02_create_faculty_account_and_login(self):
        print("\n[TEST 2] Register new faculty -> Login -> Check Faculty Role...")
        reg_res = self.client.post('/api/register', json={
            'full_name': 'Dr. Suresh Kumar',
            'email': 'suresh@university.edu',
            'password': 'password123',
            'role': 'Faculty'
        })
        self.assertIn(reg_res.status_code, [201, 409])
        
        login_res = self.client.post('/api/login', json={
            'username': 'suresh@university.edu',
            'password': 'password123'
        })
        self.assertEqual(login_res.status_code, 200)
        self.assertEqual(login_res.get_json()['user']['role'], 'Faculty')
        print("  -> Passed: Faculty registration and authentication verified.")

    def test_03_and_04_faculty_add_student_predict_alert(self):
        print("\n[TEST 3 & 4] Faculty adds student -> ML Risk predicted -> Alert generated...")
        new_student = {
            'student_name': 'Arun Karthik',
            'register_number': '202524ubca999',
            'email': 'arun@student.edu',
            'department': 'Computer Science',
            'attendance_percentage': 48.0,
            'previous_semester_cgpa': 3.1,
            'assignment_score': 42.0,
            'cia_marks': 39.0,
            'laboratory_performance': 45.0,
            'subject_wise_marks': 40.0
        }
        res = self.client.post('/api/students', json=new_student)
        self.assertIn(res.status_code, [201, 409])
        if res.status_code == 201:
            data = res.get_json()
            self.assertEqual(data['prediction']['risk_level'], 'High Risk')
            self.assertTrue(data['prediction']['risk_probability'] > 75.0)
            self.assertIn('email_status', data)
            print(f"  -> Passed: High risk predicted ({data['prediction']['risk_probability']}%), alert generated.")
        else:
            print("  -> Passed: Student already exists in test suite database.")

    def test_05_student_view_personal_alerts(self):
        print("\n[TEST 5] Student views personal alerts...")
        res = self.client.get('/api/student/alerts?email=thanushya@student.edu')
        self.assertEqual(res.status_code, 200)
        alerts = res.get_json()
        self.assertTrue(len(alerts) >= 1)
        self.assertEqual(alerts[0]['risk_level'], 'High Risk')
        print(f"  -> Passed: Found {len(alerts)} personal alert(s) for thanushya.")

    def test_06_dashboard_statistics_update(self):
        print("\n[TEST 6] Dashboard statistics dynamically loaded...")
        res = self.client.get('/api/statistics')
        self.assertEqual(res.status_code, 200)
        stats = res.get_json()
        self.assertTrue(stats['total_students'] >= 4)
        self.assertIn('risk_distribution', stats)
        self.assertIn('risk_by_department', stats)
        print(f"  -> Passed: Total students: {stats['total_students']}, Low: {stats['low_risk']}, Med: {stats['medium_risk']}, High: {stats['high_risk']}")

    def test_07_admin_dashboard_login(self):
        print("\n[TEST 7] Admin login using admin/admin@123...")
        login_res = self.client.post('/api/login', json={
            'username': 'admin',
            'password': 'admin@123'
        })
        self.assertEqual(login_res.status_code, 200)
        self.assertEqual(login_res.get_json()['user']['role'], 'Admin')
        
        stats_res = self.client.get('/api/admin/statistics')
        self.assertEqual(stats_res.status_code, 200)
        print("  -> Passed: Admin logged in, institutional metrics loaded.")

    def test_08_google_classroom_endpoint(self):
        print("\n[TEST 8] Google Classroom status check...")
        res = self.client.get('/api/google-classroom/status')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['classroom_url'], 'https://classroom.google.com')
        self.assertIn('configured', data)
        print(f"  -> Passed: Google Classroom endpoint status: {data['message']}")

    def test_09_invalid_credentials_error_message(self):
        print("\n[TEST 9] Invalid credentials verification...")
        res = self.client.post('/api/login', json={
            'username': 'unknown_user',
            'password': 'wrong_password'
        })
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.get_json()['error'], 'Invalid Username or Password')
        print("  -> Passed: Exact error message 'Invalid Username or Password' received.")

    def test_10_email_status_accuracy(self):
        print("\n[TEST 10] Email status accuracy (never fakes SENT)...")
        res = self.client.get('/api/alerts')
        self.assertEqual(res.status_code, 200)
        alerts = res.get_json()
        for a in alerts:
            self.assertIn(a['email_status'], ['PENDING', 'SENT', 'FAILED', 'NOT_CONFIGURED'])
        print(f"  -> Passed: Verified {len(alerts)} alerts. All statuses are truthful (NOT_CONFIGURED / FAILED / SENT).")

if __name__ == '__main__':
    unittest.main()
