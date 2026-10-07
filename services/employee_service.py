### services/employee_service.py
# The Service should not contain SQL.  It handles business rules and transformation.

from fastapi import HTTPException

from repositories.employee_repository import (
    get_all_employees,
    get_employee_by_id,
    insert_employee,
    update_employee,
    delete_employee
)

from schemas.employee_schema import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    Address
)

# -----------------------------------------

# Create a Helper ---- Convert database row → response
def row_to_employee(row):

    if row is None:
        return None

    data = {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "department": row[3],
        "designation": row[4],
        "salary": float(row[5]),
        "status": row[6],
        "address": {
            "street": row[7],
            "city": row[8],
            "state": row[9],
            "pincode": row[10]
        }
    }

    return EmployeeResponse.model_validate(data) # Pydantic validates and converts the data into an EmployeeResponse.
### Note: The service layer is responsible for handling business logic and transformations, 
            # while the repository layer handles direct database interactions. 
            # This separation of concerns ensures that the service layer remains clean and focused on business rules, 
            # while the repository layer manages data persistence.   
# response = EmployeeResponse.model_validate(data) --- Used when converting database data into a validated response.
'''
dict/object
    ↓
Pydantic object
'''

# -----------------------------------------
'''
This is a very good example of:

Database row
     ↓
Dictionary
     ↓
model_validate()
     ↓
Pydantic Response Model
'''

# -----------------------------------------

# GetAll Employees Service
async def get_employees():

    rows = await get_all_employees()

    return [
        row_to_employee(row)
        for row in rows
    ]
# -----------------------------------------

# Get Employee By ID Service
async def get_employee(employee_id: int):

    row = await get_employee_by_id(
        employee_id
    )

    if row is None:

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return row_to_employee(row)
# -----------------------------------------

# Create Employee Record  Service (Create Service)
async def create_employee(
    employee: EmployeeCreate
):

    # Business rule
    if (
        employee.department.lower()
        == "development"
        and employee.salary < 30000
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Development employee salary "
                "must be at least 30000"
            )
        )

    # Pydantic model → dictionary
    data = employee.model_dump()  # This is a dictionary representation of the Pydantic model.

    row = await insert_employee(data)

    return row_to_employee(row)

### In Pydantic v2, model_dump() is the primary method used to convert a Pydantic model instance into 
# a standard Python dictionary (dict). It replaces the deprecated .dict() method 
#---------------------------------------------

### Update Employee Record Service (Update Service)
async def update_existing_employee(
    employee_id: int,
    employee: EmployeeUpdate
):

    existing = await get_employee_by_id(
        employee_id
    )

    if existing is None:

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    data = employee.model_dump() # This is very useful before sending data to the repository.

    row = await update_employee(
        employee_id,
        data
    )

    return row_to_employee(row)
# -----------------------------------------

### Delete Employee Record Service (Delete Service)
async def delete_existing_employee(
    employee_id: int
):

    existing = await get_employee_by_id(
        employee_id
    )

    if existing is None:

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    deleted_id = await delete_employee(
        employee_id
    )

    return {
        "message": "Employee deleted successfully",
        "employee_id": deleted_id
    }
# -----------------------------------------


