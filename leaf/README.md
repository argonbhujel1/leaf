# Leafletang Enterprises — Public Corporate Website

Production-ready public corporate website for **Leafletang Enterprises**.

**Domain:** https://leafletang.argan.com.np  
**HMS (separate):** https://hms.leafletang.argan.com.np

This application is **completely independent** from the private HMS system. It does not connect to, query, or display any HMS data.

## Features

- Professional manufacturing-focused corporate website
- Dynamic product catalog with categories, search, pagination
- Manufacturing & Quality public overview pages
- Dynamic image gallery with categories and lightbox
- News / updates system
- Business inquiry contact form
- Full CMS / Admin panel for all public content
- SEO (meta tags, Open Graph, sitemap, structured data)
- Responsive design (mobile, tablet, desktop)
- Secure admin authentication
- Independent database (no HMS connection)

## Technology Stack

- Python 3.10+
- Flask
- Jinja2
- SQLAlchemy
- PostgreSQL (production) / SQLite (development)
- HTML5 + Custom CSS3
- Vanilla JavaScript
- Pillow (image optimization)

**Not used:** React, Next.js, Vue, Angular, Tailwind CSS, Bootstrap

## Quick Start (Development)

```bash
# Clone / extract
cd leafletang-public

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run
python run.py
```

Visit: http://localhost:5000

**Admin panel:** http://localhost:5000/admin  
**Default credentials:**  
- Username: `admin`  
- Password: `ChangeMeNow123!`  

**Change the admin password immediately after first login.**

## Production Deployment

1. Set environment variables (see `.env.example`)
2. Use PostgreSQL: set `DATABASE_URL`
3. Set a strong `SECRET_KEY`
4. Set `FLASK_ENV=production`
5. Set `SESSION_COOKIE_SECURE=True`
6. Run with Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "run:app"
```

Or use the included `vercel.json` for Vercel-compatible deployment (with serverless adapter if needed).

## Project Structure

```
leafletang-public/
├── app/
│   ├── __init__.py          # App factory
│   ├── extensions.py        # Flask extensions
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # Public, Admin, API blueprints
│   ├── services/            # Seed, SEO, uploads
│   ├── templates/           # Jinja2 templates
│   └── static/              # CSS, JS, images, uploads
├── config.py
├── run.py
├── requirements.txt
├── .env.example
├── README.md
└── vercel.json
```

## Admin CMS Capabilities

- Manage products & categories
- Manage news posts
- Manage gallery images
- Edit homepage / about / manufacturing / quality content
- Edit contact information & social links
- View & manage business inquiries
- SEO settings per page
- Site settings (logo, tagline, etc.)

## Absolute HMS Separation

This public website:

- Does **NOT** query the HMS database
- Does **NOT** use HMS credentials or APIs
- Does **NOT** embed or iframe the HMS application
- Remains fully functional if HMS is offline
- Stores inquiries only in its own database

The "Client / HMS Login" button simply links to:  
https://hms.leafletang.argan.com.np

## Developer Credit

Footer displays: **Engineered by Argon Bhujel**  
Link: https://argan.com.np

## License

Proprietary — Leafletang Enterprises / Argon Bhujel
