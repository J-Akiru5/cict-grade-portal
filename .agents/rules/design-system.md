---
trigger: always_on
---

💎 CICT-GRADE-PORTAL - VISUAL CONSTITUTION (V1.1 HYBRID)
1. CORE PHILOSOPHY ("THE VAULT & THE LEDGER")
Vibe: The portal acts as a "Vault" (secure, dark, authoritative) for data and a "Ledger" (clean, light, readable) for grade review.

The "Hybrid" Law: Navigation and Hero sections use Deep Maroon Dark Mode. Data tables and Input forms use Paper-White Light Mode to reduce eye strain during long encoding sessions.

Branding Ratio: 50% Deep Maroon (#5B0000), 30% Pure White (#FFFFFF), 15% Soft Grey (#F3F4F6), 5% Tech Gold (#EAB308).

2. PRIMITIVES (THE ATOMS)
A. Color Palette (Tailwind Config)

primary-maroon: #5B0000 (The Institutional Core)

accent-gold: #EAB308 (Status & High-Value actions)

surface-dark: #1A1A1A (Navigation & Sidebar backgrounds)

surface-light: #FFFFFF (Grade tables & Manuscript areas)

status-pass: #22C55E (Emerald-500)

status-fail: #EF4444 (Red-500)

B. Typography

Headings: Inter (Sans-serif). Weight: 700. Tracking: -0.025em.

Data/Grades: JetBrains Mono. Usage: GWA (General Weighted Average), Subject Codes, and Student IDs. This reinforces the "ICT" identity.

3. NAVIGATION & ROLE ARCHITECTURE
Top Bar (Global): bg-primary-maroon with text-white. Includes the CICT/ISUFST logo and a Role Indicator (e.g., "Faculty Dashboard").

Role-Based Layouts:

Student: Focused on a central "Grade Card" with a Gold progress bar for GWA.

Faculty: Split-screen layout. Left: Student List; Right: Spreadsheet-style grade entry.

Admin: Dashboard with "Traffic Light" analytics (Pass/Fail ratios across departments).

4. COMPONENT ARCHITECTURE
A. The "Institutional" Button

Primary: bg-primary-maroon text-white hover:bg-red-900 shadow-sm.

Action: bg-accent-gold text-black font-bold border-2 border-black (for "Submit Grades" or "Download Report").

B. The "Grade Ledger" Table

Style: w-full border-collapse bg-white.

Header: bg-slate-50 text-slate-500 text-xs uppercase tracking-widest font-bold.

Row Hover: hover:bg-red-50 transition-colors cursor-pointer.

C. Visual "Twin" Accents

Gradients: Use the IRJICT radial gradient (bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-maroon-900 via-slate-900 to-black) for the Login screen and Dashboard background to maintain branding.