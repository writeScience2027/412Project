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

## Database Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/writeScience2027/412Project.git
cd 412Project
```

### 2. Install PostgreSQL

Download and install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)

### 3. Create Python Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Python Dependencies
```bash
pip install flask psycopg2-binary python-dotenv
```

### 5. Configure Database Connection

Create a `.env` file in the project root:
```env
cat > .env << 'EOF'
PGDATABASE=CSE412Project (Mac is case sensitive, so do cse412project)
PGUSER=postgres (Replace with your PostgreSQL username)
PGPASSWORD=your_postgres_password (Replace with your actual PostgreSQL password)
PGHOST=localhost
PGPORT=5432
EOF
```

### 6. Initialize the Database

> [!NOTE]
> If on a Mac and have brew installed, run `brew services start postgresql@15` before running the following commands. It ensures that they are successful.

```bash
# Create database
psql -U postgres -c "CREATE DATABASE CSE412Project;"

# Load schema
psql -U postgres -d CSE412Project -f schema.sql

# Load sample data
psql -U postgres -d CSE412Project -f data.sql
```

### 7. Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`
