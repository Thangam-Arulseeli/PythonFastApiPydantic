from fastapi import APIRouter

from schemas.department_schema import (
    DepartmentCreate,
    DepartmentResponse
)

from services.department_service import (
    create_department,
    get_departments,
    get_department
)


router = APIRouter(
    prefix="/api/departments",
    tags=["Departments"]
)


# Get all deparments
@router.get(
    "/",
    response_model=list[DepartmentResponse]
)
async def get_all_departments():

    return await get_departments()


# Get one department
@router.get(
    "/{department_id}",
    response_model=DepartmentResponse
)
async def get_one_department(
    department_id: int
):

    return await get_department(
        department_id
    )


# Create Department
@router.post(
    "/",
    response_model=DepartmentResponse,
    status_code=201
)
async def create(
    department: DepartmentCreate
):

    return await create_department(
        department
    )


