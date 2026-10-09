PostgreSQL 
-----------
Department table
------------------
CREATE TABLE departments
(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(250),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

INSERT INTO departments
(
    name,
    description,
    is_active
)
VALUES
(
    'Development',
    'Software development and application engineering team',
    TRUE
),
(
    'Testing',
    'Software testing and quality assurance team',
    TRUE
),
(
    'HR',
    'Human resources and employee management team',
    TRUE
),
(
    'Finance',
    'Finance, accounting and payroll team',
    TRUE
),
(
    'Administration',
    'Office administration and operations team',
    TRUE
);

select * from departments
-----------------------------

 Employee table
-------------------
CREATE TABLE employees
(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    department_id INT NOT NULL,
    designation VARCHAR(100) NOT NULL,
    salary NUMERIC(12,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    street VARCHAR(150),
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    photo_path VARCHAR(500),
    resume_path VARCHAR(500),
    CONSTRAINT fk_employee_department
        FOREIGN KEY (department_id)
        REFERENCES departments(id)
);

INSERT INTO employees
(
    name,
    email,
    department_id,
    designation,
    salary,
    status,
    street,
    city,
    state,
    pincode
)
VALUES
(
    'Arun Kumar',
    'arun.kumar@company.com',
    1,
    'Software Engineer',
    55000.00,
    'ACTIVE',
    '100 Main Road',
    'Coimbatore',
    'Tamil Nadu',
    '641001'
),
(
    'Priya Sharma',
    'priya.sharma@company.com',
    1,
    'Senior Software Engineer',
    75000.00,
    'ACTIVE',
    '25 Gandhi Street',
    'Chennai',
    'Tamil Nadu',
    '600001'
),
(
    'Karthik Raj',
    'karthik.raj@company.com',
    1,
    'Technical Lead',
    95000.00,
    'ACTIVE',
    '12 Lake View Road',
    'Bangalore',
    'Karnataka',
    '560001'
),
(
    'Divya Kumar',
    'divya.kumar@company.com',
    2,
    'QA Engineer',
    50000.00,
    'ACTIVE',
    '45 Nehru Street',
    'Coimbatore',
    'Tamil Nadu',
    '641002'
),
(
    'Suresh Babu',
    'suresh.babu@company.com',
    2,
    'Senior QA Engineer',
    68000.00,
    'ACTIVE',
    '78 Park Road',
    'Chennai',
    'Tamil Nadu',
    '600002'
),
(
    'Malathi',
    'malathi@company.com',
    3,
    'HR Executive',
    45000.00,
    'ACTIVE',
    '10 Anna Street',
    'Madurai',
    'Tamil Nadu',
    '625001'
),
(
    'Ravi Shankar',
    'ravi.shankar@company.com',
    3,
    'HR Manager',
    72000.00,
    'ACTIVE',
    '55 Temple Road',
    'Coimbatore',
    'Tamil Nadu',
    '641005'
),
(
    'Anitha Raj',
    'anitha.raj@company.com',
    4,
    'Accountant',
    48000.00,
    'ACTIVE',
    '20 Market Road',
    'Salem',
    'Tamil Nadu',
    '636001'
),
(
    'Vijay Kumar',
    'vijay.kumar@company.com',
    4,
    'Finance Manager',
    85000.00,
    'ACTIVE',
    '30 College Road',
    'Chennai',
    'Tamil Nadu',
    '600006'
),
(
    'Divya Priya',
    'Divya.priya@company.com',
    5,
    'Admin Executive',
    42000.00,
    'ACTIVE',
    '15 Railway Road',
    'Coimbatore',
    'Tamil Nadu',
    '641018'
);
NOTE: ONE TO MANY RELATIONSHIP SET between Departments and Employees tables

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

PythonFasApiFileUploadRelations - Folder Structure
----------------------------------------
PythonFasApiFileUploadRelations/
│
├── .env
├── main.py
├── config.py
├── database.py
│
├── models/
│   ├── __init__.py
│   ├── employee_model.py
│   └── department_model.py
│
├── schemas/
│   ├── __init__.py
│   ├── employee_schema.py
│   └── department_schema.py
│
├── repositories/
│   ├── __init__.py
│   ├── employee_repository.py
│   └── department_repository.py
│
├── services/
│   ├── __init__.py
│   ├── employee_service.py
│   └── department_service.py
│
└── routers/
    ├── __init__.py
    ├── employee_router.py
    └── department_router.py

------------------------------------------

Commands:

1.
> python -m venv .venv
### Installation -- Use the virtual environment

2.
Activate it:

.\.venv\Scripts\Activate.ps1

You should see:

(.venv) PS D:\...\PythonFastApiPydantic>

3.
> python -m pip install fastapi "uvicorn[standard]" "psycopg[binary]" python-dotenv email-validator

NOTE : For async PostgreSQL connections, psycopg 3 is used.

# -------------------------------

4. Execute
> python -m uvicorn main:app --reload


> Run your application in the Swagger 
http://127.0.0.1:8000/docs 


# ========================================

FILE UPLOAD AND SAVE TO DISK OPERATION
---------------------------------------
There are two separate operations (Actual file-upload/save-to-disk)

1. Upload actual photo/resume
       ↓
   Save file to uploads/employees/...

2. Update PostgreSQL
       ↓
   photo_path
   resume_path

STEPS
-----------
1. Install required packages
-----------------------------
> python -m pip install python-multipart aiofiles
NOTE:  python-multipart → required by FastAPI for UploadFile
         aiofiles → asynchronous file writing

2. Recommended folder structure
-----------------------------------
Your project should have:

PythonFasApiFileUploadRelations
│
├── uploads/
│   └── employees/
│
├── schemas/
│   └── employee_schema.py
│
├── repositories/
│   └── employee_repository.py
│
├── services/
│   └── employee_service.py
│
└── routers/
    └── employee_router.py

After uploading employee 1:

uploads/
└── employees/
    └── 1/
        ├── photo/
        │   └── <unique-file-name>.jpg
        │
        └── resume/
            └── <unique-file-name>.pdf


3. Add upload code to employee_service.py
-----------------------------------------

from pathlib import Path
from uuid import uuid4

import aiofiles

from fastapi import HTTPException, UploadFile, status

Then Add this code,

# =========================================================
# FILE UPLOAD CONFIGURATION
# =========================================================

BASE_UPLOAD_DIR = Path("uploads") / "employees"


ALLOWED_PHOTO_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp"
}


ALLOWED_RESUME_TYPES = {
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx"
}


MAX_PHOTO_SIZE = 5 * 1024 * 1024       # 5 MB

MAX_RESUME_SIZE = 10 * 1024 * 1024     # 10 MB

4. Function to save the uploaded file (Add this function to employee_service.py:)
-----------------------------------------------------------------------------------
async def save_upload_file(
    file: UploadFile,
    employee_id: int,
    file_type: str
):
    """
    Save uploaded employee photo/resume to disk.

    Returns:
        Relative path of the saved file.
    """

    # -----------------------------------------------------
    # Validate file type
    # -----------------------------------------------------

    if file_type == "photo":

        allowed_types = ALLOWED_PHOTO_TYPES

        max_size = MAX_PHOTO_SIZE

    elif file_type == "resume":

        allowed_types = ALLOWED_RESUME_TYPES

        max_size = MAX_RESUME_SIZE

    else:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type"
        )

    # -----------------------------------------------------
    # Validate content type
    # -----------------------------------------------------

    if file.content_type not in allowed_types:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid {file_type} file type. "
                f"Allowed types: {', '.join(allowed_types.keys())}"
            )
        )

    # -----------------------------------------------------
    # Create employee directory
    # -----------------------------------------------------

    employee_directory = (
        BASE_UPLOAD_DIR
        / str(employee_id)
        / file_type
    )

    employee_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Generate unique filename
    # -----------------------------------------------------

    extension = allowed_types[file.content_type]

    unique_filename = (
        f"{uuid4().hex}{extension}"
    )

    file_path = (
        employee_directory
        / unique_filename
    )

    # -----------------------------------------------------
    # Save file
    # -----------------------------------------------------

    total_size = 0

    try:

        async with aiofiles.open(
            file_path,
            "wb"
        ) as output_file:

            while True:

                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                # -----------------------------------------
                # Check maximum file size
                # -----------------------------------------

                if total_size > max_size:

                    # Remove partially saved file
                    if file_path.exists():
                        file_path.unlink()

                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=(
                            f"{file_type.capitalize()} file "
                            f"size cannot exceed "
                            f"{max_size // (1024 * 1024)} MB"
                        )
                    )

                await output_file.write(chunk)

    finally:

        await file.close()

    # -----------------------------------------------------
    # Return relative path
    # -----------------------------------------------------

    return file_path.as_posix()



    5. Add the main upload function
