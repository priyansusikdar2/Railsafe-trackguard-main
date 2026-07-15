"""Top-level pipeline: wires together the detector, braking system, and
renderer, and drives the video read/process/write loop."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from railsafe_trackguard.config import BrakingConfig, DetectionConfig, TrackGeometry
from railsafe_trackguard.core.braking import BrakingSystem
from railsafe_trackguard.core.detector import TrackObstacleDetector
from railsafe_trackguard.utils.rendering import HUDRenderer


class RailSafeTrackGuard:
    """Real-time railway obstacle detection with ROI filtering, distance
    estimation, and automatic emergency braking simulation.

    Pipeline: PERCEPTION -> HAZARD FILTER -> ROI CHECK -> RISK SCORING ->
    BRAKING RESPONSE -> RENDER.
    """

    def __init__(self, model_path: str = "yolo11n.pt",
                 geometry: Optional[TrackGeometry] = None,
                 det_cfg: Optional[DetectionConfig] = None,
                 brake_cfg: Optional[BrakingConfig] = None,
                 freeze_on_stop: bool = True):
        self.geometry = geometry or TrackGeometry()
        self.det_cfg = det_cfg or DetectionConfig()
        self.brake_cfg = brake_cfg or BrakingConfig()
        self.detector = TrackObstacleDetector(model_path, self.geometry, self.det_cfg)
        self.renderer = HUDRenderer(self.det_cfg, self.geometry.polygon())
        self.freeze_on_stop = freeze_on_stop

    def process(self, source: str, output: str) -> list[dict]:
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open source: {source}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 24
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        Path(output).parent.mkdir(parents=True, exist_ok=True)
        writer = cv2.VideoWriter(output, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

        brake = BrakingSystem(self.brake_cfg)
        alert_log: list[dict] = []
        frame_idx = 0
        stopped_frame: Optional[np.ndarray] = None
        t0 = time.time()

        while frame_idx < total_frames:
            if self.freeze_on_stop and brake.stopped:
                # a stopped train's camera view wouldn't keep changing
                frame = stopped_frame.copy()
            else:
                ok, frame = cap.read()
                if not ok:
                    break

            on_track, off_track = self.detector.detect(frame)
            hazard_present = len(on_track) > 0
            speed = brake.update(hazard_present)

            if self.freeze_on_stop and speed == 0.0 and stopped_frame is None:
                stopped_frame = frame.copy()

            self.renderer.draw_roi(frame, hazard_present)
            top_risk = self.renderer.draw_detections(frame, on_track, off_track)
            self.renderer.draw_banner(frame, hazard_present, top_risk, len(on_track), brake)
            self.renderer.draw_object_panel(frame, on_track, off_track)
            self.renderer.draw_cabin_alarm(frame, hazard_present, frame_idx)

            for d in on_track:
                alert_log.append({
                    "frame": frame_idx, "class": d.cls, "confidence": round(d.confidence, 3),
                    "risk": d.risk, "distance_m_est": round(d.distance_m, 1) if d.distance_m else None,
                    "bbox": [round(v, 1) for v in d.box], "speed": round(speed, 3),
                })

            writer.write(frame)
            frame_idx += 1

        cap.release()
        writer.release()

        elapsed = time.time() - t0
        print(f"Processed {frame_idx} frames in {elapsed:.1f}s ({frame_idx/max(elapsed,1e-6):.1f} FPS)")
        print(f"Total on-track alert events: {len(alert_log)}")

        log_path = str(Path(output).with_suffix("")) + "_alerts.json"
        with open(log_path, "w") as f:
            json.dump(alert_log, f, indent=2)
        print(f"Alert log written to {log_path}")

        return alert_log
