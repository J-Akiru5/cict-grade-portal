---
trigger: always_on
---

🏛️ CICT-GRADE-PORTAL - ARCHITECTURAL BLUEPRINT (V1.2 - HYBRID POWER)
This architecture is designed to replicate the Next.js DX (Developer Experience) within a Flask ecosystem. By using SQLAlchemy for the data layer and HTMX for the interface, we achieve high performance and "Single Page Application" (SPA) behavior without the overhead of a heavy JavaScript framework.

1. THE "NEXT-FLASK" STACK
Engine: Flask 3.0+ (Asynchronous support enabled).

ORM: SQLAlchemy (with Flask-SQLAlchemy for seamless integration).

Reactivity: HTMX 2.0+ (The "Next.js Simulator").

Styling: Tailwind CSS JIT (Just-In-Time) via Node.js watcher or standalone CLI.

Templating: Jinja2 (Structured with "Partial" fragments for HTMX swaps).

2. DATA ARCHITECTURE (SQLAlchemy ORM)
The AI Agents must implement a strict Relational Schema to ensure academic integrity:

Student Model: id, student_id (Unique), name, curriculum_year.

Faculty Model: id, faculty_code, department, access_level.

Grade Model: id, student_id (FK), subject_code, grade_value (Float), semester, academic_year.

Audit Trail: A hidden logs table to track who changed a grade and when (Crucial for Grade Portals).

3. REACTIVITY & HTMX FLOW
To maintain the "Twin" feel of the IRJICT site:

Fragment Swapping: Instead of render_template('page.html'), use if request.headers.get('HX-Request'): to return only the specific table_body.html or grade_card.html.

Loading States: Use the IRJICT Maroon spinner. When HTMX makes a request, the hx-indicator must show a CSS-based loading animation in the #5B0000 primary color.

Live Search: Implement "Search Students" using hx-get with a 300ms trigger delay to simulate a real-time Next.js search bar.

4. REPOSITORY STRUCTURE (FOR AI AGENTS)
Plaintext
/cict-grade-portal
├── /app
│   ├── /models          # SQLAlchemy Models
│   ├── /routes          # Blueprints (Auth, Student, Faculty, Admin)
│   ├── /services        # Business Logic (Grade calculations, GPA)
│   └── /static          # Compiled Tailwind, HTMX.js, Branding Images
├── /templates
│   ├── /base.html       # The "Shell" (Navbar, Sidebar, Footer)
│   ├── /partials        # HTMX Fragments (The "secret sauce" for speed)
│   └── /pages           # Full page views
├── /migrations          # Alembic (SQLAlchemy version control)
├── tailwind.config.js   # Twin of IRJICT config
└── requirements.txt     # Flask, Flask-SQLAlchemy, Flask-Migrate
5. THE "TWIN" UI CONTRACT
Server-Side Logic: All grade calculations (GWA) must happen in the services/ layer, not the template.

Client-Side Polish: Even though we use Flask, every button click should use HTMX's hx-push-url="true" to ensure the browser back-button works exactly like a Next.js app.