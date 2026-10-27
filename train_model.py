import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(MODEL_DIR, 'academic_risk_rf_model.joblib')
SCALER_FILE = os.path.join(MODEL_DIR, 'feature_scaler.joblib')

FEATURE_NAMES = [
    'attendance_percentage',
    'previous_semester_cgpa_scaled',  # CGPA * 10
    'assignment_score',
    'cia_marks',
    'laboratory_performance',
    'subject_wise_marks'
]

def generate_synthetic_data(num_samples=2500, random_state=42):
    """Generates realistic academic dataset for risk prediction training."""
    np.random.seed(random_state)
    
    # Feature distributions
    attendance = np.random.uniform(35, 100, num_samples)
    cgpa = np.random.uniform(2.0, 10.0, num_samples)
    cgpa_scaled = cgpa * 10.0
    assignment = np.random.uniform(30, 100, num_samples)
    cia = np.random.uniform(25, 100, num_samples)
    lab = np.random.uniform(35, 100, num_samples)
    subject = np.random.uniform(30, 100, num_samples)
    
    # Calculate composite academic score (weighted)
    # Weights: Attendance 20%, CGPA 25%, CIA 20%, Assignment 15%, Lab 10%, Subject 10%
    overall = (
        0.20 * attendance +
        0.25 * cgpa_scaled +
        0.20 * cia +
        0.15 * assignment +
        0.10 * lab +
        0.10 * subject
    )
    
    # Ground truth labels based on academic risk thresholds:
    # High Risk (< 50%), Medium Risk (50% to < 75%), Low Risk (>= 75%)
    labels = []
    for score in overall:
        if score < 50.0:
            labels.append(2)  # High Risk
        elif score < 75.0:
            labels.append(1)  # Medium Risk
        else:
            labels.append(0)  # Low Risk
            
    df = pd.DataFrame({
        'attendance_percentage': attendance,
        'previous_semester_cgpa_scaled': cgpa_scaled,
        'assignment_score': assignment,
        'cia_marks': cia,
        'laboratory_performance': lab,
        'subject_wise_marks': subject,
        'risk_label': labels
    })
    return df

def train_and_save():
    print("Generating training dataset...")
    df = generate_synthetic_data()
    
    X = df[FEATURE_NAMES]
    y = df['risk_label']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Training Random Forest Classifier...")
    rf = RandomForestClassifier(
        n_estimators=120,
        max_depth=8,
        min_samples_split=4,
        random_state=42
    )
    rf.fit(X_train, y_train)
    
    score = rf.score(X_test, y_test)
    print(f"Model test accuracy: {score * 100:.2f}%")
    
    joblib.dump(rf, MODEL_FILE)
    joblib.dump(scaler, SCALER_FILE)
    print(f"Model saved to {MODEL_FILE}")
    print(f"Scaler saved to {SCALER_FILE}")
    return rf, scaler

if __name__ == '__main__':
    train_and_save()
