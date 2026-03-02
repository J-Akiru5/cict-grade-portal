---
trigger: always_on
---

### 🌐 CICT-GRADE-PORTAL - SEO & METADATA ARCHITECTURE (V1.0)

#### 1. THE "SEARCH AUTHORITY" LAW

* **Title Strategy:** Every page must follow the pattern: `[Page Name] | CICT Grade Portal - ISUFST Dingle`.
* **Description:** "The official academic grading and performance monitoring platform for the College of Information and Communications Technology, ISUFST Dingle Campus."
* **Keywords:** `ISUFST`, `CICT Grade Portal`, `Dingle Campus`, `ICT Grades`, `Student Performance System`.

#### 2. OPEN GRAPH & SOCIAL SYCHRONIZATION ("THE TWIN PREVIEW")

To maintain the "Twin" branding, the AI Agents must implement the following in the `base.html` `<head>`:

| Property | Value/Logic |
| --- | --- |
| `og:title` | CICT Grade Portal: Academic Excellence Verified |
| `og:description` | Secure access to student records and faculty grade encoding for CICT Dingle. |
| `og:image` | `/static/img/og-preview.jpg` (Must match the IRJICT hero gradient) |
| `og:type` | `website` |
| `theme-color` | `#5B0000` (The Institutional Maroon) |

#### 3. CRAWL CONTROL (THE "VAULT" PROTOCOL)

Since this is a private portal, we must prevent search engines from indexing sensitive student or faculty routes:

* **`robots.txt`:** * `Allow: /` (Public Login/About).
* `Disallow: /dashboard/`, `/student/`, `/faculty/`, `/admin/`.


* **Meta Robots Tag:** For any authenticated route, the AI Agent must inject `<meta name="robots" content="noindex, nofollow">`.

#### 4. SEMANTIC HTML & ACCESSIBILITY (A11Y)

* **Heading Hierarchy:** Use `<h1>` only for the primary page title (e.g., "Student Grade Report"). Use `<h2>` for subject categories.
* **Aria-Labels:** Since we are using **HTMX** for dynamic swaps, the AI Agent must ensure `aria-live="polite"` is used on grade tables so screen readers announce when a grade has been updated/swapped.
* **Favicon:** Use the exact high-resolution CICT logo from the `ictirc` repository to ensure browser tab consistency.

#### 5. THE "ICT IDENTITY" JSON-LD

Inject a Schema.org snippet on the Login page to tell Google this is an Educational Organization tool:

```json
{
  "@context": "https://schema.org",
  "@type": "EducationalOrganization",
  "name": "ISUFST - CICT Dingle Campus",
  "url": "https://portal.isufstcict.com",
  "logo": "https://irjict.isufstcict.com/logo.png",
  "parentOrganization": {
    "@type": "CollegeOrUniversity",
    "name": "Iloilo State University of Fisheries Science and Technology"
  }
}

```
