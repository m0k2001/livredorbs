@echo off
echo ===================================================
echo   Demarrage du Livre d'Or - Dr Beatrice
echo ===================================================

echo [1/2] Lancement du Backend FastAPI...
start "Backend FastAPI" cmd /k ".\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --app-dir backend"

echo [2/2] Lancement du Frontend Svelte...
set "PATH=C:\Program Files\nodejs;%PATH%"
start "Frontend Svelte" cmd /k "npm --prefix frontend run dev"

echo.
echo Application en cours d'execution !
echo - Livre d'Or : http://localhost:5173/
echo - Formulaire client : http://localhost:5173/#/participer/retraitebs-7x8k2q
echo - Espace Moderation : http://localhost:5173/#/admin (mot de passe: beatrice2026)
echo - Format Album Papier : http://localhost:5173/#/imprimer
echo ===================================================
pause
