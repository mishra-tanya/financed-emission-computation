from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..serializers.project_finance import ProjectFinanceSerializer
from ..serializers.commercial_estate import CommercialRealEstateSerializer
from ..serializers.mortages import MortagesLoanSerializer
from ..serializers.motor_vehicle import MotorVehicleLoanSerializer
from ..serializers.listed_equity import ListedEquitySerializer
from ..serializers.business_loan import BusinessLoanSerializer
from rest_framework.permissions import IsAuthenticated

# motor vehicle asset class
class MotorVehicleLoan(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.data['user_id'] = request.user.id
        serializer = MotorVehicleLoanSerializer(data=request.data )
        if serializer.is_valid():
            saved_data = serializer.save() 
            return Response(saved_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# mortages
class Mortages(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        request.data['user_id'] = request.user.id
        serializer = MortagesLoanSerializer(data=request.data )
        if serializer.is_valid():
            saved_data = serializer.save() 
            return Response(saved_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# commercial estate
class CommercialEstate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.data['user_id'] = request.user.id
        serializer = CommercialRealEstateSerializer(data=request.data )
        if serializer.is_valid():
            saved_data = serializer.save() 
            return Response(saved_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# project finance ProjectFinanceSerializer
class ProjectFinance(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.data['user_id'] = request.user.id
        serializer = ProjectFinanceSerializer(data=request.data)
        if serializer.is_valid():
            saved_data = serializer.save() 
            return Response(saved_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
# listed ewuity
class ListedEquity(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.data['user_id'] = request.user.id
        serializer = ListedEquitySerializer(data=request.data )
        if serializer.is_valid():
            saved_data = serializer.save() 
            return Response(saved_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Business loan
class BusinessLoan(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.data['user_id'] = request.user.id
        serializer = BusinessLoanSerializer(data=request.data )
        if serializer.is_valid():
            saved_data = serializer.save() 
            return Response(saved_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)