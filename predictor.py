import os
import joblib
import numpy as np

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(MODEL_DIR, 'academic_risk_rf_model.joblib')
SCALER_FILE = os.path.join(MODEL_DIR, 'feature_scaler.joblib')

class AcademicRiskPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = [
            'Attendance',
            'CGPA',
            'Assignment Score',
            'CIA Marks',
            'Laboratory Performance',
            'Subject Marks'
        ]
        self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(MODEL_FILE) and os.path.exists(SCALER_FILE):
                self.model = joblib.load(MODEL_FILE)
                self.scaler = joblib.load(SCALER_FILE)
                print("ML Model and Scaler loaded successfully.")
            else:
                print("Model files not found, fallback to rule-based prediction.")
        except Exception as e:
            print(f"Error loading ML model: {e}. Fallback to rule-based prediction.")

    def calculate_overall_performance(self, attendance, cgpa, assignment, cia, lab, subject):
        """Calculates weighted composite academic performance score (0-100)."""
        cgpa_scaled = float(cgpa) * 10.0
        overall = (
            0.20 * float(attendance) +
            0.25 * cgpa_scaled +
            0.20 * float(cia) +
            0.15 * float(assignment) +
            0.10 * float(lab) +
            0.10 * float(subject)
        )
        return round(float(overall), 1)

    def predict(self, attendance, cgpa, assignment, cia, lab, subject):
        """
        Predicts academic risk level, probability, contributing factors,
        and personalized interventions.
        """
        overall = self.calculate_overall_performance(attendance, cgpa, assignment, cia, lab, subject)
        cgpa_scaled = float(cgpa) * 10.0
        
        # Determine risk level based on project requirements:
        # HIGH RISK: below 50%
        # MEDIUM RISK: 50% or more but below 75%
        # LOW RISK: 75% or more (100% remains Low Risk)
        if overall < 50.0 or float(attendance) < 55.0 or float(cgpa) < 4.0:
            risk_level = "High Risk"
            # Base probability for high risk
            prob_high = max(75.0, min(96.0, 100.0 - (overall * 0.7)))
            risk_probability = round(prob_high, 1)
        elif overall < 75.0 or float(attendance) < 75.0 or float(cgpa) < 7.0:
            risk_level = "Medium Risk"
            prob_med = max(50.0, min(74.9, 100.0 - overall))
            risk_probability = round(prob_med, 1)
        else:
            risk_level = "Low Risk"
            prob_low = max(5.0, min(35.0, 100.0 - overall))
            risk_probability = round(prob_low, 1)

        # ML Model confirmation & refinement if available
        if self.model and self.scaler:
            try:
                features = np.array([[attendance, cgpa_scaled, assignment, cia, lab, subject]])
                features_scaled = self.scaler.transform(features)
                probabilities = self.model.predict_proba(features_scaled)[0]
                # classes: 0: Low Risk, 1: Medium Risk, 2: High Risk
                p_low = float(probabilities[0]) * 100.0
                p_med = float(probabilities[1]) * 100.0 if len(probabilities) > 1 else 0.0
                p_high = float(probabilities[2]) * 100.0 if len(probabilities) > 2 else 0.0

                if risk_level == "High Risk":
                    risk_probability = round(max(risk_probability, p_high), 1)
                elif risk_level == "Medium Risk":
                    risk_probability = round(max(risk_probability, p_med), 1)
                else:
                    risk_probability = round(max(5.0, min(30.0, 100.0 - p_low)), 1)
            except Exception as e:
                print(f"Prediction ML inference warning: {e}")

        # Extract Risk Factors
        risk_factors = []
        if float(attendance) < 75.0:
            risk_factors.append(f"Low Attendance ({attendance}%)")
        if float(cia) < 60.0:
            risk_factors.append(f"Low CIA Marks ({cia}%)")
        if float(assignment) < 65.0:
            risk_factors.append(f"Low Assignment Score ({assignment}%)")
        if float(cgpa) < 6.5:
            risk_factors.append(f"Below Average CGPA ({cgpa} / 10)")
        if float(lab) < 60.0:
            risk_factors.append(f"Low Laboratory Performance ({lab}%)")
        if float(subject) < 55.0:
            risk_factors.append(f"Low Subject-wise Marks ({subject}%)")

        if not risk_factors:
            risk_factors.append("Consistent Academic Performance Across All Metrics")

        # Formulate Targeted Recommendations
        recommendations = []
        if float(attendance) < 75.0:
            recommendations.append("Improve attendance to meet the mandatory 75% minimum threshold.")
        if float(assignment) < 65.0:
            recommendations.append("Complete and submit pending assignments with faculty feedback.")
        if float(cia) < 60.0:
            recommendations.append("Attend additional CIA tutorial and remedial revision sessions.")
        if float(lab) < 60.0:
            recommendations.append("Attend additional laboratory practice and hands-on sessions.")
        if float(cgpa) < 6.5 or float(subject) < 55.0:
            recommendations.append("Schedule one-on-one academic counseling and subject mentoring.")
        
        if not recommendations:
            recommendations.append("Maintain current study schedule and participate in advanced academic seminars.")

        return {
            'overall_performance': overall,
            'risk_level': risk_level,
            'risk_probability': risk_probability,
            'risk_factors': risk_factors,
            'recommendations': recommendations
        }

    def get_feature_importances(self):
        """Returns feature importance ranking for Model Insights."""
        if self.model:
            importances = self.model.feature_importances_
            feature_data = []
            for name, imp in zip(self.feature_names, importances):
                feature_data.append({
                    'feature': name,
                    'importance': round(float(imp) * 100, 1)
                })
            feature_data.sort(key=lambda x: x['importance'], reverse=True)
            return feature_data
        
        # Standard weights if model not loaded
        return [
            {'feature': 'Previous Semester CGPA', 'importance': 28.5},
            {'feature': 'Attendance', 'importance': 24.2},
            {'feature': 'CIA Marks', 'importance': 19.8},
            {'feature': 'Assignment Score', 'importance': 14.5},
            {'feature': 'Laboratory Performance', 'importance': 8.0},
            {'feature': 'Subject Marks', 'importance': 5.0}
        ]

predictor = AcademicRiskPredictor()

