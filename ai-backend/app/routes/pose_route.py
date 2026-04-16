from __future__ import annotations

import logging

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.models.schemas import PoseDetectionResponse
from app.services.pose_service import detect_pose

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Pose Detection"])

_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/detect-pose", response_model=PoseDetectionResponse, summary="Detect body pose from an image")
async def detect_pose_endpoint(
    file: UploadFile = File(...),
) -> PoseDetectionResponse:
    content_type = (file.content_type or "").split(";")[0].strip()
    if content_type not in _ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported media type '{content_type}'. Allowed: {sorted(_ALLOWED_TYPES)}",
        )

    try:
        image_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if not image_bytes:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Uploaded file is empty.")

    try:
        response = detect_pose(image_bytes)
        if response and getattr(response, "keypoints", None):
            print("\n----- DEBUG POSE -----")
            print(f"Keypoints Extracted: {len(response.keypoints)}")
            print("----------------------\n")
        return response
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected error during pose detection.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Pose detection failed.") from exc
