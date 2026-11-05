from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse

from app.api.deps import get_client_ip, get_job_store, get_limiter
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.ratelimit import InMemoryRateLimiter
from app.schemas import ErrorDetail, ErrorResponse, TryOnResponse
from app.services.images import ImageService
from app.services.jobs import InMemoryJobStore

router = APIRouter(tags=["try-on"])


@router.post("/try-on", status_code=202)
async def try_on(
    request: Request,
    person: bytes = File(...),
    garment: bytes = File(...),
    category: str | None = Form(default=None),
    garment_description: str | None = Form(default=None),
    job_store: InMemoryJobStore = Depends(get_job_store),
    limiter: InMemoryRateLimiter = Depends(get_limiter),
    client_ip: str = Depends(get_client_ip),
) -> JSONResponse:
    settings = get_settings()
    allowed, retry_after = limiter.check(client_ip)
    if not allowed:
        headers = {"Retry-After": str(retry_after)}
        return JSONResponse(
            status_code=429,
            content=ErrorResponse(
                error=ErrorDetail(code="rate_limited", message="Too many requests. Try again later.")
            ).model_dump(),
            headers=headers,
        )

    person_ct = request.headers.get("content-type")
    # read content types from multipart if possible - but we get bytes; rely on image service

    try:
        person_norm = ImageService.normalize_upload(person, filename="person")
        garment_norm = ImageService.normalize_upload(garment, filename="garment")
    except AppError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.to_detail().model_dump())

    job_id = str(uuid.uuid4()).replace("-", "")
    job = job_store.create(
        job_id,
        category=category,
        person_bytes=person_norm.bytes,
        garment_bytes=garment_norm.bytes,
        garment_description=garment_description,
    )
    runner = request.app.state.runner
    runner.submit(job_id)
    response = TryOnResponse(
        id=job.id,
        status=job.status,
        category=job.category,
        provider=settings.tryon_provider,
        created_at=job.created_at,
        updated_at=job.updated_at,
        expires_at=job.expires_at,
        result_url=None,
        error=None,
    )
    return JSONResponse(status_code=202, content=response.model_dump(mode="json"), headers={"Location": f"/api/jobs/{job_id}"})
