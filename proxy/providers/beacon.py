import httpx
import os
from models import Employee, SourceIds

BEACON_URL = os.getenv("BEACON_URL", "http://localhost:9002")
BEACON_API_KEY = os.getenv("BEACON_API_KEY")

async def fetch_beacon_employees() -> list[Employee]:
    headers = {"X-API-Key": BEACON_API_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BEACON_URL}/staff",
            params={"api_key": BEACON_API_KEY},  
        )
        response.raise_for_status()
        body = response.json()

    return [_normalize(emp) for emp in body]


def _normalize(emp: dict) -> Employee:
    first_name, *rest = emp["full_name"].split(" ", 1)
    last_name = rest[0] if rest else ""

    return Employee(
        id=str(emp["staff_id"]),
        source_ids=SourceIds(beacon=emp["staff_id"]),
        first_name=first_name,
        last_name=last_name,
        email=emp["email"],
        job_title=emp["position"],
        department=emp["team"]["name"],
        status=_map_status(emp["is_active"], emp["on_leave"]),
        annual_salary=float(emp["compensation"]["amount"]) * 12,
        currency=emp["compensation"]["currency"],
        hire_date=_parse_date(emp["started_at"]),
        source="beacon",
    )


def _map_status(is_active: bool, on_leave: bool) -> str:
    if not is_active:
        return "inactive"
    if on_leave:
        return "on_leave"
    return "active"


def _parse_date(timestamp_ms: int) -> str:
    from datetime import datetime, timezone
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d")