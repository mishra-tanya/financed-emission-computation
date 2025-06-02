from ..helpers.motor import MotorVehicleCalculator
from django.contrib.auth.models import User
from ..models import EmissionFactor

class MotorVehicleService:
    def __init__(self, validated_data):
        self.validated_data = validated_data
        self.ef = validated_data["emission_factor"]
        self.asset_class = validated_data["asset_class"]
        self.calculator = MotorVehicleCalculator(
            loan=self.safe_float(self.ef.get("outstanding_loan")),
            total_value=self.safe_float(self.ef.get("original_value"))
        )
        self.attribution_factor = self.calculator.get_attribution_factor()
        self.method = None
        self.data_quality_score = None

    def safe_float(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def process(self):
        self.method = self.select_method()
        emission_result = self.calculate_emissions()
        formatted_result = self.format_output(emission_result)
        self.save_emission_data(formatted_result)
        return formatted_result

    def select_method(self):
        ef = self.ef

        if ef.get("actual_fuel_yes_or_no") == "Yes":
            self.data_quality_score = 1
            return "1a"
        elif ef.get("actual_distance_data_yes_or_no") == "Yes" and ef.get("vehicle_make"):
            self.data_quality_score = 1
            return "1b"
        elif ef.get("vehicle_make") and ef.get("country") and ef.get("region"):
            self.data_quality_score = 2
            return "2a"
        elif ef.get("vehicle_make") and ef.get("country"):
            self.data_quality_score = 3
            return "2b"
        elif ef.get("vehicle_type") and ef.get("fuel_type"):
            self.data_quality_score = 4
            return "3a"
        else:
            self.data_quality_score = 5
            return "3b"

    def calculate_emissions(self):
        ef = self.ef
        attr = self.attribution_factor
        method = self.method

        if method == "1a":
            fuel = self.safe_float(ef.get("fuel_consumption"))
            fuel_type = ef.get("fuel_type") or "unknown"
            region = ef.get("region") or "unknown"
            emission_factor = self.calculator.get_emission_factor(fuel_type, region)
            financed_emissions = attr * fuel * emission_factor

        elif method == "1b":
            distance = self.safe_float(ef.get("distance_traveled"))
            distance_unit = ef.get("distance_unit") or "km"
            distance_km = self.calculator.convert_distance_to_km(distance, distance_unit)
            efficiency = self.calculator.get_vehicle_efficiency(
                ef.get("vehicle_make"),
                ef.get("vehicle_model"),
                ef.get("model_year")
            )

            is_hybrid = ef.get("percentage_yes_or_no") == "Yes"
            if is_hybrid:
                electric_percent = self.safe_float(ef.get("percentage_electric")) / 100 or 0.4
                fuel_eff = efficiency.get("fuel", 0)
                elec_eff = efficiency.get("electric", 0)

                fuel_emission_factor = self.calculator.get_emission_factor(ef.get("fuel_type", "unknown"), ef.get("region", "unknown"))
                electricity_emission_factor = self.calculator.get_emission_factor("electricity", ef.get("region", "unknown"))

                fuel_emissions = attr * distance_km * fuel_eff * (1 - electric_percent) * fuel_emission_factor
                elec_emissions = attr * distance_km * elec_eff * electric_percent * electricity_emission_factor

                financed_emissions = fuel_emissions + elec_emissions
            else:
                emission_factor = self.calculator.get_emission_factor(ef.get("fuel_type", "unknown"), ef.get("region", "unknown"))
                financed_emissions = attr * distance_km * efficiency.get("fuel", 0) * emission_factor

        else:
            financed_emissions = attr * 100

        loan_amount = self.safe_float(ef.get("outstanding_loan"))
        emission_intensity = financed_emissions / loan_amount if loan_amount != 0 else 0

        return {
            "financed_emissions": financed_emissions,
            "emission_intensity": emission_intensity
        }

    def format_output(self, calc):
        ef = self.ef
        format = self.calculator.format_or_na

        return {
            "heading1": "Loan Details",
            "loan_id": ef.get("loan_id", "N/A"),
            "outstanding_loan": self.safe_float(ef.get("outstanding_loan")),
            "original_value": self.safe_float(ef.get("original_value")),
            "currency": ef.get("currency", "N/A"),

            "heading2": "Attribution Factor",
            "attribution_factor": format(self.attribution_factor),

            "heading3": "Method and Score",
            "method_used": self.method,
            "data_quality_score": self.data_quality_score,

            "heading4": "Emission Result",
            "financed_emissions": format(calc["financed_emissions"]),
            "emission_intensity": format(calc["emission_intensity"]),
        }

    def save_emission_data(self, data):
        EmissionFactor.objects.create(
            user_id=User.objects.get(id=self.validated_data["user_id"].id),
            asset_class=self.asset_class,
            emission_factors=data,
            data_quality_score=self.data_quality_score
        )
