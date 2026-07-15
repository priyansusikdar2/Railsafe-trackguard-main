"""Configuration objects for track geometry, detection, and braking behavior."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TrackGeometry:
    """Defines the track Region-of-Interest as a trapezoid polygon,
    following the rails from the horizon down to the bottom of frame."""

    frame_w: int = 1280
    frame_h: int = 720
    horizon_y: int = 260
    vanish_x: int = 640
    vanish_half_width: int = 30
    left_bottom_x_frac: float = 0.18
    right_bottom_x_frac: float = 0.80

    def polygon(self) -> list[tuple[int, int]]:
        left_bottom = int(self.frame_w * self.left_bottom_x_frac)
        right_bottom = int(self.frame_w * self.right_bottom_x_frac)
        return [
            (self.vanish_x - self.vanish_half_width, self.horizon_y),
            (self.vanish_x + self.vanish_half_width, self.horizon_y),
            (right_bottom, self.frame_h),
            (left_bottom, self.frame_h),
        ]


@dataclass
class DetectionConfig:
    hazard_classes: set[str] = field(default_factory=lambda: {
        "person", "car", "truck", "bus", "motorcycle", "bicycle",
        "dog", "cat", "horse", "cow", "sheep", "elephant", "bear",
    })
    display_name_override: dict[str, str] = field(default_factory=dict)
    conf_threshold: float = 0.25
    infer_imgsz: int = 1280
    max_box_area_frac: float = 0.35
    risk_bands: list[tuple[float, str]] = field(default_factory=lambda: [
        (0.55, "CRITICAL"), (0.32, "HIGH"), (0.16, "MEDIUM"), (0.0, "LOW"),
    ])
    risk_colors: dict[str, tuple[int, int, int]] = field(default_factory=lambda: {
        "CRITICAL": (0, 0, 255), "HIGH": (0, 80, 255),
        "MEDIUM": (0, 200, 255), "LOW": (0, 200, 120),
    })


@dataclass
class BrakingConfig:
    brake_rate: float = 0.0076
    accel_rate: float = 0.02
    grace_frames: int = 10


# Real-world object heights (meters), used for the distance estimate.
OBJECT_HEIGHT_M = {
    "person": 1.7, "car": 1.55, "truck": 3.2, "bus": 3.2,
    "motorcycle": 1.3, "bicycle": 1.3, "dog": 0.5, "cat": 0.3,
    "horse": 1.6, "cow": 1.5, "sheep": 1.0, "elephant": 3.0, "bear": 1.2,
}
ASSUMED_FOCAL_PX = 900
