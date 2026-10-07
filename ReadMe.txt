PostgreSQL 
-----------
DB
---
CREATE DATABASE Company_Db;

TABLE
-----

CREATE TABLE employees
(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    designation VARCHAR(100) NOT NULL,
    salary NUMERIC(12,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    street VARCHAR(150),
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10)
);

# ----------------------------------------

Overall Architecture
---------------------
Client
   │
   ▼
FastAPI Router
   │
   ▼
Pydantic Request Schema
   │
   ▼
Service Layer
   │
   ▼
Repository Layer
   │
   ▼
Psycopg 3 Async
   │
   ▼
PostgreSQL

--------------------------------------

PythonFasApiPydantic - Folder Structure
----------------------------------------
PythonFasApiPydantic/
│
├── .env
├── main.py
├── config.py
├── database.py
│
├── models/
│   ├── __init__.py
│   └── employee_model.py
│
├── schemas/
│   ├── __init__.py
│   └── employee_schema.py
│
├── repositories/
│   ├── __init__.py
│   └── employee_repository.py
│
├── services/
│   ├── __init__.py
│   └── employee_service.py
│
└── routers/
    ├── __init__.py
    └── employee_router.py

------------------------------------------

Commands:

> python -m venv .venv
### Installation -- Use the virtual environment

> python -m pip install fastapi "uvicorn[standard]" "psycopg[binary]" python-dotenv email-validator

Activate it:

.\.venv\Scripts\Activate.ps1

You should see:

(.venv) PS D:\...\PythonFastApiPydantic>


NOTE : For async PostgreSQL connections, psycopg 3 is used.

# -------------------------------


python -m uvicorn main:app --reload

> Run your application in the Swagger 
http://127.0.0.1:8000/docs 


# ------------------------------------

API End Points
----------------
| Method | URL                                      | Purpose    |
| ------ | ---------------------------------------- | ---------- |
| GET    | `/api/employees/`                        | Get all    |
| GET    | `/api/employees/?department=Development` | Get/filter |
| GET    | `/api/employees/101`                     | Get one    |
| POST   | `/api/employees/`                        | Insert     |
| PUT    | `/api/employees/101`                     | Update     |
| DELETE | `/api/employees/101`                     | Delete     |


