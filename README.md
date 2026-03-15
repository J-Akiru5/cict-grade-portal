# CICT Grade Portal

> The official academic grading and performance monitoring platform for the College of Information and Communications Technology, ISUFST Dingle Campus.

This repository contains the source code for the CICT Grade Portal, designed as a highly responsive, secure, and modern web application built on a "Next-Flask" stack architecture. The architecture perfectly emulates the Developer Experience (DX) and UX of a single-page application (SPA) using Flask, HTMX, and Tailwind CSS.

## 🚀 Tech Stack

- **Backend / Core Engine**: 
  - Python 3.13 / Flask 3.1.3 (Native Async support)
  - Werkzeug 3.1.3 (Security)
- **Data Engine:**
  - Supabase (PostgreSQL 18.3) via Transactional Pooler
  - SQLAlchemy 2.0.47 (ORM) / Flask-SQLAlchemy
  - Alembic 1.15.x (via Flask-Migrate)
- **Frontend / UI:**
  - Tailwind CSS 4.0.0 (Oxide Engine)
  - HTMX 2.0.4 ("Hypermedia-on-the-Wire")
  - Jinja2 (Templating & Partial fragment swapping)
- **AI Integration**:
  - Google GenAI (`google-genai>=1.0.0`) for built-in Chatbot assistance.
- **Production Readiness**:
  - Gunicorn 23.0 & Gevent for serverless deployment optimizations (Vercel).

---

## 🛠 Prerequisites

To run and contribute to this project locally, ensure you have the following installed on your machine:

1. **Python 3.13+**
   - Download from [python.org](https://www.python.org/downloads/)
2. **Node.js (LTS)** and **npm** (Required to compile Tailwind CSS)
   - Download from [nodejs.org](https://nodejs.org/)
3. **Git**
   - Download from [git-scm.com](https://git-scm.com/)

---

## ⚙️ Environment Variables

Before starting the server, you must set up the necessary environment configurations. Create a `.env` file in the root directory and copy the contents of `.env.example`.

```ini
# Flask
FLASK_APP=run.py
FLASK_ENV=development
FLASK_SECRET_KEY=your-strong-secret-key-here

# Supabase (Online Database)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here

# Database (Supabase Postgres via Transaction Pooler)
DATABASE_URL=postgresql+psycopg://postgres.YOUR_PROJECT_REF:YOUR_DB_PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres

# Resend (account approval notifications)
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxx
RESEND_FROM_EMAIL=CICT Portal <no-reply@your-domain.com>

# Public app URL (used in approval emails)
APP_BASE_URL=https://gradeportal.isufstcict.com
```

*Note: Since there is no local database instance being used, the `DATABASE_URL` must point directly to your live/dev Supabase PostgreSQL connection URI.*

---

## 📥 Getting Started / Installation Guide

Follow these steps to clone and run the application locally.

### 1. Clone the Repository
```bash
git clone https://github.com/J-Akiru5/cict-grade-portal.git
cd cict-grade-portal
```

### 2. Set Up Python Virtual Environment
It is highly recommended to isolate dependencies using `venv`.

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Node.js Dependencies
This installs the `tailwindcss` CLI needed for styling.
```bash
npm install
```

### 5. Setup the Database (Migrations)
Since we are using a remote Supabase instance, ensure the schema is up to date with the latest Alembic migrations.
```bash
flask db upgrade
```

### 6. Run the Application

The portal requires two process streams running simultaneously in development:

**Terminal 1: Start the Tailwind CSS JIT Watcher**
This will automatically recompile CSS changes when you modify HTML templates.
```bash
npm run watch:css
```

**Terminal 2: Start the Flask Development Server**
Ensure your virtual environment is activated in this terminal.
```bash
flask run --debug
```

Visit the application at: `http://127.0.0.1:5000`

---

## 🏗 System Status: What has been implemented?

The CICT Grade Portal has achieved significant scaffolding and feature integration. Here is a granular breakdown of the features implemented so far:

### Core Architecture & Routing Integration
✅ **Flask + HTMX Setup:** Fragment rendering and SPA-like navigation via `hx-boost` and `hx-get`.
✅ **Tailwind CSS V4 Setup:** Build system configured, input CSS initialized, CICT/IRJICT Hybrid Design tokens defined (Maroon `#800000`, Tech Gold `#D4AF37`, Glassmorphism constraints).
✅ **Database ORM Setup:** Comprehensive SQLAlchemy mapping for Students, Faculty, Grades, Subjects, Schedules, Enrollment, and Academic Settings.
✅ **Authentication:** Supabase Auth mapping alongside Flask-Login for session management. Includes Role-Based Access Control (RBAC) primitives.
✅ **Error Handling Utils:** Custom Flask error responses mapped into UI templates (`404`, `500`, `403` Access Denied errors styled in CICT Maroon).

### Portals & Interfaces
✅ **Login Page (`/auth/login`)**:
- Styled using the CICT Hybrid Visual Constitution (Radial Maroon gradient, Animated Network dots SVG, Glassmorphic card).
- Responsive forms, visual feedback, error flash messaging.

✅ **Student Portal (`/student/*`)**:
- **Dashboard Overview (`/student/dashboard`)**: Hero card, current General Weighted Average (GWA) card with Gold ring indicators, "Traffic Light" status badges, and quick stats.
- **Grades Ledger (`/student/grades`)**: Tabular view of subject grades separated by Semester using paper card styles and hover states (`bg-[#800000]/5`).
- **Subjects/Schedules (`/student/subjects`)**: Renders lists of enrolled subjects.
- **Student Layout Shell (`/student/layout.html`)**: Interactive sidebar navigation, top bar navigation with avatar dropdown, responsive mobile-friendly off-canvas menu toggles.

✅ **Admin/Faculty Subsystems (`/panel/*`)**:
- Comprehensive Blueprint initialized structure serving as the scaffolding for Data Management. Includes dashboard views for managing Users, Students, Faculty, Subjects, and Academic Term definitions.
- View templates partially rendered for User Management, Faculty List, and Global Settings tracking.

✅ **AI Assistant Integration (`/chatbot/*`)**:
- Google GenAI powered conversational widget endpoint seamlessly stitched into the application to answer user inquiries regarding their academics or portal usage.

---

### Security Implementations (The "Anti-Tamper Layer")
✅ Action `Audit Logs` model created to track any changes applied to a student's grade.
✅ IDOR & CSRF middleware structure set up via Flask-WTF and RBAC service methods (`admin_service`, `faculty_service`, `student_service`).

### SEO & Metadata
✅ Injecting precise `Open Graph` tags, accurate hierarchical semantics (`<h1>`, `<h2>`), and `Schema.org` payload descriptors on the root interface templates to communicate "Educational Organization" status to search engine crawlers.
