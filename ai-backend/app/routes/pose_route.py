"""
pose_route.py
-------------
FastAPI router that exposes the ``POST /detect-pose`` endpoint.

This is the primary, real-time-oriented endpoint for single-image pose
detection.  It is intentionally kept thin — all business logic lives inside
``services/pose_service.py``.

Endpoint
~~~~~~~~
POST /detect-pose
    • Input  : multipart/form-data — one image file (JPEG / PNG / WebP)
    • Output : JSON matching the contract below

Output contract::

    {
      "pose_detected": true,
      "landmark_count": 33,
      "processing_time_ms": 52.4,
      "landmarks": [
        {"id": 0, "name": "NOSE",       "x": 0.512, "y": 0.123, "z": -0.015, "visibility": 0.998},
        {"id": 1, "name": "LEFT_EYE_INNER", ...},
        ...
        {"id": 32, "name": "RIGHT_FOOT_INDEX", ...}
      ]
    }

When no pose is detected::

    {
      "pose_detected": false,
      "landmark_count": 0,
      "processing_time_ms": 38.1,
      "landmarks": []
    }
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.models.schemas import PoseDetectionResponse
from app.services.pose_service import detect_pose

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Pose Detection"])

# Permitted image MIME types
_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post(
    "/detect-pose",
    response_model=PoseDetectionResponse,
    summary="Detect body pose from an image",
    description=(
        "Upload a **JPEG, PNG, or WebP** image.  "
        "BlazePose runs and returns all 33 body landmarks with their normalised "
        "``(x, y, z)`` coordinates and per-landmark visibility scores.\n\n"
        "Optimised for **real-time** use — processing typically completes in "
        "30\u2013150 ms depending on image resolution and hardware."
    ),
    responses={
        200: {"description": "Pose detection completed (pose may or may not have been found)."},
        415: {"description": "Unsupported image format."},
        422: {"description": "Image could not be decoded."},
        500: {"description": "Unexpected server-side error."},
    },
)
async def detect_pose_endpoint(
    file: UploadFile = File(
        ...,
        description="Image file to analyse (JPEG / PNG / WebP, max ~10 MB recommended).",
    ),
) -> PoseDetectionResponse:
    """
    Run MediaPipe BlazePose on the uploaded image and return structured
    landmark data.

    The endpoint is safe to call concurrently — each request creates its own
    short-lived MediaPipe session.
    """
    # ── Validate MIME type ────────────────────────────────────────────────────
    content_type = (file.content_type or "").split(";")[0].strip()
    if content_type not in _ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported media type '{content_type}'. "
                f"Allowed types: {sorted(_ALLOWED_TYPES)}"
            ),
        )

    # ── Read file bytes ───────────────────────────────────────────────────────
    try:
        image_bytes = await file.read()
    except Exception as exc:
        logger.exception("Failed to read uploaded image from request.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read uploaded file: {exc}",
        ) from exc

    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file is empty.",
        )

    # ── Run pose detection ────────────────────────────────────────────────────
    try:
        response = detect_pose(image_bytes)
    except ValueError as exc:
        # Image decoding failure (e.g. corrupt file despite correct MIME type)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error during pose detection.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Pose detection failed due to an internal error.",
        ) from exc

    return response
