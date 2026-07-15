"""Core data model shared across the detection and rendering pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Detection:
    cls: str
    confidence: float
    box: tuple[float, float, float, float]  # x1, y1, x2, y2
    bbox_height: float
    distance_m: Optional[float] = None
    risk: Optional[str] = None
