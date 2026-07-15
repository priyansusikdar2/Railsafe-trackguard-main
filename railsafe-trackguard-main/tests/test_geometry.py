"""Unit tests for railsafe_trackguard.utils.geometry.

These test real behavior against known values, not placeholders.
"""

import pytest

from railsafe_trackguard.utils.geometry import (
    point_in_polygon, risk_level, estimate_distance_m,
)


class TestPointInPolygon:
    def setup_method(self):
        # simple square for predictable testing
        self.square = [(0, 0), (100, 0), (100, 100), (0, 100)]

    def test_point_inside(self):
        assert point_in_polygon((50, 50), self.square) is True

    def test_point_outside(self):
        assert point_in_polygon((150, 50), self.square) is False

    def test_point_on_border(self):
        assert point_in_polygon((0, 50), self.square) is True

    def test_trapezoid_roi_wider_at_bottom(self):
        # mimics a real track ROI: narrow at horizon, wide at the bottom
        roi = [(590, 260), (650, 260), (1000, 720), (280, 720)]
        assert point_in_polygon((620, 265), roi) is True   # near horizon, inside
        assert point_in_polygon((100, 265), roi) is False  # near horizon, off to the side
        assert point_in_polygon((500, 700), roi) is True   # near bottom, inside (wide here)


class TestRiskLevel:
    BANDS = [(0.55, "CRITICAL"), (0.32, "HIGH"), (0.16, "MEDIUM"), (0.0, "LOW")]

    def test_critical_when_object_fills_most_of_frame(self):
        assert risk_level(bbox_height=450, frame_h=720, bands=self.BANDS) == "CRITICAL"

    def test_low_when_object_is_small(self):
        assert risk_level(bbox_height=20, frame_h=720, bands=self.BANDS) == "LOW"

    def test_boundary_is_inclusive(self):
        # exactly at the HIGH threshold (0.32 * 720 = 230.4)
        assert risk_level(bbox_height=230.4, frame_h=720, bands=self.BANDS) == "HIGH"


class TestEstimateDistance:
    def test_larger_bbox_means_closer_object(self):
        far = estimate_distance_m("person", bbox_height_px=30)
        near = estimate_distance_m("person", bbox_height_px=300)
        assert near < far

    def test_zero_height_returns_none(self):
        assert estimate_distance_m("car", bbox_height_px=0) is None

    def test_unknown_class_falls_back_to_default_height(self):
        # should not raise, should use the 1.5m fallback
        result = estimate_distance_m("kangaroo", bbox_height_px=100)
        assert result is not None
        assert result > 0
