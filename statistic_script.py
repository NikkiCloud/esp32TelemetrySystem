import statistics
import datetime
import json

class StatisticCalculator:
    def __init__(self, data):
        self.data = data
        self.mean = self.calculate_mean()
        self.min = self.calculate_min()
        self.max = self.calculate_max()
        self.median = self.calculate_median()

    def calculate_mean(self, key: str = "temperatureCelcius"):
        if self.data:
            return statistics.mean(self.data)
        else: 
            return None

    def calculate_min(self, key: str = "temperatureCelcius"):
        if self.data:
            return min(self.data)
        else:
            return None
    
    def calculate_max(self, key: str = "temperatureCelcius"):
        if self.data:
            return max(self.data)
        else:
            return None
    
    def calculate_median(self, key: str = "temperatureCelcius"):
        if self.data:
            return statistics.median(self.data)
        else:
            return None       
    def get_data_from_key(self, key: str = "temperatureCelcius"):
        return [entry[key] for entry in self.data if key in entry]
        
def main():
    filename = "data.jsonl"
    with open(filename, "r") as read_file:
            try:
                data =  json.load(read_file)
            except : 
                raise ValueError("Error reading JSON data from file " + filename)
    
    statistic_calculator = StatisticCalculator(data)

if __name__ == "__main__":
    main()


