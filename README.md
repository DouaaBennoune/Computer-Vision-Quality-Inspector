#   AI Quality Inspector & IIoT Factory Simulator

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-yellow)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![MQTT](https://img.shields.io/badge/MQTT-Mosquitto-660066?logo=eclipse-mosquitto)
![Factory IO](https://img.shields.io/badge/Factory%20IO-PLC%20Simulation-orange)

An enterprise-grade **Computer Vision and Industrial IoT (IIoT) system** designed to detect manufacturing defects on steel surfaces in real-time. 

Moving beyond standard AI notebooks, this project is a fully containerized microservice architecture. It streams live video via WebSockets, runs YOLOv8 inference at the edge, and triggers physical factory hardware (PLCs) via MQTT and Modbus TCP to halt production when critical defects are found.

## System Architecture

1. **Frontend (Streamlit & WebRTC):** Provides a modern dashboard for batch uploads and live camera streaming.
2. **Backend (FastAPI & WebSockets):** Handles async REST requests, unzips/validates batch data, and processes 30 FPS video streams natively.
3. **AI Engine (Ultralytics YOLOv8):** Custom-trained on the **NEU-DET Steel Defect Dataset** (6 classes: *crazing, inclusion, patches, pitted surface, rolled-in scale, scratches*).
4. **IIoT Gateway (MQTT & Modbus TCP):** Bridges the software/hardware gap. The AI publishes emergency alerts to a Dockerized Mosquitto MQTT broker, which an Edge Gateway script translates into Modbus TCP signals to control a 3D Factory I/O conveyor belt.

##  Key Engineering Challenges Solved

### 1. Physics-Based Synthetic Data Generation (Domain Shift)
Standard AI models fail in real-world factories due to harsh shadows and glare. I identified that standard linear HSV augmentation artificially *increases* the contrast of dark defects, causing the model to overfit to lab conditions. 
* **The Solution:** I engineered an offline Python pipeline applying a **Non-Linear Highlight Compression Curve** and **Gaussian ISO Sensor Noise**. This forced the model to learn spatial *feature invariance* rather than pixel intensity, maintaining a high mAP in actual low-light deployment environments.

### 2. Business Logic Rules Engine (Defect Severity)
Not all manufacturing defects require stopping a production line. I implemented a real-time severity engine:
* **Critical Defects (Inclusion, Crazing, Pitted Surface):** Instantly triggers an MQTT emergency stop if even 1 is detected.
* **Accumulation Defects (Scratches, Patches):** Utilizes a threshold logic (e.g., stop only if ≥ 3 scratches are clustered in a single frame), minimizing unnecessary factory downtime.
* **Safety Latching:** Once a machine stops, it is locked out until a human operator safely clears the defect and manually resets the line.

### 3. IT/OT Hardware Convergence (Cloud to PLC)
The AI never controls the machine directly (an industry security best-practice). Instead, FastAPI publishes QoS-verified packets to an MQTT Broker. A separate Python Edge Gateway subscribes to this topic, translates the payload, and writes physical bit states to a Modbus TCP server (`Coil 0`) to halt the motors.


## Home Page
<img width="2478" height="1402" alt="image" src="https://github.com/user-attachments/assets/22383f7f-3c37-47af-9eec-feb24a2a6dfa" />


## Upload Page
<img width="2491" height="1407" alt="image" src="https://github.com/user-attachments/assets/b97a45cf-a2d4-472c-aa05-158db9304533" />

## dashboard Page
<img width="2488" height="1166" alt="image" src="https://github.com/user-attachments/assets/080cc7f8-6d07-4314-85b2-6fe92922171a" />
<img width="2491" height="860" alt="image" src="https://github.com/user-attachments/assets/c9fa20b7-db05-4217-bda6-4b55a2b83354" />

## PLC simulation Page
<img width="2484" height="1401" alt="image" src="https://github.com/user-attachments/assets/990b8cf7-11d6-4b90-9835-45e303cbd6cc" />

## Documentation Page
<img width="2476" height="1394" alt="image" src="https://github.com/user-attachments/assets/50f820fb-126c-432d-bc6d-a1a0c8c6e267" />

## Quick Start

git clone https://github.com/DouaaBennoune/Computer-Vision-Quality-Inspector.git

cd src

docker compose up --build

## Open the app
Streamlit UI -> http://localhost:8501

FastAPI Swagger docs -> http://localhost:8000/docs

## Factory I/O
To see the AI physically stop a machine:


1. Open Factory I/O.

2. Drag a 6m Conveyor Belt into the scene.

3. Drag another one.

4. Drag objects on the Conveyor Belt to see them moving.

5. Go to File -> Drivers, select Modbus TCP/IP Server, and map Conveyor to Coil 0 and Coil 1.

6. Press Play in Factory I/O.

7. On your local machine, run the Edge Gateway:  python src/gateway.py

8. Go to the Streamlit Live Simulation tab, turn on your webcam, and hold up a picture of an Inclusion defect. Watch the 3D conveyor belt instantly halt!
