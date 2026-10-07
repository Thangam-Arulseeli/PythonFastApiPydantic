### use Pydantic v2 features --- enum.py 
from enum import Enum


class EmployeeStatus(str, Enum):  # Instead of accepting arbitrary values: { "status": "ACTIVE" }, we can restrict it to a set of predefined values.

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ON_LEAVE = "ON_LEAVE"