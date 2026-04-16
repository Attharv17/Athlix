"""
angle_utils.py
--------------
Geometric utility functions for computing joint angles from 3-D pose
landmarks.  All angles are derived using the dot-product / cosine rule on
vectors built from three joint positions and are returned in **degrees**.

Public surface
~~~~~~~~~~~~~~
Low-level (generic)
    calculate_angle(a, b, c)       — angle at vertex b (3-D)
    calculate_angle_2d(a, b, c)    — angle at vertex b (2-D, ignores z)
    euclidean_distance(p1, p2)     — 3-D Euclidean distance
    normalize_landmark(x, y, z)    — clamp to MediaPipe expected ranges

High-level (named biomechanical angles)
    compute_knee_angle(landmarks)  — average left/right knee flexion
    compute_hip_angle(landmarks)   — average left/right hip flexion
    compute_back_angle(landmarks)  — trunk/spine inclination
    compute_all_angles(landmarks)  — returns all three as a dict
"""

from __future__ import annotations

import math
import logging
from typing import Dict, List, Optional, Tuple

import numpy as np

from app.models.schemas import PoseLandmarkItem

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------
Point3D = Tuple[float, float, float]   # (x, y, z) normalised image space

# ---------------------------------------------------------------------------
# BlazePose landmark indices (33-point model)
# Only the subset used for injury-relevant angles.
# ---------------------------------------------------------------------------
_IDX = {
    "LEFT_SHOULDER":    11,
    "RIGHT_SHOULDER":   12,
    "LEFT_HIP":         23,
    "RIGHT_HIP":        24,
    "LEFT_KNEE":        25,
    "RIGHT_KNEE":       26,
    "LEFT_ANKLE":       27,
    "RIGHT_ANKLE":      28,
    "LEFT_FOOT_INDEX":  31,
    "RIGHT_FOOT_INDEX": 32,
}

# Minimum visibility to trust a landmark
_MIN_VIS: float = 0.4


# ===========================================================================
# ─── Core math primitives ──────────────────────────────────────────────────
# ===========================================================================

def _to_array(point: Point3D) -> np.ndarray:
    """Convert a (x, y, z) tuple to a float64 NumPy array."""
    return np.array(point, dtype=np.float64)


def calculate_angle(a: Point3D, b: Point3D, c: Point3D) -> float:
    """
    Calculate the interior angle (in degrees) at joint **b**, formed by the
    vectors b→a and b→c.

    Uses the dot-product / cosine rule::

        cos θ = (b→a · b→c) / (‖b→a‖ · ‖b→c‖)

    Parameters
    ----------
    a : Point3D
        First endpoint joint (e.g. hip when measuring the knee angle).
    b : Point3D
        Vertex joint at which the angle is measured (e.g. knee).
    c : Point3D
        Second endpoint joint (e.g. ankle when measuring the knee angle).

    Returns
    -------
    float
        Angle in degrees, always in **[0, 180]**.
        Returns ``0.0`` if either vector is zero-length (degenerate input).
    """
    vec_ba = _to_array(a) - _to_array(b)
    vec_bc = _to_array(c) - _to_array(b)

    norm_ba = float(np.linalg.norm(vec_ba))
    norm_bc = float(np.linalg.norm(vec_bc))

    # Guard: zero-length vector means two landmarks are coincident / missing
    if norm_ba < 1e-9 or norm_bc < 1e-9:
        return 0.0

    # Clamp cos to [-1, 1] to absorb floating-point drift before acos
    cos_theta = float(np.clip(np.dot(vec_ba, vec_bc) / (norm_ba * norm_bc), -1.0, 1.0))
    return round(math.degrees(math.acos(cos_theta)), 4)


def calculate_angle_2d(
    a: Tuple[float, float],
    b: Tuple[float, float],
    c: Tuple[float, float],
) -> float:
    """
    2-D variant of :func:`calculate_angle` — ignores the z axis entirely.

    Useful when depth estimation from a monocular camera is unreliable.

    Parameters
    ----------
    a, b, c : (x, y) tuples
        Same semantics as :func:`calculate_angle`.

    Returns
    -------
    float
        Angle in degrees in **[0, 180]**.
    """
    return calculate_angle(
        (a[0], a[1], 0.0),
        (b[0], b[1], 0.0),
        (c[0], c[1], 0.0),
    )


