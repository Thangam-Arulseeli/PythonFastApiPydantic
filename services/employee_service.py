### services/employee_service.py
# The Service should not contain SQL.  It handles business rules and transformation.

# Now the service converts the flat SQL JOIN result into the nested Pydantic response.
# This is very important for avoiding the 500 error you were seeing
 
# Import necessary modules and classes for file upload

#################################################

from math import ceil
from pathlib import Path
from uuid import uuid4

import aiofiles

from fastapi import HTTPException, UploadFile, status

from repositories.employee_repository import (
    create_employee as repo_create_employee,
    get_employee_by_id as repo_get_employee_by_id,
    get_employee_count as repo_get_employee_count,
    get_all_employees as repo_get_all_employees,
    update_employee as repo_update_employee,
    delete_employee as repo_delete_employee,
    email_exists,
    update_employee_files as repo_update_employee_files
)

from repositories.department_repository import (
    department_exists
)

from schemas.employee_schema import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeListResponse
)


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


MAX_PHOTO_SIZE = 5 * 1024 * 1024

MAX_RESUME_SIZE = 10 * 1024 * 1024


# =========================================================
# HELPER
# DATABASE ROW -> EMPLOYEE RESPONSE
# =========================================================

def build_employee_response(row):

    employee_data = {

        "id": row["id"],

        "name": row["name"],

        "email": row["email"],

        "department_id": row["department_id"],

        "department": {

            "id": row["department_ref_id"],

            "name": row["department_name"],

            "description": row["department_description"],

            "is_active": row["department_is_active"]
        },

        "designation": row["designation"],

        "salary": float(row["salary"]),

        "status": row["status"],

        "address": {

            "street": row["street"],

            "city": row["city"],

            "state": row["state"],

            "pincode": row["pincode"]
        },

        "photo_path": row["photo_path"],

        "resume_path": row["resume_path"]
    }

    return EmployeeResponse.model_validate(
        employee_data
    )


# =========================================================
# CREATE EMPLOYEE
# =========================================================

async def create_employee(
    employee_data: EmployeeCreate
):

    # -----------------------------------------------------
    # Check department exists
    # -----------------------------------------------------

    department_exists_result = await department_exists(
        employee_data.department_id
    )

    if not department_exists_result:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    # -----------------------------------------------------
    # Check duplicate email
    # -----------------------------------------------------

    email_already_exists = await email_exists(
        str(employee_data.email)
    )

    if email_already_exists:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee email already exists"
        )

    # -----------------------------------------------------
    # Insert employee
    # -----------------------------------------------------

    employee = await repo_create_employee(

        name=employee_data.name.strip(),

        email=str(employee_data.email),

        department_id=employee_data.department_id,

        designation=employee_data.designation.strip(),

        salary=employee_data.salary,

        status=employee_data.status.value,

        street=employee_data.address.street,

        city=employee_data.address.city,

        state=employee_data.address.state,

        pincode=employee_data.address.pincode
    )

    # -----------------------------------------------------
    # Get complete employee with department
    # -----------------------------------------------------

    employee = await repo_get_employee_by_id(
        employee["id"]
    )

    return build_employee_response(
        employee
    )


# =========================================================
# GET EMPLOYEE BY ID
# =========================================================

async def get_employee(
    employee_id: int
):

    employee = await repo_get_employee_by_id(
        employee_id
    )

    if employee is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    return build_employee_response(
        employee
    )


# =========================================================
# GET EMPLOYEES
#
# Supports:
#   - Pagination
#   - Department filtering
# =========================================================

