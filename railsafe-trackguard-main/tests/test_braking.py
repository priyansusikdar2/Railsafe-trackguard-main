"""Unit tests for railsafe_trackguard.core.braking.BrakingSystem."""

import pytest

from railsafe_trackguard.config import BrakingConfig
from railsafe_trackguard.core.braking import BrakingSystem


def make_system(brake_rate=0.1, accel_rate=0.1, grace_frames=5):
    cfg = BrakingConfig(brake_rate=brake_rate, accel_rate=accel_rate, grace_frames=grace_frames)
    return BrakingSystem(cfg)


class TestBrakingSystem:
    def test_starts_at_full_speed(self):
        sys_ = make_system()
        assert sys_.speed == 1.0
        assert sys_.stopped is False

    def test_decelerates_when_hazard_present(self):
        sys_ = make_system(brake_rate=0.1)
        speed = sys_.update(hazard_present=True)
        assert speed == 0.9

    def test_reaccelerates_when_clear_and_grace_expired(self):
        sys_ = make_system(brake_rate=0.1, accel_rate=0.05, grace_frames=0)
        sys_.update(hazard_present=True)  # speed -> 0.9
        speed = sys_.update(hazard_present=False)  # grace expired immediately
        assert speed == pytest.approx(0.95)

    def test_grace_period_holds_brake_through_short_gaps(self):
        sys_ = make_system(brake_rate=0.1, accel_rate=0.05, grace_frames=3)
        sys_.update(hazard_present=True)  # speed 0.9, frames_since_alert=0
        # 3 frames with no detection, still within grace period
        for _ in range(3):
            speed = sys_.update(hazard_present=False)
        # should still be braking (not accelerating) through the grace window
        assert speed < 0.9

    def test_reaches_full_stop_and_marks_stopped(self):
        sys_ = make_system(brake_rate=0.5)
        sys_.update(hazard_present=True)  # 0.5
        sys_.update(hazard_present=True)  # 0.0
        assert sys_.speed == 0.0
        assert sys_.stopped is True

    def test_speed_never_goes_negative(self):
        sys_ = make_system(brake_rate=0.9)
        for _ in range(5):
            sys_.update(hazard_present=True)
        assert sys_.speed == 0.0

    def test_speed_never_exceeds_one(self):
        sys_ = make_system(accel_rate=0.5)
        for _ in range(10):
            sys_.update(hazard_present=False)
        assert sys_.speed == 1.0

    def test_status_text_reports_stopped(self):
        sys_ = make_system(brake_rate=1.0)
        sys_.update(hazard_present=True)  # speed -> 0.0
        text, _ = sys_.status_text(hazard_present=True)
        assert "STOPPED" in text
