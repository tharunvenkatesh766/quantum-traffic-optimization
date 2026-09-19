@echo off
cd /d "%~dp0"
echo ============================================================
echo Starting QuantumTraffic AI (Hackathon Edition)...
echo ============================================================
py -m streamlit run app.py
pause
