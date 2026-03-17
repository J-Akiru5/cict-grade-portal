# CICT Grade Portal - Schedule Seeding Guide

## Prerequisites

Ensure your Flask environment has all dependencies installed:

```bash
cd s:\Dev\Flask\cict-grade-portal
pip install -r requirements.txt
```

## Seeding Process

### Step 1: Create Missing Sections
First, create any missing academic sections:

```bash
python -m flask seed-sections
```

This will create sections like:
- BSIT-1A, BSIT-1B, BSIT-1C (1st year)
- BSIT-2A, BSIT-2B, BSIT-2C-NT, BSIT-2D-NT (2nd year)
- BSIT-3A-WM, BSIT-3A-NT, BSIT-3B-WM, BSIT-3B-NT, BSIT-3C-WM (3rd year)

### Step 2: Seed All Schedules
Import all extracted schedule data:

```bash
python -m flask seed-schedules
```

Or with custom parameters:
```bash
python -m flask seed-schedules --academic-year "2025-2026" --semester "2nd"
```

### Alternative: Direct Python Execution
If Flask CLI commands don't work:

```bash
python seed_sections.py
python seed_schedules_2025_2026.py
```

## Data Extracted - Validation Summary

### 📊 **Schedule Statistics:**
- **Total Sections:** 12 sections
- **Total Schedule Entries:** ~150+ entries
- **Academic Year:** 2025-2026
- **Semester:** 2nd Semester

### 🏫 **Sections Included:**

#### **1st Year BSIT (3 sections):**
- **BSIT-1A** - 13 schedule entries
- **BSIT-1B** - 13 schedule entries
- **BSIT-1C** - 13 schedule entries

#### **2nd Year BSIT (4 sections):**
- **BSIT-2A** - 11 schedule entries (Web/Mobile track)
- **BSIT-2B** - 11 schedule entries (Web/Mobile track)
- **BSIT-2C-NT** - 7 schedule entries (Non-Traditional, evening classes)
- **BSIT-2D-NT** - 7 schedule entries (Non-Traditional, evening classes)

#### **3rd Year BSIT (5 sections):**
- **BSIT-3A-WM** - 8 schedule entries (Web/Mobile track)
- **BSIT-3A-NT** - 6 schedule entries (Non-Traditional)
- **BSIT-3B-WM** - 10 schedule entries (Web/Mobile track)
- **BSIT-3B-NT** - 6 schedule entries (Non-Traditional)
- **BSIT-3C-WM** - 10 schedule entries (Web/Mobile track)

### 👨‍🏫 **Faculty Extracted (8 instructors):**
1. **Jenyfer Nardo** - Programming, OOP, Data Structures, Systems Analysis, HCI
2. **Jay-ar Baronda** - Web Development, Database Management, Mobile Development
3. **Arianne Cagape** - Understanding the Self, Rizal, Ethics
4. **Jenevie A. Siaron** - Contemporary World, Science Technology & Society
5. **English Faculty** - Purposive Communication
6. **Filipino Faculty** - Filipino sa Iba't-ibang Disiplina
7. **PE Instructor** - Physical Education courses
8. **NSTP Coordinator** - National Service Training Program

### 📚 **Subjects Extracted (25+ subjects):**

#### **GEC (General Education) Courses:**
- GEC1101 - Understanding the Self
- GEC1103 - Contemporary World
- GEC1104 - Purposive Communication
- GEC1105 - Mathematics in the Modern World
- GEC1106 - Science, Technology and Society
- GEC1107 - The Life and Works of Rizal
- GEC1108 - Ethics
- GEC1109 - Filipino sa IBA't-IBAng Disiplina

#### **IT Core Courses:**
- IT1101 - Introduction to Computing
- IT1102 - Computer Programming 1
- IT2101 - Data Structures and Algorithms
- IT2102 - Object Oriented Programming
- IT2103 - Web Development 1
- IT3101 - Database Management Systems
- IT3103 - Systems Analysis and Design
- IT3105 - Human Computer Interaction

#### **IT Specialization (Web/Mobile):**
- IT3102WM - Mobile Application Development
- IT3104WM - Advanced Web Development

#### **Other Courses:**
- PE2, PE3 - Physical Education
- NSTP2 - National Service Training Program

### ⏰ **Time Schedules:**

#### **Regular Day Classes:**
- Morning: 8:00 AM - 12:00 PM
- Afternoon: 1:00 PM - 5:00 PM

#### **Non-Traditional Evening Classes:**
- Evening: 5:00 PM - 9:00 PM (17:00-21:00)
- Saturday: 8:00 AM - 11:00 AM

### 🗓 **Weekly Distribution:**
- **Monday to Friday:** Main class days
- **Saturday:** NT sections only (limited classes)
- **No Sunday classes**

## Expected Results After Seeding

After successful seeding, you should have:

✅ **Database Tables Populated:**
- `sections` - 12 new section records
- `subjects` - 25+ subject records (if not already existing)
- `faculty` - 8 faculty records with user accounts
- `users` - 8 new faculty user accounts
- `schedules` - 150+ schedule entries

✅ **Functional Features:**
- Students can view their section schedules
- Faculty can see their assigned classes
- Admins can manage all schedules
- Schedule conflicts detection (if implemented)

## Troubleshooting

### Common Issues:

1. **Missing Dependencies:**
   ```bash
   pip install Flask Flask-SQLAlchemy Flask-Login Flask-Migrate python-dotenv
   ```

2. **Database Not Initialized:**
   ```bash
   python -m flask db init
   python -m flask db migrate -m "Initial migration"
   python -m flask db upgrade
   ```

3. **Supabase Configuration:**
   Ensure your `.env` file has proper Supabase credentials.

### Validation Queries:

After seeding, verify data with these SQL queries:

```sql
-- Check section count
SELECT COUNT(*) FROM sections;

-- Check schedule entries
SELECT s.display_name, sub.subject_code, f.full_name, sch.day_of_week, sch.time_start
FROM schedules sch
JOIN sections s ON sch.section_id = s.id
JOIN subjects sub ON sch.subject_id = sub.id
LEFT JOIN faculty f ON sch.faculty_id = f.id
ORDER BY s.display_name, sch.day_of_week, sch.time_start;

-- Check faculty assignments
SELECT f.full_name, COUNT(sch.id) as class_count
FROM faculty f
LEFT JOIN schedules sch ON f.id = sch.faculty_id
GROUP BY f.id, f.full_name
ORDER BY class_count DESC;
```

## Contact & Support

If you encounter any issues during seeding:
1. Check the Flask app logs for detailed error messages
2. Verify database connection and migrations
3. Ensure all required sections exist before seeding schedules

The seeding scripts are designed to be safe and idempotent - you can run them multiple times without creating duplicates.