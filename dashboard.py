from datetime import UTC, datetime
import time
from statistic_calculator import StatisticCalculator
from rich import print as rprint
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Group, Console
from rich.live import Live


    
def build_layout(filename: str) -> Layout: 
    stats_cal = StatisticCalculator(filename)
    snapshot = {
        "last_entry" : stats_cal.entries[-1] if stats_cal.entries else None,
        "statistics":  {
            "mean": stats_cal.calculate_mean(),
            "min": stats_cal.calculate_min(),
            "max": stats_cal.calculate_max(),
            "median": stats_cal.calculate_median()
        },
        "status": "LIVE",
        "missing_msg": stats_cal.detect_missing_messages(),
        "anomalies": {
            "out_of_range": stats_cal.out_of_range_detection(),
            "sudden_changes": stats_cal.sudden_change_detection()
        }
    }

    # --- LIVE vs STALE ---
    if snapshot["last_entry"]:
        last_received = float(snapshot["last_entry"]["received at"])
        now = time.time()
        delta_sec = now - last_received

        expected = getattr(stats_cal, "EXPECTED_MESSAGE_INTERVAL_SECONDS", 10)
        tolerance = getattr(stats_cal, "TOLERANCE_SECONDS", 1)
        seuil = (expected * 2) + tolerance

        status = "LIVE" if delta_sec <= seuil else "OFFLINE"
        last_update_dt = datetime.fromtimestamp(snapshot['last_entry']['received at'], tz=UTC)
        last_update_str = last_update_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    else:
        delta_sec = None
        status = "OFFLINE"
        last_update_str = "No data received yet"
    
    msg_total = len(stats_cal.entries)
    total_missing_msgs, total_gaps = stats_cal.detect_missing_messages()

    if snapshot["last_entry"]:
        temperatureC = snapshot["last_entry"].get("temperatureCelcius", "N/A")
        humidity = snapshot["last_entry"].get("humidityPercent", "N/A")
        heat_index_celcius = snapshot["last_entry"].get("heatIndexCelcius", "N/A")
        device_timestamp = snapshot["last_entry"].get("timestamp", "N/A")
    else:
        temperatureC = humidity = heat_index_celcius = device_timestamp = "N/A"
    
    alerts: list[tuple[float, str]] = []
    out_of_range_entries = snapshot["anomalies"]["out_of_range"]
    for issue in out_of_range_entries:
        entry = issue.get("entry", {})
        ra = entry.get("received at", None)
        t_str = format_time_hhmmss(ra)

        key = issue.get("key", "unknown_key")
        value = issue.get("value", "N/A")
        valid_range = issue.get("valid_range", ("?", "?"))
    
        try:
                min_v, max_v = valid_range
                range_str = f"{min_v}..{max_v}"
        except Exception:
            range_str = str(valid_range)
    
        line = f"{t_str}  Out of range {key}: {value} ({range_str})"
        # sort key: received_at if possible, else 0
        alerts.append((float(ra) if ra is not None else 0.0, line))

    sudden_change_entries = snapshot["anomalies"]["sudden_changes"]
    for issue in sudden_change_entries:
        entry = issue.get("entry", {})
        ra = entry.get("received at", None)
        t_str = format_time_hhmmss(ra)

        key = issue.get("key", "unknown_key")
        prev_v = issue.get("previous_value", "N/A")
        curr_v = issue.get("value", "N/A")
        max_jump = issue.get("max_jump", "N/A")

        line = f"{t_str}  Sudden jump {key}: {prev_v} -> {curr_v} (max {max_jump})"
        alerts.append((float(ra) if ra is not None else 0.0, line))

    alerts.sort(key=lambda x: x[0])
    last_alert_lines = [line for _, line in alerts[-10:]]
    if not last_alert_lines:
        last_alert_lines = ["(no alerts)"]
    
    alerts_text = (
        "ALERTS (last 10)\n"
        "------------------------------\n"
        + "\n".join(last_alert_lines)
    )

    # --- layout ---
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=6),
        Layout(name="body"),
    )
    layout["body"].split_row(
        Layout(name="right_body", ratio=2),
        Layout(name="left_body", ratio=1),
    )

    header_group = Group(
        Panel("Dashboard | Broker: CONNECTED | Topic: esp32/dht11_sensor"),
        Panel(
            f"Status: {status} | "
            f"Last update: {last_update_str} | "
            + (f"Data age: {delta_sec:.1f}s | " if delta_sec is not None else "")
            + f"Received: {msg_total} | Gaps: {total_gaps} | Missing: {total_missing_msgs}"
        ),
    )
    layout["header"].update(header_group)

    right_panel = Panel(
        "Current Sensor Values (from last message received)\n"
        "--------------------------------------------------\n"
        f"Temperature (C): {temperatureC}\n"
        f"Humidity (%): {humidity}\n"
        f"Heat Index (C): {heat_index_celcius}\n"
        f"Device: esp32/dht11_sensor\n"
        f"Device timestamp (ms since boot): {device_timestamp}\n"
        f"Received at (UTC): {last_update_str}\n"
    )
    layout["right_body"].update(right_panel)

    layout["left_body"].update(Panel(alerts_text))
    return layout
    
def format_time_hhmmss(received_at: float | int | None) -> str:
    if received_at is None:
        return "??:??:??"
    
    dt = datetime.fromtimestamp(float(received_at), tz=UTC)
    return dt.strftime("%H:%M:%S")
    
def main():
    console = Console()
    filename = "data.jsonl"
    #live refresh loop
    with Live(build_layout(filename), console=console, refresh_per_second=2, screen=True) as live:
        while True:
            live.update(build_layout(filename))
            time.sleep(5)  #refresh interval 1sec

if __name__ == "__main__":
    main()
