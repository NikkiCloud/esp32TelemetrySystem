import statistics
import datetime
import json
import time

OFFLINE_TIMEOUT_SEC = 30  

class TelemetryAnalyzer:
    def __init__(self, filename: str, expected_msg_interval_sec: int = 10, tolerance_sec: float = 1.5):
        self.entries = self.read_jsonl_file(filename)
        self.entries_by_sensor = self.read_jsonl_file_by_sensor(filename)
        self.mean = self.calculate_mean()
        self.mean_by_sensor = self.calculate_mean_by_sensor()
        self.min = self.calculate_min()
        self.min_by_sensor = self.calculate_min_by_sensor()
        self.max = self.calculate_max()
        self.max_by_sensor = self.calculate_max_by_sensor()
        self.median = self.calculate_median()
        self.median_by_sensor = self.calculate_median_by_sensor()

        self.EXPECTED_MESSAGE_INTERVAL_MILLISECONDS = expected_msg_interval_sec
        self.TOLERANCE_MESSAGE_INTERVAL = tolerance_sec
        self.VALID_RANGES = {
            "temperatureCelcius": (0, 50),
            "temperatureFahrenheit": (32, 122),
            "humidityPercent": (0, 100)
        }
        self.VALID_CHANGES_JUMPS = {
            "temperatureCelcius": 1.5,
            "temperatureFahrenheit": 3.0,
            "humidityPercent": 5.0
        }
        

    def read_jsonl_file(self, filename: str) -> list[dict]:
        entries = []
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if not line :
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print("JSON error:", e)
                    print("Bad line (preview):", line[:120])
                    continue
        return entries

    def read_jsonl_file_by_sensor(self, filename: str) -> dict[str, list[dict]]:
        entries_by_sensor = {}
        for entry in self.entries:
            sensor_id = entry.get("sensor_id")
            if sensor_id:
                if sensor_id not in entries_by_sensor:
                    entries_by_sensor[sensor_id] = []
                entries_by_sensor[sensor_id].append(entry)
        for sensor_id, entries in entries_by_sensor.items():
            entries.sort(key=get_detected_time)
        return entries_by_sensor

    def extrat_value_list(self, key: str = "temperatureCelcius", sensor_id : str| None = None) -> list[float|int]:       
        value_list = []
        entries = self.entries if sensor_id is None else self.entries_by_sensor.get(sensor_id, [])
        for entry in entries:
            if key in entry:
                try :
                    value_list.append(entry[key])
                except (ValueError, TypeError):
                    continue
        return value_list


    def calculate_mean(self, key: str = "temperatureCelcius", sensor_id : str| None = None) -> float|None:
            value_list = self.extrat_value_list(key, sensor_id)
            if value_list:
                return statistics.mean(value_list)
            else:
                return None

    def calculate_mean_by_sensor(self, key: str = "temperatureCelcius") -> dict[str, float|None]:
        value_list_by_sensor = {}
        for sensor_id in self.entries_by_sensor.keys():
            value_list_by_sensor[sensor_id] = self.calculate_mean(key=key, sensor_id=sensor_id)
        return value_list_by_sensor
    
    def calculate_min(self, key: str = "temperatureCelcius", sensor_id : str| None = None) -> float|None:
        value_list = self.extrat_value_list(key, sensor_id)
        if value_list:
            return min(value_list)
        else:
            return None
    
    def calculate_min_by_sensor(self, key: str = "temperatureCelcius") -> dict[str, float|None]:
        value_list_by_sensor = {}
        for sensor_id in self.entries_by_sensor.keys():
            value_list_by_sensor[sensor_id] = self.calculate_min(key=key, sensor_id=sensor_id)
        return value_list_by_sensor
    
    def calculate_max(self, key: str = "temperatureCelcius", sensor_id : str| None = None) -> float|None:
        value_list = self.extrat_value_list(key, sensor_id)
        if value_list:
            return max(value_list)
        else:
            return None
    
    def calculate_max_by_sensor(self, key: str = "temperatureCelcius") -> dict[str, float|None]:
        value_list_by_sensor = {}
        for sensor_id in self.entries_by_sensor.keys():
            value_list_by_sensor[sensor_id] = self.calculate_max(key=key, sensor_id=sensor_id)
        return value_list_by_sensor
    
    def calculate_median(self, key: str = "temperatureCelcius", sensor_id : str| None = None) -> float|None:
        value_list = self.extrat_value_list(key, sensor_id)
        if value_list:
            return statistics.median(value_list)
        else:
            return None  

    def calculate_median_by_sensor(self, key: str = "temperatureCelcius") -> dict[str, float|None]:
        value_list_by_sensor = {}
        for sensor_id in self.entries_by_sensor.keys():
            value_list_by_sensor[sensor_id] = self.calculate_median(key=key, sensor_id=sensor_id)
        return value_list_by_sensor
             
    def calculate_timestamp_delta(self, sensor_id: str) -> list[float]:
        timestamp_list = self.extrat_value_list("received at", sensor_id)
        #print(timestamp_list[0:5])
        timestamp_list.sort()
        #print(timestamp_list[0:5])
        delta_timestamp_list = []
        for i in range(1, len(timestamp_list)):
            delta_timestamp_list.append(timestamp_list[i] - timestamp_list[i-1])
        return delta_timestamp_list


    def detect_missing_messages(self, sensor_id: str) -> tuple[int, int]:
        entries = self.entries_by_sensor.get(sensor_id, [])
        delta_timestamp_list = self.calculate_timestamp_delta(sensor_id)
        total_gaps = 0;
        total_missing_msgs = 0;
        for delta in delta_timestamp_list:
            if(delta > self.EXPECTED_MESSAGE_INTERVAL_MILLISECONDS * self.TOLERANCE_MESSAGE_INTERVAL):
                total_gaps += 1
                number_of_missing_msg = round(delta/self.EXPECTED_MESSAGE_INTERVAL_MILLISECONDS) - 1
                total_missing_msgs += number_of_missing_msg
                print(
                f"Expected interval (in seconds): {self.EXPECTED_MESSAGE_INTERVAL_MILLISECONDS/1000} \n"
                f"Delta observed (in seconds): {delta/1000} \n"
                f"Estimated number of missing messages: {number_of_missing_msg} \n")
                
        print(
            f"Sensor ID: {sensor_id}\n"
            f"Total of recorded messages: {len(entries)}\n"
            f"Total of missing messages: {total_missing_msgs}\n"
            f"Total of expected messages: {len(entries) + total_missing_msgs}\n"
            f"Number of gaps (meaning how many interruption occured) {total_gaps}\n")
        
        return total_missing_msgs, total_gaps
    
    def out_of_range_detection(self, sensor_id: str):
        out_of_range_entries = []
        entries = self.entries_by_sensor.get(sensor_id, [])
        for entry in entries:
            for key, value in entry.items():
                if(key in self.VALID_RANGES):
                    min_value, max_value = self.VALID_RANGES[key]
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        continue
                    if value < min_value or value > max_value:
                        out_of_range_entries.append({"entry": entry, "key": key, "value": value, "valid_range": (min_value, max_value)})
     
        return out_of_range_entries 

    def sudden_change_detection(self, sensor_id: str):
        sudden_change_entries = []
        entries = self.entries_by_sensor.get(sensor_id, [])

        for i in range(1, len(entries)):
            current_entry = entries[i]
            previous_entry = entries[i-1]

            for key, max_jump in self.VALID_CHANGES_JUMPS.items():
                if key in current_entry and key in previous_entry:
                        try:
                            current_value = float(current_entry[key])
                            previous_value = float(previous_entry[key])
                        except (ValueError, TypeError):
                            continue
                        if abs(current_value - previous_value) > max_jump:
                            sudden_change_entries.append({"entry": current_entry, "key": key, "value": current_value, "previous_value": previous_value, "max_jump": max_jump})

        return sudden_change_entries
    
    def is_last_entry_out_of_range(self, sensor_id: str) -> bool:
        entries = self.entries_by_sensor.get(sensor_id, [])
        if not entries:
            return False

        last = entries[-1]
        for key, (min_val, max_val) in self.VALID_RANGES.items():
            if key in last:
                try:
                    value = float(last[key])
                except (ValueError, TypeError):
                    continue
                if value < min_val or value > max_val:
                    return True
        return False


    def is_last_entry_sudden_change(self, sensor_id: str) -> bool:
        entries = self.entries_by_sensor.get(sensor_id, [])
        if len(entries) < 2:
            return False

        last_entry = entries[-1]
        previous_entry = entries[-2]

        for key, max_jump in self.VALID_CHANGES_JUMPS.items():
            if key in last_entry and key in previous_entry:
                try:
                    value_last = float(last_entry[key])
                    value_prev = float(previous_entry[key])
                except (ValueError, TypeError):
                    continue
                if abs(value_last - value_prev) > max_jump:
                    return True
        return False

    def evaluate_sensor_status(self, sensor_id: str):
        reasons = []
        if self.is_last_entry_out_of_range(sensor_id):
            reasons.append("OUT_OF_RANGE")
        if self.is_last_entry_sudden_change(sensor_id):
            reasons.append("SUDDEN_CHANGE")

        status = "ANOMALY" if reasons else "OK"
        return status, reasons

    def out_of_range_detection_recent(self, entries: list[dict]) -> list[dict]:
        issues = []
        for entry in entries:
            for key, (min_value, max_value) in self.VALID_RANGES.items():
                if key not in entry:
                    continue
                try:
                    value = float(entry[key])
                except (ValueError, TypeError):
                    continue
                if value < min_value or value > max_value:
                    issues.append({"entry": entry, "key": key, "value": value, "valid_range": (min_value, max_value)})
        return issues


    def sudden_change_detection_recent(self, entries: list[dict]) -> list[dict]:
        issues = []
        for i in range(1, len(entries)):
            current = entries[i]
            prev = entries[i - 1]
            for key, max_jump in self.VALID_CHANGES_JUMPS.items():
                if key not in current or key not in prev:
                    continue
                try:
                    current_v = float(current[key])
                    prev_v = float(prev[key])
                except (ValueError, TypeError):
                    continue
                if abs(current_v - prev_v) > max_jump:
                    issues.append({"entry": current, "key": key, "value": current_v, "previous_value": prev_v, "max_jump": max_jump})
        return issues


