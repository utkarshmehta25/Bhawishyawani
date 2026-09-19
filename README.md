# BhawishyaWani V1
Indian Vedic astrology web application using Swiss Ephemeris / Lahiri sidereal calculations.

## Run locally
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.app

## Production
Use Gunicorn with `gunicorn app.app:app`.

## Important
Review Swiss Ephemeris licensing obligations before public/commercial deployment. The free/open-source licensing route may require corresponding source-code obligations.
Astrology interpretations are traditional/cultural and are not scientifically validated predictions.
