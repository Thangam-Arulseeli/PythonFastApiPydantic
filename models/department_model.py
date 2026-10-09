#  Model for Department table
#  models/department_model.py --- DepartmentModel dataclass definition
from dataclasses import dataclass

@dataclass
class DepartmentModel:

    id: int
    name: str
    description: str | None
    is_active: bool