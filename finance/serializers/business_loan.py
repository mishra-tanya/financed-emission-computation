from django.contrib.auth.models import User
from rest_framework import serializers
from ..models import  Company, EmissionFactor

# business loan and investment 
class BusinessLoanDetailsSerializer(serializers.Serializer):
    borrower_name = serializers.CharField(max_length=200)
    outstanding_loan = serializers.DecimalField(max_digits=15, decimal_places=2)
    physical_activity_data = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    borrower_total_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    borrower_industry_sector = serializers.CharField(max_length=200)
    reported_emissions = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    borrower_revenue = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    borrower_region = serializers.CharField(max_length=200)

    def validate(self, data):
        if data["outstanding_loan"] <= 0 :
            raise serializers.ValidationError("Loan and project cost must be positive numbers.")
        return data


class BusinessLoanSerializer(serializers.Serializer):
   
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True
    )
    asset_class = serializers.CharField(max_length=200)
    emission_factor = BusinessLoanDetailsSerializer()
    data_quality_score = serializers.IntegerField()

    def validate(self, data):
        emission_factor_data = data.get("emission_factor")
        if emission_factor_data:
            if emission_factor_data["outstanding_loan"] <= 0 :
                raise serializers.ValidationError("Loan  must be positive numbers in emission factor.")
          
        return data

    def create(self, validated_data):
        emission_factor_data = validated_data["emission_factor"]
        outstanding_loan = emission_factor_data["outstanding_loan"]
        borrower_total_value = emission_factor_data["borrower_total_value"]
        physical_activity_data = emission_factor_data.get("physical_activity_data")
        borrower_industry_sector = emission_factor_data.get("borrower_industry_sector")
        borrower_revenue = emission_factor_data.get("borrower_revenue")
        reported_emissions = emission_factor_data.get("reported_emissions")
        borrower_region = emission_factor_data["borrower_region"]
        user_id = validated_data["user_id"]

        if reported_emissions is not None:
            total_emissions = float(reported_emissions)
            financed_emissions = (float(outstanding_loan) / float(borrower_total_value)) * total_emissions
            data_quality_score = 1
        elif physical_activity_data is not None:
            electric_emission = 0.233 #can be changeable later according to the provided emsiondata
            total_emissions = float(physical_activity_data) * electric_emission
            financed_emissions = (float(outstanding_loan) / float(borrower_total_value)) * total_emissions
            data_quality_score = 2
        elif borrower_revenue is not None:
            sector_emission_factor=0.05 #changeable
            total_emissions = float(borrower_revenue) * float(sector_emission_factor)
            financed_emissions = (float(outstanding_loan) / float(borrower_total_value)) * total_emissions
            data_quality_score = 3
        else:
            benchmark_emissions = 0.233
            total_emissions = float(benchmark_emissions) 
            financed_emissions = float(benchmark_emissions) 
            data_quality_score = 4


        emission_data = {
            "borrower_name": emission_factor_data["borrower_name"],
            "outstanding_loan": float(outstanding_loan),
            "borrower_total_value": float(borrower_total_value),
            "borrower_region": borrower_region,
            "borrower_industry_sector":borrower_industry_sector,
            "reported_emissions": float(reported_emissions) if reported_emissions is not None else 0.0,
            "physical_activity_data": float(physical_activity_data) if physical_activity_data is not None else 0.0,
            "borrower_revenue": float(borrower_revenue) if borrower_revenue is not None else 0.0,
            "financed_emissions": round(float(financed_emissions),4),
            "total_emissions": round(float(total_emissions),4),
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
            
            "asset_class": validated_data["asset_class"],
            "borrower_name": emission_factor_data["borrower_name"],
            "outstanding_loan": float(outstanding_loan),
            "borrower_total_value": float(borrower_total_value),
            "borrower_revenue": float(borrower_revenue) if borrower_revenue is not None else 0.0,
            "borrower_region": borrower_region,
            "borrower_industry_sector":borrower_industry_sector,
            "reported_emissions": float(reported_emissions) if reported_emissions is not None else 0.0,
            "physical_activity_data": float(physical_activity_data) if physical_activity_data is not None else 0.0,
        }

        return response_data
