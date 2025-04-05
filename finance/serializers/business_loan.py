from django.contrib.auth.models import User
from rest_framework import serializers
from ..services.business_loan_service import BusinessLoanService

# business loan and investment 
class BusinessLoanDetailsSerializer(serializers.Serializer):

    # general emsisino data 
    borrower_name = serializers.CharField(max_length=200)
    outstanding_loan = serializers.DecimalField(max_digits=15, decimal_places=2)
    borrower_total_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    borrower_industry_sector = serializers.CharField(max_length=200)
    borrower_revenue = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    borrower_region = serializers.CharField(max_length=200)

    # reported esmission (optional)
    reported_emissions_1 = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    reported_emissions_2 = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)

    # fuel based (optional)
    fuel_quantity_amount_1 = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    fuel_1 = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    fuel_quantity_amount_2 = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    fuel_2 = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    fuel_quantity_amount_3 = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    fuel_3 = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)

    # elecctrivity (optional)
    electricity_quantity_amount = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    electricity = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)

    # production emission (optional)
    production_quantity_1 = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    production_quantity_2 = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)

    # revenue emission (optional)
    revenue_emission_1 = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    revenue_emission_2 = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)

    # asset emission (optional)
    asset_emission = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
  
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
    
    def create(self, validated_data):
        service = BusinessLoanService(validated_data)
        return service.process()
        