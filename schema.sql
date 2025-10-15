CREATE TABLE users (
    userID varchar(50) primary key,
    password varchar(50) NOT NULL UNIQUE 
);

CREATE TABLE reader (
    userID varchar(50) references users(userID),
    numBooksCheckedOut int NOT NULL
);

CREATE TABLE librarian (
    userID varchar(50) references users(userID)
);

CREATE TABLE book (
    numAvailable int,
    title varchar(500),
    author varchar(50),
    genre varchar(50),
    audienceAge int,
    releaseYear int,
    totalQuantity int,
    isbn int primary key
);

CREATE TABLE checkedOut (
    userID varchar(50) references users(userID),
    isbn int references book(isbn),
    isOverdue boolean,
    returnDate date,
    dueDate DATE DEFAULT CURRENT_DATE + INTERVAL '30 days',
    borrowDate DATE DEFAULT CURRENT_DATE
);

-- not too sure if this should be its own table or somehow merged into an existing one
CREATE TABLE status (
    userID varchar(50) references users(userID),
    isbn int references book(isbn),
    added varchar(50),
    removed varchar(50)
);