--data.sql

\set ON_ERROR_STOP on

BEGIN;

TRUNCATE checkedOut, status, reader, librarian, book, users RESTART IDENTITY CASCADE;

INSERT INTO users (userID, password) VALUES
  ('r_alex',   'pw_alex_1'),
  ('r_bailey', 'pw_bailey_2'),
  ('r_cody',   'pw_cody_3'),
  ('r_dana',   'pw_dana_4'),
  ('l_morgan', 'pw_morgan_5'),
  ('l_sky',    'pw_sky_6'),
  ('l_taylor', 'pw_taylor_7');

INSERT INTO reader (userID, numBooksCheckedOut) VALUES
  ('r_alex',   0),
  ('r_bailey', 0),
  ('r_cody',   0),
  ('r_dana',   0);

INSERT INTO librarian (userID) VALUES
  ('l_morgan'),
  ('l_sky'),
  ('l_taylor');

INSERT INTO book (isbn, title, author, genre, audienceAge, releaseYear, totalQuantity, numAvailable) VALUES
  (100000001, 'Harry Potter and the Chamber of Secrets', 'J.K. Rowling', 'Fantasy', 12, 1998, 10, 10),
  (100000002, 'Harry Potter and the Sorcerer''s Stone',   'J.K. Rowling', 'Fantasy', 12, 1997,  6,  6),
  (100000003, 'The Catcher in the Rye',                   'J.D. Salinger','Fiction', 16, 1951,  5,  5),
  (100000004, 'To Kill a Mockingbird',                    'Harper Lee',   'Fiction', 14, 1960,  8,  8),
  (100000005, 'Fahrenheit 451',                           'Ray Bradbury', 'Sci-Fi',  14, 1953,  7,  7),
  (100000006, 'The Hobbit',                               'J.R.R. Tolkien','Fantasy',10, 1937,  9,  9),
  (100000007, 'Into Thin Air',                            'Jon Krakauer', 'Nonfiction',16, 1997, 4,  4),
  (100000008, 'The Odyssey',                              'Homer',        'Classics', 16, 1999,  3,  3),
  (100000009, 'Guns, Germs, and Steel',                   'Jared Diamond','Nonfiction',16, 1997,5,  5),
  (100000010, 'The Road',                                 'C. McCarthy',  'Fiction',  16, 2006, 6,  6),
  (100000011, 'Fluent Python',                            'L. Ramalho',   'Tech',     18, 2015, 3,  3),
  (100000012, 'Effective Java',                           'J. Bloch',     'Tech',     18, 2018, 3,  3),
  (100000013, 'Clean Code',                               'R.C. Martin',  'Tech',     18, 2008, 4,  4),
  (100000014, 'Design Patterns',                          'GoF',          'Tech',     18, 1994, 2,  2),
  (100000015, 'Designing Data-Intensive Applications',    'M. Kleppmann', 'Tech',     18, 2017, 2,  2);

INSERT INTO checkedOut (userID, isbn, borrowDate, dueDate, returnDate, isOverdue) VALUES
  ('r_alex',   100000001, CURRENT_DATE - INTERVAL '14 days', CURRENT_DATE - INTERVAL '1 day', NULL, TRUE),

  ('r_bailey', 100000006, CURRENT_DATE - INTERVAL '20 days', CURRENT_DATE - INTERVAL '6 days', CURRENT_DATE - INTERVAL '7 days', FALSE),

  ('r_cody',   100000004, CURRENT_DATE - INTERVAL '17 days', CURRENT_DATE - INTERVAL '3 days', NULL, TRUE),

  ('r_dana',   100000003, CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE - INTERVAL '16 days', CURRENT_DATE - INTERVAL '10 days', FALSE),

  ('r_alex',   100000009, CURRENT_DATE - INTERVAL '60 days', CURRENT_DATE - INTERVAL '46 days', CURRENT_DATE - INTERVAL '45 days', FALSE),
  ('r_bailey', 100000009, CURRENT_DATE - INTERVAL '44 days', CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE - INTERVAL '29 days', FALSE),
  ('r_cody',   100000009, CURRENT_DATE - INTERVAL '28 days', CURRENT_DATE - INTERVAL '14 days', CURRENT_DATE - INTERVAL '12 days', FALSE),

  ('r_bailey', 100000011, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '4 days',  NULL, FALSE),
  ('r_dana',   100000013, CURRENT_DATE - INTERVAL '8 days',  CURRENT_DATE + INTERVAL '6 days',  NULL, FALSE),
  ('r_cody',   100000010, CURRENT_DATE - INTERVAL '12 days', CURRENT_DATE + INTERVAL '2 days',  NULL, FALSE),

  ('r_alex',   100000010, CURRENT_DATE - INTERVAL '40 days', CURRENT_DATE - INTERVAL '26 days', CURRENT_DATE - INTERVAL '25 days', FALSE),
  ('r_dana',   100000002, CURRENT_DATE - INTERVAL '50 days', CURRENT_DATE - INTERVAL '36 days', CURRENT_DATE - INTERVAL '30 days', FALSE),

  ('r_alex',   100000012, CURRENT_DATE - INTERVAL '15 days', CURRENT_DATE - INTERVAL '1 day',   NULL, TRUE);

INSERT INTO status (userID, isbn, added, removed) VALUES
  ('l_morgan', 100000001, '2025-08-20', NULL),
  ('l_morgan', 100000002, '2025-08-21', NULL),
  ('l_sky',    100000006, '2025-08-22', NULL),
  ('l_taylor', 100000011, '2025-08-23', NULL),
  ('l_taylor', 100000013, '2025-08-24', NULL);

WITH active AS (
  SELECT isbn, COUNT(*)::INT AS active_loans
  FROM checkedOut
  WHERE returnDate IS NULL
  GROUP BY isbn
)
UPDATE book b
SET numAvailable = GREATEST(b.totalQuantity - COALESCE(a.active_loans, 0), 0)
FROM active a
WHERE b.isbn = a.isbn;

UPDATE book b
SET numAvailable = b.totalQuantity
WHERE NOT EXISTS (
  SELECT 1 FROM checkedOut co
  WHERE co.isbn = b.isbn AND co.returnDate IS NULL
);

UPDATE reader r
SET numBooksCheckedOut = COALESCE(sub.cnt, 0)
FROM (
  SELECT userID, COUNT(*)::INT AS cnt
  FROM checkedOut
  WHERE returnDate IS NULL
  GROUP BY userID
) AS sub
WHERE r.userID = sub.userID;

UPDATE reader
SET numBooksCheckedOut = 0
WHERE userID NOT IN (
  SELECT DISTINCT userID FROM checkedOut WHERE returnDate IS NULL
);

COMMIT;
