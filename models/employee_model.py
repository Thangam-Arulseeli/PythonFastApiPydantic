# models/employee_model.py --- EmployeeModel dataclass definition

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class EmployeeModel:

    id: int
    name: str
    email: str
    department: str
    designation: str
    salary: Decimal
    status: str
    street: str | None
    city: str | None
    state: str | None
    pincode: str | None

### NOTE: Since we're not using SQLAlchemy,
#  this model is simply a Python representation of database data.
