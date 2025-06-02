from django.contrib.auth.models import User
from rest_framework import serializers
from ..models import EmissionFactor
from ..services.motor_vehicle_service import MotorVehicleService

# motor vehicle
class MotorEmissionFactorDetailsSerializer(serializers.Serializer):
    loan_id = serializers.CharField(max_length=200)
    outstanding_loan = serializers.DecimalField(max_digits=15, decimal_places=4)
    original_value = serializers.DecimalField(max_digits=15, decimal_places=4)
    currency = serializers.CharField(max_length=200)
    loan_originated_date = serializers.DateField(required=False, allow_null=True)
    reporting_start_date = serializers.DateField(required=False, allow_null=True)
    reporting_end_date = serializers.DateField(required=False, allow_null=True)
    specific_model_yes_or_no = serializers.ChoiceField(choices=["Yes", "No"], required=False, allow_null=True),
    vehicle_make = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    vehicle_model = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    model_year =  serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    vehicle_type = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    fuel_type = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    actual_fuel_yes_or_no = serializers.ChoiceField(choices=["Yes", "No"], required=False, allow_null=True),
    fuel_consumption =  serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    fuel_unit = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    actual_distance_data_yes_or_no = serializers.ChoiceField(choices=["Yes", "No"], required=False, allow_null=True),
    distance_traveled =   serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    distance_unit = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    vehicle_location = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    country = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    region = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    percentage_yes_or_no = serializers.ChoiceField(choices=["Yes", "No"], required=False, allow_null=True),
    percentage_electric =  serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    source_yes_or_no = serializers.ChoiceField(choices=["Yes", "No"], required=False, allow_null=True  ),
    electric_source = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)

class MotorVehicleLoanSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True
    )
    asset_class = serializers.CharField(max_length=200)
    emission_factor = MotorEmissionFactorDetailsSerializer()
    data_quality_score = serializers.IntegerField()

    def create(self, validated_data):
        service = MotorVehicleService(validated_data)
        return service.process( )
        