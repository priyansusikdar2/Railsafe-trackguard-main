"""Command-line entry point."""

from __future__ import annotations

import argparse

from railsafe_trackguard.config import DetectionConfig
from railsafe_trackguard.pipeline import RailSafeTrackGuard


def main():
    ap = argparse.ArgumentParser(description="RailSafe-TrackGuard: railway obstacle detection + auto-braking")
    ap.add_argument("--source", required=True, help="video path or '0' for webcam")
    ap.add_argument("--output", default="output.mp4", help="annotated output video path")
    ap.add_argument("--model", default="yolo11n.pt", help="YOLO weights (COCO or custom)")
    ap.add_argument("--conf", type=float, default=0.25, help="confidence threshold")
    ap.add_argument("--no-freeze", action="store_true", help="disable freeze-on-stop visual behavior")
    args = ap.parse_args()

    det_cfg = DetectionConfig(conf_threshold=args.conf)
    pipeline = RailSafeTrackGuard(
        model_path=args.model, det_cfg=det_cfg, freeze_on_stop=not args.no_freeze,
    )
    pipeline.process(args.source, args.output)


if __name__ == "__main__":
    main()
