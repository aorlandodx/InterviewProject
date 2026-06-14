import httpx
import os
from models import Employee, SourceIds

COBALT_URL = os.getenv("COBALT_URL", "http://localhost:9003")
COBALT_TOKEN = os.getenv("COBALT_TOKEN")

async def fetch_cobalt_employees() -> list[Employee]:
    headers = {"Authorization": f"Bearer {COBALT_TOKEN}"}
    employees = []
    cursor = None

    async with httpx.AsyncClient() as client:
        while True:
            body_payload = {"limit": 100}
            if cursor is not None:
                body_payload["cursor"] = cursor

            response = await client.post(
                f"{COBALT_URL}/api/directory/search",
                headers=headers,
                json=body_payload,
            )
            response.raise_for_status()
            body = response.json()

            for emp in body["results"]:
                employees.append(_normalize(emp))

            cursor = body.get("cursor")
            if cursor is None:
                break

    return employees


def _normalize(emp: dict) -> Employee:
    return Employee(
        id=emp["uuid"],
        source_ids=SourceIds(cobalt=emp["uuid"]),
        first_name=emp["name"]["given"],
        last_name=emp["name"]["family"],
        email=emp["contact"]["email"],
        job_title=emp["assignment"]["role"],
        department=_clean_department(emp["assignment"]["org_unit"]),
        status=_map_status(emp["lifecycle_status"]),
        annual_salary=_parse_salary(emp["pay"]),
        currency=emp["pay"]["iso_currency"],
        hire_date=_parse_date(emp["joined"]),
        source="cobalt",
    )


def _clean_department(org_unit: str) -> str:
    return org_unit.replace(" Dept", "").replace(" Team", "").strip()


def _map_status(lifecycle_status: str) -> str:
    return {
        "employed": "active",
        "on_leave": "on_leave",
        "terminated": "inactive",
    }.get(lifecycle_status.lower(), "inactive")


def _parse_salary(pay: dict) -> float:
    value = float(pay["value"])
    if pay["unit"] == "year":
        return value
    if pay["unit"] == "monthly":
        return value * 12
    if pay["unit"] == "weekly":
        return value * 52
    return value


def _parse_date(date_str: str) -> str:
    from datetime import datetime
    return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")