async def get_employees(
    page: int = 1,
    page_size: int = 10,
    department_id: int | None = None
):

    # -----------------------------------------------------
    # Validate department
    # -----------------------------------------------------

    if department_id is not None:

        exists = await department_exists(
            department_id
        )

        if not exists:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )

    # -----------------------------------------------------
    # Get total count
    # -----------------------------------------------------

    total = await repo_get_employee_count(
        department_id
    )

    # -----------------------------------------------------
    # Get employees
    # -----------------------------------------------------

    employees = await repo_get_all_employees(

        page=page,

        page_size=page_size,

        department_id=department_id
    )

    # -----------------------------------------------------
    # Convert rows to response models
    # -----------------------------------------------------

    items = [

        build_employee_response(
            employee
        )

        for employee in employees
    ]

    # -----------------------------------------------------
    # Calculate pagination
    # -----------------------------------------------------

    total_pages = (
        ceil(total / page_size)
        if total > 0
        else 0
    )

    return EmployeeListResponse(

        items=items,

        page=page,

        page_size=page_size,

        total=total,

        total_pages=total_pages,

        has_next=page < total_pages,

        has_previous=page > 1
    )


# =========================================================
# UPDATE EXISTING EMPLOYEE
# =========================================================

async def update_existing_employee(
    employee_id: int,
    employee_data: EmployeeUpdate
):

    # -----------------------------------------------------
    # 1. Check employee exists
    # -----------------------------------------------------

    existing_employee = await repo_get_employee_by_id(
        employee_id
    )

    if existing_employee is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # -----------------------------------------------------
    # 2. Check department if department is being changed
    # -----------------------------------------------------

    if employee_data.department_id is not None:

        department_found = await department_exists(
            employee_data.department_id
        )

        if not department_found:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )

    # -----------------------------------------------------
    # 3. Check email uniqueness
    # -----------------------------------------------------

    if employee_data.email is not None:

        email_already_exists = await email_exists(

            str(employee_data.email),

            exclude_employee_id=employee_id
        )

        if email_already_exists:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another employee already uses this email"
            )

    # -----------------------------------------------------
    # 4. Get address values
    # -----------------------------------------------------

    address = employee_data.address

    street = None
    city = None
    state = None
    pincode = None

    if address is not None:

        street = address.street

        city = address.city

        state = address.state

        pincode = address.pincode

    # -----------------------------------------------------
    # 5. Update employee
    # -----------------------------------------------------

    updated_employee = await repo_update_employee(

        employee_id=employee_id,

        name=(
            employee_data.name.strip()
            if employee_data.name is not None
            else None
        ),

        email=(
            str(employee_data.email)
            if employee_data.email is not None
            else None
        ),

        department_id=employee_data.department_id,

        designation=(
            employee_data.designation.strip()
            if employee_data.designation is not None
            else None
        ),

        salary=employee_data.salary,

        status=(
            employee_data.status.value
            if employee_data.status is not None
            else None
        ),

        street=street,

        city=city,

        state=state,

        pincode=pincode
    )

    # -----------------------------------------------------
    # 6. Make sure update succeeded
    # -----------------------------------------------------

    if updated_employee is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # -----------------------------------------------------
    # 7. Get complete employee again
    #
    # This gives us department information through JOIN.
    # -----------------------------------------------------

    employee = await repo_get_employee_by_id(
        employee_id
    )

    return build_employee_response(
        employee
    )


# =========================================================
# DELETE EMPLOYEE
# =========================================================

async def delete_existing_employee(
    employee_id: int
):

    employee = await repo_get_employee_by_id(
        employee_id
    )

    if employee is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    deleted = await repo_delete_employee(
        employee_id
    )

    if deleted is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    return {

        "message": "Employee deleted successfully",

        "employee_id": employee_id
    }


# =========================================================
# SAVE UPLOADED FILE
# =========================================================

async def save_upload_file(
    file: UploadFile,
    employee_id: int,
    file_type: str
):

    # -----------------------------------------------------
    # Determine allowed file types and size
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
    # Validate MIME type
    # -----------------------------------------------------

    if file.content_type not in allowed_types:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid {file_type} file type. "
                f"Allowed types: "
                f"{', '.join(allowed_types.keys())}"
            )
        )

    # -----------------------------------------------------
    # Create directory
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

    extension = allowed_types[
        file.content_type
    ]

    unique_filename = (
        f"{uuid4().hex}{extension}"
    )

    file_path = (
        employee_directory
        / unique_filename
    )

    # -----------------------------------------------------
    # Save file in chunks
    # -----------------------------------------------------

    total_size = 0

    try:

        async with aiofiles.open(
            file_path,
            "wb"
        ) as output_file:

            while True:

                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > max_size:

                    if file_path.exists():

                        file_path.unlink()

                    raise HTTPException(
                        status_code=(
                            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                        ),
                        detail=(
                            f"{file_type.capitalize()} "
                            f"file size cannot exceed "
                            f"{max_size // (1024 * 1024)} MB"
                        )
                    )

                await output_file.write(
                    chunk
                )

    finally:

        await file.close()

    return file_path.as_posix()


