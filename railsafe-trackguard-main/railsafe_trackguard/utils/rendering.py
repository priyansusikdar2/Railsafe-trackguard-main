"""HUD rendering: ROI overlay, alert banner, bounding boxes, object panel."""

from __future__ import annotations

import cv2
import numpy as np

from railsafe_trackguard.config import DetectionConfig
from railsafe_trackguard.core.braking import BrakingSystem
from railsafe_trackguard.core.models import Detection


class HUDRenderer:
    def __init__(self, cfg: DetectionConfig, roi_polygon: list[tuple[int, int]]):
        self.cfg = cfg
        self.roi_polygon = roi_polygon

    def draw_roi(self, frame: np.ndarray, active: bool) -> None:
        overlay = frame.copy()
        pts = np.array(self.roi_polygon, dtype=np.int32)
        color = (0, 0, 255) if active else (0, 220, 90)
        cv2.fillPoly(overlay, [pts], color)
        cv2.addWeighted(overlay, 0.12, frame, 0.88, 0, dst=frame)
        cv2.polylines(frame, [pts], True, color, 2, cv2.LINE_AA)

    def draw_banner(self, frame: np.ndarray, active: bool, top_risk: str,
                     count: int, brake: BrakingSystem) -> None:
        h, w = frame.shape[:2]
        banner_h = 50
        color = (0, 0, 200) if active else (30, 120, 30)
        cv2.rectangle(frame, (0, 0), (w, banner_h), color, -1)
        text = f"OBSTACLE ON TRACK | RISK: {top_risk} | {count} object(s)" if active else "TRACK CLEAR"
        cv2.putText(frame, text, (14, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        brake_text, brake_color = brake.status_text(active)
        (tw, th), _ = cv2.getTextSize(brake_text, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
        cv2.rectangle(frame, (0, banner_h), (tw + 24, banner_h + 34), (20, 20, 20), -1)
        cv2.putText(frame, brake_text, (12, banner_h + 25), cv2.FONT_HERSHEY_SIMPLEX,
                    0.65, brake_color, 2, cv2.LINE_AA)

        bar_w, bar_h = 220, 14
        bx, by = w - bar_w - 16, 16
        cv2.rectangle(frame, (bx, by), (bx + bar_w, by + bar_h), (60, 60, 60), -1)
        fill_w = int(bar_w * brake.speed)
        bar_color = (0, 200, 0) if brake.speed > 0.5 else (0, 140, 255) if brake.speed > 0.05 else (0, 0, 255)
        cv2.rectangle(frame, (bx, by), (bx + fill_w, by + bar_h), bar_color, -1)
        cv2.rectangle(frame, (bx, by), (bx + bar_w, by + bar_h), (255, 255, 255), 1)

    def draw_detections(self, frame: np.ndarray, on_track: list[Detection],
                         off_track: list[Detection], show_ignored: bool = True) -> str:
        if show_ignored:
            for d in off_track:
                x1, y1, x2, y2 = map(int, d.box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (140, 140, 140), 1)
                cv2.putText(frame, f"{d.cls} (off-track)", (x1, max(0, y1 - 6)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (160, 160, 160), 1, cv2.LINE_AA)

        risk_rank = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        top_risk = "LOW"
        for d in on_track:
            x1, y1, x2, y2 = map(int, d.box)
            color = self.cfg.risk_colors[d.risk]
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            dist_txt = f" {d.distance_m:.0f}m" if d.distance_m else ""
            label = f"{d.cls} {d.confidence:.2f}{dist_txt} | {d.risk}"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 6, y1), color, -1)
            cv2.putText(frame, label, (x1 + 3, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 1, cv2.LINE_AA)
            if risk_rank[d.risk] > risk_rank[top_risk]:
                top_risk = d.risk
        return top_risk

    def draw_cabin_alarm(self, frame: np.ndarray, active: bool, frame_idx: int) -> None:
        """Pulsing red border + cabin alarm text while a hazard is on-track,
        simulating an audible-alarm-style visual warning for the driver."""
        if not active:
            return
        h, w = frame.shape[:2]
        pulse = 0.5 + 0.5 * abs((frame_idx % 12) - 6) / 6  # triangular pulse, ~2Hz at 24fps
        thickness = int(10 + 14 * pulse)
        color = (0, 0, int(200 + 55 * pulse))
        cv2.rectangle(frame, (0, 0), (w - 1, h - 1), color, thickness)

        text = "!! CABIN ALARM - OBSTACLE ON TRACK !!"
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        tx, ty = (w - tw) // 2, h - 24
        if pulse > 0.5:
            cv2.rectangle(frame, (tx - 10, ty - th - 8), (tx + tw + 10, ty + 8), (0, 0, 0), -1)
            cv2.putText(frame, text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (255, 255, 255), 2, cv2.LINE_AA)

    def draw_object_panel(self, frame: np.ndarray, on_track: list[Detection],
                           off_track: list[Detection]) -> None:
        h, w = frame.shape[:2]
        entries = sorted(on_track, key=lambda d: d.distance_m or 9e9) + off_track
        if not entries:
            return

        line_h, pad, panel_w = 22, 10, 330
        panel_h = pad * 2 + line_h * (len(entries) + 1)
        px0, py0 = 10, h - panel_h - 10

        overlay = frame.copy()
        cv2.rectangle(overlay, (px0, py0), (px0 + panel_w, py0 + panel_h), (15, 15, 15), -1)
        cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, dst=frame)
        cv2.rectangle(frame, (px0, py0), (px0 + panel_w, py0 + panel_h), (90, 90, 90), 1)
        cv2.putText(frame, "DETECTED OBJECTS", (px0 + pad, py0 + pad + 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        y = py0 + pad + 14 + line_h
        for d in entries:
            if d.risk:
                color = self.cfg.risk_colors[d.risk]
                dist_txt = f"{d.distance_m:.0f}m (est.)" if d.distance_m else "--"
                line = f"{d.cls:<10} {d.confidence*100:>3.0f}%  {dist_txt:>10}  {d.risk}"
            else:
                color = (140, 140, 140)
                line = f"{d.cls:<10} {d.confidence*100:>3.0f}%  off-track (ignored)"
            cv2.putText(frame, line, (px0 + pad, y), cv2.FONT_HERSHEY_SIMPLEX, 0.48, color, 1, cv2.LINE_AA)
            y += line_h
