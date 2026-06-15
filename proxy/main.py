"""Proxy (BFF) — STARTER SKELETON.

This is intentionally almost empty. Your task is to turn this into a proxy that:
  1. fetches employees from the three Provider APIs,
  2. normalizes each Provider's shape into one canonical Employee model you design,
  3. resolves duplicate people that appear across Providers and merges them,
  4. exposes the result to the frontend.

See the top-level README.md for the Provider URLs and credentials. Structure the
code however you think is best — there are no required files or function names.

Run:  uv run uvicorn main:app --port 8000 --reload
Docs: http://localhost:8000/docs
"""

import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from models import Employee, EmployeeListResponse, ProviderStatus
from errors import (
    ProviderError,
    EmployeeNotFound,
    InvalidQueryParam,
    new_request_id,
    log_event,
    provider_error_handler,
    not_found_handler,
    invalid_param_handler,
)
from aggregator import merge_employees
from providers.atlas import fetch_atlas_employees
from providers.beacon import fetch_beacon_employees
from providers.cobalt import fetch_cobalt_employees

# Middleware
class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.request_id = new_request_id()
        start = time.monotonic()
        response = await call_next(request)
        latency_ms = int((time.monotonic() - start) * 1000)
        log_event(
            request_id=request.state.request_id,
            endpoint=str(request.url.path),
            status=str(response.status_code),
            latency_ms=latency_ms,
        )
        response.headers["X-Request-Id"] = request.state.request_id
        return response
    


app = FastAPI(title="Employee Aggregator Proxy")

# Open CORS for local frontend dev — not part of the exercise, leave as-is.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIdMiddleware)

app.add_exception_handler(ProviderError, provider_error_handler)
app.add_exception_handler(EmployeeNotFound, not_found_handler)
app.add_exception_handler(InvalidQueryParam, invalid_param_handler)

# Helpers
async def _fetch_all() -> tuple[list[Employee], dict]:
    """Llama a los tres providers en paralelo. Partial success si alguno falla."""

    async def safe_fetch(name: str, coro):
        try:
            return name, await coro, None
        except Exception as e:
            return name, [], str(e)

    results = await asyncio.gather(
        safe_fetch("atlas",  fetch_atlas_employees()),
        safe_fetch("beacon", fetch_beacon_employees()),
        safe_fetch("cobalt", fetch_cobalt_employees()),
    )

    employees_by_provider = {}
    provider_status = {}

    for name, data, error in results:
        employees_by_provider[name] = data
        provider_status[name] = "error" if error else "ok"
        if error:
            log_event(
                request_id="background",
                endpoint="/employees",
                provider=name,
                status="error",
                error=error,
            )

    return employees_by_provider, provider_status


# Endpoints
@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/employees", response_model=EmployeeListResponse)
async def list_employees(
    page: int = Query(default=1, ge=1, description="Página (1-based)"),
    page_size: int = Query(default=20, ge=1, le=2000, description="Empleados por página"),
):
    if page_size > 2000:
        raise InvalidQueryParam("page_size", "el máximo permitido es 2000")

    employees_by_provider, provider_status = await _fetch_all()

    merged = merge_employees(
        atlas=employees_by_provider["atlas"],
        beacon=employees_by_provider["beacon"],
        cobalt=employees_by_provider["cobalt"],
    )

    total = len(merged)
    start = (page - 1) * page_size
    end = start + page_size
    page_data = merged[start:end]

    return EmployeeListResponse(
        data=page_data,
        meta={
            "providers": provider_status,
            "partial": any(s == "error" for s in provider_status.values()),
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": -(-total // page_size),
        },
    )


@app.get("/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: str):
    employees_by_provider, _ = await _fetch_all()

    merged = merge_employees(
        atlas=employees_by_provider["atlas"],
        beacon=employees_by_provider["beacon"],
        cobalt=employees_by_provider["cobalt"],
    )

    # print(f"Buscando: '{employee_id}'")
    # for emp in merged:
    #     print(f"  id={emp.id} | atlas={emp.source_ids.atlas} | beacon={emp.source_ids.beacon} | cobalt={emp.source_ids.cobalt}")
    for emp in merged:
        if employee_id in [
            emp.id,
            emp.source_ids.atlas,
            str(emp.source_ids.beacon) if emp.source_ids.beacon is not None else None,
            emp.source_ids.cobalt,
        ]:
            return emp

    raise EmployeeNotFound(employee_id)


@app.get("/admin/logs")
def get_logs(
    provider: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
):
    import json, os
    from errors import LOGS_PATH

    if not os.path.exists(LOGS_PATH):
        return {"logs": [], "total": 0}

    with open(LOGS_PATH) as f:
        lines = [json.loads(line) for line in f if line.strip()]

    if provider:
        lines = [l for l in lines if l.get("provider") == provider]
    if status:
        lines = [l for l in lines if l.get("status") == status]

    lines = lines[-limit:]

    return {"logs": lines, "total": len(lines)}
