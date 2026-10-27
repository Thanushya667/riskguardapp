-- ====================================================================
-- RiskGuard: Academic Risk Intelligence & Intervention System
-- Database Schema for PostgreSQL
-- All predefined/demo data removed. Clean initial schema.
-- ====================================================================

-- Drop existing tables if re-initializing
DROP TABLE IF EXISTS prediction_history CASCADE;
DROP TABLE IF EXISTS risk_alerts CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 1. Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('Faculty', 'Student', 'Admin')),
    department VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Students Table
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    student_name VARCHAR(150) NOT NULL,
    register_number VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) NOT NULL,
    department VARCHAR(100) NOT NULL,
    attendance_percentage NUMERIC(5, 2) NOT NULL CHECK (attendance_percentage >= 0 AND attendance_percentage <= 100),
    previous_semester_cgpa NUMERIC(4, 2) NOT NULL CHECK (previous_semester_cgpa >= 0 AND previous_semester_cgpa <= 10),
    assignment_score NUMERIC(5, 2) NOT NULL CHECK (assignment_score >= 0 AND assignment_score <= 100),
    cia_marks NUMERIC(5, 2) NOT NULL CHECK (cia_marks >= 0 AND cia_marks <= 100),
    laboratory_performance NUMERIC(5, 2) NOT NULL CHECK (laboratory_performance >= 0 AND laboratory_performance <= 100),
    subject_wise_marks NUMERIC(5, 2) NOT NULL CHECK (subject_wise_marks >= 0 AND subject_wise_marks <= 100),
    overall_performance NUMERIC(5, 2) NOT NULL,
    risk_level VARCHAR(50) NOT NULL CHECK (risk_level IN ('Low Risk', 'Medium Risk', 'High Risk')),
    risk_probability NUMERIC(5, 2) NOT NULL,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Risk Alerts Table
CREATE TABLE risk_alerts (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    risk_level VARCHAR(50) NOT NULL,
    alert_message TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email_status VARCHAR(50) NOT NULL DEFAULT 'PENDING' CHECK (email_status IN ('PENDING', 'SENT', 'FAILED', 'NOT_CONFIGURED'))
);

-- 4. Prediction History Table
CREATE TABLE prediction_history (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    risk_level VARCHAR(50) NOT NULL,
    risk_probability NUMERIC(5, 2) NOT NULL,
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);

-- Indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_students_reg_no ON students(register_number);
CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_students_risk_level ON students(risk_level);
CREATE INDEX idx_students_department ON students(department);
CREATE INDEX idx_risk_alerts_student_id ON risk_alerts(student_id);
CREATE INDEX idx_prediction_history_student_id ON prediction_history(student_id);

-- Initial Administrator Account (admin: admin@123)
INSERT INTO users (username, email, full_name, password_hash, role, department) VALUES
('admin', 'admin@university.edu', 'System Administrator', 'scrypt:32768:8:1$7f7xR9uY$8f8a846c48325a7469a489115bbf7ca6331165ee291c944f6f8bb156093ca568d4a97ee9cf28ca1a78da08e92f2323c21361ff5733f37a505bfe14bb9cb01584', 'Admin', 'Institutional Administration');
```sql
-- 5. Intervention Tracking Table
CREATE TABLE intervention_tracking (
    id SERIAL PRIMARY KEY,

    student_id INTEGER NOT NULL
        REFERENCES students(id) ON DELETE CASCADE,

    risk_level VARCHAR(50) NOT NULL,

    -- Email tracking
    email_status VARCHAR(50) DEFAULT 'PENDING',
    email_sent_at TIMESTAMP NULL,

    email_acknowledged BOOLEAN DEFAULT FALSE,
    email_acknowledged_at TIMESTAMP NULL,

    -- Email reply tracking
    email_reply_status VARCHAR(50) NOT NULL
        DEFAULT 'AWAITING_REPLY',
    email_reply_at TIMESTAMP NULL,

    -- Unique email acknowledgement token
    acknowledgement_token VARCHAR(200) UNIQUE NOT NULL,

    -- Google Classroom tracking
    classroom_course_id VARCHAR(100) NULL,
    classroom_coursework_id VARCHAR(100) NULL,
    classroom_student_id VARCHAR(100) NULL,

    classroom_status VARCHAR(50) DEFAULT 'NOT_CREATED',

    classroom_accessed BOOLEAN DEFAULT FALSE,
    classroom_accessed_at TIMESTAMP NULL,

    assignment_submitted BOOLEAN DEFAULT FALSE,
    assignment_submitted_at TIMESTAMP NULL,

    -- Reminder tracking
    reminder_sent BOOLEAN DEFAULT FALSE,
    reminder_sent_at TIMESTAMP NULL,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for intervention tracking
CREATE INDEX idx_intervention_student_id
    ON intervention_tracking(student_id);

CREATE INDEX idx_intervention_acknowledgement_token
    ON intervention_tracking(acknowledgement_token);

CREATE INDEX idx_intervention_created_at
    ON intervention_tracking(created_at);

CREATE INDEX idx_intervention_classroom_status
    ON intervention_tracking(classroom_status);
