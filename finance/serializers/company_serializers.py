from rest_framework import serializers
from ..models import  Company, AssetClass, LoanInvestment, EmissionFactor

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['user_id', 'company_name', 'geography','sector']


class AssetClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetClass
        fields = ['id', 'asset_class_name', 'input_fields', 'others', 'created_at']

class LoanInvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanInvestment
        fields = ['id', 'user_id', 'company', 'asset_class', 'outstanding_amount', 'total_value', 'created_at']


class EmissionFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionFactor
        fields = ['id', 'user_id', 'company', 'asset_class', 'emission_factors', 'data_quality_score', 'created_at']
