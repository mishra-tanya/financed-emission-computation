from django.urls import path
# from finance import views
# from . import views
from .views.user_views import Register,Login,Logout
from .views.company_views import (CompanyCreate, AssetClass, LoanInvestment, EmissionFactor)
from .views.dif_assets_view import (MotorVehicleLoan,Mortages,CommercialEstate, ProjectFinance,ListedEquity,
                                    BusinessLoan)
                    
urlpatterns = [
    # authemtications
    path('api/register/', Register.as_view(), name='register'),
    path('api/login/', Login.as_view(), name='token_obtain_pair'),
    path('api/logout/', Logout.as_view(), name='logout'),

    # company detials
    path('api/add-company/',CompanyCreate.as_view(), name='company'),
    path('api/add-asset-class/',AssetClass.as_view(), name='asset'),
    path('api/add-loan-investment/',LoanInvestment.as_view(), name='loanInvestment'),
    path('api/add-emission-factor/', EmissionFactor.as_view(), name='emissionFactor'),

    # asset classwise emissions
    path('api/add-motor/', MotorVehicleLoan.as_view(), name='MotorVehicleLoanAPIView'),
    path('api/add-mortages/', Mortages.as_view(), name='MortagesAPIView'),
    path('api/add-commercial-estate/', CommercialEstate.as_view(), name='CommercialEstate'),
    path('api/add-project-finance/', ProjectFinance.as_view(), name='ProjectFinance'),
    path('api/add-listed-equity/', ListedEquity.as_view(), name='ListedEquity'),
    path('api/add-business-loan/', BusinessLoan.as_view(), name='BusinessLoanSerializer'),

]
