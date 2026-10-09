from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------
# Department Create Request
# ---------------------------------------------------------
class DepartmentCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    description: str | None = Field(
        default=None,
        max_length=250
    )


# ---------------------------------------------------------
# Department Update Request
# ---------------------------------------------------------
class DepartmentUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    description: str | None = Field(
        default=None,
        max_length=250
    )

    is_active: bool | None = None


# ---------------------------------------------------------
# Department Response
# ---------------------------------------------------------
class DepartmentResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    is_active: bool


# ---------------------------------------------------------
# Employee Summary
#
# Used when returning employees under a department.
# We do NOT return the complete EmployeeResponse here.
# Otherwise we can create unnecessary nested data.
# ---------------------------------------------------------
class EmployeeSummary(BaseModel):

    id: int
    name: str
    email: str
    designation: str
    salary: float
    status: str


# ---------------------------------------------------------
# Department with Employees
#
# One Department -> Many Employees
# ---------------------------------------------------------
class DepartmentWithEmployeesResponse(BaseModel):

    id: int
    name: str
    description: str | None
    is_active: bool

    employees: list[EmployeeSummary] = []

#---------------------------------------------------------

'''
Why EmployeeSummary?

Suppose we request:

GET /api/departments/1/employees

We don't necessarily need the complete employee response containing:

department
address
photo
resume
...

We can return a simpler representation:

{
    "id": 1,
    "name": "Development",
    "description": "Software development team",
    "is_active": true,
    "employees": [
        {
            "id": 101,
            "name": "Arun Kumar",
            "email": "arun@gmail.com",
            "designation": "Software Engineer",
            "salary": 50000,
            "status": "ACTIVE"
        }
    ]
}
This also avoids unnecessarily complicated nested schemas.
'''