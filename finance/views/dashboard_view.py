from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from ..models import EmissionFactor
from django.db.models import Avg

# 1.outstanding loan top 5
class TopOutstandingLoansView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        possible_keys = ["project_name", "vehicle_name", "borrower_name", "company_name", "building_name"]

        emission_factors = EmissionFactor.objects.filter(user_id=user)

        data = []
        for ef in emission_factors:
            emission_data = ef.emission_factors  

            project_name = next((emission_data.get(key) for key in possible_keys if key in emission_data), "Unknown")
            outstanding_loan = emission_data.get("outstanding_loan", 0)  

            data.append({
                "project_name": project_name,
                "outstanding_loan": outstanding_loan,
            })

        sorted_data = sorted(data, key=lambda x: x["outstanding_loan"], reverse=True)[:5]

        return Response(sorted_data)


# asset
class AssetFinanceEmission(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        possible_keys = ["project_name", "vehicle_name", "borrower_name", "company_name", "building_name"]

        emission_factors = EmissionFactor.objects.filter(user_id=user)
        all_data = []

        for ef in emission_factors:
            emission_data = ef.emission_factors  
            asset_class = ef.asset_class
            project_name = next((emission_data.get(key) for key in possible_keys if key in emission_data), "Unknown")

            financed_emissions_1 = emission_data.get("financed_emissions_1", 0)  

            all_data.append({
                "asset_class": asset_class,
                "project_name": project_name,
                "financed_emissions_1": financed_emissions_1,
            })

        top_5_data = sorted(all_data, key=lambda x: float(x["financed_emissions_1"]), reverse=True)[:5]
        print(top_5_data)
        return Response(top_5_data)


# 3.total financed emission
class TotalFinanceEmission(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        emission_factors = EmissionFactor.objects.filter(user_id=user)
        data = []
        for ef in emission_factors:
            emission_data = ef.emission_factors  
            total_financed_emissions=0
            financed_emissions_1 = emission_data.get("financed_emissions_1", 0)  
            financed_emissions_2 = emission_data.get("financed_emissions_2", 0)  
            
            total_financed_emissions= float(financed_emissions_2 )+ float(financed_emissions_1)
            print(total_financed_emissions)
        return Response({"total_financed_emissions":total_financed_emissions})

# 4.asset class grouped 
class TotalFinanceEmissionByAssetClass(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        emission_factors = EmissionFactor.objects.filter(user_id=user)

        emissions_by_asset_class = {}

        for ef in emission_factors:
            emission_data = ef.emission_factors
            asset_class = ef.asset_class 
            financed_emissions = emission_data.get("financed_emissions_1", 0)  

            if asset_class not in emissions_by_asset_class:
                emissions_by_asset_class[asset_class] = 0
            emissions_by_asset_class[asset_class] += float(financed_emissions)

        return Response(emissions_by_asset_class)

# 5.data quality average
class WeightedDataQualityScore(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        avg_quality_score = EmissionFactor.objects.filter(user_id=user).aggregate(Avg('data_quality_score'))
        avg_score = avg_quality_score.get('data_quality_score__avg', 0)  

        return Response({"average_data_quality_score": avg_score})