# CampusPulse

CampusPulse is a Python-powered campus energy intelligence dashboard built for Devpost submissions. It simulates building-level occupancy and energy sensor readings, detects inefficient usage patterns, ranks anomalies, estimates avoidable energy, and presents the results in a polished browser dashboard.

## Why It Matters

Universities run many buildings that are only partially occupied at certain hours, yet HVAC and lighting schedules often remain fixed. CampusPulse gives student sustainability teams and facilities staff a simple way to spot waste, explain it, and prioritize concrete interventions.

## Features

- Python-generated sensor dataset for six campus buildings
- Anomaly detection for energy spikes and high energy-per-person readings
- Hourly energy load visualization
- Building-level energy intensity ranking
- Action recommendations with estimated kWh and CO2 impact
- Downloadable CSV for auditability
- No external runtime dependencies

## Run Locally

```bash
python3 app.py
```

Then open:

```text
http://127.0.0.1:8000
```

To regenerate the synthetic dataset:

```bash
python3 app.py --regen-data
```

## How Python Is Used

The backend in `app.py` uses Python to:

- generate realistic timestamped occupancy and energy readings;
- calculate per-building averages, trends, and kWh-per-person intensity;
- detect anomalies with z-score and intensity thresholds;
- estimate avoidable energy and emissions;
- serve JSON and CSV endpoints from a local web server.

## Devpost Fit

This project is suitable for:

- Built with Python Hackathon: Python is central to the analytics and data-serving layer.
- Mind the Product: the product targets a real campus operations problem with a clear user and measurable value.
- VoltHacks: the concept uses IoT-style sensor data, AI-assisted recommendations, and real-world sustainability impact.
