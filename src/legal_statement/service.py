from fastapi import FastAPI, HTTPException

from .infrai_client import InfraiClient, InfraiError
from .models import StatementExport, StatementRequest
from .statement_service import export_statement

service = FastAPI(title="Legal matter statement service")


@service.post("/statements/export", response_model=StatementExport)
def create_statement(request: StatementRequest) -> StatementExport:
    try:
        return export_statement(request, InfraiClient())
    except InfraiError as exc:
        status_code = exc.status_code if 400 <= exc.status_code < 500 else 502
        raise HTTPException(
            status_code=status_code,
            detail={"code": exc.code, "error": exc.detail},
        ) from exc
