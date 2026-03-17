-- ISUFST CICT Official Schedule Data for 2025-2026, 2nd Semester
-- FIXED VERSION - Handles missing columns and PostgreSQL compatibility
-- Run this in your Supabase SQL Editor

-- Step 1: Clear existing schedule data for this semester
DELETE FROM schedules WHERE academic_year = '2025-2026' AND semester = '2nd';

-- Step 2: Create missing sections (simplified approach)
-- First check what columns exist in sections table
-- This will show you the exact structure
-- SELECT column_name FROM information_schema.columns WHERE table_name = 'sections';

-- Create sections one by one to avoid column issues
DO $$
BEGIN
    -- 1st Year sections
    INSERT INTO sections (program, year_level, section_letter)
    VALUES ('BSIT', 1, 'A') ON CONFLICT DO NOTHING;

    INSERT INTO sections (program, year_level, section_letter)
    VALUES ('BSIT', 1, 'B') ON CONFLICT DO NOTHING;

    INSERT INTO sections (program, year_level, section_letter)
    VALUES ('BSIT', 1, 'C') ON CONFLICT DO NOTHING;

    -- 2nd Year sections
    INSERT INTO sections (program, year_level, section_letter)
    VALUES ('BSIT', 2, 'A-WM') ON CONFLICT DO NOTHING;

    INSERT INTO sections (program, year_level, section_letter)
    VALUES ('BSIT', 2, 'B-WM') ON CONFLICT DO NOTHING;

    INSERT INTO sections (program, year_level, section_letter)
    VALUES ('BSIT', 2, 'C-NT') ON CONFLICT DO NOTHING;

    INSERT INTO sections (program, year_level, section_letter)
    VALUES ('BSIT', 2, 'D-NT') ON CONFLICT DO NOTHING;

    -- 3rd Year sections
    INSERT INTO sections (program, year_level, section_letter)
    VALUES ('BSIT', 3, 'A-WM') ON CONFLICT DO NOTHING;

    INSERT INTO sections (program, year_level, section_letter)
    VALUES ('BSIT', 3, 'A-NT') ON CONFLICT DO NOTHING;

    INSERT INTO sections (program, year_level, section_letter)
    VALUES ('BSIT', 3, 'B-WM') ON CONFLICT DO NOTHING;

    INSERT INTO sections (program, year_level, section_letter)
    VALUES ('BSIT', 3, 'B-NT') ON CONFLICT DO NOTHING;

    INSERT INTO sections (program, year_level, section_letter)
    VALUES ('BSIT', 3, 'C-WM') ON CONFLICT DO NOTHING;
END $$;

-- Step 3: Create missing subjects (simplified approach)
DO $$
BEGIN
    -- 1st Year IT Subjects
    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('IT1204', 'Introduction to Computing', 3, 'CICT') ON CONFLICT DO NOTHING;

    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('IT1205', 'Data Structures and Algorithms', 3, 'CICT') ON CONFLICT DO NOTHING;

    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('IT1206', 'Computer Programming 1', 3, 'CICT') ON CONFLICT DO NOTHING;

    -- 1st Year GEC Subjects
    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('GEE1201', 'Understanding the Self', 3, 'CICT') ON CONFLICT DO NOTHING;

    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('GEC1204', 'Contemporary World', 3, 'CICT') ON CONFLICT DO NOTHING;

    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('GEM2201', 'Mathematics in the Modern World', 3, 'CICT') ON CONFLICT DO NOTHING;

    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('PATHFIT2', 'Physical Education 2', 2, 'CICT') ON CONFLICT DO NOTHING;

    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('NSTP2', 'National Service Training Program 2', 3, 'CICT') ON CONFLICT DO NOTHING;

    -- 2nd Year IT Subjects
    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('IT2214', 'Object Oriented Programming', 3, 'CICT') ON CONFLICT DO NOTHING;

    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('IT2216', 'Database Management Systems', 3, 'CICT') ON CONFLICT DO NOTHING;

    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('IT2217', 'Systems Analysis and Design', 3, 'CICT') ON CONFLICT DO NOTHING;

    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('ITAS2218', 'Web Development 1', 3, 'CICT') ON CONFLICT DO NOTHING;

    -- 2nd Year GEC Subjects
    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('GEE2205', 'The Life and Works of Rizal', 3, 'CICT') ON CONFLICT DO NOTHING;

    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('GEE2207', 'Ethics', 3, 'CICT') ON CONFLICT DO NOTHING;

    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('PATHFIT4', 'Physical Education 4', 2, 'CICT') ON CONFLICT DO NOTHING;

    -- 3rd Year IT Subjects
    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('IT3225', 'Software Engineering', 3, 'CICT') ON CONFLICT DO NOTHING;

    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('IT3226', 'Information Systems', 3, 'CICT') ON CONFLICT DO NOTHING;

    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('ITPE3227', 'Human Computer Interaction', 3, 'CICT') ON CONFLICT DO NOTHING;

    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('ITAS3228', 'Mobile Application Development', 3, 'CICT') ON CONFLICT DO NOTHING;

    INSERT INTO subjects (subject_code, subject_title, units, department)
    VALUES ('ITAS3229', 'Advanced Web Development', 3, 'CICT') ON CONFLICT DO NOTHING;
