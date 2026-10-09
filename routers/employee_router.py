# routers/employee_router.py
# --- For defining API routes related to employees

from fastapi import (
    APIRouter,
    Cookie,
    Header,
    Path,
    Query,
    status
)

from schemas.employee_schema import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeListResponse
)

from services.employee_service import (
    get_employees,
    get_employee,
    create_employee,
    update_existing_employee,
    delete_existing_employee
)


from fastapi import APIRouter, File, UploadFile

from services.employee_service import (
    upload_employee_files
)

#  -----------------------------------------

router = APIRouter(
    prefix="/api/employees",
    tags=["Employees"]
)
# -----------------------------------------

@router.get(
    "/",
    response_model=list[EmployeeResponse]
)
# -----------------------------------------

@router.get(
    "/",
    response_model=EmployeeListResponse
)
async def get_all(

    page: int = Query(
        default=1,
        ge=1,
        description="Page number"
    ),

    page_size: int = Query(
        default=3,
        ge=1,
        le=3,
        description="Number of employees per page"
    ),

    department_id: int | None = Query(
        default=None,
        gt=0,
        description="Filter employees by department ID"
    )
):

    return await get_employees(

        page=page,

        page_size=page_size,

        department_id=department_id
    )


# =========================================================
# GET EMPLOYEE BY ID
# =========================================================

@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse
)
async def get_one(

    employee_id: int = Path(
        ...,
        gt=0
    )
):

    return await get_employee(
        employee_id
    )
'''
Now:
    GET /api/employees/

or:

    GET /api/employees/?department=Development

This demonstrates:

    Query(...)
'''

# ------------------------------------

##### GET ONE — Path parameter  
### Our standard route:   GET /api/employees/101

@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse
)
async def get_one(
    employee_id: int = Path(
        ...,
        gt=0
    ),

    x_api_key: str = Header(...),   # The request must contain an HTTP header named X-Api-Key. ... indicates without the value in the header, FastAPI returns a validation error,

    session_id: str | None = Cookie(
        default=None   
    )    # Read the session_id value from the browser/client's cookies, but the cookie is optional.
):

    return await get_employee(
        employee_id
    )


'''
| Python parameter | FastAPI function | Comes from  | Required? |
| ---------------- | ---------------- | ----------- | --------- |
| `employee_id`    | `Path(...)`      | URL         | Yes       |
| `x_api_key`      | `Header(...)`    | HTTP Header | Yes       |
| `session_id`     | `Cookie(None)`   | HTTP Cookie | No        |

'''

'''
This demonstrates three different parameter sources:
----------------------------------------------------
1. /api/employees/101
       ↑
     Path

2. X-API-Key
   ↑
 Header

3. Cookie: session_id=ABC123
   ↑
 Cookie
'''
#----------------------------------------------

'''
Why use Path?

Instead of:

    employee_id: int

we can write:

    employee_id: int = Path(
        ...,
        gt=0
    )

So:

    /api/employees/101

    is valid.

But:

    /api/employees/0

fails validation.

And:

    /api/employees/-10

also fails.

'''
# ----------------------------------------------

#### POST — Body parameter

@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED
)
async def create(
    employee: EmployeeCreate      # employee: EmployeeCreate    --- is the request body.
):

    return await create_employee(
        employee
    )
# ----------------------------------------------

#### PUT — Path + Body + Header    

@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse
)
async def update(
    employee_id: int = Path(
        ...,
        gt=0
    ),

    employee: EmployeeUpdate = None,

    x_api_key: str = Header(...)
):

    return await update_existing_employee(
        employee_id,
        employee
    )
# ----------------------------------------------
'''
The request contains
----------------------
Path
 ↓
/api/employees/101

Header
 ↓
X-API-Key: ABC123

Body
 ↓
Employee JSON
'''

# ----------------------------------------------

#### DELETE — Path + Header

@router.delete(
    "/{employee_id}"
)
async def delete(
    employee_id: int = Path(
        ...,
        gt=0
    ),

    x_api_key: str = Header(...)
):

    return await delete_existing_employee(
        employee_id
    )

# -------------------------------------------------


##### File Handling — Upload Employee Files (Photo and Resume)

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



##### =====================================





###### Complete Router

'''
from fastapi import (
    APIRouter,
    Cookie,
    Header,
    Path,
    Query,
    status
)

from schemas.employee_schema import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse
)

from services.employee_service import (
    get_employees,
    get_employee,
    create_employee,
    update_existing_employee,
    delete_existing_employee
)


router = APIRouter(
    prefix="/api/employees",
    tags=["Employees"]
)


@router.get(
    "/",
    response_model=list[EmployeeResponse]
)
async def get_all(
    department: str | None = Query(
        default=None
    )
):

    employees = await get_employees()

    if department:

        employees = [
            employee
            for employee in employees
            if employee.department.lower()
            == department.lower()
        ]

    return employees


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse
)
async def get_one(
    employee_id: int = Path(
        ...,
        gt=0
    ),

    x_api_key: str = Header(...),

    session_id: str | None = Cookie(
        default=None
    )
):

    return await get_employee(
        employee_id
    )


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED
)
async def create(
    employee: EmployeeCreate
):

    return await create_employee(
        employee
    )


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse
)
async def update(
    employee_id: int = Path(
        ...,
        gt=0
    ),

    employee: EmployeeUpdate = None,

    x_api_key: str = Header(...)
):

    return await update_existing_employee(
        employee_id,
        employee
    )


@router.delete(
    "/{employee_id}"
)
async def delete(
    employee_id: int = Path(
        ...,
        gt=0
    ),

    x_api_key: str = Header(...)
):

    return await delete_existing_employee(
        employee_id
    )

'''