-- ISUFST CICT Official Schedule Data for 2025-2026, 2nd Semester
-- Run this in your Supabase SQL Editor

-- First, clear existing schedule data for this semester
DELETE FROM schedules WHERE academic_year = '2025-2026' AND semester = '2nd';

-- Create missing sections if they don't exist
INSERT INTO sections (program, year_level, section_letter)
SELECT 'BSIT', year_level, section_letter
FROM (VALUES
    (1, 'A'), (1, 'B'), (1, 'C'),
    (2, 'A-WM'), (2, 'B-WM'), (2, 'C-NT'), (2, 'D-NT'),
    (3, 'A-WM'), (3, 'A-NT'), (3, 'B-WM'), (3, 'B-NT'), (3, 'C-WM')
) AS sections(year_level, section_letter)
WHERE NOT EXISTS (
    SELECT 1 FROM sections s
    WHERE s.program = 'BSIT'
    AND s.year_level = sections.year_level
    AND s.section_letter = sections.section_letter
);

-- Create missing subjects with official ISUFST codes
INSERT INTO subjects (subject_code, subject_title, units, department)
SELECT subject_code, subject_title, units, 'CICT'
FROM (VALUES
    -- 1st Year IT Subjects
    ('IT1204', 'Introduction to Computing', 3),
    ('IT1205', 'Data Structures and Algorithms', 3),
    ('IT1206', 'Computer Programming 1', 3),
    -- 1st Year GEC Subjects
    ('GEE1201', 'Understanding the Self', 3),
    ('GEC1204', 'Contemporary World', 3),
    ('GEM2201', 'Mathematics in the Modern World', 3),
    ('PATHFIT2', 'Physical Education 2', 2),
    ('NSTP2', 'National Service Training Program 2', 3),
    -- 2nd Year IT Subjects
    ('IT2214', 'Object Oriented Programming', 3),
    ('IT2216', 'Database Management Systems', 3),
    ('IT2217', 'Systems Analysis and Design', 3),
    ('ITAS2218', 'Web Development 1', 3),
    -- 2nd Year GEC Subjects
    ('GEE2205', 'The Life and Works of Rizal', 3),
    ('GEE2207', 'Ethics', 3),
    ('PATHFIT4', 'Physical Education 4', 2),
    -- 3rd Year IT Subjects
    ('IT3225', 'Software Engineering', 3),
    ('IT3226', 'Information Systems', 3),
    ('ITPE3227', 'Human Computer Interaction', 3),
    ('ITAS3228', 'Mobile Application Development', 3),
    ('ITAS3229', 'Advanced Web Development', 3)
) AS new_subjects(subject_code, subject_title, units)
WHERE NOT EXISTS (
    SELECT 1 FROM subjects s WHERE s.subject_code = new_subjects.subject_code
);

