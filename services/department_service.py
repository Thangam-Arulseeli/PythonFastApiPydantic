from fastapi import HTTPException, status

from repositories.department_repository import (
    create_department as repo_create_department,
    get_department_by_id as repo_get_department_by_id,
    get_all_departments as repo_get_all_departments,
    update_department as repo_update_department,
    delete_department as repo_delete_department,
    department_exists,
    department_name_exists,
    department_has_employees,
    get_employees_by_department
)

from schemas.department_schema import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentWithEmployeesResponse,
    EmployeeSummary
)


# =========================================================
# CREATE DEPARTMENT
# =========================================================

async def create_department(
    department_data: DepartmentCreate
):

    name = department_data.name.strip()

    # -----------------------------------------------------
    # Check duplicate department name
    # -----------------------------------------------------

    exists = await department_name_exists(name)

    if exists:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department name already exists"
        )

    # -----------------------------------------------------
    # Create department
    # -----------------------------------------------------

    department = await repo_create_department(
        name=name,
        description=department_data.description
    )

    return DepartmentResponse.model_validate(department)


# =========================================================
# GET DEPARTMENT BY ID
# =========================================================

async def get_department(
    department_id: int
):

    department = await repo_get_department_by_id(
        department_id
    )

    if department is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    return DepartmentResponse.model_validate(
        department
    )


# =========================================================
# GET ALL DEPARTMENTS
# =========================================================

async def get_departments():

    departments = await repo_get_all_departments()

    return [
        DepartmentResponse.model_validate(
            department
        )
        for department in departments
    ]


# =========================================================
# UPDATE DEPARTMENT
# =========================================================

async def update_department(
    department_id: int,
    department_data: DepartmentUpdate
):

    # -----------------------------------------------------
    # Check department exists
    # -----------------------------------------------------

    exists = await department_exists(
        department_id
    )

    if not exists:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    # -----------------------------------------------------
    # Check duplicate name
    # -----------------------------------------------------

    if department_data.name is not None:

        name = department_data.name.strip()

        name_exists = await department_name_exists(
            name=name,
            exclude_department_id=department_id
        )

        if name_exists:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another department already has this name"
            )

    else:

        name = None

    # -----------------------------------------------------
    # Update department
    # -----------------------------------------------------

    department = await repo_update_department(
        department_id=department_id,
        name=name,
        description=department_data.description,
        is_active=department_data.is_active
    )

    if department is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    return DepartmentResponse.model_validate(
        department
    )


# =========================================================
# DELETE DEPARTMENT
# =========================================================

async def delete_department(
    department_id: int
):

    # -----------------------------------------------------
    # Check department exists
    # -----------------------------------------------------

    exists = await department_exists(
        department_id
    )

    if not exists:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    # -----------------------------------------------------
    # Check employees
    # -----------------------------------------------------

    has_employees = await department_has_employees(
        department_id
    )

    if has_employees:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Cannot delete department because "
                "employees are assigned to this department"
            )
        )

    # -----------------------------------------------------
    # Delete department
    # -----------------------------------------------------

    deleted = await repo_delete_department(
        department_id
    )

    if deleted is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    return {
        "message": "Department deleted successfully",
        "department_id": department_id
    }


# =========================================================
# GET EMPLOYEES OF A DEPARTMENT
# =========================================================

async def get_department_employees(
    department_id: int
):

    # -----------------------------------------------------
    # Check department exists
    # -----------------------------------------------------

    department = await repo_get_department_by_id(
        department_id
    )

    if department is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    # -----------------------------------------------------
    # Get employees
    # -----------------------------------------------------

    employees = await get_employees_by_department(
        department_id
    )

    employee_list = [
        EmployeeSummary.model_validate(employee)
        for employee in employees
    ]

    # -----------------------------------------------------
    # Build department response
    # -----------------------------------------------------

    return DepartmentWithEmployeesResponse(
        id=department["id"],
        name=department["name"],
        description=department["description"],
        is_active=department["is_active"],
        employees=employee_list
    )