---------------------------------------
Now add:

async def upload_employee_files(
    employee_id: int,
    photo: UploadFile | None = None,
    resume: UploadFile | None = None
):
    """
    Upload employee photo and/or resume
    and update their paths in PostgreSQL.
    """

    # -----------------------------------------------------
    # Check employee exists
    # -----------------------------------------------------

    employee = await repo_get_employee_by_id(
        employee_id
    )

    if employee is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # -----------------------------------------------------
    # At least one file required
    # -----------------------------------------------------

    if photo is None and resume is None:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload photo or resume"
        )

    photo_path = None

    resume_path = None

    # -----------------------------------------------------
    # Upload photo
    # -----------------------------------------------------

    if photo is not None:

        photo_path = await save_upload_file(
            file=photo,
            employee_id=employee_id,
            file_type="photo"
        )

    # -----------------------------------------------------
    # Upload resume
    # -----------------------------------------------------

    if resume is not None:

        resume_path = await save_upload_file(
            file=resume,
            employee_id=employee_id,
            file_type="resume"
        )

    # -----------------------------------------------------
    # Update database
    # -----------------------------------------------------

    updated = await repo_update_employee_files(

        employee_id=employee_id,

        photo_path=photo_path,

        resume_path=resume_path
    )

    return {
        "message": "Employee files uploaded successfully",

        "employee_id": updated["id"],

        "photo_path": updated["photo_path"],

        "resume_path": updated["resume_path"]
    }

