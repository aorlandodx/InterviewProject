import uuid
import json
import os
from datetime import datetime, timezone
from fastapi import Request
from fastapi.responses import JSONResponse

LOGS_PATH = os.path.join(os.path.dirname(__file__), "logs", "requests.jsonl")

os.makedirs(os.path.dirname(LOGS_PATH), exist_ok=True)


# Excepciones
class ProviderError(Exception):
    """Un provider upstream falló."""
    def __init__(self, provider: str, detail: str, status_code: int = 502):
        self.provider = provider
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class EmployeeNotFound(Exception):
    """El empleado solicitado no existe en ningún provider."""
    def __init__(self, employee_id: str):
        self.employee_id = employee_id
        super().__init__(f"No employee found with id '{employee_id}'")


class InvalidQueryParam(Exception):
    """El cliente mandó un parámetro inválido."""
    def __init__(self, param: str, reason: str):
        self.param = param
        self.reason = reason
        super().__init__(f"Invalid parameter '{param}': {reason}")


# Logging

def new_request_id() -> str:
    return str(uuid.uuid4())


def log_event(
    request_id: str,
    endpoint: str,
    provider: str | None = None,
    status: str = "ok",
    latency_ms: int | None = None,
    error: str | None = None,
) -> None:
    entry = {
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "provider": provider,
        "status": status,
        "latency_ms": latency_ms,
        "error": error,
    }
    with open(LOGS_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


# Handlers

async def provider_error_handler(request: Request, exc: ProviderError) -> JSONResponse:
    request_id = request.state.request_id if hasattr(request.state, "request_id") else new_request_id()
    log_event(
        request_id=request_id,
        endpoint=str(request.url.path),
        provider=exc.provider,
        status="error",
        error=exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "provider_unavailable",
            "message": f"El proveedor '{exc.provider}' no está disponible en este momento.",
            "detail": exc.detail,
            "request_id": request_id,
        },
    )


async def not_found_handler(request: Request, exc: EmployeeNotFound) -> JSONResponse:
    request_id = request.state.request_id if hasattr(request.state, "request_id") else new_request_id()
    log_event(
        request_id=request_id,
        endpoint=str(request.url.path),
        status="not_found",
        error=str(exc),
    )
    return JSONResponse(
        status_code=404,
        content={
            "error": "employee_not_found",
            "message": f"No se encontró ningún empleado con el ID '{exc.employee_id}'.",
            "request_id": request_id,
        },
    )


async def invalid_param_handler(request: Request, exc: InvalidQueryParam) -> JSONResponse:
    request_id = request.state.request_id if hasattr(request.state, "request_id") else new_request_id()
    log_event(
        request_id=request_id,
        endpoint=str(request.url.path),
        status="bad_request",
        error=str(exc),
    )
    return JSONResponse(
        status_code=400,
        content={
            "error": "invalid_parameter",
            "message": f"El parámetro '{exc.param}' es inválido: {exc.reason}",
            "request_id": request_id,
        },
    )