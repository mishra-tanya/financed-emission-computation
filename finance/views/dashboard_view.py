from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from ..models import EmissionFactor
from decimal import Decimal

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
            data = ef.emission_factors or {}
            loan = float(data.get("outstanding_loan", 0))
            total_value = float(data.get("borrower_total_value", 1)) or 1
            ratio = loan / total_value

            project_name = next((data.get(key) for key in possible_keys if key in data), "Unknown")
            asset_class = ef.asset_class

            emissions = [
                ("Declared", float(data.get("declared_emission_scope_1", 0)), float(data.get("declared_emission_scope_2", 0))),
                ("Asset-Based", float(data.get("asset_based_emission_1", 0)), float(data.get("asset_based_emission_2", 0))),
                ("Fuel-Based", float(data.get("fuel_emission_scope_1", 0)), float(data.get("fuel_emission_scope_2", 0))),
                ("Production-Based", float(data.get("production_emission_scope_1", 0)), float(data.get("production_emission_scope_2", 0))),
                ("Revenue-Based", float(data.get("revenue_emission_scope_1", 0)), float(data.get("revenue_emission_scope_2", 0))),
            ]

            for label, e1, e2 in emissions:
                if e1 != 0 or e2 != 0:
                    fe_1 = ratio * e1
                    fe_2 = ratio * e2
                    total_fe = fe_1 + fe_2
                    all_data.append({
                        "project_name": project_name,
                        "asset_class": asset_class,
                        "emission_type_used": label,
                        "financed_emissions_1": round(fe_1, 2),
                        "financed_emissions_2": round(fe_2, 2),
                        "total_financed_emissions": round(total_fe, 2)
                    })
                    break 

        top_5_data = sorted(all_data, key=lambda x: x["total_financed_emissions"], reverse=True)[:5]
        return Response(top_5_data)


# 3.total financed emission
class TotalFinanceEmission(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        emission_factors = EmissionFactor.objects.filter(user_id=user)

        total_fe_1 = 0
        total_fe_2 = 0

        for ef in emission_factors:
            data = ef.emission_factors
            loan = float(data.get("outstanding_loan", 0))
            total_value = float(data.get("borrower_total_value", 1)) or 1
            ratio = loan / total_value

            emissions = [
                ("Declared", float(data.get("declared_emission_scope_1", 0)), float(data.get("declared_emission_scope_2", 0))),
                ("Asset-Based", float(data.get("asset_based_emission_1", 0)), float(data.get("asset_based_emission_2", 0))),
                ("Fuel-Based", float(data.get("fuel_emission_scope_1", 0)), float(data.get("fuel_emission_scope_2", 0))),
                ("Production-Based", float(data.get("production_emission_scope_1", 0)), float(data.get("production_emission_scope_2", 0))),
                ("Revenue-Based", float(data.get("revenue_emission_scope_1", 0)), float(data.get("revenue_emission_scope_2", 0))),
            ]

            for _, e1, e2 in emissions:
                if e1 != 0 or e2 != 0:
                    total_fe_1 += ratio * e1
                    total_fe_2 += ratio * e2
                    break  

        # return Response({
        #     "financed_emissions_1": round(total_fe_1, 2),
        #     "financed_emissions_2": round(total_fe_2, 2),
        #     "total_financed_emissions": round(total_fe_1 + total_fe_2, 2)
        # })
        return Response({"total_financed_emissions": round(total_fe_1 + total_fe_2, 2)})

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
# class WeightedDataQualityScore(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         avg_quality_score = EmissionFactor.objects.filter(user_id=user).aggregate(Avg('data_quality_score'))
#         avg_score = avg_quality_score.get('data_quality_score__avg', 0)  

#         return Response({"average_data_quality_score": round(avg_score, 2)})

class WeightedDataQualityScore(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        emission_factors = EmissionFactor.objects.filter(user_id=user)

        numerator = 0
        denominator = 0

        for factor in emission_factors:
            data_quality_score = factor.data_quality_score or Decimal('0')
            borrower_loan = 0

            if factor.emission_factors and 'outstanding_loan' in factor.emission_factors:
                loan_value = factor.emission_factors.get('outstanding_loan', 0) or 0
                borrower_loan = Decimal(str(loan_value)) 

            numerator += data_quality_score * borrower_loan
            denominator += borrower_loan

        if denominator == 0:
            weighted_avg = 0
        else:
            weighted_avg = numerator / denominator

        return Response({"average_data_quality_score": round(weighted_avg, 2)})

# emissions data
class EmissionFactorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get_scope_values(self, score, ef_data):
        if score == 1.0:
            s1 = float(ef_data.get("declared_emission_scope_1", 0) or 0)
            s2 = float(ef_data.get("declared_emission_scope_2", 0) or 0)
        elif score == 2.0:
            s1 = float(ef_data.get("fuel_emission_scope_1", 0) or 0)
            s2 = float(ef_data.get("electricity_emission_scope_2", 0) or 0)
        elif score == 3.0:
            s1 = float(ef_data.get("production_emission_scope_1", 0) or 0)
            s2 = float(ef_data.get("production_emission_scope_2", 0) or 0)
        elif score == 4.0:
            s1 = float(ef_data.get("revenue_emission_scope_1", 0) or 0)
            s2 = float(ef_data.get("revenue_emission_scope_2", 0) or 0)
        elif score == 5.0:
            s1 = float(ef_data.get("asset_based_emission_1", 0) or 0)
            s2 = float(ef_data.get("asset_based_emission_2", 0) or 0)

        return round(s1, 2), round(s2, 2)

    def get(self, request):
        user = request.user
        emission_factors = EmissionFactor.objects.filter(user_id=user).order_by('-created_at')

        results = []
        numerator = 0
        denominator = 0
        total=0
        for ef in emission_factors:
            ef_data = ef.emission_factors or {}
            score = float(ef.data_quality_score)  
            s1, s2 = self.get_scope_values(int(score), ef_data)
            total = round(s1 + s2, 2)

            numerator += total * score
            denominator += total

            results.append({
                "id": ef.id,
                "asset_class": ef.asset_class,
                "emission_factors": ef_data,
                "data_quality_score": int(score),
                "calculated_emission_total": total,
                "created_at": ef.created_at,
                "user_id_id": ef.user_id_id,
            })
        average_score = round(numerator / denominator, 2) if denominator != 0 else "N/A"
        
        return Response({
            "average_data_quality_score": average_score,
            "data": results
        })
