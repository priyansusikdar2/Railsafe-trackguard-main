# RailSafe-TrackGuard

Real-time railway track obstacle detection with ROI-based false-positive filtering, distance estimation, and automatic emergency braking simulation — including a cabin alarm response.

![Track Clear](screenshots/1.png)
![Obstacle Detected](screenshots/2.png)
![Cabin Alarm Active](screenshots/3.png)
![Train Stopped](screenshots/4.png)

## What it does

A computer vision pipeline that watches railway track footage, detects real-world hazards (vehicles, people, animals, debris), filters out anything that isn't actually on the track, estimates how close it is, and triggers an automatic braking response — complete with a cabin alarm — when a genuine threat is confirmed.

**Tested across 5 real-world scenarios:** a stalled vehicle, a level crossing violation, cattle on the tracks, a landslide, and night-vision operation. 700+ detection events logged, with 5+ seconds of warning before a full stop in every case.

## Pipeline

```
Video frame
    │
    ▼
PERCEPTION      YOLOv11 detects all objects in frame
    │
    ▼
HAZARD FILTER   keep only railway-relevant classes above confidence threshold,
                reject oversized boxes (sensor/dashboard artifacts)
    │
    ▼
ROI CHECK       is the object's ground-contact point inside the track polygon?
                (this is what prevents platform/roadside objects from
                triggering false alerts)
    │
    ▼
RISK SCORING    bbox height → distance estimate → LOW/MEDIUM/HIGH/CRITICAL
    │
    ▼
BRAKING         speed state machine: brakes on hazard, holds through brief
                gaps (grace period), releases once clear
    │
    ▼
CABIN ALARM     audible + visual alarm fires while a hazard is confirmed on-track
    │
    ▼
RENDER          ROI polygon, banner, bounding boxes, live object panel
```

## Repository structure

```
railsafe_trackguard/
├── config.py              # TrackGeometry, DetectionConfig, BrakingConfig
├── pipeline.py             # RailSafeTrackGuard — top-level orchestrator
├── cli.py                  # command-line entry point
├── core/
│   ├── models.py            # Detection dataclass
│   ├── detector.py          # TrackObstacleDetector — YOLO + ROI + risk scoring
│   └── braking.py           # BrakingSystem — speed state machine
└── utils/
    ├── geometry.py           # point-in-polygon, risk banding, distance estimation
    └── rendering.py          # HUDRenderer — ROI overlay, banners, object panel

tests/
├── test_geometry.py         # unit tests for geometry/risk/distance
└── test_braking.py          # unit tests for the braking state machine

screenshots/                 # demo screenshots (see below)
```

## Install

```bash
pip install -r requirements.txt
# or, for CLI installation:
pip install -e .
```

## Usage

```bash
python3 -m railsafe_trackguard.cli --source video.mp4 --output output.mp4

# webcam
python3 -m railsafe_trackguard.cli --source 0 --output live_output.mp4
```

### As a library

```python
from railsafe_trackguard.pipeline import RailSafeTrackGuard
from railsafe_trackguard.config import TrackGeometry, DetectionConfig, BrakingConfig

geometry = TrackGeometry(frame_w=1280, frame_h=720, horizon_y=260, vanish_x=640)

pipeline = RailSafeTrackGuard(
    model_path="yolo11n.pt",
    geometry=geometry,
    det_cfg=DetectionConfig(conf_threshold=0.3),
    brake_cfg=BrakingConfig(brake_rate=0.0076),
)
alert_log = pipeline.process("input.mp4", "output.mp4")
```

## Tests

```bash
PYTHONPATH=. pytest tests/ -v
```

18 tests covering ROI geometry (including realistic trapezoid track shapes), risk banding thresholds, distance estimation edge cases, and the full braking state machine.

## Results

| Scenario | Real detections | Outcome |
|---|---|---|
| Stalled vehicle | ✅ verified | Full stop, 7.2s warning |
| Level crossing violation | ✅ verified | Full stop, 5.5s warning |
| Cattle on track | ✅ verified | Full stop |
| Landslide | ⚠️ partial (see notes) | Full stop, 5.5s warning |
| Night-vision operation | ✅ verified | Full stop, ~5.1s warning |

## Design notes & honest limitations

- **Distance estimates are geometric approximations** (pinhole-camera model using an assumed object height and focal length), not calibrated sensor measurements.
- **The area filter** exists because real dashcam/cab footage often has fixed interior elements (window pillars, dashboard edges) that get misclassified as vehicles. This is a pragmatic filter, not a guarantee — tune per camera.
- This is a **research/portfolio prototype**, not a certified safety system. Real deployment would need to solve stopping-distance physics at speed, sensor redundancy, weather robustness, and integration with existing signaling infrastructure (e.g., Kavach in the Indian Railways context).

## Tech stack

Python · OpenCV · Ultralytics YOLOv11 · NumPy · pytest
