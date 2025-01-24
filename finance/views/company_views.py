from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..serializers.company_serializers import (CompanySerializer,AssetClassSerializer,
                                     LoanInvestmentSerializer,EmissionFactorSerializer)
from rest_framework.permissions import IsAuthenticated
from finance.models import Company

# storing companies user specific
class CompanyCreate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        company_name = request.data.get('company_name', '').strip().lower()
        request.data['company_name'] = company_name 
        request.data['user_id'] = request.user.id

        if Company.objects.filter(user_id=request.user.id, company_name__iexact=company_name).exists():
            return Response({"message": "Company already exists for this user"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Company added successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# asset class
class AssetClass(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = AssetClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# loan investments
class LoanInvestment(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        request.data['user_id'] = request.user.id
        serializer = LoanInvestmentSerializer(data=request.data)
        if serializer.is_valid():
            company_id = request.data.get('company')
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return Response({"error": "Company does not exist"}, status=status.HTTP_404_NOT_FOUND)

            serializer.save(company=company)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#emission factor
class EmissionFactor(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        serializer  = EmissionFactorSerializer(data=request.data)
        if serializer.is_valid():
            comapny_id=request.data.get('company')
            try:
                company=Company.objects.get(id=comapny_id)
            except Company.DoesNotExist:
                return Response({"error":"Company doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
            serializer.save(company=company)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    