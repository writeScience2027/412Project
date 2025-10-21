# CSE 412 Database Project

## Overview
This project implements a **Library Management System** using **PostgreSQL**, demonstrating the core phases of relational database design:
1. **ER-to-Relational Mapping** (`schema.sql`)
2. **Data Population** (`data.sql`)
3. **Query Demonstration** (`queries.sql`)

Together, they form a fully functional database that models a library’s users, books, and checkout activity.

---

## Files Included
| File | Description |
|------|--------------|
| **schema.sql** | Contains all `CREATE TABLE` statements that define the relational schema and constraints. |
| **data.sql** | Populates the tables with sample synthetic data for users, books, and transactions. |
| **queries.sql** | Includes SQL `SELECT`, `UPDATE`, `INSERT`, and `DELETE` statements to demonstrate system functionality. |
| **README.md** | Project setup and usage guide. |

---

## Setup Instructions

### Clone the Repository
``bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>

Start PostgreSQL

If running locally (e.g., through VS Code):

export PATH="/opt/homebrew/opt/postgresql@15/bin:${PATH}"
export PGPORT=8888
export PGHOST=/tmp
pg_ctl -D $HOME/db412 -o '-k /tmp' start

### Create a New Database

Only do this once:

createdb CSE412Project

### Connect to the Database
psql -d CSE412Project

5️### Run the Schema and Data Scripts

Inside the PostgreSQL console:

\i schema.sql
\i data.sql


You can verify successful setup by listing tables:

\dt

### Run Queries

To demonstrate functionality, run:

\i queries.sql

Example queries include:

 - Listing all overdue books and who borrowed them

 - Viewing all books available by genre or audience age

 - Checking the total number of books a reader currently has checked out

 - Updating a record when a reader returns a book
