from rest_framework import serializers
from ..models import EmissionFactor

class EmissionFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionFactor
        fields = ['user_id', 'asset_class', 'emission_factors', 'data_quality_score', 'created_at']
