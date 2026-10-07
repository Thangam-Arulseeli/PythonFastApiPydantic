### use Pydantic v2 features --- enum.py 

'''
### In Pydantic v2, model_dump() is the primary method used to convert a Pydantic model instance 
    # into a standard Python dictionary (dict). It replaces the deprecated .dict() method 
    # from Pydantic v1 (https://docs.pydantic.dev/latest/migration/#model-dump-and-model-dump-json).
### ConfigDict is a type-safe dictionary used to set configuration parameters on Pydantic models,
    #  dataclasses, and type adapters. It replaces the older, deprecated Config inner class from Pydantic v1
    ConfigDict provides a more structured and type-safe way to define model configurations,
    #  making it easier to manage and understand the settings applied to Pydantic models.
### Field is a function used to define metadata and validation rules for model fields.
    #  It replaces the older, deprecated FieldInfo class from Pydantic v1.
### EmailStr is a specialized type provided by Pydantic that validates whether a given string is a valid email address. 
    # It is used to ensure that email fields in models contain properly formatted email addresses.    
### field_validator is a decorator used to define custom validation logic for individual fields in a Pydantic model. 
    # It allows you to specify validation rules that are applied to specific fields when the model is instantiated or validated. 
#### model_validator is a decorator used to define custom validation logic for the entire model. 
    # It allows you to specify validation rules that are applied to the model as a whole, rather than individual fields. 
    # This is useful for enforcing constraints that involve multiple fields or require more complex validation logic. 

'''
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator
)


class EmployeeStatus(str, Enum):

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ON_LEAVE = "ON_LEAVE"


class Address(BaseModel):

    street: str = Field(
        min_length=3,
        max_length=150
    )

    city: str = Field(
        min_length=2,
        max_length=100
    )

    state: str = Field(
        min_length=2,
        max_length=100
    )

    pincode: str = Field(
        pattern=r"^\d{6}$"
    )


class EmployeeCreate(BaseModel):

    name: str = Field(
        min_length=3,
        max_length=100
    )

    email: EmailStr

    department: str = Field(
        min_length=2,
        max_length=100
    )

    designation: str = Field(
        min_length=2,
        max_length=100
    )

    salary: float = Field(
        gt=0,
        le=10_000_000
    )

    status: EmployeeStatus

    address: Address


    @field_validator("name")
    @classmethod
    def validate_name(cls, value):

        if any(char.isdigit() for char in value):

            raise ValueError(
                "Employee name cannot contain numbers"
            )

        return value.strip()


    @model_validator(mode="after")
    def validate_employee(self):

        if (
            self.status == EmployeeStatus.INACTIVE
            and self.salary > 10000
        ):
            raise ValueError(
                "Inactive employee cannot have salary above 10000"
            )

        return self


# class EmployeeUpdate(EmployeeCreate):

#     pass

#--------------------------------
class EmployeeUpdate(BaseModel):

    name: str = Field(
        min_length=3,
        max_length=100
    )

    email: EmailStr

    department: str = Field(
        min_length=2,
        max_length=100
    )

    designation: str = Field(
        min_length=2,
        max_length=100
    )

    salary: float = Field(
        gt=0,
        le=10_000_000
    )

    status: EmployeeStatus

    address: Address

#--------------------------------

class EmployeeResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    name: str
    email: EmailStr
    department: str
    designation: str
    salary: float
    status: EmployeeStatus
    address: Address


