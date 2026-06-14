from pydantic import BaseModel, field_validator
from typing import Optional

class SourceIds(BaseModel):
    atlas: Optional[str] = None
    beacon: Optional[int] = None
    cobalt: Optional[str] = None

class Employee(BaseModel):
    id: str
    source_ids: SourceIds
    first_name: str
    last_name: str
    email: str
    job_title: str
    department: str
    status: str          
    annual_salary: float
    currency: str
    hire_date: str       
    source: str          

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

class ProviderStatus(BaseModel):
    atlas: str    
    beacon: str
    cobalt: str

class EmployeeListResponse(BaseModel):
    data: list[Employee]
    meta: dict