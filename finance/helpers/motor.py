class MotorVehicleCalculator:
    def __init__(self, loan, total_value):
        self.loan = float(loan)
        self.total_value = float(total_value)

    def get_attribution_factor(self):
        try:
            return self.loan / self.total_value
        except ZeroDivisionError:
            return 0

    @staticmethod
    def format_or_na(value):
        return "{:.4f}".format(value) if isinstance(value, (int, float)) else "NA"

    @staticmethod
    def convert_distance_to_km(value, unit):
        if unit == "miles":
            return float(value) * 1.60934
        return float(value)

    @staticmethod
    def get_emission_factor(fuel_type, region):
        emission_map = {
            ("petrol", "India"): 2.31,
            ("diesel", "India"): 2.68,
            ("electricity", "India"): 0.92,
        }
        return emission_map.get((fuel_type.lower(), region), 2.5)

    @staticmethod
    def get_vehicle_efficiency(make, model=None, year=None):
        return {
            "fuel": 0.08,
            "electric": 0.02
        }
