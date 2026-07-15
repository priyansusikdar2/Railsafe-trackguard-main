# 🚆 **RailSafe-TrackGuard**

## **📌 Overview**
RailSafe-TrackGuard is an AI-powered railway safety system designed to detect obstacles on railway tracks in real time. The project combines computer vision, ROI-based filtering, distance estimation, and an automatic emergency braking simulation to improve railway operational safety and reduce accident risks.

---

# **✨ Key Features**

- 🚆 **Real-Time Track Monitoring**
  - Continuously monitors railway tracks using computer vision.

- 🎯 **Obstacle Detection**
  - Detects people, vehicles, animals, and other obstacles on railway tracks.

- 📍 **ROI (Region of Interest) Filtering**
  - Eliminates false detections outside the railway track area.

- 📏 **Distance Estimation**
  - Estimates the distance between the train and detected obstacles.

- 🚨 **Cabin Alarm System**
  - Activates warning alarms when dangerous obstacles are detected.

- 🛑 **Automatic Emergency Braking Simulation**
  - Simulates train braking when collision risk exceeds the safety threshold.

- 📊 **Visual Detection Overlay**
  - Displays bounding boxes, labels, warning indicators, and braking status.

---

# **🛠️ Technology Stack**

- **Language:** Python
- **Computer Vision:** OpenCV
- **Object Detection:** YOLO
- **Numerical Computing:** NumPy
- **Configuration:** Python Config Files

---

# **📂 Project Structure**

```
railsafe-trackguard/
│── railsafe_trackguard/
│   ├── core/
│   ├── utils/
│   ├── pipeline.py
│   ├── cli.py
│   └── config.py
│
├── screenshots/
├── requirements.txt
├── README.md
└── .gitignore
```

---

# **⚙️ Installation**

### **1. Clone the Repository**

```bash
git clone <repository-url>
cd railsafe-trackguard
```

### **2. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3. Run the Project**

```bash
python -m railsafe_trackguard.cli
```

---

# **🚄 System Workflow**

1. Capture video frames.
2. Detect railway tracks.
3. Detect obstacles using AI.
4. Apply ROI filtering.
5. Estimate obstacle distance.
6. Trigger warning alarm.
7. Simulate emergency braking.
8. Display real-time output.

---

# **📸 Output**

The application provides:

- ✅ Live obstacle detection
- ✅ Railway track highlighting
- ✅ Distance estimation
- ✅ Cabin warning alerts
- ✅ Emergency brake simulation
- ✅ Real-time visualization

---

# **🎯 Applications**

- Railway Safety Monitoring
- Smart Transportation Systems
- Autonomous Railway Research
- AI-Based Surveillance
- Accident Prevention Systems
- Computer Vision Research

---

# **🔮 Future Enhancements**

- GPS integration
- LiDAR sensor support
- Multiple camera synchronization
- Real-time train speed estimation
- Cloud monitoring dashboard
- Railway signaling integration
- Edge AI deployment
- Night vision optimization

---

# **🤝 Contributing**

Contributions are welcome!

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push the branch.
5. Submit a Pull Request.

---

# **📄 License**

This project is intended for educational, research, and demonstration purposes. Modify the license according to your project requirements before public release.

---

# **👨‍💻 Author**

**RailSafe-TrackGuard Development Team**

---

# **⭐ Support**

If you found this project useful, consider giving it a **⭐ Star** and sharing it with others interested in AI-powered railway safety systems.
