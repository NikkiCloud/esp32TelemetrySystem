import statistics
import datetime
import json

class StatisticCalculator:
    def __init__(self, filename: str):
        self.entries = self.read_jsonl_file(filename)
        self.mean = self.calculate_mean()
        self.min = self.calculate_min()
        self.max = self.calculate_max()
        self.median = self.calculate_median()

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

    def extrat_value_list(self, key: str = "temperatureCelcius") -> list[float]:       
        value_list = []
        for entry in self.entries:
            if key in entry:
                try :
                    value_list.append(float(entry[key]))
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
             
    """ def get_data_from_key(self, key: str = "temperatureCelcius"):
        return [entry[key] for entry in self.data if key in entry] """
        
def main():
    filename = "data.jsonl"
    stats_calculator = StatisticCalculator(filename)
    print(f"Mean: {stats_calculator.mean}")
    print(f"Min: {stats_calculator.min}")
    print(f"Max: {stats_calculator.max}")
    print(f"Median: {stats_calculator.median}")
    

if __name__ == "__main__":
    main()


