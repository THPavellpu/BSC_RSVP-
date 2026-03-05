#!/bin/bash
# LPU BSC Platform - Setup Script
# Run this script once to set up the project

echo "============================================"
echo "  LPU Bangladesh Students Community"
echo "  Event Management Platform Setup"
echo "============================================"
echo ""

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Running migrations..."
python manage.py makemigrations accounts events rsvp tickets attendance notifications
python manage.py migrate

echo ""
echo "Creating superuser..."
echo "Please create an admin account:"
python manage.py createsuperuser

echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "============================================"
echo "  Setup complete!"
echo "  Run: python manage.py runserver"
echo "  Visit: http://127.0.0.1:8000"
echo "  Admin: http://127.0.0.1:8000/admin"
echo "============================================"
