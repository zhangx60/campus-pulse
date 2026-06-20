# Devpost Submission Draft

## Project Title

CampusPulse

## Tagline

Campus energy intelligence that finds wasted power before it becomes invisible.

## Inspiration

As a UCI student, I see campus buildings shift between crowded, half-used, and empty throughout the day. Energy systems often do not adapt that quickly. CampusPulse explores how student builders can use Python, sensor-style data, and a clear dashboard to help universities spot preventable energy waste.

## What It Does

CampusPulse analyzes simulated campus occupancy and energy readings across six university buildings. It detects abnormal energy spikes, ranks inefficient building periods, estimates potential kWh and emissions savings, and recommends operational actions such as tuning HVAC schedules during low-use periods.

## How We Built It

The project uses a Python standard-library backend in `app.py` to generate the dataset, calculate trends, detect anomalies, estimate savings, and serve API endpoints. The dashboard is built with HTML, CSS, and JavaScript so judges can open and use it immediately without installing packages.

## Python Usage

Python powers the core product logic:

- synthetic campus sensor data generation;
- hourly aggregation and building comparisons;
- anomaly detection using z-score and energy-per-person intensity;
- recommendation ranking by avoidable kWh;
- JSON and CSV API serving.

## Challenges

The main challenge was making the project feel like a real product while keeping it easy for judges to run. I chose a dependency-free Python backend so the submission remains reliable and transparent.

## Accomplishments

- Built an end-to-end data product from raw readings to recommendations.
- Designed a clear dashboard for both technical and non-technical users.
- Made the analysis explainable with downloadable CSV data and readable scoring.

## What I Learned

I learned how much product clarity matters in data tools. A model or chart is only useful if the user can immediately see what changed, why it matters, and what action to take next.

## What's Next

CampusPulse could connect to real IoT meters, room booking data, weather APIs, or campus facilities dashboards. It could also support student sustainability challenges where teams measure the impact of behavior and scheduling changes over time.

## Demo Video Outline

1. Problem: campus buildings waste energy when schedules do not match actual usage.
2. Show dashboard summary: savings, anomalies, occupancy, trends.
3. Click a building and explain energy-per-person intensity.
4. Show anomaly queue and recommendations.
5. Explain Python backend and downloadable CSV.
6. Close with impact: a student-built tool for campus sustainability teams.
