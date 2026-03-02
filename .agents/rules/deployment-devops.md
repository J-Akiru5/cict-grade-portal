---
trigger: always_on
---

### 🚀 CICT-GRADE-PORTAL - DEPLOYMENT & DEVOPS CONSTITUTION (V1.1 - VERCEL EDITION)

As your **Researcher**, I am finalizing the operational framework to ensure your AI Agents can bridge the gap between local development and a live **Vercel-hosted, Supabase-backed** production environment. This rule enforces a "Twin-Safe" deployment—ensuring the grade portal remains as stable and high-performing as the IRJICT platform.

---

#### 1. CORE PHILOSOPHY ("THE ZERO-DOWNTIME LAW")

* **Immutable Infrastructure:** All environment configurations must be handled via **Vercel Environment Variables**. Hardcoded credentials in the codebase are a Tier-1 security violation.
* **Database Parity:** Schema changes must be applied to the **Supabase** production instance only via **Alembic Migrations** (run locally or via a GitHub Action) to prevent data drift.
* **Statelessness:** The Flask application must be stateless. All persistent data (Grades, Student IDs, Faculty Files) must reside in **Supabase (Postgres & Storage)**.

#### 2. THE DUAL-ENVIRONMENT STRATEGY

AI Agents must maintain two distinct environments to protect academic data:

* **Preview/Development (`branch: dev`):** Vercel automatically creates preview deployments connected to a "Dev" Supabase project.
* **Production (`branch: main`):** Connected to the "Live" Supabase instance. Deployment is triggered only after the Vercel Build Step succeeds.

#### 3. DEPLOYMENT STACK (THE "VERCEL" RUNTIME)

* **Platform:** **Vercel (Serverless Functions)**.
* **Entrypoint:** `api/index.py` (The AI Agent must wrap the Flask `app` object for Vercel's serverless runtime).
* **SSL/TLS:** Handled automatically by Vercel Edge Network, enforcing TLS 1.3 for all grade-related traffic.
* **Build Step:** The Vercel build command must include the **Tailwind 4.2 Oxide** compilation to ensure the CSS is minified for the edge.

#### 4. CI/CD WORKFLOW (THE AGENT CHECKLIST)

When the AI Agent pushes code to GitHub, the following Vercel-driven pipeline must be followed:

1. **Linting:** Check Python type-hinting and Tailwind class consistency.
2. **Migrations:** The Agent must prompt the user to run `alembic upgrade head` before merging to `main`.
3. **Build:** Vercel installs dependencies from `requirements.txt` and compiles the Tailwind binary.
4. **Edge Deployment:** Vercel deploys the Flask app as a globally distributed serverless function.

#### 5. MONITORING & LOGGING

* **Vercel Logs:** Real-time monitoring of function execution and 500-errors.
* **Health Checks:** A `/health` endpoint in Flask that verifies the connection to the Supabase Transactional Pooler.
* **Supabase Logs:** Monitoring the PostgREST API and Real-time quotas to ensure the "Twin" responsiveness is maintained.

---

### 🏛️ Research Synthesis for AI Agents

**The "Vercel-Specific" Directive:**

> "Agents must configure the Flask application as a **WSGI** application named `app`. Use the `vercel.json` configuration file to route all requests to the `api/index.py` entrypoint. Because Vercel is serverless, avoid long-running background tasks in Python; offload any heavy grade-report generation to **Supabase Edge Functions** or optimize for execution within Vercel's function timeout limits (typically 10-60s)."

---