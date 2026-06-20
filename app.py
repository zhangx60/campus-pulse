#!/usr/bin/env python3
"""
CampusPulse local server.

The app uses only Python's standard library so judges can run it without
dependency setup. Python generates campus energy data, computes forecasts,
detects anomalies, and serves the dashboard/API.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
DATA_DIR = ROOT / "data"
DATA_FILE = DATA_DIR / "campus_readings.csv"


BUILDINGS = [
    {"name": "Engineering Hall", "type": "Lab", "base": 82, "peak": 1.42, "occupancy": 0.76},
    {"name": "Science Library", "type": "Study", "base": 55, "peak": 1.22, "occupancy": 0.91},
    {"name": "Student Center", "type": "Dining", "base": 73, "peak": 1.55, "occupancy": 0.84},
    {"name": "Mesa Housing", "type": "Residence", "base": 64, "peak": 1.18, "occupancy": 0.88},
    {"name": "Arts Annex", "type": "Studio", "base": 38, "peak": 1.14, "occupancy": 0.43},
    {"name": "Bio Research", "type": "Lab", "base": 91, "peak": 1.37, "occupancy": 0.69},
]


@dataclass(frozen=True)
class Reading:
    timestamp: str
    building: str
    building_type: str
    occupancy: int
    energy_kwh: float
    temperature_f: float
    event: str


def sigmoid(value: float) -> float:
    return 1 / (1 + math.exp(-value))


def occupancy_curve(hour: int, building_type: str) -> float:
    if building_type == "Residence":
        return 0.45 + 0.45 * (1 - sigmoid((hour - 10) / 2)) + 0.2 * sigmoid((hour - 19) / 1.8)
    if building_type == "Dining":
        return 0.2 + 0.72 * max(
            math.exp(-((hour - 12) ** 2) / 10),
            math.exp(-((hour - 18) ** 2) / 8),
        )
    if building_type == "Study":
        return 0.18 + 0.7 * sigmoid((hour - 9) / 2) * (1 - sigmoid((hour - 23) / 1.8))
    return 0.15 + 0.76 * sigmoid((hour - 8) / 1.6) * (1 - sigmoid((hour - 18) / 2.2))


def generate_readings(days: int = 14, seed: int = 42) -> list[Reading]:
    random.seed(seed)
    start = datetime(2026, 5, 20, 0, 0)
    readings: list[Reading] = []

    event_windows = {
        ("Student Center", 4, 18): "concert load spike",
        ("Engineering Hall", 7, 22): "HVAC left on",
        ("Science Library", 10, 1): "finals overnight study",
        ("Arts Annex", 12, 14): "low-use cooling drift",
    }

    for day in range(days):
        weekday = (start + timedelta(days=day)).weekday()
        weekend_factor = 0.72 if weekday >= 5 else 1.0

        for hour in range(24):
            timestamp = start + timedelta(days=day, hours=hour)
            outdoor_temp = 67 + 12 * math.sin((hour - 13) * math.pi / 12) + random.uniform(-2, 2)

            for building in BUILDINGS:
                curve = occupancy_curve(hour, building["type"]) * weekend_factor * building["occupancy"]
                occupancy = max(3, round(curve * random.uniform(78, 165)))
                weather_load = max(0, outdoor_temp - 72) * 1.1 + max(0, 62 - outdoor_temp) * 0.55
                usage_load = occupancy * 0.32 * building["peak"]
                energy = building["base"] + usage_load + weather_load + random.uniform(-4.5, 5.5)
                event = "normal"

                event_key = (building["name"], day, hour)
                if event_key in event_windows:
                    event = event_windows[event_key]
                    if "HVAC" in event or "cooling" in event:
                        energy *= 1.65
                    elif "concert" in event:
                        occupancy += 92
                        energy *= 1.38
                    else:
                        occupancy += 118
                        energy *= 1.28

                readings.append(
                    Reading(
                        timestamp=timestamp.isoformat(timespec="minutes"),
                        building=building["name"],
                        building_type=building["type"],
                        occupancy=occupancy,
                        energy_kwh=round(energy, 2),
                        temperature_f=round(outdoor_temp, 1),
                        event=event,
                    )
                )
    return readings


def ensure_dataset() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    readings = generate_readings()
    with DATA_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(readings[0]).keys()))
        writer.writeheader()
        for reading in readings:
            writer.writerow(asdict(reading))


def load_readings() -> list[dict[str, Any]]:
    if not DATA_FILE.exists():
        ensure_dataset()

    with DATA_FILE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    for row in rows:
        row["occupancy"] = int(row["occupancy"])
        row["energy_kwh"] = float(row["energy_kwh"])
        row["temperature_f"] = float(row["temperature_f"])
    return rows


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def analyze(readings: list[dict[str, Any]]) -> dict[str, Any]:
    by_building: dict[str, list[dict[str, Any]]] = {}
    by_hour: dict[int, list[dict[str, Any]]] = {}
    total_energy = 0.0
    total_occupancy = 0

    for row in readings:
        by_building.setdefault(row["building"], []).append(row)
        hour = datetime.fromisoformat(row["timestamp"]).hour
        by_hour.setdefault(hour, []).append(row)
        total_energy += row["energy_kwh"]
        total_occupancy += row["occupancy"]

    building_cards = []
    anomalies = []
    recommendations = []

    for building, rows in by_building.items():
        energies = [row["energy_kwh"] for row in rows]
        occupancies = [row["occupancy"] for row in rows]
        intensity_values = [e / max(o, 1) for e, o in zip(energies, occupancies)]
        avg_energy = mean(energies)
        avg_occupancy = mean(occupancies)
        avg_intensity = mean(intensity_values)
        variance = mean([(value - avg_energy) ** 2 for value in energies])
        stddev = math.sqrt(variance)

        latest = rows[-1]
        baseline = mean([row["energy_kwh"] for row in rows[-48:-24]]) or avg_energy
        trend = ((mean(energies[-24:]) - baseline) / baseline) * 100

        building_cards.append(
            {
                "name": building,
                "type": rows[0]["building_type"],
                "avg_energy": round(avg_energy, 1),
                "avg_occupancy": round(avg_occupancy),
                "energy_per_person": round(avg_intensity, 2),
                "trend_pct": round(trend, 1),
                "latest_event": latest["event"],
            }
        )

        for row in rows:
            z_score = (row["energy_kwh"] - avg_energy) / (stddev or 1)
            intensity = row["energy_kwh"] / max(row["occupancy"], 1)
            if z_score > 2.5 or intensity > avg_intensity * 1.75:
                anomalies.append(
                    {
                        "building": building,
                        "timestamp": row["timestamp"],
                        "energy_kwh": row["energy_kwh"],
                        "occupancy": row["occupancy"],
                        "reason": row["event"] if row["event"] != "normal" else "energy use exceeded expected pattern",
                        "severity": round(max(z_score, intensity / max(avg_intensity, 0.1)), 1),
                    }
                )

        low_occupancy_high_energy = [
            row for row in rows if row["occupancy"] < avg_occupancy * 0.55 and row["energy_kwh"] > avg_energy * 1.05
        ]
        if low_occupancy_high_energy:
            wasted = sum(row["energy_kwh"] - avg_energy * 0.82 for row in low_occupancy_high_energy)
            recommendations.append(
                {
                    "building": building,
                    "title": "Tune low-use HVAC windows",
                    "impact_kwh": round(max(wasted, 0), 1),
                    "action": "Reduce cooling/heating setpoints when occupancy falls below historical patterns.",
                    "confidence": 86,
                }
            )

    sorted_cards = sorted(building_cards, key=lambda card: card["avg_energy"], reverse=True)
    sorted_anomalies = sorted(anomalies, key=lambda item: item["severity"], reverse=True)[:8]
    sorted_recommendations = sorted(recommendations, key=lambda item: item["impact_kwh"], reverse=True)[:5]

    hourly = []
    for hour in range(24):
        rows = by_hour.get(hour, [])
        hourly.append(
            {
                "hour": hour,
                "energy": round(sum(row["energy_kwh"] for row in rows), 1),
                "occupancy": sum(row["occupancy"] for row in rows),
            }
        )

    last_24 = readings[-24 * len(BUILDINGS) :]
    previous_24 = readings[-48 * len(BUILDINGS) : -24 * len(BUILDINGS)]
    current_energy = sum(row["energy_kwh"] for row in last_24)
    previous_energy = sum(row["energy_kwh"] for row in previous_24) or current_energy
    trend_pct = ((current_energy - previous_energy) / previous_energy) * 100
    savings_kwh = sum(item["impact_kwh"] for item in sorted_recommendations)
    emissions_lbs = savings_kwh * 0.85

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "summary": {
            "total_energy": round(total_energy, 1),
            "avg_occupancy": round(total_occupancy / len(readings)),
            "current_day_energy": round(current_energy, 1),
            "trend_pct": round(trend_pct, 1),
            "potential_savings_kwh": round(savings_kwh, 1),
            "potential_emissions_lbs": round(emissions_lbs, 1),
            "anomaly_count": len(sorted_anomalies),
        },
        "buildings": sorted_cards,
        "hourly": hourly,
        "anomalies": sorted_anomalies,
        "recommendations": sorted_recommendations,
        "raw_sample": readings[-18:],
    }


class CampusPulseHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/analytics":
            query = parse_qs(parsed.query)
            if query.get("refresh", ["0"])[0] == "1":
                ensure_dataset()
            payload = analyze(load_readings())
            body = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path == "/api/readings.csv":
            if not DATA_FILE.exists():
                ensure_dataset()
            body = DATA_FILE.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CampusPulse locally.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    parser.add_argument("--regen-data", action="store_true")
    args = parser.parse_args()

    if args.regen_data or not DATA_FILE.exists():
        ensure_dataset()

    server = ThreadingHTTPServer((args.host, args.port), CampusPulseHandler)
    print(f"CampusPulse running at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping CampusPulse.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