-- Now insert the official schedule data (117 entries)
WITH schedule_data AS (
    SELECT
        s.id as section_id,
        sub.id as subject_id,
        day_of_week,
        time_start::time,
        time_end::time
    FROM (VALUES
        -- BSIT-1A Schedule (13 entries)
        ('BSIT', 1, 'A', 'IT1204', 'Mon', '07:30:00', '10:30:00'),
        ('BSIT', 1, 'A', 'GEE1201', 'Mon', '10:30:00', '12:00:00'),
        ('BSIT', 1, 'A', 'GEM2201', 'Mon', '13:00:00', '14:30:00'),
        ('BSIT', 1, 'A', 'IT1205', 'Tue', '07:30:00', '10:30:00'),
        ('BSIT', 1, 'A', 'IT1206', 'Tue', '13:00:00', '16:00:00'),
        ('BSIT', 1, 'A', 'IT1204', 'Wed', '07:30:00', '10:30:00'),
        ('BSIT', 1, 'A', 'GEE1201', 'Wed', '10:30:00', '12:00:00'),
        ('BSIT', 1, 'A', 'GEM2201', 'Wed', '13:00:00', '14:30:00'),
        ('BSIT', 1, 'A', 'IT1205', 'Thu', '07:30:00', '10:30:00'),
        ('BSIT', 1, 'A', 'IT1206', 'Thu', '13:00:00', '16:00:00'),
        ('BSIT', 1, 'A', 'GEC1204', 'Fri', '07:30:00', '10:30:00'),
        ('BSIT', 1, 'A', 'PATHFIT2', 'Fri', '13:00:00', '15:00:00'),
        ('BSIT', 1, 'A', 'NSTP2', 'Fri', '15:00:00', '17:00:00'),

        -- BSIT-1B Schedule (13 entries)
        ('BSIT', 1, 'B', 'IT1206', 'Mon', '07:30:00', '10:30:00'),
        ('BSIT', 1, 'B', 'GEC1204', 'Mon', '13:00:00', '16:00:00'),
        ('BSIT', 1, 'B', 'GEE1201', 'Tue', '10:30:00', '12:00:00'),
        ('BSIT', 1, 'B', 'IT1204', 'Tue', '13:00:00', '16:00:00'),
        ('BSIT', 1, 'B', 'GEM2201', 'Tue', '16:00:00', '17:30:00'),
        ('BSIT', 1, 'B', 'IT1206', 'Wed', '07:30:00', '10:30:00'),
        ('BSIT', 1, 'B', 'GEC1204', 'Wed', '13:00:00', '16:00:00'),
        ('BSIT', 1, 'B', 'GEE1201', 'Thu', '10:30:00', '12:00:00'),
        ('BSIT', 1, 'B', 'IT1204', 'Thu', '13:00:00', '16:00:00'),
        ('BSIT', 1, 'B', 'GEM2201', 'Thu', '16:00:00', '17:30:00'),
        ('BSIT', 1, 'B', 'IT1205', 'Fri', '07:30:00', '10:30:00'),
        ('BSIT', 1, 'B', 'PATHFIT2', 'Fri', '13:00:00', '15:00:00'),
        ('BSIT', 1, 'B', 'NSTP2', 'Fri', '15:00:00', '17:00:00'),

        -- BSIT-1C Schedule (13 entries)
        ('BSIT', 1, 'C', 'IT1205', 'Mon', '07:30:00', '10:30:00'),
        ('BSIT', 1, 'C', 'IT1206', 'Mon', '13:00:00', '16:00:00'),
        ('BSIT', 1, 'C', 'GEC1204', 'Tue', '07:30:00', '10:30:00'),
        ('BSIT', 1, 'C', 'GEE1201', 'Tue', '13:00:00', '14:30:00'),
        ('BSIT', 1, 'C', 'GEM2201', 'Tue', '14:30:00', '16:00:00'),
        ('BSIT', 1, 'C', 'IT1205', 'Wed', '07:30:00', '10:30:00'),
        ('BSIT', 1, 'C', 'IT1206', 'Wed', '13:00:00', '16:00:00'),
        ('BSIT', 1, 'C', 'GEC1204', 'Thu', '07:30:00', '10:30:00'),
        ('BSIT', 1, 'C', 'GEE1201', 'Thu', '13:00:00', '14:30:00'),
        ('BSIT', 1, 'C', 'GEM2201', 'Thu', '14:30:00', '16:00:00'),
        ('BSIT', 1, 'C', 'IT1204', 'Fri', '07:30:00', '10:30:00'),
        ('BSIT', 1, 'C', 'PATHFIT2', 'Fri', '13:00:00', '15:00:00'),
        ('BSIT', 1, 'C', 'NSTP2', 'Fri', '15:00:00', '17:00:00'),

        -- BSIT-2A-WM Schedule (11 entries)
        ('BSIT', 2, 'A-WM', 'IT2214', 'Mon', '07:30:00', '10:30:00'),
        ('BSIT', 2, 'A-WM', 'GEE2205', 'Mon', '13:00:00', '14:30:00'),
        ('BSIT', 2, 'A-WM', 'ITAS2218', 'Mon', '14:30:00', '17:30:00'),
        ('BSIT', 2, 'A-WM', 'IT2216', 'Tue', '07:30:00', '10:30:00'),
        ('BSIT', 2, 'A-WM', 'IT2217', 'Tue', '13:00:00', '16:00:00'),
        ('BSIT', 2, 'A-WM', 'IT2214', 'Wed', '07:30:00', '10:30:00'),
        ('BSIT', 2, 'A-WM', 'GEE2205', 'Wed', '13:00:00', '14:30:00'),
        ('BSIT', 2, 'A-WM', 'ITAS2218', 'Wed', '14:30:00', '17:30:00'),
        ('BSIT', 2, 'A-WM', 'IT2216', 'Thu', '07:30:00', '10:30:00'),
        ('BSIT', 2, 'A-WM', 'IT2217', 'Thu', '13:00:00', '16:00:00'),
        ('BSIT', 2, 'A-WM', 'GEE2207', 'Fri', '07:30:00', '10:30:00'),
        ('BSIT', 2, 'A-WM', 'PATHFIT4', 'Fri', '13:00:00', '15:00:00'),

        -- BSIT-2B-WM Schedule (11 entries)
        ('BSIT', 2, 'B-WM', 'IT2216', 'Mon', '07:30:00', '10:30:00'),
        ('BSIT', 2, 'B-WM', 'ITAS2218', 'Mon', '13:00:00', '16:00:00'),
        ('BSIT', 2, 'B-WM', 'GEE2205', 'Tue', '09:00:00', '10:30:00'),
        ('BSIT', 2, 'B-WM', 'IT2214', 'Tue', '13:00:00', '16:00:00'),
        ('BSIT', 2, 'B-WM', 'IT2216', 'Wed', '07:30:00', '10:30:00'),
        ('BSIT', 2, 'B-WM', 'ITAS2218', 'Wed', '13:00:00', '16:00:00'),
        ('BSIT', 2, 'B-WM', 'GEE2205', 'Thu', '09:00:00', '10:30:00'),
        ('BSIT', 2, 'B-WM', 'IT2214', 'Thu', '13:00:00', '16:00:00'),
        ('BSIT', 2, 'B-WM', 'IT2217', 'Fri', '07:30:00', '10:30:00'),
        ('BSIT', 2, 'B-WM', 'GEE2207', 'Fri', '13:00:00', '14:30:00'),
        ('BSIT', 2, 'B-WM', 'PATHFIT4', 'Fri', '14:30:00', '16:00:00'),

        -- BSIT-2C-NT Schedule (Evening - 7 entries)
        ('BSIT', 2, 'C-NT', 'IT2214', 'Mon', '17:30:00', '20:30:00'),
        ('BSIT', 2, 'C-NT', 'IT2216', 'Tue', '17:30:00', '20:30:00'),
        ('BSIT', 2, 'C-NT', 'GEE2205', 'Wed', '17:30:00', '19:00:00'),
        ('BSIT', 2, 'C-NT', 'GEE2207', 'Wed', '19:00:00', '20:30:00'),
        ('BSIT', 2, 'C-NT', 'ITAS2218', 'Thu', '17:30:00', '20:30:00'),
        ('BSIT', 2, 'C-NT', 'IT2217', 'Fri', '17:30:00', '20:30:00'),
        ('BSIT', 2, 'C-NT', 'PATHFIT4', 'Sat', '07:30:00', '09:00:00'),

        -- BSIT-2D-NT Schedule (Evening - 7 entries)
        ('BSIT', 2, 'D-NT', 'IT2216', 'Mon', '17:30:00', '20:30:00'),
        ('BSIT', 2, 'D-NT', 'IT2217', 'Tue', '17:30:00', '20:30:00'),
        ('BSIT', 2, 'D-NT', 'IT2214', 'Wed', '17:30:00', '20:30:00'),
        ('BSIT', 2, 'D-NT', 'GEE2205', 'Thu', '17:30:00', '19:00:00'),
        ('BSIT', 2, 'D-NT', 'GEE2207', 'Thu', '19:00:00', '20:30:00'),
        ('BSIT', 2, 'D-NT', 'ITAS2218', 'Fri', '17:30:00', '20:30:00'),
        ('BSIT', 2, 'D-NT', 'PATHFIT4', 'Sat', '07:30:00', '09:00:00'),

        -- BSIT-3A-WM Schedule (10 entries)
        ('BSIT', 3, 'A-WM', 'IT3225', 'Mon', '07:30:00', '10:30:00'),
        ('BSIT', 3, 'A-WM', 'ITAS3228', 'Mon', '13:00:00', '16:00:00'),
        ('BSIT', 3, 'A-WM', 'IT3226', 'Tue', '07:30:00', '10:30:00'),
        ('BSIT', 3, 'A-WM', 'ITAS3229', 'Tue', '13:00:00', '16:00:00'),
        ('BSIT', 3, 'A-WM', 'IT3225', 'Wed', '07:30:00', '10:30:00'),
        ('BSIT', 3, 'A-WM', 'ITAS3228', 'Wed', '13:00:00', '16:00:00'),
        ('BSIT', 3, 'A-WM', 'IT3226', 'Thu', '07:30:00', '10:30:00'),
        ('BSIT', 3, 'A-WM', 'ITAS3229', 'Thu', '13:00:00', '16:00:00'),
        ('BSIT', 3, 'A-WM', 'GEE2205', 'Fri', '07:30:00', '10:30:00'),
        ('BSIT', 3, 'A-WM', 'ITPE3227', 'Fri', '13:00:00', '15:00:00'),

        -- BSIT-3A-NT Schedule (Evening - 6 entries)
        ('BSIT', 3, 'A-NT', 'IT3225', 'Mon', '17:30:00', '20:30:00'),
        ('BSIT', 3, 'A-NT', 'IT3226', 'Tue', '17:30:00', '20:30:00'),
        ('BSIT', 3, 'A-NT', 'ITAS3228', 'Wed', '17:30:00', '20:30:00'),
        ('BSIT', 3, 'A-NT', 'ITAS3229', 'Thu', '17:30:00', '20:30:00'),
        ('BSIT', 3, 'A-NT', 'GEE2205', 'Fri', '17:30:00', '20:30:00'),
        ('BSIT', 3, 'A-NT', 'ITPE3227', 'Sat', '07:30:00', '10:30:00'),

        -- BSIT-3B-WM Schedule (10 entries)
        ('BSIT', 3, 'B-WM', 'IT3226', 'Mon', '07:30:00', '10:30:00'),
        ('BSIT', 3, 'B-WM', 'ITPE3227', 'Mon', '13:00:00', '15:00:00'),
        ('BSIT', 3, 'B-WM', 'IT3225', 'Tue', '07:30:00', '10:30:00'),
        ('BSIT', 3, 'B-WM', 'ITAS3229', 'Tue', '13:00:00', '16:00:00'),
        ('BSIT', 3, 'B-WM', 'IT3226', 'Wed', '07:30:00', '10:30:00'),
        ('BSIT', 3, 'B-WM', 'ITPE3227', 'Wed', '13:00:00', '15:00:00'),
        ('BSIT', 3, 'B-WM', 'IT3225', 'Thu', '07:30:00', '10:30:00'),
        ('BSIT', 3, 'B-WM', 'ITAS3229', 'Thu', '13:00:00', '16:00:00'),
        ('BSIT', 3, 'B-WM', 'GEE2205', 'Fri', '07:30:00', '10:30:00'),
        ('BSIT', 3, 'B-WM', 'ITAS3228', 'Fri', '13:00:00', '16:00:00'),

        -- BSIT-3B-NT Schedule (Evening - 6 entries)
        ('BSIT', 3, 'B-NT', 'IT3226', 'Mon', '17:30:00', '20:30:00'),
        ('BSIT', 3, 'B-NT', 'IT3225', 'Tue', '17:30:00', '20:30:00'),
        ('BSIT', 3, 'B-NT', 'ITAS3229', 'Wed', '17:30:00', '20:30:00'),
        ('BSIT', 3, 'B-NT', 'ITAS3228', 'Thu', '17:30:00', '20:30:00'),
        ('BSIT', 3, 'B-NT', 'GEE2205', 'Fri', '17:30:00', '20:30:00'),
        ('BSIT', 3, 'B-NT', 'ITPE3227', 'Sat', '07:30:00', '10:30:00'),

        -- BSIT-3C-WM Schedule (10 entries)
        ('BSIT', 3, 'C-WM', 'GEE2205', 'Mon', '07:30:00', '10:30:00'),
        ('BSIT', 3, 'C-WM', 'ITAS3228', 'Mon', '13:00:00', '16:00:00'),
        ('BSIT', 3, 'C-WM', 'ITPE3227', 'Tue', '07:30:00', '09:00:00'),
        ('BSIT', 3, 'C-WM', 'IT3226', 'Tue', '09:00:00', '12:00:00'),
        ('BSIT', 3, 'C-WM', 'GEE2205', 'Wed', '07:30:00', '10:30:00'),
        ('BSIT', 3, 'C-WM', 'ITAS3228', 'Wed', '13:00:00', '16:00:00'),
        ('BSIT', 3, 'C-WM', 'ITPE3227', 'Thu', '07:30:00', '09:00:00'),
        ('BSIT', 3, 'C-WM', 'IT3226', 'Thu', '09:00:00', '12:00:00'),
        ('BSIT', 3, 'C-WM', 'IT3225', 'Fri', '07:30:00', '10:30:00'),
        ('BSIT', 3, 'C-WM', 'ITAS3229', 'Fri', '13:00:00', '16:00:00')

    ) AS data(program, year_level, section_letter, subject_code, day_of_week, time_start, time_end)

    JOIN sections s ON s.program = data.program
        AND s.year_level = data.year_level
        AND s.section_letter = data.section_letter
    JOIN subjects sub ON sub.subject_code = data.subject_code
)

INSERT INTO schedules (section_id, faculty_id, subject_id, day_of_week, time_start, time_end, academic_year, semester)
SELECT
    section_id,
    NULL as faculty_id,  -- Faculty assignment can be done later
    subject_id,
    day_of_week,
    time_start,
    time_end,
    '2025-2026' as academic_year,
    '2nd' as semester
FROM schedule_data;

-- Show results
SELECT
    COUNT(*) as total_schedules,
    COUNT(DISTINCT s.section_id) as sections_covered,
    COUNT(DISTINCT s.subject_id) as subjects_used
FROM schedules s
WHERE s.academic_year = '2025-2026' AND s.semester = '2nd';

-- Optional: View a sample of the created schedules
SELECT
    (sec.program || '-' || sec.year_level || sec.section_letter) as section_name,
    sub.subject_code,
    sub.subject_title,
    s.day_of_week,
    s.time_start,
    s.time_end
FROM schedules s
JOIN sections sec ON s.section_id = sec.id
JOIN subjects sub ON s.subject_id = sub.id
WHERE s.academic_year = '2025-2026' AND s.semester = '2nd'
ORDER BY section_name, s.day_of_week, s.time_start
LIMIT 20;  -- Show first 20 entries as sample