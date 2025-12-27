# dashboard.py
# Rich terminal dashboard (multi-sensor) using LAST 20 entries per sensor for stats + anomalies

from datetime import UTC, datetime
import time
import statistics

from backend.telemetry_analyzer import TelemetryAnalyzer

from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console
from rich.live import Live
from rich.columns import Columns


OFFLINE_TIMEOUT_SEC = 15
RECENT_N = 20

def timestamp_to_utc(ts: float | int | None) -> str:
    if ts is None:
        return "N/A"
    try:
        return datetime.fromtimestamp(float(ts), tz=UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return "N/A"


def compute_stats_from_recent(recent_entries: list[dict], key: str) -> dict:
    vals: list[float] = []
    for e in recent_entries:
        if key not in e:
            continue
        try:
            vals.append(float(e[key]))
        except (ValueError, TypeError):
            continue

    if not vals:
        return {"mean": None, "min": None, "max": None, "median": None}

    return {
        "mean": statistics.mean(vals),
        "min": min(vals),
        "max": max(vals),
        "median": statistics.median(vals),
    }

def build_sensor_snapshots(filename: str) -> dict[str, dict]:
    telemetry = TelemetryAnalyzer(filename)
    now = time.time()

    snapshots: dict[str, dict] = {}

    for sensor_id, entries in telemetry.entries_by_sensor.items():
        if not entries:
            snapshots[sensor_id] = {
                "sensor_id": sensor_id,
                "last_entry": None,
                "online": False,
                "age_sec": None,
                "last_update_str": "No data",
                "anomaly_status": "OFFLINE",
                "reasons": ["NO_DATA"],
                "stats_last20": {"temperatureCelcius": {}, "humidityPercent": {}},
                "alerts_last20": [],
            }
            continue

        recent = entries[-RECENT_N:]
        last_entry = entries[-1]

        last_received = float(last_entry.get("received at", 0.0))
        age_sec = now - last_received
        online = age_sec <= OFFLINE_TIMEOUT_SEC

        temp_stats = compute_stats_from_recent(recent, "temperatureCelcius")
        hum_stats = compute_stats_from_recent(recent, "humidityPercent")

        out_range = telemetry.out_of_range_detection_recent(recent)
        sudden_change = telemetry.sudden_change_detection_recent(recent)

        reasons: list[str] = []
        if out_range:
            reasons.append("OUT_OF_RANGE_LAST20")
        if sudden_change:
            reasons.append("SUDDEN_CHANGE_LAST20")

        anomaly_status = "ANOMALY" if reasons else "OK"

        if not online:
            anomaly_status = "OFFLINE"
            reasons = ["NO_RECENT_DATA"]

        alert_lines: list[str] = []

        for issue in out_range[-3:]:
            entry = issue.get("entry", {})
            utc_string = timestamp_to_utc(entry.get("received at"))
            key = issue.get("key", "unknown")
            value = issue.get("value", "N/A")
            valid_range = issue.get("valid_range", ("?", "?"))
            alert_lines.append(f"{utc_string}  Out of range {key}={value} (valid {valid_range[0]}..{valid_range[1]})")

        for issue in sudden_change[-3:]:
            entry = issue.get("entry", {})
            utc_string = timestamp_to_utc(entry.get("received at"))
            key = issue.get("key", "unknown")
            previous_value = issue.get("previous_value", "N/A")
            current_value = issue.get("value", "N/A")
            max_jump = issue.get("max_jump", "N/A")
            alert_lines.append(f"{utc_string}  Sudden change {key}: {previous_value} -> {current_value} (max {max_jump})")

        last_update_str = timestamp_to_utc(last_received)

        snapshots[sensor_id] = {
            "sensor_id": sensor_id,
            "last_entry": last_entry,
            "online": online,
            "age_sec": age_sec,
            "last_update_str": last_update_str,
            "anomaly_status": anomaly_status,
            "reasons": reasons,
            "stats_last20": {
                "temperatureCelcius": temp_stats,
                "humidityPercent": hum_stats,
            },
            "alerts_last20": alert_lines if alert_lines else ["(no alerts in last 20)"],
        }

    return snapshots


def build_sensor_panels(snapshot_by_sensor: dict[str, dict]) -> Columns:
    panels = []
    for sensor_id in sorted(snapshot_by_sensor.keys()):
        s = snapshot_by_sensor[sensor_id]

        online = s["online"]
        state = "ONLINE" if online else "OFFLINE"
        age = s["age_sec"]

        last = s["last_entry"]
        anomaly_status = s["anomaly_status"]
        reasons = s["reasons"]
        alerts = s["alerts_last20"]

        if anomaly_status == "OFFLINE":
            border = "bright_red"
        elif anomaly_status == "ANOMALY":
            border = "bright_yellow"
        else:
            border = "green"

        if last:
            temp = last.get("temperatureCelcius", "N/A")
            hum = last.get("humidityPercent", "N/A")
            received_str = s["last_update_str"]
        else:
            temp = hum = "N/A"
            received_str = "No data"

        reasons_str = ", ".join(reasons) if reasons else "(none)"
        age_str = f"{age:.1f}s" if age is not None else "N/A"

        temp_stats = s["stats_last20"]["temperatureCelcius"]
        humid_stats = s["stats_last20"]["humidityPercent"]

        def format_numeric_stats_for_display(v):
            return "N/A" if v is None else f"{v:.2f}"

        stats_text = (
            f"Temperature (last 20): mean = {format_numeric_stats_for_display(temp_stats.get('mean'))}   "
            f"min ={format_numeric_stats_for_display(temp_stats.get('min'))}  "
            f"max = {format_numeric_stats_for_display(temp_stats.get('max'))}  "
            f"med = {format_numeric_stats_for_display(temp_stats.get('median'))}\n"
            f"Humidity (last 20): mean = {format_numeric_stats_for_display(humid_stats.get('mean'))}  "
            f"min = {format_numeric_stats_for_display(humid_stats.get('min'))}  "
            f"max = {format_numeric_stats_for_display(humid_stats.get('max'))}  "
            f"med = {format_numeric_stats_for_display(humid_stats.get('median'))}   "
        )

        alerts_text = "\n".join(alerts[-6:])

        text = (
            f"[bold]{sensor_id}[/bold]  {state}\n"
            f"Last update: {received_str} | age: {age_str}\n"
            f"Last values: Temp={temp} °C | Humidity={hum} %\n"
            f"Status: {anomaly_status} | reasons: {reasons_str}\n"
            "\n"
            f"[bold]Stats (last {RECENT_N})[/bold]\n"
            f"{stats_text}\n"
            "\n"
            f"[bold]Alerts (from last {RECENT_N})[/bold]\n"
            f"{alerts_text}"
        )

        panels.append(Panel(text, border_style=border))

    return Columns(panels, expand=True)


def build_layout(filename: str) -> Layout:
    snapshot_by_sensor = build_sensor_snapshots(filename)

    total = len(snapshot_by_sensor)
    online_count = sum(1 for s in snapshot_by_sensor.values() if s["online"])
    offline_count = total - online_count
    anomaly_count = sum(1 for s in snapshot_by_sensor.values() if s["anomaly_status"] == "ANOMALY")

    header_text = (
        f"[bold]IoT Dashboard[/bold] | File: {filename} | Window: last {RECENT_N}\n"
        f"Sensors: {total} | Online: {online_count} | Offline: {offline_count} | Anomaly: {anomaly_count}"
    )

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=4),
        Layout(name="body"),
    )

    layout["header"].update(Panel(header_text, border_style="cyan"))
    layout["body"].update(Panel(build_sensor_panels(snapshot_by_sensor), title="Sensors", border_style="magenta"))

    return layout


def main():
    console = Console()
    filename = "data.jsonl"

    with Live(build_layout(filename), console=console, refresh_per_second=2, screen=True) as live:
        while True:
            live.update(build_layout(filename))
            time.sleep(2)


if __name__ == "__main__":
    main()
