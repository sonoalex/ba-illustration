# Berta Albas – Portfolio & Shop (Flask)

A modern portfolio and shop built with Flask for designer Berta Albas. Includes a browsable portfolio, product catalog, cart, Stripe checkout (demo-ready), a landing page with a typewriter hero, dark mode toggle, and a responsive navbar.

## Stack
- Python 3.11, Flask 3
- SQLAlchemy, Flask-Migrate (SQLite by default)
- Jinja2 templates, Vanilla JS/CSS
- Stripe Payment Intents (demo by default)

## Requirements
- Python 3.11
- pip (or Conda)

## Setup (Conda recommended)
```bash
conda create -n ba-illustration python=3.11 -y
conda activate ba-illustration
python -m pip install -r requirements.txt
```

Alternatively, using venv:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run locally
```bash
python run.py
# Open: http://localhost:5000
```
On first run, the SQLite database and sample data are created automatically.

## Configuration (.env optional)
Create a `.env` file in the project root (all optional):
```
SECRET_KEY=change-me
DATABASE_URL=sqlite:////absolute/path/to/app.db
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=you@example.com
MAIL_PASSWORD=secret
```
If not provided, sensible defaults are used (local SQLite, no Stripe keys).

## Migrations (Flask-Migrate)
If you need to apply migrations (the `migrations/` folder already exists):
```bash
export FLASK_APP=run.py   # macOS/Linux
flask db upgrade
```

## Project structure
```
app.py                 # app factory and blueprint registration
run.py                 # entry point (DB init + dev server)
config.py              # environment configs
models/                # SQLAlchemy models
routes/                # Blueprints (main, portfolio, shop, api)
templates/             # Jinja2 templates (incl. errors/404.html & 500.html)
static/                # static assets (css, js, uploads)
instance/              # SQLite DB (if used)
```

## Features
- Typewriter hero and responsive landing layout
- Responsive navbar with mobile hamburger menu
- Dark mode with floating toggle (persisted in localStorage; honors prefers-color-scheme)
- Filterable portfolio by categories
- Shop with products, session-backed cart, and Stripe checkout (Payment Intent)
- Pages: Home `/`, About `/about`, Contact `/contact`, Portfolio `/portfolio/`, Shop `/shop/`
- JSON API under `/api/` (portfolio, products, stats, etc.)

## Stripe (demo mode)
To process real payments, set `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY`. In development you can leave them empty: UI will render but payment will fail with a config error.

## Deployment (Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```
Make sure to configure environment variables (SECRET_KEY, DB, STRIPE, etc.).

## Troubleshooting
- BuildError `url_for('index')`: blueprints are used; prefer `main.index`, `shop.index`, `portfolio.index`.
- `TemplateNotFound errors/404.html`: templates exist under `templates/errors/`.
- Cart badge: synced from `/cart_count`. If it doesn’t update, try a hard refresh.

## License
Not specified. Internal/demo use.
