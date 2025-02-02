from django.contrib.auth.models import User
from rest_framework import serializers
from ..models import EmissionFactor

# motor vehicle
class MotorEmissionFactorDetailsSerializer(serializers.Serializer):
    vehicle_name = serializers.CharField(max_length=200)
    outstanding_loan = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_vehicle_cost = serializers.DecimalField(max_digits=15, decimal_places=2)
    vehicle_type = serializers.ChoiceField(choices=["Petrol", "Diesel", "Hybrid", "Electric"])
    annual_fuel_consumption = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    emission_factor = serializers.DecimalField(max_digits=15, decimal_places=4, required=False, allow_null=True)
    
    def validate(self, data):
        if data["outstanding_loan"] <= 0 or data["total_vehicle_cost"] <= 0:
            raise serializers.ValidationError("Loan and vehicle cost must be positive numbers.")
        if data.get("annual_fuel_consumption") is not None and data["annual_fuel_consumption"] <= 0:
            raise serializers.ValidationError("Annual fuel consumption must be a positive number.")
        if data.get("emission_factor") is not None and data["emission_factor"] <= 0:
            raise serializers.ValidationError("Emission factor must be a positive number.")
        return data


class MotorVehicleLoanSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True
    )
    asset_class = serializers.CharField(max_length=200)
    emission_factor = MotorEmissionFactorDetailsSerializer()
    data_quality_score = serializers.IntegerField()

    def validate(self, data):
        emission_factor_data = data.get("emission_factor")
        if emission_factor_data:
            if emission_factor_data["outstanding_loan"] <= 0 or emission_factor_data["total_vehicle_cost"] <= 0:
                raise serializers.ValidationError("Loan and vehicle cost must be positive numbers in emission factor.")
        return data

    def create(self, validated_data):
        emission_factor_data = validated_data["emission_factor"]
        user_id = validated_data["user_id"]
        outstanding_loan = emission_factor_data["outstanding_loan"]
        total_vehicle_cost = emission_factor_data["total_vehicle_cost"]
        annual_fuel_consumption = emission_factor_data.get("annual_fuel_consumption")
        emission_factor = emission_factor_data.get("emission_factor")

        pcaf_level = 2
        financed_emissions = None
        total_emissions = None

        if annual_fuel_consumption and emission_factor:
            pcaf_level = 1
            total_emissions = annual_fuel_consumption * emission_factor
            financed_emissions = (outstanding_loan / total_vehicle_cost) * total_emissions
        else:
            benchmark_emissions = {
                "Petrol": 2.31,
                "Diesel": 2.68,
                "Hybrid": 1.5,
                "Electric": 0.0,
            }
            total_emissions = benchmark_emissions[emission_factor_data["vehicle_type"]] * 2000
            financed_emissions = (outstanding_loan / total_vehicle_cost) * total_emissions

        emission_data = {
            "vehicle_name": emission_factor_data["vehicle_name"],
            "outstanding_loan": float(outstanding_loan),
            "total_vehicle_cost": float(total_vehicle_cost),
            "vehicle_type": emission_factor_data["vehicle_type"],
            "annual_fuel_consumption": float(annual_fuel_consumption) if annual_fuel_consumption else None,
            "emission_factor": float(emission_factor) if emission_factor else None,
            "total_emissions": round(float(total_emissions), 4),
            "financed_emissions": round(float(financed_emissions), 4),
            "pcaf_level": pcaf_level,
        }
        user = User.objects.get(id=user_id.id)
        EmissionFactor.objects.create(
            user_id=user,
            asset_class=validated_data["asset_class"],
            emission_factors=emission_data,
            data_quality_score=pcaf_level
        )
        response_data = {
            "asset_class": validated_data["asset_class"],
            "data_quality_score": pcaf_level,
            "emission_factor": emission_factor_data,
            "total_emissions": round(float(total_emissions),4),
            "financed_emissions": round(float(financed_emissions),4),
        }

        return response_data