END $$;

-- Step 4: Insert schedule data (first 39 entries - BSIT 1st Year)
-- BSIT-1A (13 entries)
INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'A'
AND sub.subject_code = 'IT1204';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '10:30:00'::time, '12:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'A'
AND sub.subject_code = 'GEE1201';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '13:00:00'::time, '14:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'A'
AND sub.subject_code = 'GEM2201';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'A'
AND sub.subject_code = 'IT1205';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'A'
AND sub.subject_code = 'IT1206';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'A'
AND sub.subject_code = 'IT1204';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '10:30:00'::time, '12:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'A'
AND sub.subject_code = 'GEE1201';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '13:00:00'::time, '14:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'A'
AND sub.subject_code = 'GEM2201';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'A'
AND sub.subject_code = 'IT1205';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'A'
AND sub.subject_code = 'IT1206';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'A'
AND sub.subject_code = 'GEC1204';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '13:00:00'::time, '15:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'A'
AND sub.subject_code = 'PATHFIT2';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '15:00:00'::time, '17:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'A'
AND sub.subject_code = 'NSTP2';

-- BSIT-1B Schedule (13 entries)
INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'B'
AND sub.subject_code = 'IT1206';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'B'
AND sub.subject_code = 'GEC1204';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '10:30:00'::time, '12:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'B'
AND sub.subject_code = 'GEE1201';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'B'
AND sub.subject_code = 'IT1204';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '16:00:00'::time, '17:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'B'
AND sub.subject_code = 'GEM2201';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'B'
AND sub.subject_code = 'IT1206';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'B'
AND sub.subject_code = 'GEC1204';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '10:30:00'::time, '12:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'B'
AND sub.subject_code = 'GEE1201';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'B'
AND sub.subject_code = 'IT1204';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '16:00:00'::time, '17:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'B'
AND sub.subject_code = 'GEM2201';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'B'
AND sub.subject_code = 'IT1205';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '13:00:00'::time, '15:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'B'
AND sub.subject_code = 'PATHFIT2';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '15:00:00'::time, '17:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'B'
AND sub.subject_code = 'NSTP2';

-- BSIT-1C Schedule (13 entries)
INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'C'
AND sub.subject_code = 'IT1205';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'C'
AND sub.subject_code = 'IT1206';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'C'
AND sub.subject_code = 'GEC1204';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '13:00:00'::time, '14:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'C'
AND sub.subject_code = 'GEE1201';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '14:30:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'C'
AND sub.subject_code = 'GEM2201';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'C'
AND sub.subject_code = 'IT1205';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'C'
AND sub.subject_code = 'IT1206';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'C'
AND sub.subject_code = 'GEC1204';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '13:00:00'::time, '14:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'C'
AND sub.subject_code = 'GEE1201';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '14:30:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'C'
AND sub.subject_code = 'GEM2201';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'C'
AND sub.subject_code = 'IT1204';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '13:00:00'::time, '15:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'C'
AND sub.subject_code = 'PATHFIT2';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '15:00:00'::time, '17:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 1 AND s.section_letter = 'C'
AND sub.subject_code = 'NSTP2';

-- BSIT-2A-WM Schedule (11 entries - corrected count)
INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'IT2214';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '13:00:00'::time, '14:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'GEE2205';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '14:30:00'::time, '17:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'ITAS2218';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'IT2216';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'IT2217';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'IT2214';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '13:00:00'::time, '14:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'GEE2205';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '14:30:00'::time, '17:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'ITAS2218';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'IT2216';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'IT2217';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '13:00:00'::time, '15:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'PATHFIT4';

-- BSIT-2B-WM Schedule (11 entries)
INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'IT2216';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'ITAS2218';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '09:00:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'GEE2205';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'IT2214';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'IT2216';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'ITAS2218';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '09:00:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'GEE2205';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'IT2214';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'IT2217';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '13:00:00'::time, '14:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'GEE2207';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '14:30:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'PATHFIT4';

-- BSIT-2C-NT Schedule (7 entries - Evening classes)
INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'C-NT'
AND sub.subject_code = 'IT2214';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'C-NT'
AND sub.subject_code = 'IT2216';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '17:30:00'::time, '19:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'C-NT'
AND sub.subject_code = 'GEE2205';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '19:00:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'C-NT'
AND sub.subject_code = 'GEE2207';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'C-NT'
AND sub.subject_code = 'ITAS2218';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'C-NT'
AND sub.subject_code = 'IT2217';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Sat', '07:30:00'::time, '09:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'C-NT'
AND sub.subject_code = 'PATHFIT4';

-- BSIT-2D-NT Schedule (7 entries - Evening classes)
INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'D-NT'
AND sub.subject_code = 'IT2216';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'D-NT'
AND sub.subject_code = 'IT2217';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'D-NT'
AND sub.subject_code = 'IT2214';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '17:30:00'::time, '19:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'D-NT'
AND sub.subject_code = 'GEE2205';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '19:00:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'D-NT'
AND sub.subject_code = 'GEE2207';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'D-NT'
AND sub.subject_code = 'ITAS2218';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Sat', '07:30:00'::time, '09:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 2 AND s.section_letter = 'D-NT'
AND sub.subject_code = 'PATHFIT4';

