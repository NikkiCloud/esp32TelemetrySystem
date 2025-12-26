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

    
    

    layout = Layout()
    layout.split_column(
        Layout(name="header"),
        Layout(name="upper_body", ratio= 1),
        Layout(name="lower_body", ratio=1)
    )
    panel_group_header = Group(
        Panel("Dashboard | Broker: CONNECTED | Topic: esp32/dht11_sensor"),
        Panel(f"Last update: {last_update} | Received Messages : {msg_total} | Gaps: {total_gaps} | Missing messages: {total_missing_msgs}"),
    )
    layout["header"].update(panel_group_header)
    rprint(layout)

if __name__ == "__main__":
    main()
