from ..helpers.emissions import EmissionCalculator
from ..models import EmissionFactor
from django.contrib.auth.models import User

class BusinessLoanService:
    def __init__(self, validated_data):
        self.validated_data=validated_data
        self.emission_factor_data= validated_data["emission_factor"]
        self.calculator=EmissionCalculator(
            self.emission_factor_data["outstanding_loan"],
            self.emission_factor_data["borrower_total_value"]
        )

    def process(self):
        data=self.compute_emission()
        self.save_emission_data(data)
        return data
    
    def compute_emission(self):
        ef=self.emission_factor_data
        format=self.calculator.format_or_na
        asset_emission_1, asset_emission_2 = self.calculator.assetbased(
            ef.get("borrower_region"),
            ef["borrower_industry_sector"]
            )
        print(ef)
        return {
            "financed_emissions (Basic)": format(self.calculator.financed_emission(
                self.calculator.prepare_industry_sector_factor(ef["borrower_region"])
            )),
            "declared_emission_scope_1": format(self.calculator.financed_emission(ef.get("reported_emissions_1"))),
            "declared_emission_scope_2": format(self.calculator.financed_emission(ef.get("reported_emissions_2"))),

            "fuel_emission_scope_1": format(self.calculator.fuel_emission(
                [ef.get("fuel_1"), ef.get("fuel_2"), ef.get("fuel_3")],
                [ef.get("fuel_quantity_amount_1"), ef.get("fuel_quantity_amount_2"), ef.get("fuel_quantity_amount_3")],
                 ef["borrower_region"]
            )),

            "electricity_emission_scope_2": format(self.calculator.electricity_emission(ef.get("electricity"), ef["electricity_quantity_amount"], ef["borrower_region"])),
            "production_emission_scope_1": format(self.calculator.financed_emission(ef.get("production_quantity_1"))),
            "production_emission_scope_2": format(self.calculator.financed_emission(ef.get("production_quantity_2"))),
            "revenue_emission_scope_1": format(self.calculator.financed_emission(ef.get("revenue_emission_1"))),
            "revenue_emission_scope_2": format(self.calculator.financed_emission(ef.get("revenue_emission_2"))),

            # "asset_based_emission_1": format(self.calculator.assetbased(ef.get("borrower_region"),ef["borrower_industry_sector"])),
            # "asset_based_emission_2": format(self.calculator.assetbased(ef.get("borrower_region"),ef["borrower_industry_sector"])),
            "asset_based_emission_1": format(asset_emission_1),
            "asset_based_emission_2": format(asset_emission_2),

            "data_quality_score": self.validated_data["data_quality_score"],
            "asset_class": self.validated_data["asset_class"],
            "borrower_name": ef["borrower_name"],
            "outstanding_loan": float(ef["outstanding_loan"]),
            "borrower_total_value": float(ef["borrower_total_value"]),
            "borrower_revenue": float(ef.get("borrower_revenue") or 0),
            "borrower_region": ef["borrower_region"],
            "borrower_industry_sector": ef["borrower_industry_sector"],
            "reported_emissions_1": float(ef.get("reported_emissions_1") or 0),
            "reported_emissions_2": float(ef.get("reported_emissions_2") or 0),
            
            "fuel_quantity_amount_1" :ef.get("fuel_quantity_amount_1") or "N/A",
            "fuel_1": float(ef.get("fuel_1") or 0),

            "fuel_quantity_amount_2":ef.get("fuel_quantity_amount_2") or "N/A",
            "fuel_2": float(ef.get("fuel_2") or 0),

            "fuel_quantity_amount_3":ef.get("fuel_quantity_amount_3") or "N/A",
            "fuel_3": float(ef.get("fuel_3") or 0),

            "electricity_quantity_amount":ef.get("electricity_quantity_amount") or "N/A",
            "electricity": float(ef.get("electricity") or 0),

            "production_quantity_1": float(ef.get("production_quantity_1") or 0),
            "production_quantity_2": float(ef.get("production_quantity_2") or 0),
            "revenue_emission_1": float(ef.get("revenue_emission_1") or 0),
            "revenue_emission_2": float(ef.get("revenue_emission_2") or 0),
     
        }

    def save_emission_data(self,data):
        EmissionFactor.objects.create(
            user_id=User.objects.get(id=self.validated_data["user_id"].id),
            asset_class=self.validated_data["asset_class"],
            emission_factors=data,
            data_quality_score=self.validated_data["data_quality_score"],
        )