# =========================================================
# UPLOAD EMPLOYEE PHOTO / RESUME
# =========================================================

async def upload_employee_files(
    employee_id: int,
    photo: UploadFile | None = None,
    resume: UploadFile | None = None
):

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
    # At least one file is required
    # -----------------------------------------------------

    if photo is None and resume is None:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload photo or resume"
        )

    photo_path = None

    resume_path = None

    # -----------------------------------------------------
    # Save photo
    # -----------------------------------------------------

    if photo is not None:

        photo_path = await save_upload_file(

            file=photo,

            employee_id=employee_id,

            file_type="photo"
        )

    # -----------------------------------------------------
    # Save resume
    # -----------------------------------------------------

    if resume is not None:

        resume_path = await save_upload_file(

            file=resume,

            employee_id=employee_id,

            file_type="resume"
        )

    # -----------------------------------------------------
    # Update database paths
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


####################################################


# from pathlib import Path
# from uuid import uuid4

# import aiofiles


# from fastapi import HTTPException, UploadFile, status


# from math import ceil

# #from fastapi import HTTPException, status

# from repositories.employee_repository import (
#     create_employee as repo_create_employee,
#     get_employee_by_id as repo_get_employee_by_id,
#     get_employee_count as repo_get_employee_count,
#     get_all_employees as repo_get_all_employees,
#     update_employee as repo_update_employee,
#     delete_employee as repo_delete_employee,
#     email_exists,
#     update_employee_files as repo_update_employee_files
# )

# from repositories.department_repository import (
#     department_exists
# )

# from schemas.employee_schema import (
#     EmployeeCreate,
#     EmployeeUpdate,
#     EmployeeResponse,
#     EmployeeListResponse
# )


# # =========================================================
# # FILE UPLOAD CONFIGURATION
# # =========================================================

# BASE_UPLOAD_DIR = Path("uploads") / "employees"

# ALLOWED_PHOTO_TYPES = {
#     "image/jpeg": ".jpg",
#     "image/png": ".png",
#     "image/webp": ".webp"
# }

# ALLOWED_RESUME_TYPES = {
#     "application/pdf": ".pdf",
#     "application/msword": ".doc",
#     "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx"
# }


# MAX_PHOTO_SIZE = 5 * 1024 * 1024       # 5 MB

# MAX_RESUME_SIZE = 10 * 1024 * 1024     # 10 MB


# # =========================================================
# # HELPER
# #
# # Converts database JOIN row into EmployeeResponse
# # =========================================================

# def build_employee_response(
#     row
# ):

#     employee_data = {

#         "id": row["id"],

#         "name": row["name"],

#         "email": row["email"],

#         "department_id": row["department_id"],

#         "department": {

#             "id": row["department_ref_id"],

#             "name": row["department_name"],

#             "description": row["department_description"],

#             "is_active": row["department_is_active"]
#         },

#         "designation": row["designation"],

#         "salary": float(row["salary"]),

#         "status": row["status"],

#         "address": {

#             "street": row["street"],

#             "city": row["city"],

#             "state": row["state"],

#             "pincode": row["pincode"]
#         },

#         "photo_path": row["photo_path"],

#         "resume_path": row["resume_path"]
#     }

#     return EmployeeResponse.model_validate(
#         employee_data
#     )


# # =========================================================
# # CREATE EMPLOYEE
# # =========================================================

# async def create_employee(
#     employee_data: EmployeeCreate
# ):

