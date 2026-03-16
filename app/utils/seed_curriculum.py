"""
seed_curriculum.py — Seed the BSIT curriculum, students, enrollments & mock grades.

⚠️  ALL GRADES ARE MOCK DATA — randomly generated for demonstration purposes.
    They do not reflect actual student performance.

Usage:  flask seed-curriculum
"""

import random
import click
from datetime import datetime, timezone

from app.extensions import db
from app.models.subject import Subject
from app.models.student import Student
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.models.academic_settings import AcademicSettings

# ═══════════════════════════════════════════════════════════════════════════════
#  CURRICULUM DATA  —  keyed by (year_level, semester)
#  Each entry: (subject_code, subject_title, units)
# ═══════════════════════════════════════════════════════════════════════════════

CURRICULUM = {
    # ── First Year, 1st Semester ──────────────────────────────────────────────
    (1, '1st'): [
        ('IT1101',     'Introduction to Computing',                       3),
        ('IT1102',     'Computer Programming 1',                          3),
        ('IT1103',     'Human-Computer Interaction',                      3),
        ('GEC1101',    'Understanding the Self',                          3),
        ('GEC1102',    'The Contemporary World',                          3),
        ('GEC1103',    'Purposive Communication',                         3),
        ('PATHFIT1',   'Movement Competency Training',                    2),
        ('NSTP1',      'National Service Training Program 1',             3),
    ],
    # ── First Year, 2nd Semester ──────────────────────────────────────────────
    (1, '2nd'): [
        ('IT1204',     'Computer Programming 2',                          3),
        ('IT1205',     'Data Structures and Algorithms',                  3),
        ('IT1206',     'Digital Logic and Design',                        3),
        ('ITPE1207',   'Platform Technologies',                           3),
        ('GEC1204',    'Readings in Philippine History',                  3),
        ('GEC1205',    'Mathematics in the Modern World',                 3),
        ('PATHFIT2',   'Exercise-Based Fitness Activities',               2),
        ('NSTP2',      'National Service Training Program 2',             3),
    ],

    # ── Second Year, 1st Semester ─────────────────────────────────────────────
    (2, '1st'): [
        ('IT2108',     'Fundamentals of Database System',                 3),
        ('IT2109',     'Computer Networking 1',                           3),
        ('IT2110',     'Discrete Mathematics',                            3),
        ('IT2111',     'Computer Hardware Maintenance and Troubleshooting', 3),
        ('ITPE2113',   'Object Oriented Programming',                     3),
        ('GEC2107',    'Science, Technology, and Society',                 3),
        ('PATHFIT3',   'Dance',                                           2),
    ],
    # ── Second Year, 2nd Semester ─────────────────────────────────────────────
    (2, '2nd'): [
        ('IT2214',     'Information Management',                          3),
        ('IT2215',     'Method of Research in IT',                        3),
        ('IT2216',     'Computer Networking 2',                           3),
        ('IT2217',     'Integrative Programming and Technologies 1',      3),
        ('GEE2201',    'People and Earth Ecosystems',                     3),
        ('GEM2201',    'Life and Works of Rizal',                         3),
        ('PATHFIT4',   'Sports',                                          2),
    ],

    # ── Third Year, 1st Semester ──────────────────────────────────────────────
    (3, '1st'): [
        ('IT3119',     'Advanced Database Management System',             3),
        ('IT3120',     'System Integration and Architecture (SIA)',       3),
        ('IT3121',     'Application Development & Emerging Technologies', 3),
        ('IT3122',     'Quantitative Methods with Statistics & Simulation', 3),
        ('ITPE3124',   'Web Systems Technologies',                        3),
        ('GEE3101',    'Gender and Society',                              3),
        ('GEE3102',    'The Entrepreneurial Mind',                        3),
    ],
    # ── Third Year, 2nd Semester ──────────────────────────────────────────────
    (3, '2nd'): [
        ('IT3225',     'Information Assurance and Security 1',            3),
        ('IT3226',     'Capstone Project 1',                              3),
        ('ITPE3227',   'Integrative Programming and Technologies 2',      3),
        ('GEE3205',    'Reading Visual Arts',                             3),
        ('GEC3208',    'Ethics',                                          3),
    ],

    # ── Fourth Year, 1st Semester ─────────────────────────────────────────────
    (4, '1st'): [
        ('IT4130',     'Systems Administration and Maintenance',          3),
        ('IT4131',     'Information Assurance & Security 2',              3),
        ('IT4132',     'Capstone Project 2',                              3),
        ('IT4133',     'Social and Professional Issues in IT w/ Seminar', 3),
        ('GEC2108',    'Art Appreciation',                                3),
    ],
    # ── Fourth Year, 2nd Semester ─────────────────────────────────────────────
    (4, '2nd'): [
        ('IT4134',     'On-the-Job Training w/ Report (500hrs)',          6),
    ],
}

# ─── Specialization Subjects (ITAS) ──────────────────────────────────────────
# Track mapping per section is applied during enrollment, not stored here.

