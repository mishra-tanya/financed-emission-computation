from ..helpers.emissions import EmissionCalculator
from ..models import EmissionFactor
from django.contrib.auth.models import User

class ListedEquityService:
    def __init__(self, validated_data):
        self.validated_data=validated_data
        self.emission_factor_data= validated_data["emission_factor"]
        self.calculator=EmissionCalculator(
            self.emission_factor_data["outstanding_loan"],
            self.emission_factor_data["evic"]
        )

    def process(self):
        data=self.compute_emission()
        self.save_emission_data(data)
        return data
    
    def compute_emission(self):
        ef=self.emission_factor_data
        format=self.calculator.format_or_na
        print("hi", ef.get("geography"),
            ef["sector"])
        asset_emission_1, asset_emission_2 = self.calculator.assetbased(
            ef.get("geography"),
            ef["sector"]
            )
        production_emission_1, production_emission_2 = self.calculator.production_based(
            ef.get("geography"),
            ef["sector"],
            ef.get("production_quantity_1")
            )
        revenue_emission_1, revenue_emission_2 = self.calculator.revenue_based(
            ef.get("geography"),
            ef["sector"],
            ef.get("revenue_emission_1")
            )
        print(ef)
        return {
            "heading1":"General Details",
            "company_name": ef["company_name"],
            "outstanding_loan": float(ef["outstanding_loan"]),
            "evic": float(ef["evic"]),
            "geography": ef["geography"],
            "sector": ef["sector"],
            "asset_class": self.validated_data["asset_class"],

            "heading2":"Entered Data",
            
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

            "revenue_emission_1": float(ef.get("revenue_emission_1") or 0),

            "heading4":"Declared Emission",
            "declared_emission_scope_1": format(self.calculator.financed_emission(ef.get("reported_emissions_1"))),
            "declared_emission_scope_2": format(self.calculator.financed_emission(ef.get("reported_emissions_2"))),

            "heading5":"Fuel / Electricity Based Emission",
            "fuel_emission_scope_1": format(self.calculator.fuel_emission(
                [ef.get("fuel_1"), ef.get("fuel_2"), ef.get("fuel_3")],
                [ef.get("fuel_quantity_amount_1"), ef.get("fuel_quantity_amount_2"), ef.get("fuel_quantity_amount_3")],
                 ef["geography"]
            )),

            "electricity_emission_scope_2": format(self.calculator.electricity_emission(ef.get("electricity"), ef["electricity_quantity_amount"], ef["geography"])),
            
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
            data_quality_score=self.validated_data["data_quality_score"],
        )