def euclidean_distance(p1: Point3D, p2: Point3D) -> float:
    """
    Euclidean distance between two 3-D points.

    Parameters
    ----------
    p1, p2 : Point3D

    Returns
    -------
    float
    """
    return float(np.linalg.norm(_to_array(p1) - _to_array(p2)))


def normalize_landmark(x: float, y: float, z: float) -> Point3D:
    """
    Return a validated landmark tuple, clamping x/y to [0, 1].

    Parameters
    ----------
    x, y : float
        Normalised image coordinates (0–1).
    z : float
        Depth value relative to hip depth (MediaPipe convention).

    Returns
    -------
    Point3D
    """
    return (
        float(np.clip(x, 0.0, 1.0)),
        float(np.clip(y, 0.0, 1.0)),
        float(z),
    )


# ===========================================================================
# ─── Internal landmark lookup helper ───────────────────────────────────────
# ===========================================================================

def _get_point(
    landmarks: List[PoseLandmarkItem],
    name: str,
) -> Optional[Point3D]:
    """
    Return the ``(x, y, z)`` tuple for a named landmark from a list of
    :class:`PoseLandmarkItem` objects.

    Returns ``None`` if:
    * The landmark name is not found (should never happen with BlazePose).
    * The landmark's visibility is below :data:`_MIN_VIS`.

    Parameters
    ----------
    landmarks : list of PoseLandmarkItem
        Ordered 0-indexed list as returned by BlazePose.
    name : str
        Landmark name, e.g. ``"LEFT_KNEE"``.

    Returns
    -------
    Point3D | None
    """
    target_idx = _IDX.get(name)
    if target_idx is None:
        logger.debug("_get_point: unknown landmark name '%s'", name)
        return None

    # landmarks list is ordered; direct index access is O(1)
    if target_idx >= len(landmarks):
        return None

    lm = landmarks[target_idx]
    if lm.visibility < _MIN_VIS:
        logger.debug(
            "_get_point: '%s' visibility %.2f below threshold %.2f — skipped.",
            name, lm.visibility, _MIN_VIS,
        )
        return None

    return (lm.x, lm.y, lm.z)


def _safe_angle(
    landmarks: List[PoseLandmarkItem],
    a_name: str,
    b_name: str,
    c_name: str,
) -> Optional[float]:
    """
    Calculate the angle at joint *b_name* if all three landmarks are visible.

    Returns ``None`` when any landmark is missing or below visibility threshold.
    """
    a = _get_point(landmarks, a_name)
    b = _get_point(landmarks, b_name)
    c = _get_point(landmarks, c_name)
    if a is None or b is None or c is None:
        return None
    return calculate_angle(a, b, c)


def _average(*values: Optional[float]) -> Optional[float]:
    """Return the mean of all non-None values, or None if all are missing."""
    valid = [v for v in values if v is not None]
    if not valid:
        return None
    return round(sum(valid) / len(valid), 4)


# ===========================================================================
# ─── Named biomechanical angle computations ────────────────────────────────
# ===========================================================================

def compute_knee_angle(landmarks: List[PoseLandmarkItem]) -> Optional[float]:
    """
    Compute the **knee flexion angle** averaged across both legs.

    Joint triple used::

        hip → knee → ankle

    A fully extended knee is ~180°; a deeply flexed knee is ~30-40°.

    Parameters
    ----------
    landmarks : list of PoseLandmarkItem
        All 33 BlazePose landmarks for one frame.

    Returns
    -------
    float | None
        Average left/right knee angle in degrees.
        Returns the available side if one side is occluded.
        Returns ``None`` if both knees are undetectable.
    """
    left  = _safe_angle(landmarks, "LEFT_HIP",  "LEFT_KNEE",  "LEFT_ANKLE")
    right = _safe_angle(landmarks, "RIGHT_HIP", "RIGHT_KNEE", "RIGHT_ANKLE")
    return _average(left, right)


