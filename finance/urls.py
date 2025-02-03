from django.urls import path
from finance.views.user_views import testing
from .views.user_views import Register,Login,Logout
from .views.csrf_token import get_csrf_token
from .views.company_views import (CompanyCreate, AssetClass, LoanInvestment, EmissionFactor)
from .views.dif_assets_view import (MotorVehicleLoan,Mortages,CommercialEstate, ProjectFinance,ListedEquity,
                                    BusinessLoan)
from .views.dashboard_view import (TopOutstandingLoansView, AssetFinanceEmission, TotalFinanceEmission,
                                   TotalFinanceEmissionByAssetClass, WeightedDataQualityScore)

urlpatterns = [
    # csrf token
    path("api/csrf-token/", get_csrf_token, name="get_csrf_token"),

    # authemtications
    path('api/testing/',testing, name='test'),

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

    # dashboard
    path('api/top-outstanding-loans/', TopOutstandingLoansView.as_view(), name='topoutstandingloans'),
    path('api/top-asset-finance/', AssetFinanceEmission.as_view(), name='topassetfinance'),
    path('api/total-finance-emission/', TotalFinanceEmission.as_view(), name='TotalFinanceEmission'),
    path('api/grouped-finance-emission/', TotalFinanceEmissionByAssetClass.as_view(), name='TotalFinanceEmissionByAssetClass'),
    path('api/average-data-quality/', WeightedDataQualityScore.as_view(), name='WeightedDataQualityScore'),

]