ITAS_SUBJECTS = {
    # ── Web & Mobile Track ────────────────────────────────────────────────────
    'WM': {
        (2, '1st'): ('ITAS2112-WM', 'ITAS 1: Network Programming',             3),
        (2, '2nd'): ('ITAS2218-WM', 'ITAS 2: iOS/iPhone Programming',           3),
        (3, '1st'): ('ITAS3123-WM', 'ITAS 3: Android Programming',              3),
        (3, '2nd'): [
            ('ITAS3228-WM', 'ITAS 4: Client-Side Web Development',              3),
            ('ITAS3229-WM', 'ITAS 5: Server-Side Web Development',              3),
        ],
    },
    # ── Networking Track ──────────────────────────────────────────────────────
    'NET': {
        (2, '1st'): ('ITAS2112-NET', 'ITAS 1: Data & Digital Communications',   3),
        (2, '2nd'): ('ITAS2218-NET', 'ITAS 2: Network Security',                3),
        (3, '1st'): ('ITAS3123-NET', 'ITAS 3: Tools Development',               3),
        (3, '2nd'): [
            ('ITAS3228-NET', 'ITAS 4: Cyber Operations',                        3),
            ('ITAS3229-NET', 'ITAS 5: Security Law',                            3),
        ],
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION → SPECIALIZATION TRACK MAPPING
# ═══════════════════════════════════════════════════════════════════════════════

SECTION_TRACK = {
    'BSIT-1A': None,  'BSIT-1B': None,  'BSIT-1C': None,
    'BSIT-2A': 'WM',  'BSIT-2B': 'WM',
    'BSIT-2C': 'NET', 'BSIT-2D': 'NET',
    'BSIT-3A': 'WM',  'BSIT-3B': 'WM',  'BSIT-3C': 'WM',
    'BSIT-3D': 'NET', 'BSIT-3E': 'NET',
    'BSIT-4A': None,  'BSIT-4B': None,
}

# ═══════════════════════════════════════════════════════════════════════════════
#  STUDENT ROSTER  —  keyed by (section, gender)
# ═══════════════════════════════════════════════════════════════════════════════

STUDENTS = {
    # ── BSIT 1A ───────────────────────────────────────────────────────────────
    ('BSIT-1A', 'Male'): [
        'Callisen, Jhon Patrick', 'Dayot, Jaypee', 'Dolendo, Yonglek',
        'Galeno, Chad Norvic', 'Gumbam, Jhon Jhyril', 'Jallorina, Kent Gerald',
        'Kaindoy, Bernald Gian', 'Lopez, Shane Jan', 'Lorenzo, James Renz',
        'Mallorca, Gerald', 'Parcon, Prance Wann', 'Pastolero, Rowee',
        'Porras, Khenny Jay', 'Puig, Daren', 'Salo, Gian', 'Siva, Sherman',
    ],
    ('BSIT-1A', 'Female'): [
        'Asung, Ashley Nicole', 'Blanza, Kate', 'Constantinopla, Glenda',
        'Dairo, Charmae', 'Daprinal, Jewel', 'Daquita, Dezza May',
        'Dela Cruz, Roxane', 'Dela Fuente, Jocel', 'Figueroa, Saedell Rovian',
        'Garcia, Keysha Joy', 'Lebaquin, Darlyn Mae', 'Mallorca, Angel Grace',
        'Millan, Erica', 'Parcia, Lianne', 'Patingo, Hannah Paulina',
        'Quicoy, Darlen', 'Romaldo, Christine',
        'Salvadico, Ashley Jonnah Salvie', 'Senosa, Gin Marie',
    ],

    # ── BSIT 1B ───────────────────────────────────────────────────────────────
    ('BSIT-1B', 'Male'): [
        'Anorico, John Leeban L.', 'Aujero, Vince A.', 'Bedrijo, Kyle Weindel M.',
        'Bete, Christian C.', 'Carisma, Leex T.', 'Dagohoy, Alester M.',
        'Delamores, Karl M.', 'Gelladuga, Josh I.', 'Guanga, Xeus A.',
        'Jaleco, Michael D.', 'Lavadia, Carl Alvin L.', 'Lazarito, Jovan A.',
        'Lozada, John Ralph R.', 'Magno, Marion Jay C.', 'Palma, Rene John T.',
        'Patubo, Janloyd T.', 'Petisme, Andro Renz D.', 'Rios, John Lorence L.',
        'Sendico, John Paul C.', 'Somblingo, Cedric James A.',
        'Villanueva, Jamir D.',
    ],
    ('BSIT-1B', 'Female'): [
        'Anorico, Kyla Marie G.', 'Ceballos, Krisziel Jean S.',
        'Delideli, April Hazel B.', 'Diaz, Abcdee P.',
        'Doloroso, Arnela Elra P.', 'Dumio, Adrianna Brenn D.',
        'Escrebano, J-Ann M.', 'Habetacion, Antonnete G.', 'Jasulin, Joy M.',
        'Ladoing, Jamie P.', 'Lagayao, Virgie Mae S.', 'Lazo, Asley Faith L.',
        'Mendoza, Gebelle P.', 'Parreño, Krae Cielle L.',
        'Provido, Rechie Mae P.', 'Segaya, Marian Belle A.',
        'Soriano, Richel Joy C.',
    ],

    # ── BSIT 1C ───────────────────────────────────────────────────────────────
    ('BSIT-1C', 'Male'): [
        'Abello, Geger', 'Cachopero, Mark Ebenezer', 'Codera, Clarence Ian',
        'Collado, Michael Ian', 'Dasmariñas, Jayvie', 'Daza, Joren Clark',
        'Locsin, Jasper', 'Melancho, Sedric Raphael', 'Olido, Kenneth',
        'Ortiz, Vince Roger', 'Reyes, John Rio', 'Sioco, Joeryl',
        'Supresencia, Kit Joey', 'Suya, Rens', 'Vargas, Dandreb',
        'Zamora, Joel',
    ],
    ('BSIT-1C', 'Female'): [
        'Anecita, Liezel', 'Daig, Mariane', 'Doquiza, Rezshel Mae',
        'Ewayan, Jane', 'Flores, Julia Rica', 'Glaiz, Jelian',
        'Guzman, Jayce Lyn', 'Landero, Nicole', 'Laurea, Mikyla',
        'Lingaya, Lea Clarize', 'Maderse, Rhyzia Mae', 'Paparon, Shaney Mary',
        'Plaga, Lorlyn', 'Quinlat, Mariel', 'Salveron, Sarah Jean',
    ],

    # ── BSIT 2A ───────────────────────────────────────────────────────────────
    ('BSIT-2A', 'Male'): [
        'Amonoy, Dave', 'Berja, Justine', 'Canastra, Jhon Clark',
        'Casuyon, Gabby', 'Catalan, Sean Fredrick', 'Dagohoy, Kenth',
        'Daguro, Julito', 'Dato-on, John Paul', 'Dolendo, Nathaniel',
        'Flores, Rey Jolar', 'Lagamon, Kaizer', 'Latumbo, Ken Jay',
        'Ortizo, Paul John', 'Pangantihon, Jhan Symel', 'Pelagio, Gilbert',
        'Percia, Cel John', 'Quimba, Wilfred', 'Sibigan, Cyrex',
        'Siva, Josh', 'Sugano, John Lloyd', 'Tanquerido, Eron',
        'Villamor, Jhon Paul',
    ],
    ('BSIT-2A', 'Female'): [
        'Anecita, Jeslaine', 'Aspera, Marivell', 'Calde, Clares',
        'Clavines, Jewel Mae', 'Cuentro, Althea Mae', 'Dangautan, Leah Jane',
        'Dato-on, Angel Trecia', 'Dela Cruz, Eleza Mae', 'Dela Cruz, Killy',
        'Dequiso, Jelan', 'Donasco, Kiezil Joeve',
        'Fabillo, Kathleen Loraine', 'Gajeto, Roda', 'Hechanova, Hope Joy',
        'Lubas, Mrytel Abigael', 'Magno, Angelica', 'Montinola, Angel',
        'Notada, Regine', 'Palorma, Kristine', 'Pentojo, Eden',
        'Sayosa, Ysmien', 'Tipo, Rowela Marie',
    ],

    # ── BSIT 2B ───────────────────────────────────────────────────────────────
    ('BSIT-2B', 'Male'): [
        'Abiday, Von Axzll Loise Donguines',
        'Amoto, John Mickel Abraham',
        'Bandejas, Phryxus Antonio Dela Cerna',
        'Beboso, Christian Helarion Patroncio',
        'Bolima, Alfred Jumabong',
        'Calambro, Romel Bata-Anon',
        'Calzadora, Romil Victoriano',
        'Carias, Paul Lawrence Peña',
        'Catunao, Erwin Lagundo',
        'Dalde, Ken Mark Baylon',
        'Dayatan, Chris Ivan Delos-Santos',
        'La-Anan, Cyrich John Padasas',
        'Lazarito, Jovan Alvero',
        'Luriosa, John Vonh Tingzon',
        'Pacifico, Kenneth Sarceña',
        'Paquingan, William Hari-On',
        'Perez, Christian De Leon',
        'Portugues, Ryan Richard Todavia',
        'Rigor, Allen Sheen Cabayao',
        'Sugano, Juney Leonida',
        'Zabala, Nelson',
    ],
    ('BSIT-2B', 'Female'): [
        'Baroma, Allea Fabiáña',
        'Canones, Aaliyah Mae Misterio',
        'Cordero, Angel Padernal',
        'Danócup, Karen Pelarin',
        'De La Fuente, Shane Bandillon',
        'De La Peña, Julia Nicole Bigayan',
        'Diacuna, Divine Grace Labus',
        'Dumalogdog, Haily Nicole Escobin',
        'Figueroa, Eden Grace Na',
        'Galapon, Jhunalea Grace Perono',
        'Jinon, Sarah Joy Dequillo',
        'Laudato, Ellen Joy Del Rosario',
        'Lazarito, Lyka Rose Pacularea',
        'Macahilo, Sheina Lyn Mascarinas',
        'Magbanua, Lee Anne Degones',
        'Malones, Prences Fernandez',
        'Narboneto, Mary Grace Rendon',
        'Pacheco, Christine Nicole Pendon',
        'Panes, Jhane Zaragoza',
        'Penuela, Michelle Jane Nolasco',
        'Perono, Liana Heart Carpio',
        'Precia, Jeziel Ann Madrid',
        'Provenido, Syla Jane Ladingin',
        'Siva, Jeill Dao-Ang',
        'Tolentino, Kyanna Rose Pamaong',
        'Torres, Zara Jean De La Cruz',
    ],

    # ── BSIT 2C ───────────────────────────────────────────────────────────────
    ('BSIT-2C', 'Male'): [
        'Acuesta, John Aries',
        'Barbero, Xyzine D.',
        'Cabayao, Jade Andre C.',
        'Carisma, Jan Rex T.',
        'Catunao, John Rey D.',
        'Dadal, Rian Nikko A.',
        'Dañucop, Aldrin G.',
        'Delideli, Jev Leonard L.',
        'Gemina, Benjamin Jr. M.',
        'Getulle, John Kennery C.',
        'Macahilo, Marky P.',
        'Muyco, John Lee L.',
        'Pegante, John D.',
        'Perez, Jesry A.',
        'Puig, John David I.',
        'Pradas, Filger G.',
        'Sacramento, Jerome P.',
        'Sorongon, Khenji P.',
        'Suaga, Kendrick John P.',
        'Sumbilla, Bryle Jhon P.',
        'Tamayo, Fran D.',
        'Tarala, Louise Andrei L.',
    ],
    ('BSIT-2C', 'Female'): [
        'Antojado, Rosse Ann C.',
        'Aragones, Johanna D.',
        'Bedrejo, Shine',
        'Biñas, Tracy Ann',
        'Castillano, Amelia C.',
        'Dangaran, Gecyl Garcia',
        'Del Prado, Queenie A.',
        'Delatanid, Johanna Jean F.',
        'Dimaala, Ma. Beatriz Suelo',
        'Diorda, Jerilyn M.',
        'Dofeliz, Jovielyn P.',
        'Figueroa, Shemell A.',
        'Galgo, Amy M.',
        'Juliano, Tyrese Kyan C.',
        'Lozada, Geryll June V.',
        'Manuel, Jeany P.',
        'Niebla, Klye Eunice B.',
        'Notada, Shailen',
        'Osano, Erlyn Joy',
        'Paclibar, Renalyn G.',
        'Pareja, Triscia Ann L.',
        'Perero, Rosiel L.',
        'Siva, Shiela Marie S.',
    ],

    # ── BSIT 2D ───────────────────────────────────────────────────────────────
    ('BSIT-2D', 'Male'): [
        'Alejandro, Harold Jay', 'Asentista, Jerson', 'Cabrera, Jemuel',
        'Cajurao, Jhon Francies', 'Calimpay, Renmark', 'Casumpang, Rey',
        'Celiz, Ropear', 'Cordova, Lance', 'Daet, Kent Anthony',
        'Darroca, Jeffreel', 'Delobio, Jezreel', 'Gerona, Keith Adrian',
        'Labor, Leogen', 'Lozada, DJ', 'Neri, Kent Bryl',
        'Panes, John Paul', 'Peñarubia, Benz Macky', 'Piano, Ron Angelo',
        'Prondo, Florence', 'Soropia, Justine', 'Suprecencia, Rafgyric Kyle',
        'Vallenzuela, Adrian',
    ],
    ('BSIT-2D', 'Female'): [
        'Apellado, Michaella', 'Castillano, Killa Mae', 'Catolico, Shella',
        'Dagohoy, Lorieme', 'Daniel, Patricia Ann', 'Daquilanea, Zeny',
        'Dela Cruz, Laisa Joy', 'Delideli, Nova Rose',
        'Divinagracia, Mary Christ', 'Flores, Andrea Ross',
        'Gacayan, Alexis Marie', 'Gilbaliga, Jelly', 'Ladoing, Angel Kyp',
        'Lance, Diannie', 'Lazarito, Angela', 'Maduramente, Dannielle Jane',
        'Miag-ao, Rubylyn', 'Miranda, Ella Mae', 'Paez, Fritzy Joy',
        'Parreño, Claire Ann', 'Perio, Angel', 'Romaldo, Cherry',
        'Samsona, Jastine Anne', 'Somido, Edmarie', 'Villamor, Hazyl',
    ],

    # ── BSIT 3A ───────────────────────────────────────────────────────────────
    ('BSIT-3A', 'Male'): [
        'Acuesta, Beryl A. (Irregular)', 'Adia, Selwyn G.',
        'Arca, Jan Guiller J.', 'Cabayao, Rey Valen C.',
        'Cancino, MC Kenneth G.', 'Clarito, Jan Rholy S.',
        'Clavines, Mark Vincent M.', 'Cuachin, Franklin L.',
        'Da-anoy, Charles H.', 'Dacuscus, Jhon Lorence',
        'Derubio, Alfred P.', 'Diaz, Anthony D.',
        'Galelea, John Anthony H.', 'Galeno, Fritz Carl G.',
        'Hechanova, Jun Micheal D.', 'Hermonio, Ferdinand S.',
        'Labaco, Hanselljan A.', 'Lozada, John Anthony D.',
        'Ordanel, Kyle Raven G.', 'Panes, Clarenze S.',
        'Segaya, Jann Lenron D.', 'Sorongon, Jhon Llyod P.',
        'Yap, John Hejie S.',
    ],
    ('BSIT-3A', 'Female'): [
        'Acuesta, Norhy P.', 'Banas, Princes P.', 'Bayaban, Solemn Mia T.',
        'Biboso, Chary E.', 'Cabalfin, Rhesa B.', 'Calanao, Ana Marie D.',
        'Carumba, Corason C.', 'Daras, Hannah A.', 'Dayaday, Arah Mae',
        'Deronio, Fridea Grace C.', 'Diaz, Rychell Ann O.',
        'Figueroa, Nove Jane L.', 'Francelizo, Noemay Thyrn D.',
        'Gultiano, Glydelle Mae', 'Labrador, Arianne Mae L.',
        'Lasiog, Kaila Marie D.', 'Lopez, Renajean L.', 'Loria, Rechel N.',
        'Manderico, April D.', 'Miranda, Cyris Erika D.',
        'Palarisan, Kylle P.', 'Penaflorida, Jeanica M.',
        'Relator, Kate Russel L.', 'Sables, Jenelyn P.',
        'Solocoban, Kate R.', 'Toniacao, Elnie Joy D.',
    ],

    # ── BSIT 3B ───────────────────────────────────────────────────────────────
    ('BSIT-3B', 'Male'): [
        'Baroro, Lou Vincent J.', 'Calimotan, Karl F.',
        'Cantuba, Christian Paulo C.', 'Castillo, Jay R C.',
        'Cobrador, Jerolle N.', 'Depaclayon, James M.',
        'Duron, Frenzy Mar G.', 'Guiao, Jevie D.',
        'Ladoing, Sean Andre C.', 'Lagayao, Gel L.',
        'Linterna, Jay-r P.', 'Macahilo, Allyxis P.',
        'Martinez, Jeff Edrick G.', 'Oberio, Regodin P.',
        'Oberio, Rinz P.', 'Panila, Allyrey P.',
        'Perez, Chuquel P.', 'Sapin, Rodolfo Jr. P.',
        'Villafuerte, Ron Jhofil P.',
    ],
    ('BSIT-3B', 'Female'): [
        'Aguirre, Mary Charlyn L.', 'Amit, Shiene Mae M.',
        'Apresto, Therence Eunice L.', 'Bicodo, Katherine Anne B.',
        'De Fiesta, Daine B.', 'Denoman, Kyle Jasmine A.',
        'Descalsota, Shamy P.', 'Detore, Aime G.',
        'Espia, Jan Allysandra I.', 'Falalimpa, Lynden Joy I.',
        'Fernandez, Mary Camille D.', 'Fiel, Karen D.',
        'Gerona, Gee Ann Q.', 'Gumban, Clarieze Anne A.',
        'Lanado, Catherine L.', 'Lastimoso, Shinette C.',
        'Muro, Jiezel Mae C.', 'Notada, Joysie Ann T.',
        'Olido, Katherine B.', 'Pelaez, Roseby P.',
        'Peñaflorida, Kia Marie M.', 'Penuela, Kara Atena D.',
        'Perez, Kyla Marie M.', 'Simangca, Ashely Shassy P.',
    ],

    # ── BSIT 3C ───────────────────────────────────────────────────────────────
    ('BSIT-3C', 'Male'): [
        'Allas, Raffy D.', 'Cabanal, Manuel P.', 'Cabayao, Krylle A.',
        'Cabrera, Kenth Laurence M.', 'Calimpay, Remjun L.',
        'Comision, Ryan Jay C.', 'Daig, Martin Cloyd L.',
        'Daniel, Rolie Jr. M.', 'Dapat, Jan Christian D.',
        'Dumaraog, Dexter G.', 'Galan, Geryll A.',
        'Herran, Diego Francis P.', 'Magbanua, Karl D.',
        'Ordanel, Jimmy C.', 'Orio, Joshua D.',
        'Palorma, Artemio Jr. G.', 'Pasigna, Justine Ray S.',
        'Patena, Joshua A.', 'Peusca, Andie A.',
        'Porras, John Llyod B.', 'Rendon, Wayne Aldrin',
    ],
    ('BSIT-3C', 'Female'): [
        'Arinez, Trisha D.', 'Atonducan, Erna T.', 'Binal, Kia Mae G.',
        'Castillano, Arlene May C.', 'Castor, Izza Jane C.',
        'Celle, Thea Jean C.', 'Chavas, Ashley O.',
        'Dangautan, Christine Love A.', 'Dangautan, Lorraine Grace C.',
        'Dato-on, Hazel D.', 'Dobria, Anamae A.', 'Estribor, Berry Z.',
        'Gregorio, Diane Claire D.', 'Gumban, Ashrain B.',
        'Magbanua, Gina D.', 'Maligas, Mary Rose L.',
        'Nino, Jacky Lou', 'Salazar, Hannah Mae O.',
        'Sana, Rosalyn V.', 'Sebandra, Ju-ann B.',
        'Sumaribus, Jennirose P.', 'Viran, Bea C.',
    ],

    # ── BSIT 3D ───────────────────────────────────────────────────────────────
    ('BSIT-3D', 'Male'): [
        'Agramon, Lorenel P.', 'Aguirre, Bernardo Jr. S.',
        'Aujero, Christian A.', 'Bionat, Janzper Ivanne Jee R.',
        'Brillo, Carl Louie D.', 'Dangani, Ramuel D.',
        'Delsolor, Ceasar Ian C.', 'Dioglois, Lyndon Bryan B.',
        'Donasco, Vincent Jhay F.', 'Escovidal, Kent S.',
        'Estole, John Paul S.', 'Jamili, Eivon Genecis A.',
        'Jordan, Christian T.', 'Labaro, Jeiel B.',
        'Lagayao, Jeremi S.', 'Miclat, Ryan P.',
        'Muyco, Dickson H.', 'Onso, Vios Sam B.',
        'Palomado, Jeson B.', 'Panel, Christian Lee D.',
        'Panes, Leonardo M.', 'Pari-an, Clint Martin P.',
        'Porras, Marvin John Q.', 'Salazar, Jan Brent L.',
        'Samorillo, Andro G.',
    ],
    ('BSIT-3D', 'Female'): [
        'Amparo, Ana May J.', 'Baldevieso, Rocelyn S.',
        'De Asis, Mae S.', 'Despojo, Fennilin P.',
        'Donasco, Maribel E.', 'Joven, Reisha Gwyneth M.',
        'Lance, Geneva D.', 'Laroza, Louica Denn O.',
        'Lazarito, Heart A.', 'Mencede, Chela Mae M.',
        'Notada, Lorrean Ann H.', 'Pama, Daisy B.',
        'Perez, Janice L.', 'Quimod, Arianne Ricci D.',
        'Siva, Dona Jean C.', 'Siva, Krishel Ann S.',
        'Tino, Diana D.', 'Vicente, Laarnie A.',
    ],

    # ── BSIT 3E ───────────────────────────────────────────────────────────────
    ('BSIT-3E', 'Male'): [
        'Aujero, Zaldy Jr. Q.', 'Cordero, Nico P.',
        'Dalde, Benjie B.', 'Danitaras, Renjaen L.',
        'Deocampo, Sunny Jr. T.', 'Detore, John Mykelle A.',
        'Gelladuga, Jade I.', 'Herrera, Arjie Q.',
        'Isare, Chrisel John P.', 'Lamanero, Edwin E. III',
        'Laperme, Joemarie P.', 'Mabulay, Ednizon Joseph L.',
        'Muyco, Ken-Ken', 'Olores, Jackie D.',
        'Ortizo, Arwin L.', 'Palabrica, Hans L.',
        'Palma, AJ G.', 'Panila, Christian Rey P.',
        'Pelaez, Manuel Jr. D.', 'Pillo, John Michael Angelo N.',
        'Porras, Bryan Rey L.', 'Sables, Jeffrey O.',
        'Salva, Christian Jade J.', 'Santural, Arjay L.',
        'Suelo, Justine F.', 'Taladhay, Nestor Jr. E.',
        'Umadhay, Arby Jann S.', 'Villareal, John Madison L.',
        'Zerrudo, Novie John',
    ],
    ('BSIT-3E', 'Female'): [
        'Beboso, Annie T.', 'Cabello, Ma. Jeneca L.',
        'Daquita, Mae Joy S.', 'Diorda, Jaynie Rose G.',
        'Donasco, Joyce A.', 'Emboltura, Angel Rose P.',
        'Jagorin, Danica H.', 'Lamery, Elmie D.',
        'Lemor, Leyan B.', 'Notada, Kyle M.',
        'Pacardo, Mia B.', 'Salazar, Meryldin C.',
        'Ventura, Danica A.', 'Villalobos, Nicole J.',
    ],

    # ── BSIT 4A ───────────────────────────────────────────────────────────────
    ('BSIT-4A', 'Male'): [
        'Acuesta, Beryl', 'Albuna, Carlo', 'Araquil, Jaoro',
        'Bandillon, Michael', 'Cordero, Jhon Christian',
        'Corpuz, Christopher', 'Daguro, Joefe', 'Dazo, Mickent',
        'Deala, Wilanve', 'Dela Peña, Joshua Paolo',
        'Gallaza, Christian Paul', 'Galvan, Kevin John',
        'Glaiz, Rhyll Kian', 'Habunal, Kurt Russel',
        'Jara, Jemuel John', 'Labar, Kenth',
        'Ladores, Andre Miguel', 'Martinez, John Patrick',
        'Ortigoza, Edcil', 'Pedrajas, Ralph Russel',
        'Principe, Nikko Angelo', 'Romero, Kevin Justin',
        'Sables, Zyke Thomas', 'Sacatin, Rameces',
        'Silvestre, Louie Gee', 'Solde, Kervyn Fahr',
        'Sugano, Jameli', 'Yosores, Jemuel Van',
    ],
    ('BSIT-4A', 'Female'): [
        'Asturias, Rocell', 'Bionat, Mabienne', 'Calimpay, Jenie Ann',
        'Conejar, Ma. Nerry', 'Cordero, Cristil Ann', 'Daguro, Jessica',
        'Daig, Mary Jale', 'Dairo, Kiah Levie', 'Demon, Cyrene Paulen',
        'Dominguez, Nadine Faye', 'Escoton, Aleila Eunice',
        'Gonzales, Jelyn Suelo', 'Gumbao, Aleza', 'La-anan, Czyrine',
        'Magno, Evalyn', 'Pagulong, Liezel', 'Pagunsan, Norlyn',
        'Pecayo, Jenelyn', 'Peñarubia, Gladly', 'Petisme, Krizzia Ann',
    ],

    # ── BSIT 4B ───────────────────────────────────────────────────────────────
    ('BSIT-4B', 'Male'): [
        'Amosco, Kenneth', 'Arquiola, Joshua', 'Billona, Geolf Brye',
        'Brillantes, Rodolfo', 'Celo, Jay', 'Chavez, Christian',
        'Dabi, Kennedy', 'Danugrao, Ranrey', 'Dapat, Dion Henrick',
        'Dayandayan, Marvin', 'Dela Cruz, Rezy John', 'Detore, Marino',
        'Flandez, Dendo Paul', 'Gandecela, Bon', 'Labaro, Christian Ajie',
        'Leysa, Kenneth John', 'Licuran, Aisaiah James', 'Macapaz, Jojen',
        'Maestral, John Romar', 'Miranda, Peter', 'Nacion, Jeffrey',
        'Paches, Xyle', 'Pagurayan, Carl Gerald', 'Palabrica, Reubert',
        'Paparon, Dy-Jay', 'Pontero, Andrei Jerhan', 'Poral, Rj',
        'Tingzon, Joshua',
    ],
    ('BSIT-4B', 'Female'): [
        'Aguisanda, Lovely', 'Bariguez, Pharlyn', 'Batoon, Jasmine Joy',
        'Bautista, Mariela', 'Castor, Jasha Luwis', 'Delideli, Noelyn',
        'Francelizo, Noereen', 'Linterna, Erica', 'Naparete, Leizl',
        'Osorio, Ruby Mae', 'Pelegrino, Rica', 'Perez, Christy',
        'Peñamayor, Marian', 'Saynes, Pamela', 'Victorian, Kristen',
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
#  MOCK GRADE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

VALID_GRADES = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0]
FAIL_GRADES = [5.0]

# Weighted so most students pass with decent grades (bell-curved towards 1.75–2.5)
GRADE_WEIGHTS = [5, 8, 12, 18, 22, 15, 10, 6, 4]


def _random_grade():
    """Generate a random grade weighted toward passing (Philippine scale)."""
    roll = random.random()
    if roll < 0.02:     # 2% chance INC
        return None, 'INC'
    if roll < 0.05:     # 3% chance of 5.0 (FAILED)
        return 5.0, None
    grade = random.choices(VALID_GRADES, weights=GRADE_WEIGHTS, k=1)[0]
    return grade, None


# ═══════════════════════════════════════════════════════════════════════════════
#  SEED FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def seed_subjects():
    """Insert all curriculum subjects. Skips duplicates by subject_code."""
    created = 0
    skipped = 0

    # Core subjects from the main curriculum
    for (year_level, semester), subjects in CURRICULUM.items():
        for code, title, units in subjects:
            existing = Subject.query.filter_by(subject_code=code).first()
            if existing:
                skipped += 1
                continue
            db.session.add(Subject(
                subject_code=code,
                subject_title=title,
                units=units,
                department='CICT',
            ))
            created += 1

    # Specialization (ITAS) subjects from both tracks
    for track_name, track_data in ITAS_SUBJECTS.items():
        for (year_level, semester), subject_or_list in track_data.items():
            entries = subject_or_list if isinstance(subject_or_list, list) else [subject_or_list]
            for code, title, units in entries:
                existing = Subject.query.filter_by(subject_code=code).first()
                if existing:
                    skipped += 1
                    continue
                db.session.add(Subject(
                    subject_code=code,
                    subject_title=title,
                    units=units,
                    department='CICT',
                ))
                created += 1

    db.session.commit()
    click.echo(f'  📚 Subjects: {created} created, {skipped} already existed.')
    return created


def _section_to_year(section: str) -> int:
    """Extract year level from section string like BSIT-2A → 2."""
    digit = section.replace('BSIT-', '')[0]
    return int(digit)


def seed_students():
    """Insert all students from the roster. Skips duplicates by student_id."""
    created = 0
    skipped = 0
    sid_counter = 1  # running counter for student_id generation

    for (section, gender), names in sorted(STUDENTS.items()):
        year_level = _section_to_year(section)
        for name in names:
            # Generate a deterministic student_id: e.g. 2025-0001
            student_id = f'2025-{sid_counter:04d}'
            sid_counter += 1

            existing = Student.query.filter_by(student_id=student_id).first()
            if existing:
                skipped += 1
                continue

            # Also check by full_name + section to avoid true duplicates
            name_exists = Student.query.filter_by(
                full_name=name, section=section
            ).first()
            if name_exists:
                skipped += 1
                continue

            db.session.add(Student(
                user_id=None,  # No auth account — admin assigns later
                student_id=student_id,
                full_name=name,
                section=section,
                gender=gender,
                year_level=year_level,
                curriculum_year='2025-2026',
            ))
            created += 1

    db.session.commit()
    click.echo(f'  👩‍🎓 Students: {created} created, {skipped} already existed.')
    return created


def seed_enrollments_and_grades():
    """
    For each student, enroll them in the subjects matching their year level.
    Then assign random mock grades to each enrollment.
    Commits in per-student batches for performance with remote databases.
    """
    academic_year = '2025-2026'
    now = datetime.now(timezone.utc)

    enroll_count = 0
    grade_count = 0
    skipped = 0

    students = Student.query.filter(
        Student.curriculum_year == '2025-2026'
    ).all()

    # Pre-load subject lookup
    subject_map = {s.subject_code: s for s in Subject.query.all()}

    # Pre-load existing enrollments to avoid per-row queries
    existing_enrollments = set()
    for e in Enrollment.query.filter_by(academic_year=academic_year).all():
        existing_enrollments.add((e.student_id, e.subject_id, e.semester))

    total = len(students)
    for idx, student in enumerate(students, 1):
        year_level = student.year_level or 1
        section = student.section or ''
        track = SECTION_TRACK.get(section)
        pending_enrollments = []

        for semester in ['1st', '2nd']:
            # Core subjects for this year/semester
            core_key = (year_level, semester)
            core_subjects = CURRICULUM.get(core_key, [])

            # ITAS subjects for this year/semester (if applicable)
            itas_entries = []
            if track and track in ITAS_SUBJECTS:
                track_data = ITAS_SUBJECTS[track].get(core_key)
                if track_data:
                    if isinstance(track_data, list):
                        itas_entries = track_data
                    else:
                        itas_entries = [track_data]

            all_subjects = [(c, t, u) for c, t, u in core_subjects] + \
                           [(c, t, u) for c, t, u in itas_entries]

            for code, title, units in all_subjects:
                subj = subject_map.get(code)
                if not subj:
                    continue

                # Check if enrollment already exists (in-memory set)
                key = (student.id, subj.id, semester)
                if key in existing_enrollments:
                    skipped += 1
                    continue

                enrollment = Enrollment(
                    student_id=student.id,
                    subject_id=subj.id,
                    semester=semester,
                    academic_year=academic_year,
                )
                db.session.add(enrollment)
                pending_enrollments.append(enrollment)
                existing_enrollments.add(key)
                enroll_count += 1

        # Flush once per student to get all enrollment IDs
        if pending_enrollments:
            db.session.flush()

            # Create grades for all new enrollments
            for enrollment in pending_enrollments:
                grade_val, remarks = _random_grade()
                grade = Grade(
                    enrollment_id=enrollment.id,
                    grade_value=grade_val,
                    remarks=remarks,
                    date_encoded=now,
                    encoded_by_id=None,  # System-generated mock data
                )
                db.session.add(grade)
                grade_count += 1

        # Commit every 50 students to keep transactions manageable
        if idx % 50 == 0:
            db.session.commit()
            click.echo(f'    ... processed {idx}/{total} students')

    db.session.commit()
    click.echo(f'  📝 Enrollments: {enroll_count} created, {skipped} already existed.')
    click.echo(f'  📊 Mock Grades: {grade_count} generated.')
    return enroll_count, grade_count


def seed_all():
    """Run the full curriculum seed pipeline."""
    click.echo('')
    click.echo('═' * 60)
    click.echo('  ⚠️  CICT GRADE PORTAL — MOCK DATA SEEDER')
    click.echo('  All grades are RANDOMLY GENERATED for demo purposes.')
    click.echo('  They do NOT reflect actual student performance.')
    click.echo('═' * 60)
    click.echo('')

    # Update AcademicSettings to 2025-2026
    settings = AcademicSettings.get_current()
    if settings.current_year != '2025-2026':
        settings.current_year = '2025-2026'
        db.session.commit()
        click.echo('  ⚙️  Academic Year updated to 2025-2026')

    click.echo('  [1/3] Seeding subjects...')
    seed_subjects()

    click.echo('  [2/3] Seeding students...')
    seed_students()

    click.echo('  [3/3] Seeding enrollments & mock grades...')
    seed_enrollments_and_grades()

    click.echo('')
    click.echo('  ✅ Seed complete!')
    click.echo('  ⚠️  Remember: ALL projected grades are MOCK DATA.')
    click.echo('═' * 60)
    click.echo('')
