import statistics
import datetime
import json

from pydantic import InstanceOf

class StatisticCalculator:
    def __init__(self, filename: str, expected_msg_interval_millisec: int = 10000, tolerance_millisec: float = 1.01):
        self.entries = self.read_jsonl_file(filename)
        self.mean = self.calculate_mean()
        self.min = self.calculate_min()
        self.max = self.calculate_max()
        self.median = self.calculate_median()
        self.EXPECTED_MESSAGE_INTERVAL_MILLISECONDS = expected_msg_interval_millisec
        self.TOLERANCE_MESSAGE_INTERVAL = tolerance_millisec

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

    def extrat_value_list(self, key: str = "temperatureCelcius") -> list[float|int]:       
        value_list = []
        for entry in self.entries:
            if key in entry:
                try :
                    value_list.append(entry[key])
                except (ValueError, TypeError):
                    continue
        return value_list


    def calculate_mean(self, key: str = "temperatureCelcius"):
            value_list = self.extrat_value_list(key)
            if value_list:
                return statistics.mean(value_list)
            else:
                return None

    def calculate_min(self, key: str = "temperatureCelcius"):
        value_list = self.extrat_value_list(key)
        if value_list:
            return min(value_list)
        else:
            return None
    
    def calculate_max(self, key: str = "temperatureCelcius"):
        value_list = self.extrat_value_list(key)
        if value_list:
            return max(value_list)
        else:
            return None
    
    def calculate_median(self, key: str = "temperatureCelcius"):
        value_list = self.extrat_value_list(key)
        if value_list:
            return statistics.median(value_list)
        else:
            return None  
             
    def calculate_timestamp_delta(self):
        timestamp_list = self.extrat_value_list("timestamp")
        #print(timestamp_list[0:5])
        timestamp_list.sort()
        #print(timestamp_list[0:5])
        delta_timestamp_list = []
        for i in range(1, len(timestamp_list)):
            delta_timestamp_list.append(timestamp_list[i] - timestamp_list[i-1])
        return delta_timestamp_list


    def detect_missing_messages(self):
        delta_timestamp_list = self.calculate_timestamp_delta()
        number_of_gaps = 0
        for delta in delta_timestamp_list:
            if(delta > self.EXPECTED_MESSAGE_INTERVAL_MILLISECONDS * self.TOLERANCE_MESSAGE_INTERVAL):
                number_of_gaps += 1
                number_of_missing_msg = round(delta/self.EXPECTED_MESSAGE_INTERVAL_MILLISECONDS) - 1
                print(
                f"Total messages: {len(delta_timestamp_list) + number_of_missing_msg} \n"
                f"Expected interval (in seconds): {self.EXPECTED_MESSAGE_INTERVAL_MILLISECONDS/1000} \n"
                f"Delta observed (in seconds): {delta/1000} \n"
                f"Estimated number of missing messages: {number_of_missing_msg} \n"
                f"Number of gaps (meaning how many interruption occured) {number_of_gaps}\n")

        
def main():
    filename = "data.jsonl"
    stats_calculator = StatisticCalculator(filename)
    print(f"Mean: {stats_calculator.mean}")
    print(f"Min: {stats_calculator.min}")
    print(f"Max: {stats_calculator.max}")
    print(f"Median: {stats_calculator.median}")
    print("\nDetecting missing messages...")
    stats_calculator.detect_missing_messages();
    

if __name__ == "__main__":
    main()


