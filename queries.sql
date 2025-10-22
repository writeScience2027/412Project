-- need INSERT, DELETE, UPDATE, and SELECTION QUERIES


-- list all the checked out books and who borrowed them
SELECT * 
  FROM checkedOut;

-- view all books from a certain genre
SELECT * 
  FROM book
  WHERE genre = 'Fantasy';

-- view all books a certain reader has checked out
SELECT chout.userID as name, 
  bk.title, 
  bk.author,
  chout.dueDate,
  chout.isOverdue
  FROM checkedOut chout
    JOIN book bk ON chout.isbn = bk.isbn
  WHERE chout.userID = 'r_alex';

-- view all the books from one author and how many are available
SELECT author, title, numAvailable
  FROM book
  WHERE author = 'J.K. Rowling' ; 

-- view who all checkeout out one book by name and title

SELECT chout.userID, 
  bk.title, 
  chout.borrowDate as borrowedOn
  FROM checkedOut chout
    JOIN book bk on chout.isbn = bk.isbn
  WHERE
    bk.title = 'Guns, Germs, and Steel';

-- what books did one librarian add
SELECT st.userID,
  bk.title,
  st.added as "added_on", st.removed as "removed_on"
  FROM status st
    JOIN book bk ON st.isbn = bk.isbn
  WHERE st.userID = 'l_morgan';

-- add queries about librarians:
  -- add a book as a librarian
INSERT INTO book (isbn, title, author, genre, audienceAge, releaseYear, totalQuantity, numAvailable) VALUES
  (123000321, 'Percy Jackson and the Lightning Thief', 'Rick Riordan', 'Fantasy', 12, 2005, 5, 5);

INSERT INTO status (userID, isbn, added, removed) VALUES
  ('l_morgan', 123000321, '2025-10-17', NULL);

  -- remove book as a specific librarian
UPDATE status SET removed = '2025-10-23'
WHERE userID = 'l_morgan' AND  isbn = 123000321;

  --delete book as a specific librarian
DELETE FROM status WHERE isbn = 123000321;
DELETE FROM book   WHERE isbn = 123000321;


-- update a record when a reader returns a book
UPDATE checkedOut SET returnDate = CURRENT_DATE
WHERE userID = 'r_alex' AND  isbn = 100000001;