#     # -----------------------------------------------------
#     # Check department
#     # -----------------------------------------------------

#     department_exists_result = await department_exists(
#         employee_data.department_id
#     )

#     if not department_exists_result:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Department not found"
#         )

#     # -----------------------------------------------------
#     # Check duplicate email
#     # -----------------------------------------------------

#     email_already_exists = await email_exists(
#         str(employee_data.email)
#     )

#     if email_already_exists:

#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Employee email already exists"
#         )

#     # -----------------------------------------------------
#     # Create employee
#     # -----------------------------------------------------

#     employee = await repo_create_employee(

#         name=employee_data.name.strip(),

#         email=str(employee_data.email),

#         department_id=employee_data.department_id,

#         designation=employee_data.designation.strip(),

#         salary=employee_data.salary,

#         status=employee_data.status.value,

#         street=employee_data.address.street,

#         city=employee_data.address.city,

#         state=employee_data.address.state,

#         pincode=employee_data.address.pincode
#     )

#     # -----------------------------------------------------
#     # Get complete employee with department
#     # -----------------------------------------------------

#     employee = await repo_get_employee_by_id(
#         employee["id"]
#     )

#     return build_employee_response(
#         employee
#     )


# # =========================================================
# # GET EMPLOYEE BY ID
# # =========================================================

# async def get_employee(
#     employee_id: int
# ):

#     employee = await repo_get_employee_by_id(
#         employee_id
#     )

#     if employee is None:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Employee not found"
#         )

#     return build_employee_response(
#         employee
#     )


# # =========================================================
# # GET ALL EMPLOYEES
# #
# # Supports:
# #   Pagination
# #   Department filtering
# # =========================================================

# async def get_employees(
#     page: int = 1,
#     page_size: int = 10,
#     department_id: int | None = None
# ):

#     # -----------------------------------------------------
#     # Validate department
#     # -----------------------------------------------------

#     if department_id is not None:

#         exists = await department_exists(
#             department_id
#         )

#         if not exists:

#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Department not found"
#             )

#     # -----------------------------------------------------
#     # Get total count
#     # -----------------------------------------------------

#     total = await repo_get_employee_count(
#         department_id
#     )

#     # -----------------------------------------------------
#     # Get paginated employees
#     # -----------------------------------------------------

#     employees = await repo_get_all_employees(

#         page=page,

#         page_size=page_size,

#         department_id=department_id
#     )

#     # -----------------------------------------------------
#     # Convert DB rows → Pydantic responses
#     # -----------------------------------------------------

#     items = [

#         build_employee_response(
#             employee
#         )

#         for employee in employees
#     ]

#     # -----------------------------------------------------
#     # Calculate pages
#     # -----------------------------------------------------

#     total_pages = (
#         ceil(total / page_size)
#         if total > 0
#         else 0
#     )

#     return EmployeeListResponse(

#         items=items,

#         page=page,

#         page_size=page_size,

#         total=total,

#         total_pages=total_pages,

#         has_next=page < total_pages,

#         has_previous=page > 1
#     )


# # =========================================================
# # UPDATE EMPLOYEE
# # =========================================================

# async def update_employee(
#     employee_id: int,
#     employee_data: EmployeeUpdate
# ):

#     # -----------------------------------------------------
#     # Check employee
#     # -----------------------------------------------------

#     existing_employee = await repo_get_employee_by_id(
#         employee_id
#     )

#     if existing_employee is None:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Employee not found"
#         )

#     # -----------------------------------------------------
#     # Check department if changing department
#     # -----------------------------------------------------

#     if employee_data.department_id is not None:

#         exists = await department_exists(
#             employee_data.department_id
#         )

#         if not exists:

#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Department not found"
#             )

#     # -----------------------------------------------------
#     # Check email
#     # -----------------------------------------------------

#     if employee_data.email is not None:

#         email_already_exists = await email_exists(

#             str(employee_data.email),

#             exclude_employee_id=employee_id
#         )

#         if email_already_exists:

