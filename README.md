# HydroWatch

**Water Infrastructure Monitoring Dashboard**

A full-stack platform for ingesting, visualizing, and analyzing real-time hydrometric data. Built to demonstrate proficiency across the full web development stack — from data pipelines and RESTful APIs to interactive mapping, AI-powered analysis, and professional PDF reporting.

---

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌────────────────────┐
│   Browser    │────▶│     Nginx :80    │────▶│   Django :8000     │
│              │     │  (reverse proxy) │     │  (Dashboard, API,  │
│  Leaflet.js  │     └──────┬───────────┘     │   Reports, Alerts) │
│  Chart.js    │            │                 └────────┬───────────┘
│  Bootstrap   │            │                          │
└─────────────┘            │                          │
                            ▼                          ▼
                   ┌────────────────┐         ┌────────────────┐
                   │ FastAPI :8001  │         │ Celery Worker  │
                   │ (Ingestion     │         │ + Beat         │
                   │  Microservice) │         │ (Scheduled     │
                   └───────┬────────┘         │  Ingestion &   │
                           │                  │  Alert Eval)   │
                           ▼                  └───────┬────────┘
                   ┌────────────────┐                 │
                   │  External APIs │                 ▼
                   │  (Environment  │         ┌────────────────┐
                   │   Canada       │         │    Redis       │
                   │   Hydrometric) │         │  (Task Broker) │
                   └────────────────┘         └────────────────┘
                                                      │
                           ┌──────────────────────────┘
                           ▼
                   ┌────────────────┐         ┌────────────────┐
                   │  PostgreSQL    │         │  Claude API    │
                   │  + PostGIS     │         │  (AI Report    │
                   │  (Data Store)  │         │   Summaries)   │
                   └────────────────┘         └────────────────┘
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Django 5.1 + DRF | Dashboard, admin, REST API |
| **Microservice** | FastAPI | Data ingestion from third-party APIs |
| **Database** | PostgreSQL + PostGIS | Geospatial data storage |
| **Task Queue** | Celery + Redis | Scheduled ingestion, alert evaluation |
| **Frontend** | Leaflet.js, Chart.js, Bootstrap 5 | Interactive maps, charts, responsive UI |
| **PDF Reports** | ReportLab | Professional branded PDF generation |
| **AI** | Anthropic Claude API | Natural-language data analysis summaries |
| **Deployment** | Docker Compose, Nginx | Containerized multi-service deployment |

## Features

### 1. Interactive Dashboard
- Leaflet.js map showing monitoring station locations across BC
- Click-to-explore station details with real-time data
- Responsive layout with Bootstrap 5

### 2. Data Visualization
- Chart.js time-series hydrographs with dual-axis (water level + flow rate)
- Configurable time ranges (24h, 7d, 30d, 90d)
- Tabular data view with recent readings

### 3. Data Ingestion Pipeline
- FastAPI microservice fetching from Environment Canada's Hydrometric API
- Celery Beat scheduled hourly ingestion
- Synthetic fallback data for demo/offline mode
- Django management command for manual seeding

### 4. Threshold Alerts
- User-configurable alert rules (metric, operator, threshold, email)
- Automatic evaluation after each ingestion cycle
- Email notifications with cooldown period
- Alert event history log

### 5. AI-Powered Reports
- Claude API generates natural-language analysis of water level trends
- Professional PDF reports with ReportLab (branded, tabular, client-ready)
- Graceful fallback to statistical summary when API key is unavailable

### 6. RESTful API
- Full DRF-powered API at `/api/` with browsable interface
- Endpoints: stations, readings, alerts, reports
- FastAPI ingestion service with OpenAPI docs at `/docs`

## Quick Start

### Prerequisites
- Docker & Docker Compose
- (Optional) Anthropic API key for AI summaries

### Setup

```bash
# Clone the repository
git clone https://github.com/your-username/hydrowatch.git
cd hydrowatch

# Configure environment
cp .env.example .env
# Edit .env with your API key and secrets

# Start all services
docker compose up --build -d

# Seed demo data
docker compose exec django python manage.py seed_data

# Create admin user
docker compose exec django python manage.py createsuperuser
```

### Access

| Service | URL |
|---------|-----|
| Dashboard | http://localhost |
| Django Admin | http://localhost/admin/ |
| REST API (DRF) | http://localhost/api/ |
| Ingestion API Docs | http://localhost:8001/docs |

## Project Structure

```
hydrowatch/
├── docker-compose.yml          # Multi-service orchestration
├── .env.example                # Environment variable template
│
├── django_app/                 # Django project
│   ├── hydrowatch/             # Project settings, celery, URLs
│   ├── dashboard/              # Main dashboard app (models, views, templates)
│   │   ├── models.py           # Station, WaterLevelReading, PrecipitationReading
│   │   ├── views.py            # Dashboard & chart data views
│   │   ├── tasks.py            # Celery tasks (ingestion, alert evaluation)
│   │   ├── templates/          # Leaflet map, Chart.js, station detail
│   │   └── management/         # seed_data management command
│   ├── alerts/                 # Alert rules & events
│   │   ├── models.py           # AlertRule, AlertEvent
│   │   ├── forms.py            # AlertRuleForm
│   │   └── templates/          # Alert CRUD templates
│   ├── reports/                # PDF report generation
│   │   ├── models.py           # Report model
│   │   ├── pdf_generator.py    # ReportLab PDF builder
│   │   └── views.py            # Generate & download views
│   └── api/                    # DRF REST API
│       ├── serializers.py      # Model serializers
│       ├── views.py            # ViewSets
│       └── urls.py             # Router configuration
│
├── ingestion_service/          # FastAPI microservice
│   ├── main.py                 # API endpoints, CSV parsing, demo data
│   └── config.py               # Pydantic settings
│
├── ai_service/                 # AI integration
│   └── summarizer.py           # Claude API for report summaries
│
└── nginx/                      # Reverse proxy
    └── nginx.conf              # Route traffic to Django & FastAPI
```

## Development

```bash
# View logs
docker compose logs -f django

# Run Django shell
docker compose exec django python manage.py shell

# Trigger manual ingestion
curl -X POST http://localhost:8001/ingest/all

# Run alert evaluation
docker compose exec django python -c "from dashboard.tasks import evaluate_alerts; evaluate_alerts()"
```

## License

MIT