# -------------------------------
Now the complete flow is:

Upload photo
     ↓
Validate JPEG/PNG/WebP
     ↓
Save physical file
     ↓
uploads/employees/101/photo/xxxxx.jpg
     ↓
Save path in PostgreSQL
     ↓
employees.photo_path

and:

Upload resume
     ↓
Validate PDF/DOC/DOCX
     ↓
Save physical file
     ↓
uploads/employees/101/resume/xxxxx.pdf
     ↓
Save path in PostgreSQL
     ↓
employees.resume_path
# ==================================


6. Add the router endpoint
#-----------------------------

In routers/employee_router.py, add:

from fastapi import APIRouter, File, UploadFile

from services.employee_service import (
    upload_employee_files
)

Then:

@router.post("/{employee_id}/files")
async def upload_employee_files_endpoint(
    employee_id: int,

    photo: UploadFile | None = File(
        default=None
    ),

    resume: UploadFile | None = File(
        default=None
    )
):

    return await upload_employee_files(

        employee_id=employee_id,

        photo=photo,

        resume=resume
    )
# ==============================

7. Swagger result
---------------------------
Now Swagger will show:

POST /api/employees/{employee_id}/files

with:

employee_id    1

photo          Choose File
resume         Choose File

For example:

employee_id: 1
photo:       Arun.jpg
resume:      Arun_Resume.pdf

Then click:

Execute
# =============================

8. PostgreSQL result
-------------------------
Before upload:

id | name        | photo_path | resume_path
---+-------------+------------+-------------
1  | Arun Kumar  | NULL       | NULL

After upload:

id | name        | photo_path                              | resume_path
---+-------------+------------------------------------------+-----------------------------
1  | Arun Kumar  | uploads/employees/1/photo/abc123.jpg    | uploads/employees/1/resume/xyz78

# ==================================================

The actual files are on disk:

uploads/
└── employees/
    └── 1/
        ├── photo/
        │   └── abc123.jpg
        │
        └── resume/
            └── xyz789.pdf

# =================================================


##############################


from pathlib import Path
from uuid import uuid4
import aiofiles

BASE_UPLOAD_DIR = Path("uploads") / "employees"


async def save_upload_file(file, employee_id: int, file_type: str):

    # 1. Create employee folder
    employee_dir = BASE_UPLOAD_DIR / str(employee_id)

    # 2. Decide whether photo or resume
    if file_type == "photo":
        upload_dir = employee_dir / "photo"
        extension = ".jpg"
    else:
        upload_dir = employee_dir / "resume"
        extension = ".pdf"

    # 3. Create the folder
    upload_dir.mkdir(parents=True, exist_ok=True)

    # 4. Generate unique filename
    filename = f"{uuid4()}{extension}"

    # 5. Full file path
    file_path = upload_dir / filename

    # 6. Save uploaded file
    async with aiofiles.open(file_path, "wb") as buffer:

        while chunk := await file.read(1024 * 1024):
            await buffer.write(chunk)

    # 7. Return path to store in database
    return file_path.as_posix()




##############################