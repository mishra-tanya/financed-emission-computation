from django.contrib.auth.models import User
from rest_framework import serializers
from ..models import  Company, EmissionFactor

# project finance
class ProjectFinanceDetailsSerializer(serializers.Serializer):
    project_name = serializers.CharField(max_length=200)
    outstanding_loan = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_project_cost = serializers.DecimalField(max_digits=15, decimal_places=2)
    project_phase = serializers.CharField(max_length=200)
    reported_emissions = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    activity_data = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    emission_factor = serializers.DecimalField(max_digits=15, decimal_places=4, required=False, allow_null=True)

    def validate(self, data):
        if data["outstanding_loan"] <= 0 or data["total_project_cost"] <= 0:
            raise serializers.ValidationError("Loan and project cost must be positive numbers.")
        
        if data.get("activity_data") is not None and data.get("emission_factor") is None:
            raise serializers.ValidationError("Emission factor must be provided if activity data is available.")
        
        return data


class ProjectFinanceSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True
    )
    asset_class = serializers.CharField(max_length=200)
    emission_factor = ProjectFinanceDetailsSerializer()
    data_quality_score = serializers.IntegerField()

    def validate(self, data):
        emission_factor_data = data.get("emission_factor")
        if emission_factor_data:
            if emission_factor_data["outstanding_loan"] <= 0 or emission_factor_data["total_project_cost"] <= 0:
                raise serializers.ValidationError("Loan and project cost must be positive numbers in emission factor.")
        return data

    def create(self, validated_data):
        emission_factor_data = validated_data["emission_factor"]
        outstanding_loan = emission_factor_data["outstanding_loan"]
        total_project_cost = emission_factor_data["total_project_cost"]
        activity_data = emission_factor_data.get("activity_data")
        emission_factor = emission_factor_data.get("emission_factor")
        reported_emissions = emission_factor_data.get("reported_emissions")
        project_phase = emission_factor_data["project_phase"]
        user_id = validated_data["user_id"]

        if reported_emissions is not None:
            total_emissions = float(reported_emissions)
            data_quality_score = 1
        elif activity_data is not None and emission_factor is not None:
            total_emissions = float(activity_data) * float(emission_factor)
            data_quality_score = 2
        else:
            benchmark_emissions = 0.233
            total_emissions = float(activity_data) * benchmark_emissions if activity_data is not None else 0
            data_quality_score = 3

        financed_emissions = (float(outstanding_loan) / float(total_project_cost)) * total_emissions

        emission_data = {
            "project_name": emission_factor_data["project_name"],
            "outstanding_loan": float(outstanding_loan),
            "total_project_cost": float(total_project_cost),
            "project_phase": project_phase,
            "reported_emissions": float(reported_emissions) if reported_emissions is not None else 0.0,
            "activity_data": float(activity_data) if activity_data is not None else 0.0,
            "emission_factor": float(emission_factor) if emission_factor is not None else None,
            "total_emissions": round(float(total_emissions),4),
            "financed_emissions": round(float(financed_emissions),4),
            "pcaf_level": data_quality_score,
        }


        user = User.objects.get(id=user_id.id)
        EmissionFactor.objects.create(
            user_id=user,
            asset_class=validated_data["asset_class"],
            emission_factors=emission_data,
            data_quality_score=data_quality_score,
        )

        response_data = {
            "financed_emissions": round(float(financed_emissions),4),
            "total_emissions": round(float(total_emissions),4),
            "data_quality_score": data_quality_score,

           "project_name": emission_factor_data["project_name"],
            "outstanding_loan": float(outstanding_loan),
            "total_project_cost": float(total_project_cost),
            "project_phase": project_phase,
            "reported_emissions": float(reported_emissions) if reported_emissions is not None else 0.0,
            "activity_data": float(activity_data) if activity_data is not None else 0.0,
            "emission_factor": float(emission_factor) if emission_factor is not None else None,
        }

        return response_data
