from django.contrib.auth.models import User
from rest_framework import serializers
from ..models import  Company, EmissionFactor
from decimal import Decimal


# commercial real estate
class CommercialRealEstateEmissionFactorSerializer(serializers.Serializer):
    building_name = serializers.CharField(max_length=200)
    outstanding_loan = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_property_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    floor_area = serializers.DecimalField(max_digits=15, decimal_places=2)
    energy_consumption = serializers.DecimalField(max_digits=15, decimal_places=4, required=False, allow_null=True)
    emission_factor = serializers.DecimalField(max_digits=15, decimal_places=4, required=False, allow_null=True)

    def validate(self, data):
        if data["outstanding_loan"] <= 0 or data["total_property_value"] <= 0:
            raise serializers.ValidationError("Loan and property value must be positive numbers.")
        if data.get("energy_consumption") is not None and data["energy_consumption"] <= 0:
            raise serializers.ValidationError("Reported Energy Consumption must be a positive number.")
        if data.get("emission_factor") is not None and data["emission_factor"] <= 0:
            raise serializers.ValidationError("Emission factor must be a positive number.")
        return data


class CommercialRealEstateSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True
    )
    asset_class = serializers.CharField(max_length=200)
    emission_factor = CommercialRealEstateEmissionFactorSerializer()
    data_quality_score = serializers.IntegerField()

    def validate(self, data):
        emission_factor_data = data.get("emission_factor")
        if emission_factor_data:
            if emission_factor_data["outstanding_loan"] <= 0 or emission_factor_data["total_property_value"] <= 0:
                raise serializers.ValidationError("Loan and property cost must be positive numbers in emission factor.")
        return data

    def create(self, validated_data):
        emission_factor_data = validated_data["emission_factor"]
        user_id = validated_data["user_id"]
        outstanding_loan = emission_factor_data["outstanding_loan"]
        total_property_value = emission_factor_data["total_property_value"]
        energy_consumption = emission_factor_data.get("energy_consumption")
        emission_factor = emission_factor_data.get("emission_factor")
        floor_area = emission_factor_data.get("floor_area")

        pcaf_level = 2
        financed_emissions = None
        total_emissions = None

        if energy_consumption and emission_factor:
            pcaf_level = 1
            total_emissions = energy_consumption * emission_factor
            financed_emissions = (outstanding_loan / total_property_value) * total_emissions
        else:
            benchmark_emissions = {
                "North America": 0.15,
                "Europe": 0.12,
                "Asia": 0.10,
            }
            total_emissions = Decimal(benchmark_emissions["North America"]) * floor_area
            financed_emissions = (outstanding_loan / total_property_value) * total_emissions

        emission_data = {
            "building_name": emission_factor_data["building_name"],
            "outstanding_loan": float(outstanding_loan),
            "total_property_value": float(total_property_value),
            "floor_area": float(floor_area),
            "energy_consumption": float(energy_consumption) if energy_consumption else None,
            "emission_factor": float(emission_factor) if emission_factor else None,
            "total_emissions": float(total_emissions),
            "financed_emissions": float(financed_emissions),
            "pcaf_level": pcaf_level,
        }

        user = User.objects.get(id=user_id.id)
        EmissionFactor.objects.create(
            user_id=user,
            asset_class=validated_data["asset_class"],
            emission_factors=emission_data,
            data_quality_score=pcaf_level,
        )

        response_data = {
            "asset_class": validated_data["asset_class"],
            "emission_factor": emission_factor_data,
            "total_emissions": float(total_emissions),
            "financed_emissions": float(financed_emissions),
            "data_quality_score": pcaf_level,
        }

        return response_data