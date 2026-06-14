import httpx
import os
from models import Employee, SourceIds

ATLAS_URL = os.getenv("ATLAS_URL", "http://localhost:9001")
ATLAS_API_KEY = os.getenv("ATLAS_API_KEY")

async def fetch_atlas_employees() -> list[Employee]:
    headers = {"X-API-Key": ATLAS_API_KEY}
    employees = []
    page = 1

    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(
                f"{ATLAS_URL}/v1/employees",
                headers=headers,
                params={"page": page, "per_page": 100},
            )
            response.raise_for_status()
            body = response.json()

            for emp in body["data"]:
                employees.append(_normalize(emp))

            if len(employees) >= body["total"]:
                break
            page += 1

    return employees


def _normalize(emp: dict) -> Employee:
    return Employee(
        id=emp["id"],
        source_ids=SourceIds(atlas=emp["id"]),
        first_name=emp["first_name"],
        last_name=emp["last_name"],
        email=emp["work_email"],
        job_title=emp["job_title"],
        department=emp["department"],
        status=_map_status(emp["employment_status"]),
        annual_salary=emp["annual_salary_cents"] / 100,
        currency=emp["currency"],
        hire_date=emp["hire_date"],
        source="atlas",
    )


def _map_status(status: str) -> str:
    return {
        "ACTIVE": "active",
        "INACTIVE": "inactive",
        "TERMINATED": "inactive",
    }.get(status.upper(), "inactive")