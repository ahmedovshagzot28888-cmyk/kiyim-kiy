from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response

from app.api.deps import get_job_store
from app.schemas import ErrorDetail, ErrorResponse, JobResponse
from app.services.jobs import InMemoryJobStore

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, job_store: InMemoryJobStore = Depends(get_job_store)) -> JobResponse:
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(error=ErrorDetail(code="job_not_found", message="Job not found.")).model_dump(),
        )
    if job.status == "done":
        result_url = f"/api/jobs/{job.id}/result"
    else:
        result_url = None
    return JobResponse(
        id=job.id,
        status=job.status,
        category=job.category,
        provider=job.provider,
        created_at=job.created_at,
        updated_at=job.updated_at,
        expires_at=job.expires_at,
        result_url=result_url,
        error={"code": job.error_code, "message": job.error_message} if job.error_code else None,
    )


@router.get("/{job_id}/result")
def get_job_result(job_id: str, request: Request, job_store: InMemoryJobStore = Depends(get_job_store)) -> Response:
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(error=ErrorDetail(code="job_not_found", message="Job not found.")).model_dump(),
        )
    if job.status != "done" or job.result_bytes is None:
        raise HTTPException(
            status_code=409,
            detail=ErrorResponse(error=ErrorDetail(code="job_not_ready", message="Result is not ready yet.")).model_dump(),
        )
    return Response(content=job.result_bytes, media_type="image/jpeg", headers={"Cache-Control": "no-store"})


@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: str, job_store: InMemoryJobStore = Depends(get_job_store)) -> Response:
    job_store.delete(job_id)
    return Response(status_code=204)
