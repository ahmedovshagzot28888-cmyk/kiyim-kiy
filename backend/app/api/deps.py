from __future__ import annotations

from fastapi import Depends, Request

from app.core.rate_limit import InMemoryRateLimiter
from app.core.ratelimit import resolve_client_ip
from app.services.jobs import InMemoryJobStore


def get_job_store(request: Request) -> InMemoryJobStore:
    return request.app.state.job_store


def get_limiter(request: Request) -> InMemoryRateLimiter:
    return request.app.state.rate_limiter


def get_client_ip(request: Request) -> str:
    return resolve_client_ip(request)
