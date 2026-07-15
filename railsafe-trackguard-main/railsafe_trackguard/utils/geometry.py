"""Geometry helpers: ROI membership testing and risk/distance estimation."""

from __future__ import annotations

from typing import Optional

import cv2
import numpy as np

from railsafe_trackguard.config import OBJECT_HEIGHT_M, ASSUMED_FOCAL_PX


def point_in_polygon(pt: tuple[int, int], polygon: list[tuple[int, int]]) -> bool:
    """True if `pt` lies inside (or on the border of) `polygon`."""
    return cv2.pointPolygonTest(np.array(polygon, dtype=np.int32), pt, False) >= 0


def risk_level(bbox_height: float, frame_h: int, bands: list[tuple[float, str]]) -> str:
    """Maps a bounding-box height (as a fraction of frame height, a proxy
    for proximity) to a discrete risk band."""
    ratio = bbox_height / frame_h
    for threshold, label in bands:
        if ratio >= threshold:
            return label
    return "LOW"


def estimate_distance_m(cls_name: str, bbox_height_px: float) -> Optional[float]:
    """Pinhole-camera distance estimate from an assumed real-world object
    height and an assumed camera focal length. This is a geometric
    approximation, not a calibrated/sensor-based measurement."""
    if bbox_height_px <= 0:
        return None
    real_height = OBJECT_HEIGHT_M.get(cls_name, 1.5)
    return (real_height * ASSUMED_FOCAL_PX) / bbox_height_px
