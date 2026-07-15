"""Automatic braking state machine.

Tracks a virtual train speed in [0.0, 1.0] that decelerates when a hazard
is on-track and re-accelerates once clear, with a short grace period so a
single missed detection frame doesn't prematurely release the brake.
"""

from __future__ import annotations

from railsafe_trackguard.config import BrakingConfig


class BrakingSystem:
    def __init__(self, cfg: BrakingConfig):
        self.cfg = cfg
        self.speed = 1.0
        self.frames_since_alert = 999
        self.stopped = False

    def update(self, hazard_present: bool) -> float:
        if hazard_present:
            self.frames_since_alert = 0
        else:
            self.frames_since_alert += 1

        braking = hazard_present or self.frames_since_alert <= self.cfg.grace_frames
        if braking:
            self.speed = max(0.0, self.speed - self.cfg.brake_rate)
        else:
            self.speed = min(1.0, self.speed + self.cfg.accel_rate)

        if self.speed == 0.0 and not self.stopped:
            self.stopped = True
        return self.speed

    def status_text(self, hazard_present: bool) -> tuple[str, tuple[int, int, int]]:
        pct = int(self.speed * 100)
        if self.speed < 0.03:
            return "TRAIN STOPPED", (0, 0, 255)
        if hazard_present:
            return f"EMERGENCY BRAKING - SPEED {pct}%", (0, 140, 255)
        if self.speed < 0.98:
            return f"RE-ACCELERATING - SPEED {pct}%", (0, 200, 255)
        return f"SPEED {pct}%", (200, 255, 200)