#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail="Another employee already uses this email"
#             )

#     # -----------------------------------------------------
#     # Address values
#     # -----------------------------------------------------

#     address = employee_data.address

#     street = (
#         address.street
#         if address is not None
#         else None
#     )

#     city = (
#         address.city
#         if address is not None
#         else None
#     )

#     state = (
#         address.state
#         if address is not None
#         else None
#     )

#     pincode = (
#         address.pincode
#         if address is not None
#         else None
#     )

#     # -----------------------------------------------------
#     # Update
#     # -----------------------------------------------------

#     updated_employee = await repo_update_employee(

#         employee_id=employee_id,

#         name=(
#             employee_data.name.strip()
#             if employee_data.name is not None
#             else None
#         ),

#         email=(
#             str(employee_data.email)
#             if employee_data.email is not None
#             else None
#         ),

#         department_id=employee_data.department_id,

#         designation=(
#             employee_data.designation.strip()
#             if employee_data.designation is not None
#             else None
#         ),

#         salary=employee_data.salary,

#         status=(
#             employee_data.status.value
#             if employee_data.status is not None
#             else None
#         ),

#         street=street,

#         city=city,

#         state=state,

#         pincode=pincode
#     )

#     if updated_employee is None:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Employee not found"
#         )

#     # -----------------------------------------------------
#     # Get complete JOIN result
#     # -----------------------------------------------------

#     employee = await repo_get_employee_by_id(
#         employee_id
#     )

#     return build_employee_response(
#         employee
#     )


# # =========================================================
# # DELETE EMPLOYEE
# # =========================================================

# async def delete_employee(
#     employee_id: int
# ):

#     employee = await repo_get_employee_by_id(
#         employee_id
#     )

#     if employee is None:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Employee not found"
#         )

#     deleted = await repo_delete_employee(
#         employee_id
#     )

#     if deleted is None:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Employee not found"
#         )

#     return {
#         "message": "Employee deleted successfully",
#         "employee_id": employee_id
#     }


# # =========================================================
# # UPDATE PHOTO / RESUME
# # =========================================================

# async def update_employee_files(
#     employee_id: int,
#     photo_path: str | None = None,
#     resume_path: str | None = None
# ):

#     employee = await repo_get_employee_by_id(
#         employee_id
#     )

#     if employee is None:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Employee not found"
#         )

#     updated = await repo_update_employee_files(

#         employee_id=employee_id,

#         photo_path=photo_path,

#         resume_path=resume_path
#     )

#     return {
#         "message": "Employee files updated successfully",

#         "employee_id": updated["id"],

#         "photo_path": updated["photo_path"],

#         "resume_path": updated["resume_path"]
#     }

# # ---------------------------------------------

# ###Function to save the uploaded file (Add this function to employee_service.py:)
# ### -----------------------------------------------------------------------------------
# async def save_upload_file(
#     file: UploadFile,
#     employee_id: int,
#     file_type: str
# ):
#     """
#     Save uploaded employee photo/resume to disk.

#     Returns:
#         Relative path of the saved file.
#     """

#     # -----------------------------------------------------
#     # Validate file type
#     # -----------------------------------------------------

#     if file_type == "photo":

#         allowed_types = ALLOWED_PHOTO_TYPES

#         max_size = MAX_PHOTO_SIZE

#     elif file_type == "resume":

#         allowed_types = ALLOWED_RESUME_TYPES

#         max_size = MAX_RESUME_SIZE

#     else:

#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid file type"
#         )

#     # -----------------------------------------------------
#     # Validate content type
#     # -----------------------------------------------------

#     if file.content_type not in allowed_types:

#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=(
#                 f"Invalid {file_type} file type. "
#                 f"Allowed types: {', '.join(allowed_types.keys())}"
#             )
#         )

#     # -----------------------------------------------------
#     # Create employee directory
#     # -----------------------------------------------------

#     employee_directory = (
#         BASE_UPLOAD_DIR
#         / str(employee_id)
#         / file_type
#     )

