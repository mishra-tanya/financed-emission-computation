from ..helpers.emissions import EmissionCalculator
from ..models import EmissionFactor
from django.contrib.auth.models import User

class BusinessLoanService:
    def __init__(self, validated_data):
        self.validated_data = validated_data
        self.emission_factor_data = validated_data["emission_factor"]
        self.user = validated_data["user_id"]
        self.asset_class = validated_data["asset_class"]
        self.calculator = EmissionCalculator(
            self.emission_factor_data["outstanding_loan"],
            self.emission_factor_data["borrower_total_value"]
        )

    def process(self):
        data = self.compute_emission()
        self.save_emission_data(data)
        return data

    def determine_data_quality_score(self):
        ef = self.emission_factor_data

        # Priority: reported → fuel → production → revenue → none
        if ef.get("reported_emissions_1") is not None or ef.get("reported_emissions_2") is not None:
            return 1
        elif ef.get("coal") or ef.get("natural_gas") or ef.get("diesel"):
            return 2
        elif ef.get("production_quantity_1"):
            return 3
        elif ef.get("revenue_emission_1"):
            return 4
        else:
            return 5
    
    def compute_emission(self):
        ef=self.emission_factor_data
        format=self.calculator.format_or_na
        asset_emission_1, asset_emission_2 = self.calculator.assetbased(
            ef.get("borrower_region"),
            ef["borrower_industry_sector"]
            )
        production_emission_1, production_emission_2 = self.calculator.production_based(
            ef.get("borrower_region"),
            ef["borrower_industry_sector"],
            ef.get("production_quantity_1")
            )
        revenue_emission_1, revenue_emission_2 = self.calculator.revenue_based(
            ef.get("borrower_region"),
            ef["borrower_industry_sector"],
            ef.get("revenue_emission_1")
            )
        
        fuel_emission_1, fuel_emission_2 = self.calculator.fuel_emission(
            [ef.get("coal"), ef.get("natural_gas"), ef.get("diesel")],
            [ef.get("coal_quantity_amount"), ef.get("natural_gas_quantity_amount"), ef.get("diesel_quantity_amount")],
            ef["borrower_region"]
        )

        
        print(ef)
        return {
            "heading1":"Borrowers Details",
            "borrower_name": ef["borrower_name"],
            "outstanding_loan": float(ef["outstanding_loan"]),
            "borrower_total_value": float(ef["borrower_total_value"]),
            "borrower_region": ef["borrower_region"],
            "borrower_industry_sector": ef["borrower_industry_sector"],
            "asset_class": self.validated_data["asset_class"],

            "heading2":"Entered Data",
            
            "reported_emissions_1": float(ef.get("reported_emissions_1") or 0),
            "reported_emissions_2": float(ef.get("reported_emissions_2") or 0),
            
            "coal_quantity_amount" :ef.get("coal_quantity_amount") or "N/A",
            "coal": float(ef.get("coal") or 0),

            "natural_gas_quantity_amount":ef.get("natural_gas_quantity_amount") or "N/A",
            "natural_gas": float(ef.get("natural_gas") or 0),

            "diesel_quantity_amount":ef.get("diesel_quantity_amount") or "N/A",
            "diesel": float(ef.get("diesel") or 0),

            "electricity_quantity_amount":ef.get("electricity_quantity_amount") or "N/A",
            "electricity": float(ef.get("electricity") or 0),

            "production_quantity_1": float(ef.get("production_quantity_1") or 0),

            "revenue_emission_1": float(ef.get("revenue_emission_1") or 0),

            "heading4":"Declared Emission",
            "declared_emission_scope_1": format(self.calculator.financed_emission(ef.get("reported_emissions_1"))),
            "declared_emission_scope_2": format(self.calculator.financed_emission(ef.get("reported_emissions_2"))),

            "heading5":"Fuel / Electricity Based Emission",
            "fuel_emission_scope_1": format(fuel_emission_1),
            # "fuel_emission_scope_2": format(fuel_emission_2),

            "electricity_emission_scope_2": format(self.calculator.electricity_emission(ef.get("electricity"), ef["electricity_quantity_amount"], ef["borrower_region"])),
            
            "heading6":"Production Based Emission",
            "production_emission_scope_1": format(production_emission_1),
            "production_emission_scope_2": format(production_emission_2),

            "heading7":"Revenue Based Emission",
            "revenue_emission_scope_1": format(revenue_emission_1),
            "revenue_emission_scope_2": format(revenue_emission_2),
            
            "heading8":"Asset Based Emission",
            "asset_based_emission_1": format(asset_emission_1),
            "asset_based_emission_2": format(asset_emission_2),

        }

    def save_emission_data(self,data):
        EmissionFactor.objects.create(
            user_id=User.objects.get(id=self.validated_data["user_id"].id),
            asset_class=self.validated_data["asset_class"],
            emission_factors=data,
            data_quality_score=self.determine_data_quality_score(),
        )
