from datetime import datetime
from statistic_calculator import StatisticCalculator
from rich import print as rprint
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Group


class Dashboard:
    def __init__(self, statistics_calculator: StatisticCalculator):
        self.statistics_calculator = statistics_calculator


    def create_snapshot_dict(self) -> dict: 
        snapshot = {
            "last_entry" : self.statistics_calculator.entries[-1] if self.statistics_calculator.entries else None,
            "statistics":  {
            "mean": self.statistics_calculator.calculate_mean(),
            "min": self.statistics_calculator.calculate_min(),
            "max": self.statistics_calculator.calculate_max(),
            "median": self.statistics_calculator.calculate_median()
            },
            "status": "LIVE",
            "missing_msg": self.statistics_calculator.detect_missing_messages(),
            "anomalies": {
            "out_of_range": self.statistics_calculator.out_of_range_detection(),
            "sudden_changes": self.statistics_calculator.sudden_change_detection()
        }
        }
        return snapshot
    
def main():
    stats_cal = StatisticCalculator("data.jsonl")
    dashboard = Dashboard(stats_cal)
    snapshot = dashboard.create_snapshot_dict()

    if snapshot["last_entry"]:
        last_update = datetime.fromtimestamp(snapshot['last_entry']['received at'])
    else :
       last_update = "No data received yet"
    
    msg_total = len(stats_cal.entries)
    total_missing_msgs, total_gaps = stats_cal.detect_missing_messages()

    if snapshot["last_entry"]:
        temperatureC = snapshot['last_entry']["temperatureCelcius"]
    else:
        temperatureC = "N/A"
    
    if snapshot["last_entry"]:
        humidity = snapshot['last_entry']["humidityPercent"]
    else:
        humidity = "N/A"

    if snapshot["last_entry"]:
        heat_index_celcius = snapshot['last_entry']["heatIndexCelcius"]
    else:
        heat_index_celcius = "N/A"

    if snapshot["last_entry"]:
        timestamp = snapshot['last_entry']["timestamp"]
    else:
        timestamp = "N/A"

    layout = Layout()
    layout.split_column(
        Layout(name="header", size =6),
        Layout(name="upper_body", ratio= 3),
        Layout(name="lower_body", ratio=1)
    )
    panel_group_header = Group(
        Panel("Dashboard | Broker: CONNECTED | Topic: esp32/dht11_sensor"),
        Panel(f"Last update: {last_update} | Received Messages : {msg_total} | Gaps: {total_gaps} | Missing messages: {total_missing_msgs}"),
    )
    layout["header"].update(panel_group_header)

    panel_group_upper = Group(
        Panel("Current Sensor Values (from last message received)\n" \
        "-------------------------------------------------------------\n" \
        f"Temperature (celcius): {temperatureC} \n"
        f"Humidity (%): {humidity}\n"
        f"Heat Index (celcius): {heat_index_celcius} \n"
        f"Device: esp32/dht11_sensor\n"
        f"Timestamp: {timestamp}\n"
        f"Received at: {last_update}\n"
        ),
    )
    layout["upper_body"].update(panel_group_upper)
    rprint(layout)

if __name__ == "__main__":
    main()