#     employee_directory.mkdir(
#         parents=True,
#         exist_ok=True
#     )

#     # -----------------------------------------------------
#     # Generate unique filename
#     # -----------------------------------------------------

#     extension = allowed_types[file.content_type]

#     unique_filename = (
#         f"{uuid4().hex}{extension}"
#     )

#     file_path = (
#         employee_directory
#         / unique_filename
#     )

#     # -----------------------------------------------------
#     # Save file
#     # -----------------------------------------------------

#     total_size = 0

#     try:

#         async with aiofiles.open(
#             file_path,
#             "wb"
#         ) as output_file:

#             while True:

#                 chunk = await file.read(1024 * 1024)

#                 if not chunk:
#                     break

#                 total_size += len(chunk)

#                 # -----------------------------------------
#                 # Check maximum file size
#                 # -----------------------------------------

#                 if total_size > max_size:

#                     # Remove partially saved file
#                     if file_path.exists():
#                         file_path.unlink()

#                     raise HTTPException(
#                         status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
#                         detail=(
#                             f"{file_type.capitalize()} file "
#                             f"size cannot exceed "
#                             f"{max_size // (1024 * 1024)} MB"
#                         )
#                     )

#                 await output_file.write(chunk)

#     finally:

#         await file.close()

#     # -----------------------------------------------------
#     # Return relative path
#     # -----------------------------------------------------

#     return file_path.as_posix()

# # ==========================================


# #### Add the following function to employee_service.py to handle the upload of employee files ### (photo and resume):

# async def upload_employee_files(
#     employee_id: int,
#     photo: UploadFile | None = None,
#     resume: UploadFile | None = None
# ):
#     """
#     Upload employee photo and/or resume
#     and update their paths in PostgreSQL.
#     """

#     # -----------------------------------------------------
#     # Check employee exists
#     # -----------------------------------------------------

#     employee = await repo_get_employee_by_id(
#         employee_id
#     )

#     if employee is None:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Employee not found"
#         )

#     # -----------------------------------------------------
#     # At least one file required
#     # -----------------------------------------------------

#     if photo is None and resume is None:

#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Please upload photo or resume"
#         )

#     photo_path = None

#     resume_path = None

#     # -----------------------------------------------------
#     # Upload photo
#     # -----------------------------------------------------

#     if photo is not None:

#         photo_path = await save_upload_file(
#             file=photo,
#             employee_id=employee_id,
#             file_type="photo"
#         )

#     # -----------------------------------------------------
#     # Upload resume
#     # -----------------------------------------------------

#     if resume is not None:

#         resume_path = await save_upload_file(
#             file=resume,
#             employee_id=employee_id,
#             file_type="resume"
#         )

#     # -----------------------------------------------------
#     # Update database
#     # -----------------------------------------------------

#     updated = await repo_update_employee_files(

#         employee_id=employee_id,

#         photo_path=photo_path,

#         resume_path=resume_path
#     )

#     return {
#         "message": "Employee files uploaded successfully",

#         "employee_id": updated["id"],

#         "photo_path": updated["photo_path"],

#         "resume_path": updated["resume_path"]
#     }

# # =========================================================



# # from fastapi import HTTPException
# # from repositories.department_repository import  (
# #     get_department_by_id
    
# #     )

# # from repositories.employee_repository import (
# #     get_all_employees,
# #     get_employee_by_id,
# #     insert_employee,
# #     update_employee,
# #     delete_employee
# # )

# # from schemas.employee_schema import (
# #     EmployeeCreate,
# #     EmployeeUpdate,
# #     EmployeeResponse,
# #     Address
# # )

# # from schemas.department_schema import (
# #      DepartmentResponse,
# #      DepartmentCreate
# # )

# # # -----------------------------------------

# # # Create a Helper ---- Convert database row → response
# # def row_to_employee(row):

# #     if row is None:
# #         return None

# #     data = {
# #         "id": row[0],
# #         "name": row[1],
# #         "email": row[2],
# #         "department": row[3],
# #         "designation": row[4],
# #         "salary": float(row[5]),
# #         "status": row[6],
# #         "address": {
# #             "street": row[7],
# #             "city": row[8],
# #             "state": row[9],
# #             "pincode": row[10]
# #         }
# #     }

