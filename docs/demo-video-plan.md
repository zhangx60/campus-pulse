# CampusPulse Demo Video Plan

Target length: 60 to 90 seconds.

Recommended title: CampusPulse - Python Campus Energy Intelligence

Recommended upload setting: YouTube unlisted, Vimeo unlisted, or Google Drive link with "Anyone with the link can view".

## One-Sentence Hook

CampusPulse helps universities find wasted building energy by turning campus occupancy and power readings into Python-powered alerts, savings estimates, and action recommendations.

## Recording Setup

1. Open the app at `http://127.0.0.1:8010/`.
2. Use a 16:9 browser window, ideally 1440 x 900 or 1920 x 1080.
3. Hide unnecessary tabs and bookmarks.
4. Record screen only, or screen plus voice if you are comfortable.
5. Move slowly when scrolling so judges can read the charts.

## Shot List

1. 0:00-0:08 - Opening
   Show the hero section and the "Python analytics live" panel.

2. 0:08-0:22 - Problem and metrics
   Point out the summary metrics: total energy, occupancy, potential savings, anomaly count.

3. 0:22-0:40 - Signals
   Show the hourly energy chart, building filters, anomaly queue, and building performance table.

4. 0:40-0:58 - Actions
   Scroll to Recommended interventions and explain that actions are ranked by avoidable kWh.

5. 0:58-1:12 - Data and Python backend
   Show Recent sensor readings and the Download CSV link. Mention that Python generates data, analyzes it, detects anomalies, and serves JSON/CSV endpoints.

6. 1:12-1:25 - Closing
   Return to the top or actions section and close with the campus sustainability value.

## Voiceover Script

Hi, I am Isabel Zhang, a UCI student, and this is CampusPulse.

CampusPulse is a Python-powered campus energy dashboard that helps universities find wasted building energy before it becomes invisible.

The app analyzes simulated occupancy and energy readings across campus buildings. At the top, it summarizes the current energy picture, estimated savings, emissions impact, and anomaly count.

Python handles the core analytics behind the dashboard. It generates campus sensor-style data, aggregates hourly energy load, compares buildings, detects unusual spikes, and ranks recommendations by avoidable kilowatt-hours.

In the Signals section, judges can see how campus energy changes by hour, which buildings are drifting, and which readings deserve attention. The anomaly queue explains why a spike matters, such as HVAC being left on or cooling drift during low-use periods.

The Actions section turns that analysis into next steps. Instead of only showing charts, CampusPulse recommends operational interventions like tuning HVAC windows when occupancy is low.

The project is intentionally easy to run. It uses a Python standard-library backend with a static HTML, CSS, and JavaScript dashboard, so judges can inspect it without installing external packages.

Next, CampusPulse could connect to real meters, room-booking data, weather APIs, or UCI facilities dashboards to support smarter campus sustainability decisions.

## Devpost Video Description

CampusPulse is a Python-powered dashboard for finding wasted campus building energy. It analyzes occupancy and kWh readings, detects abnormal spikes, estimates savings, and recommends campus operations actions such as HVAC schedule tuning.

## Project Media Upload Order

1. `media/campuspulse-cover.png` - polished cover image for the project.
2. `media/campuspulse-dashboard.png` - main product screenshot.
3. `media/campuspulse-signals.png` - energy chart, filters, and anomaly queue.
4. `media/campuspulse-actions.png` - ranked recommendations and savings logic.
5. `media/campuspulse-data.png` - data table and CSV/API credibility.

## Final Devpost Checklist

1. Paste the video URL into the Devpost video/demo field.
2. Upload the four images above to Project Media.
3. Confirm the GitHub URL is `https://github.com/zhangx60/campus-pulse`.
4. Preview the public project page.
5. Submit before June 27, 2026 at 5:00 PM PDT.
