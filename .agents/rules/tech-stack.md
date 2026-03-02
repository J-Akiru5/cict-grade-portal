---
trigger: always_on
---

### 🛠️ CICT-GRADE-PORTAL - TECH-STACK CONSTITUTION (V1.1 - MARCH 2026)

#### 1. CORE LANGUAGE & RUNTIME

* **Language:** Python 3.13.7 (Optimized for performance and type-hinting).
* **Web Framework:** **Flask 3.1.3** (The latest stable release as of February 2026).
* *Key Feature:* Native async support for high-concurrency grade encoding during peak periods.


* **Environment:** `venv` (Virtual Environment) with a locked `requirements.txt`.

#### 2. DATA ENGINE (PERSISTENCE LAYER)

* **Platform:** **Supabase (PostgreSQL 18.3 Engine)**.
* *Why:* Leverages Supabase’s managed infrastructure with the superior JSONB performance of Postgres 18.


* **ORM:** **SQLAlchemy 2.0.47** (Connected via Supabase Transactional Pooler).
* **Migrations:** **Alembic 1.15+** (To manage schema changes and maintain parity between dev/prod environments).

#### 3. FRONTEND INTERACTIVITY (THE HYPERMEDIA STACK)

* **Reactivity:** **HTMX 2.0.4**.
* *Philosophy:* "Hypermedia-on-the-Wire." No complex state management; the server sends HTML fragments.


* **Styling Engine:** **Tailwind CSS 4.2 (Oxide Engine)**.
* *Why:* Features the Rust-powered compiler for near-instant builds and native CSS-first configuration.


* **Icons:** **Lucide-Python** or SVG-based icons for high-performance rendering.

#### 4. PRODUCTION & DEPLOYMENT

* **WSGI Server:** **Gunicorn 23.0+** with `gevent` workers for non-blocking I/O.
* **Reverse Proxy:** **Nginx** (Serving static assets and handling SSL/TLS 1.3).
* **Cache:** **Redis 7.4** (For session management and caching high-frequency GPA lookups).

---

### 📦 THE "AGENT-READY" DEPENDENCY MANIFEST

Your AI Agents should initialize the project with this specific `requirements.txt`:

```text
# Web Framework & Reactivity
Flask==3.1.3
Flask-HTMX==0.3.1
Flask-WTF==1.2.1

# Data Layer (Supabase & Postgres)
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.47
psycopg[binary]==3.2.4
Flask-Migrate==4.1.0
supabase==2.13.0
realtime==1.0.3

# Security & Utilities
Werkzeug==3.1.3
python-dotenv==1.0.1
email-validator==2.2.0

# Production
gunicorn==23.0.0
gevent==24.11.1

```

---

### 🏛️ Research Synthesis for AI Agents

**The "Single Language" Directive:**

> "Agents must write 95% of the logic in Python. Do not create separate `.js` files for interactivity; all dynamic behavior (e.g., student search, grade editing) must be handled via **HTMX attributes** on HTML elements and **Flask View Functions** returning partial templates. All database operations must be routed through **SQLAlchemy** via the Supabase connection string to ensure consistent RBAC enforcement."

---