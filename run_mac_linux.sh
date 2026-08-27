#!/bin/bash
set -e

echo "============================================"
echo "  FoodExpress - Food Delivery Application"
echo "  One-Click Setup and Run (Mac/Linux)"
echo "============================================"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt

echo "Generating placeholder images..."
python generate_images.py

if [ ! -f "food_delivery.db" ]; then
    echo "Seeding database with demo data..."
    python seed_data.py
else
    echo "Database already exists, skipping seed step."
    echo "Delete food_delivery.db and re-run this script to reseed."
fi

echo ""
echo "============================================"
echo "  Starting FoodExpress on http://127.0.0.1:5000"
echo "============================================"
python run.py
