@echo off
echo ============================================
echo  FoodWise AI - Starting servers
echo ============================================

:: ── Backend ──────────────────────────────────
echo.
echo [1/2] Starting FastAPI backend on http://localhost:8000 ...
start "FoodWise-Backend" cmd /k "cd /d %~dp0 && python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

:: Small delay so backend gets a head-start
timeout /t 2 /nobreak >nul

:: ── Frontend ─────────────────────────────────
echo [2/2] Installing frontend deps (first run only) and starting Vite ...
start "FoodWise-Frontend" cmd /k "cd /d %~dp0frontend && npm install && npm run dev"

echo.
echo ============================================
echo  Backend  → http://localhost:8000
echo  API docs → http://localhost:8000/docs
echo  Frontend → http://localhost:5173
echo ============================================
echo  Close the two new terminal windows to stop.
pause
