from setuptools import setup, find_packages

setup(
    name="railsafe-trackguard",
    version="1.0.0",
    description="Real-time railway obstacle detection with ROI filtering and automatic braking",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.9",
    install_requires=[
        "ultralytics>=8.3.0",
        "opencv-python-headless>=4.9.0",
        "numpy>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "railsafe-trackguard=railsafe_trackguard.cli:main",
        ],
    },
)
