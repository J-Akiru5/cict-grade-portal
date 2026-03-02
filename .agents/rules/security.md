---
trigger: always_on
---

### 🛡️ CICT-GRADE-PORTAL - SECURITY CONSTITUTION (V1.0)

As your **Researcher**, I am drafting this rule to ensure the **CICT Grade Portal** meets the high standards of academic integrity and data privacy (Data Privacy Act of 2012 compliance). This rule governs how AI Agents must handle authentication, authorization, and data protection.

---

#### 1. RBAC (ROLE-BASED ACCESS CONTROL) ARCHITECTURE

The system must enforce a **"Least Privilege"** policy. Access is strictly compartmentalized based on the following matrix:

| Feature | **Student** | **Faculty** | **Admin** |
| --- | --- | --- | --- |
| View Own Grades | ✅ | ✅ | ✅ |
| View Class List | ❌ | ✅ | ✅ |
| Input/Edit Grades | ❌ | ✅ (Own Subjects) | ✅ (Global) |
| Audit Log Access | ❌ | ❌ | ✅ |
| User Management | ❌ | ❌ | ✅ |

#### 2. AUTHENTICATION PROTOCOLS

* **Password Hashing:** Use `scrypt` or `bcrypt` (via `Werkzeug.security`). Plaintext passwords must **never** touch the database.
* **Session Management:**
* `SESSION_COOKIE_HTTPONLY = True` (Prevents XSS-based session theft).
* `SESSION_COOKIE_SECURE = True` (Requires HTTPS).
* `PERMANENT_SESSION_LIFETIME = 1800` (30-minute auto-timeout for high-traffic faculty computers).


* **Multi-Factor (MFA):** Recommended for **Admin** and **Faculty** roles via Email/OTP during grade submission windows.

#### 3. DATA INTEGRITY & THE "AUDIT TRAIL"

Every "Write" operation on a grade must be recorded in an immutable `GradeAudit` table.

* **Payload:** `{timestamp, actor_id, target_student_id, old_grade, new_grade, ip_address}`.
* **Logic:** AI Agents must use SQLAlchemy `after_insert` or `after_update` listeners to automate this logging so it cannot be bypassed by developers.

#### 4. THE "ANTI-TAMPER" LAYER (HTMX SECURITY)

Since we are using **HTMX**, we must defend against **IDOR (Insecure Direct Object Reference)**:

* **Server-Side Validation:** Never trust the `id` passed in an HTMX request (e.g., `hx-put="/grade/update/105"`).
* **Verification Logic:** The backend must verify that the `current_user` is the assigned instructor for the subject associated with grade ID `105` before committing the change.
* **CSRF Protection:** Every HTMX request must include the `X-CSRFToken` header.

#### 5. DATABASE & FILTRATION

* **SQL Injection:** AI Agents must use **SQLAlchemy ORM** queries exclusively. Raw SQL is prohibited unless sanitized via parameters.
* **XSS Prevention:** All user-generated content (student names, remarks) must be escaped by Jinja2. Use the `| e` filter for any custom data attributes.

---

### 🏛️ Research Synthesis for AI Agents

When the AI Agent begins coding the **Grade Portal**, it must initialize the `SecurityMiddleware` first. This middleware will wrap every route to check if the user's `role_id` matches the required permission for that endpoint.

**Example Rule for Agent:** > "If a student attempts to access `/faculty/dashboard`, the system must log a 'Security Alert' and redirect to the student home with a 403 error page styled in CICT Maroon."

