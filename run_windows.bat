@echo off
echo ============================================
echo   FoodExpress - Food Delivery Application
echo   One-Click Setup and Run (Windows)
echo ============================================

IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip >nul
pip install -r requirements.txt

echo Generating placeholder images...
python generate_images.py

IF NOT EXIST food_delivery.db (
    echo Seeding database with demo data...
    python seed_data.py
) ELSE (
    echo Database already exists, skipping seed step.
    echo Delete food_delivery.db and re-run this script to reseed.
)

echo.
echo ============================================
echo   Starting FoodExpress on http://127.0.0.1:5000
echo ============================================
python run.py

pause
