from django.contrib.auth.models import User
from rest_framework import serializers
from ..models import  Company, EmissionFactor

# listed equity
class ListedEquityDetailsSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=200)
    outstanding_loan = serializers.DecimalField(max_digits=15, decimal_places=2)
    evic = serializers.DecimalField(max_digits=15, decimal_places=2)
    geography = serializers.CharField(max_length=200)
    reported_emissions = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    revenue = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    sector = serializers.CharField(max_length=200)

    def validate(self, data):
        if data["outstanding_loan"] <= 0 or data["evic"] <= 0:
            raise serializers.ValidationError("Loan and project cost must be positive numbers.")
        
        return data


class ListedEquitySerializer(serializers.Serializer):
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        required=True
    )
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True
    )
    asset_class = serializers.CharField(max_length=200)
    emission_factor = ListedEquityDetailsSerializer()
    data_quality_score = serializers.IntegerField()

    def validate(self, data):
        emission_factor_data = data.get("emission_factor")
        if emission_factor_data:
            if emission_factor_data["outstanding_loan"] <= 0 or emission_factor_data["evic"] <= 0:
                raise serializers.ValidationError("Loan and evic must be positive numbers in emission factor.")
        return data

    def create(self, validated_data):
        emission_factor_data = validated_data["emission_factor"]
        outstanding_loan = emission_factor_data["outstanding_loan"]
        evic = emission_factor_data["evic"]
        geography = emission_factor_data.get("geography")
        revenue = emission_factor_data.get("revenue")
        reported_emissions = emission_factor_data.get("reported_emissions")
        sector = emission_factor_data["sector"]
        company = validated_data["company"]
        user_id = validated_data["user_id"]

        if reported_emissions is not None:
            total_emissions = float(reported_emissions)
            financed_emissions = (float(outstanding_loan) / float(evic)) * total_emissions
            data_quality_score = 1
        elif evic is not None:
            sector_specific_factor=0.2
            total_emissions = float(sector_specific_factor)
            financed_emissions = (float(outstanding_loan) / float(evic)) * total_emissions
            data_quality_score = 2
        elif revenue is not None:
            sector_emission_factor=0.2
            total_emissions = float(revenue) * float(sector_emission_factor)
            financed_emissions = (float(outstanding_loan) / float(evic)) * total_emissions
            data_quality_score = 3
        else:
            benchmark_emissions = 0.233
            total_emissions = float(benchmark_emissions) 
            data_quality_score = 4


        emission_data = {
            "company_name": emission_factor_data["company_name"],
            "outstanding_loan": float(outstanding_loan),
            "evic": float(evic),
            "geography": geography,
            "sector":sector,
            "reported_emissions": float(reported_emissions) if reported_emissions is not None else 0.0,
            "revenue": float(revenue) if revenue is not None else 0.0,
            "financed_emissions": float(financed_emissions),
            "pcaf_level": data_quality_score,
        }


        user = User.objects.get(id=user_id.id)
        EmissionFactor.objects.create(
            company_id=company.id,
            user_id=user,
            asset_class=validated_data["asset_class"],
            emission_factors=emission_data,
            data_quality_score=validated_data["data_quality_score"],
        )

        response_data = {
            "company": company.id,
            "company_name": company.company_name,
            "asset_class": validated_data["asset_class"],
            "data_quality_score": validated_data["data_quality_score"],
            "emission_factor": emission_factor_data,
            "financed_emissions": float(financed_emissions),
            "pcaf_level": data_quality_score,
        }

        return response_data
