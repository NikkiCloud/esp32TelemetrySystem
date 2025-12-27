# ESP32 IoT Environment Monitor

ESP32 IoT Environment Monitor  
An embedded IoT prototype focused on sensor telemetry, reliability, and device monitoring.

## Overview

This project explores how a ESP32-based embedded device behaves in a real connected environment. The focus is on telemetry, reliability, and system behavior when sensor data is transmitted over a network.

An ESP32 reads sensor data and publishes it via MQTT to a Python backend, which logs incoming telemetry and monitors device state. The system is used to observe real-world constraints such as unreliable connectivity, imperfect timing, missing data and abnormal readings and also to understand how the system reacts when these conditions occur.

## Architecture

The system is structured as a telemetry pipeline with clear separation of responsibilities between components.

**Data flow:**

Sensor → ESP32 (C++) → MQTT broker → Python backend → logs and monitoring

### Components

**ESP32 (Firmware - C++)**
- Reads data from a sensor
- Controls sampling timing
- Publishes telemetry messages over MQTT
- Handles basic reliability concerns such as reconnection and invalid readings

**MQTT Broker**
- Acts as the message transport layer between devices and backend
- Decouples embedded firmware from backend processing
- Allows the system to scale to multiple devices without direct coupling

**Backend (Python)**
- Subscribes to MQTT topics and receives telemetry data
- Logs incoming measurements to persistent storage
- Monitors device activity (online/offline detection)
- Performs data analysis and anomaly detection

This separation allows each part of the system to evolve independently and makes it easier to reason about system behavior, failure modes and timing issues in a real connected environment.

## Key Features

**Embedded Device (ESP32)**
- Sensor data acquisition using C++ firmware
- Configurable sampling intervals and periodic publishing
- Automatic Wi-Fi and MQTT reconnection logic 
- Structured MQTT payloads with device identification

**Backend & Monitoring**
- Python backend subscribing to MQTT telemetry
- Persistent logging of sensor data to JSONL files
- Real time device state monitoring (online/offline detection)
- Anomaly detection: out-of-range values, sudden changes, missing messages
- Live terminal dashboard for observing system behavior

## Telemetry Format

Telemetry is published over MQTT using structured topics and an explicit payload format.

### MQTT Topic
```iot/home/{sensor_id}/telemetry```
where `{sensor_id}` identifies the device (e.g. `A01`, `B01`)

### ESP32 Payload
```json
{
  "temperatureCelcius": 23.9,
  "temperatureFahrenheit": 75.02,
  "humidityPercent": 6.0,
  "heatIndexCelcius": 22.5,
  "heatIndexFahrenheit": 72.5,
  "isReadingsValid": true,
  "timestamp_millisec": 14835025
}

```
### Backend Log record
```json
{
  "sensor_id": "A01",
  "temperatureCelcius": 23.9,
  "temperatureFahrenheit": 75.02,
  "humidityPercent": 6.0,
  "heatIndexCelcius": 22.5,
  "heatIndexFahrenheit": 72.5,
  "detected at": 14835025,
  "received at": 1766807441.159206,
  "topic": "iot/home/A01/telemetry"
}
```


