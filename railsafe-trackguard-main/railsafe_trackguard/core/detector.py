"""YOLO-based obstacle detector with ROI filtering and risk scoring."""

from __future__ import annotations

import numpy as np
from ultralytics import YOLO

from railsafe_trackguard.config import DetectionConfig, TrackGeometry
from railsafe_trackguard.core.models import Detection
from railsafe_trackguard.utils.geometry import (
    point_in_polygon, risk_level, estimate_distance_m,
)


class TrackObstacleDetector:
    """Runs YOLO on a frame, filters to railway-relevant hazard classes,
    rejects sensor/dashboard artifacts by area, and splits detections into
    on-track (inside the ROI polygon) vs. off-track (ignored for alerting,
    but still shown for transparency)."""

    def __init__(self, model_path: str, geometry: TrackGeometry, cfg: DetectionConfig):
        self.model = YOLO(model_path)
        self.geometry = geometry
        self.cfg = cfg
        self.roi_polygon = geometry.polygon()

    def detect(self, frame: np.ndarray) -> tuple[list[Detection], list[Detection]]:
        h, w = frame.shape[:2]
        results = self.model.predict(
            frame, conf=self.cfg.conf_threshold, imgsz=self.cfg.infer_imgsz, verbose=False
        )[0]
        names = results.names

        on_track: list[Detection] = []
        off_track: list[Detection] = []

        for box in results.boxes:
            cls_name = names[int(box.cls[0])]
            if cls_name not in self.cfg.hazard_classes:
                continue

            x1, y1, x2, y2 = box.xyxy[0].tolist()
            area_frac = ((x2 - x1) * (y2 - y1)) / (w * h)
            if area_frac > self.cfg.max_box_area_frac:
                continue

            bbox_h = y2 - y1
            display_name = self.cfg.display_name_override.get(cls_name, cls_name)
            det = Detection(
                cls=display_name,
                confidence=float(box.conf[0]),
                box=(x1, y1, x2, y2),
                bbox_height=bbox_h,
                distance_m=estimate_distance_m(cls_name, bbox_h),
            )

            ground_point = (int((x1 + x2) / 2), int(y2))
            if point_in_polygon(ground_point, self.roi_polygon):
                det.risk = risk_level(bbox_h, h, self.cfg.risk_bands)
                on_track.append(det)
            else:
                off_track.append(det)

        return on_track, off_track