# #     return EmployeeResponse.model_validate(data) # Pydantic validates and converts the data into an EmployeeResponse.
# # ### Note: The service layer is responsible for handling business logic and transformations, 
# #             # while the repository layer handles direct database interactions. 
# #             # This separation of concerns ensures that the service layer remains clean and focused on business rules, 
# #             # while the repository layer manages data persistence.   
# # # response = EmployeeResponse.model_validate(data) --- Used when converting database data into a validated response.
# # '''
# # dict/object
# #     ↓
# # Pydantic object
# # '''

# # # -----------------------------------------
# # '''
# # This is a very good example of:

# # Database row
# #      ↓
# # Dictionary
# #      ↓
# # model_validate()
# #      ↓
# # Pydantic Response Model
# # '''

# # # -----------------------------------------

# # # GetAll Employees Service
# # async def get_employees():

# #     rows = await get_all_employees()

# #     return [
# #         row_to_employee(row)
# #         for row in rows
# #     ]
# # # -----------------------------------------

# # # Get Employee By ID Service
# # async def get_employee(employee_id: int):

# #     row = await get_employee_by_id(
# #         employee_id
# #     )

# #     if row is None:

# #         raise HTTPException(
# #             status_code=404,
# #             detail="Employee not found"
# #         )

# #     return row_to_employee(row)
# # # -----------------------------------------

# # #  Create Employee Record  Service with department relation (Create Service)


# # async def create_employee(
# #     employee: EmployeeCreate
# # ):

# #     department = await get_department_by_id(
# #         employee.department_id
# #     )

# #     if department is None:

# #         raise HTTPException(
# #             status_code=400,
# #             detail="Invalid department_id"
# #         )

# #     data = employee.model_dump()

# #     employee_id = await insert_employee(
# #         data
# #     )

# #     return await get_employee(
# #         employee_id
# #     )



# # # ---------------
# # # Create Employee Record  Service (Create Service)
# # async def create_employee(
# #     employee: EmployeeCreate
# # ):

# #     # Business rule
# #     if (
# #         employee.department.lower()
# #         == "development"
# #         and employee.salary < 30000
# #     ):

# #         raise HTTPException(
# #             status_code=400,
# #             detail=(
# #                 "Development employee salary "
# #                 "must be at least 30000"
# #             )
# #         )

# #     # Pydantic model → dictionary
# #     data = employee.model_dump()  # This is a dictionary representation of the Pydantic model.

# #     row = await insert_employee(data)

# #     return row_to_employee(row)

# # ### In Pydantic v2, model_dump() is the primary method used to convert a Pydantic model instance into 
# # # a standard Python dictionary (dict). It replaces the deprecated .dict() method 
# # #---------------------------------------------

# # ### Update Employee Record Service (Update Service)
# # async def update_existing_employee(
# #     employee_id: int,
# #     employee: EmployeeUpdate
# # ):

# #     existing = await get_employee_by_id(
# #         employee_id
# #     )

# #     if existing is None:

# #         raise HTTPException(
# #             status_code=404,
# #             detail="Employee not found"
# #         )

# #     data = employee.model_dump() # This is very useful before sending data to the repository.

# #     row = await update_employee(
# #         employee_id,
# #         data
# #     )

# #     return row_to_employee(row)
# # # -----------------------------------------

# # ### Delete Employee Record Service (Delete Service)
# # async def delete_existing_employee(
# #     employee_id: int
# # ):

# #     existing = await get_employee_by_id(
# #         employee_id
# #     )

# #     if existing is None:

# #         raise HTTPException(
# #             status_code=404,
# #             detail="Employee not found"
# #         )

# #     deleted_id = await delete_employee(
# #         employee_id
# #     )

# #     return {
# #         "message": "Employee deleted successfully",
# #         "employee_id": deleted_id
# #     }
# # # -----------------------------------------


