#!/usr/bin/env bash
echo "===================================================================="
echo "Starting RiskGuard: Academic Risk Intelligence & Intervention System"
echo "===================================================================="
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "[1/3] Checking Python dependencies..."
python3 -m pip install -r requirements.txt --quiet

echo "[2/3] Verifying / Training Machine Learning model..."
if [ ! -f "backend/services/prediction/academic_risk_rf_model.joblib" ]; then
    python3 backend/services/prediction/train_model.py
fi

echo "[3/3] Starting RiskGuard Web Application on http://127.0.0.1:5000 ..."
python3 backend/app.py
