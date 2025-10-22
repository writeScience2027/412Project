-- need INSERT, DELETE, UPDATE, and SELECTION QUERIES


-- list all the checked out books and who borrowed them
SELECT * 
  FROM checkedOut;

-- view all books from a certain genre
SELECT * 
  FROM book
  WHERE genre = 'Fantasy';

-- view all books a certain reader has checked out
SELECT checkedout.userID as name, 
  book.title, 
  book.author,
  checkedOut.dueDate,
  checkedOut.isOverdue
  FROM checkedOut 
    JOIN book ON checkedOut.isbn = book.isbn
  WHERE checkedOut.userID = 'r_alex';

-- view all the books from one author and how many are available
SELECT author, title, numAvailable
  FROM book
  WHERE author = 'J.K. Rowling' ; 

-- view who all checkeout out one book by name and title

SELECT checkedOut.userID, 
  book.title, 
  checkedOut.borrowDate as borrowedOn
  FROM checkedOut
    JOIN book on checkedOut.isbn = book.isbn
  WHERE
    book.title = 'Guns, Germs, and Steel';

-- what books did one librarian add
SELECT status.userID,
  book.title,
  status.added as data_added
  FROM status
    JOIN book ON status.isbn = book.isbn
  WHERE userID = 'l_morgan';

-- add queries about librarians

-- update a record when a reader returns a book