def get_detected_time(entry: dict) -> float:
    return entry.get("received at", 0)


def main():
    filename = "data.jsonl"
    telemetry_analyzer = TelemetryAnalyzer(filename)
    print(f"Mean: {telemetry_analyzer.mean_by_sensor}")
    print(f"Min: {telemetry_analyzer.min_by_sensor}")
    print(f"Max: {telemetry_analyzer.max_by_sensor}")
    print(f"Median: {telemetry_analyzer.median_by_sensor}")
    #print("\nDetecting missing messages...")
    telemetry_analyzer.detect_missing_messages("A01");
    print("\nDetecting out-of-range values...")
    out_of_range_entries = telemetry_analyzer.out_of_range_detection("A01")
    for issue in out_of_range_entries:
        print(f"Out-of-range detected: Key '{issue['key']}' with value {issue['value']} is outside valid range {issue['valid_range']} in entry: {issue['entry']}")
    sudden_change_entries = telemetry_analyzer.sudden_change_detection("A01")
    print("\nDetecting sudden changes...")
    for issue in sudden_change_entries:
        print(f"\nSudden change detected: Key '{issue['key']}' changed from {issue['previous_value']} to {issue['value']} exceeding max jump of {issue['max_jump']} in entry: {issue['entry']}")
    

if __name__ == "__main__":
    main()


