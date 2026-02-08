# Heart of Chocolate - Django Project

This project includes:
- Web UI (dashboard + Django admin)
- REST API (Django REST Framework)

## Quick start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run migrations:
   ```bash
   python manage.py migrate
   ```
3. Create admin user:
   ```bash
   python manage.py createsuperuser
   ```
4. Run the server:
   ```bash
   python manage.py runserver
   ```

## AI Assistant (Admin Tool)
The admin tool is available at `/admin/assistant/`. It uses the OpenAI API.

Set environment variables before running:
```bash
set OPENAI_API_KEY=your_key_here
set OPENAI_MODEL=gpt-4.1-mini
```

The assistant also stores Q&A history in the database and can answer basic
report-style questions (sales, receipts, payments, courier totals, and
estimated outstanding).

## URLs
- Dashboard: `/`
- Admin: `/admin/`
- API: `/api/`

## Reports
- Reports index: `/reports/`
- Reports have filters and export buttons (Excel/PDF).

## Deploy Online (Render + PostgreSQL)
1. Push this repo to GitHub.
2. In Render, create a **Blueprint** and select this repo.
3. Render will use `render.yaml` to create:
   - Web service (`mitechocolate-web`)
   - PostgreSQL database (`mitechocolate-db`)
4. After deploy finishes, create admin user from Render Shell:
   ```bash
   python manage.py createsuperuser
   ```
5. Open your Render URL and log in.