def compute_hip_angle(landmarks: List[PoseLandmarkItem]) -> Optional[float]:
    """
    Compute the **hip flexion angle** averaged across both sides.

    Joint triple used::

        shoulder → hip → knee

    A standing upright posture yields ~180°; a deep squat ~60–70°.

    Parameters
    ----------
    landmarks : list of PoseLandmarkItem

    Returns
    -------
    float | None
        Average left/right hip angle in degrees.
    """
    left  = _safe_angle(landmarks, "LEFT_SHOULDER",  "LEFT_HIP",  "LEFT_KNEE")
    right = _safe_angle(landmarks, "RIGHT_SHOULDER", "RIGHT_HIP", "RIGHT_KNEE")
    return _average(left, right)


def compute_back_angle(landmarks: List[PoseLandmarkItem]) -> Optional[float]:
    """
    Compute the **back / spine inclination angle**.

    Strategy
    --------
    1. Derive the **mid-shoulder** point (average of LEFT_SHOULDER and
       RIGHT_SHOULDER) and the **mid-hip** point (average of LEFT_HIP and
       RIGHT_HIP).
    2. Construct a downward vertical reference from mid-hip.
    3. Calculate the angle at mid-hip between the trunk vector
       (mid-hip → mid-shoulder) and the vertical reference.

    A perfectly upright posture yields ~0° (trunk aligned with vertical).
    Forward lean increases the angle toward 90°.

    Parameters
    ----------
    landmarks : list of PoseLandmarkItem

    Returns
    -------
    float | None
        Trunk inclination angle in degrees, or ``None`` if key landmarks
        are missing.
    """
    ls = _get_point(landmarks, "LEFT_SHOULDER")
    rs = _get_point(landmarks, "RIGHT_SHOULDER")
    lh = _get_point(landmarks, "LEFT_HIP")
    rh = _get_point(landmarks, "RIGHT_HIP")

    if None in (ls, rs, lh, rh):
        return None

    # Midpoints
    mid_shoulder: Point3D = (
        (ls[0] + rs[0]) / 2,
        (ls[1] + rs[1]) / 2,
        (ls[2] + rs[2]) / 2,
    )
    mid_hip: Point3D = (
        (lh[0] + rh[0]) / 2,
        (lh[1] + rh[1]) / 2,
        (lh[2] + rh[2]) / 2,
    )

    # Vertical reference: a point directly *above* the hip in image space.
    # In MediaPipe's normalised coordinates y increases downward, so subtract
    # 1.0 to place the reference above the hip.
    vertical_ref: Point3D = (mid_hip[0], mid_hip[1] - 1.0, mid_hip[2])

    angle = calculate_angle(mid_shoulder, mid_hip, vertical_ref)
    return round(angle, 4)


# ===========================================================================
# ─── Convenience wrapper ───────────────────────────────────────────────────
# ===========================================================================

def compute_all_angles(
    landmarks: List[PoseLandmarkItem],
) -> Dict[str, Optional[float]]:
    """
    Compute all three primary biomechanical angles for a single frame.

    This is the main entry-point called by :func:`pose_service.detect_pose`.

    Parameters
    ----------
    landmarks : list of PoseLandmarkItem
        All 33 BlazePose landmarks for one frame.

    Returns
    -------
    dict
        Keys: ``"knee_angle"``, ``"hip_angle"``, ``"back_angle"``.
        Values: angle in degrees (float, rounded to 4 dp) or ``None`` if the
        required landmarks were not detected with sufficient confidence.

    Example output::

        {
            "knee_angle": 162.3,
            "hip_angle":  174.7,
            "back_angle":   8.1
        }
    """
    return {
        "knee_angle": compute_knee_angle(landmarks),
        "hip_angle":  compute_hip_angle(landmarks),
        "back_angle": compute_back_angle(landmarks),
    }
