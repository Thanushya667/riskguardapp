@echo off
echo ====================================================================
echo Starting RiskGuard: Academic Risk Intelligence & Intervention System
echo ====================================================================
cd /d "%~dp0"

echo [1/3] Checking Python dependencies...
python -m pip install -r requirements.txt --quiet

echo [2/3] Verifying / Training Machine Learning model...
if not exist "backend\services\prediction\academic_risk_rf_model.joblib" (
    python backend\services\prediction\train_model.py
)

echo [3/3] Starting RiskGuard Web Application on http://127.0.0.1:5000 ...
python backend\app.py
pause