-- BSIT-3A-WM Schedule (10 entries)
INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'IT3225';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'ITAS3228';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'IT3226';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'ITAS3229';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'IT3225';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'ITAS3228';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'IT3226';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'ITAS3229';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'GEE2205';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '13:00:00'::time, '15:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'A-WM'
AND sub.subject_code = 'ITPE3227';

-- BSIT-3A-NT Schedule (6 entries - Evening classes)
INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'A-NT'
AND sub.subject_code = 'IT3225';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'A-NT'
AND sub.subject_code = 'IT3226';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'A-NT'
AND sub.subject_code = 'ITAS3228';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'A-NT'
AND sub.subject_code = 'ITAS3229';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'A-NT'
AND sub.subject_code = 'GEE2205';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Sat', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'A-NT'
AND sub.subject_code = 'ITPE3227';

-- BSIT-3B-WM Schedule (10 entries)
INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'IT3226';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '13:00:00'::time, '15:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'ITPE3227';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'IT3225';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'ITAS3229';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'IT3226';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '13:00:00'::time, '15:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'ITPE3227';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'IT3225';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'ITAS3229';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'GEE2205';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'ITAS3228';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'B-WM'
AND sub.subject_code = 'ITAS3228';

-- BSIT-3B-NT Schedule (6 entries - Evening classes)
INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'B-NT'
AND sub.subject_code = 'IT3226';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'B-NT'
AND sub.subject_code = 'IT3225';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'B-NT'
AND sub.subject_code = 'ITAS3229';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'B-NT'
AND sub.subject_code = 'ITAS3228';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '17:30:00'::time, '20:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'B-NT'
AND sub.subject_code = 'GEE2205';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Sat', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'B-NT'
AND sub.subject_code = 'ITPE3227';

-- BSIT-3C-WM Schedule (10 entries - Final section!)
INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'C-WM'
AND sub.subject_code = 'GEE2205';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Mon', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'C-WM'
AND sub.subject_code = 'ITAS3228';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '07:30:00'::time, '09:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'C-WM'
AND sub.subject_code = 'ITPE3227';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Tue', '09:00:00'::time, '12:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'C-WM'
AND sub.subject_code = 'IT3226';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'C-WM'
AND sub.subject_code = 'GEE2205';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Wed', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'C-WM'
AND sub.subject_code = 'ITAS3228';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '07:30:00'::time, '09:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'C-WM'
AND sub.subject_code = 'ITPE3227';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Thu', '09:00:00'::time, '12:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'C-WM'
AND sub.subject_code = 'IT3226';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '07:30:00'::time, '10:30:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'C-WM'
AND sub.subject_code = 'IT3225';

INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT s.id, sub.id, 'Fri', '13:00:00'::time, '16:00:00'::time, '2025-2026', '2nd'
FROM sections s, subjects sub
WHERE s.program = 'BSIT' AND s.year_level = 3 AND s.section_letter = 'C-WM'
AND sub.subject_code = 'ITAS3229';

-- 🎉 ALL 117 SCHEDULE ENTRIES COMPLETED! 🎉
-- Final Results Summary
SELECT
    COUNT(*) as total_schedules,
    COUNT(DISTINCT sch.section_id) as sections_covered,
    COUNT(DISTINCT sch.subject_id) as subjects_used
FROM schedules sch
WHERE sch.academic_year = '2025-2026' AND sch.semester = '2nd';

-- Detailed breakdown by section
SELECT
    (sec.program || '-' || sec.year_level || sec.section_letter) as section_name,
    COUNT(*) as class_count,
    STRING_AGG(DISTINCT sub.subject_code, ', ' ORDER BY sub.subject_code) as subjects
FROM schedules sch
JOIN sections sec ON sch.section_id = sec.id
JOIN subjects sub ON sch.subject_id = sub.id
WHERE sch.academic_year = '2025-2026' AND sch.semester = '2nd'
GROUP BY sec.id, sec.program, sec.year_level, sec.section_letter
ORDER BY sec.year_level, sec.section_letter;

-- Sample schedule view (first 25 entries)
SELECT
    (sec.program || '-' || sec.year_level || sec.section_letter) as section_name,
    sub.subject_code,
    sub.subject_title,
    sch.day_of_week,
    sch.time_start,
    sch.time_end
FROM schedules sch
JOIN sections sec ON sch.section_id = sec.id
JOIN subjects sub ON sch.subject_id = sub.id
WHERE sch.academic_year = '2025-2026' AND sch.semester = '2nd'
ORDER BY sec.year_level, sec.section_letter,
    CASE sch.day_of_week
        WHEN 'Mon' THEN 1 WHEN 'Tue' THEN 2 WHEN 'Wed' THEN 3
        WHEN 'Thu' THEN 4 WHEN 'Fri' THEN 5 WHEN 'Sat' THEN 6
        ELSE 7 END,
    sch.time_start
LIMIT 25;