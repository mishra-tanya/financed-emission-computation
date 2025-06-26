from ..services.business_factor.fuel_factor_data import FuelEmissionFactorProvider
from ..services.business_factor.asset_factor_data import AssetEmissionFactorProvider
from ..services.business_factor.electricity_factor_data import ElectricityEmissionFactorProvider
from ..services.business_factor.production_emission_data import ProductionEmissionFactorProvider
from ..services.business_factor.revenue_emission_data import RevenueEmissionFactorProvider

class EmissionCalculator:

    def __init__(self, loan, total_value):
        self.loan=float(loan)
        self.total_value=float(total_value)
    
    # common calc
    def financed_emission(self,value):
        if value is None:
            return 0.0
        emission = (self.loan/self.total_value) * float(value)
        return emission
    
    def asset_financed_emission(self,sector,region):
        if sector is None or region is None:
            return 0.0

        emission = (self.loan) * float(sector) * float(region)
        return emission
    
    # formatting to 4 decimals 
    @staticmethod
    def format_or_na(value):
        return "{:.4f}".format(value) if isinstance(value, (int, float)) else "NA"
    
    
    # electrictiy emissions 
    def electricity_emission(self, electricity, unit_or_amount, industry_region):
        total_emission = 0

        if electricity is None or unit_or_amount not in ["Amount", "Quantity"] or not industry_region:
            return 0

        rows = ElectricityEmissionFactorProvider.get_factors(unit_or_amount)

        for row in rows:
            if row[0] != industry_region or len(row) < 2:
                continue

            try:
                scope1 = float(row[1])
                total_emission += self.financed_emission(scope1 * float(electricity))
            except Exception as e:
                print(f"Error in electricity row {row}: {e}")
                continue

        return total_emission

        # fuel 1 fuel2 fuel3 + amount and qunaity
    def fuel_emission(self, fuels, quantity_or_amount, industry_region):
        total_emission_scope_1=0
        total_emission_scope_2=0

        for i in range(3):
            fuel_key = fuels[i] if i < len(fuels) else None
            quantity_mode = quantity_or_amount[i] if i < len(quantity_or_amount) else None

            if not fuel_key or not quantity_mode or not industry_region:
                continue

            try:
                fuel_key = float(fuel_key)
            except:
                continue

            data_source = FuelEmissionFactorProvider.get_factors(quantity_mode)
            rows = data_source.get(f"fuel_{i+1}", [])

            for row in rows:
                if row[0] != industry_region or len(row) < 2:
                    continue

                try:
                    scope1 = float(row[1])
                    scope2 =float(row[2])
                    total_emission_scope_1 += self.financed_emission(scope1 * float(fuel_key))
                    total_emission_scope_2 += self.financed_emission(scope2 * float(fuel_key)) 

                except Exception as e:
                    print(f"Error in fuel_{i + 1} row {row}: {e}")
                    continue

        return total_emission_scope_1,total_emission_scope_2

    # asset emissions
    def assetbased(self, industry_region, sector):
        emission_1=0
        emission_2=0

        sector_data = AssetEmissionFactorProvider.get_factors(sector)
        region_data = AssetEmissionFactorProvider.get_region_asset_multipliers(industry_region)


        if sector_data and region_data and len(sector_data) >= 2:
            emission_1 = self.asset_financed_emission(float(sector_data[0]), float(region_data[0])) 
            emission_2 = self.asset_financed_emission(float(sector_data[1]), float(region_data[1]))

        return emission_1, emission_2


    # production based emissions
    def production_based(self, industry_region, sector, production_quantity_1):
        emission_1 = 0
        emission_2 = 0
        if production_quantity_1 is None:
            return emission_1, emission_2  
        sector_data = ProductionEmissionFactorProvider.get_production_factors(sector)
        region_data = ProductionEmissionFactorProvider.get_region_production_multipliers(industry_region)

        if  (sector_data and region_data and len(sector_data) >= 2 and len(region_data) >= 2):
            emission_1 = self.financed_emission(float(sector_data[0])* float(region_data[0]) * float(production_quantity_1))
            emission_2 = self.financed_emission(float(sector_data[1]) * float(region_data[1]) * float(production_quantity_1))

        return emission_1, emission_2
    
    
    # revenue based emissions
    def revenue_based(self, industry_region, sector, revenue_emission_1):
        emission_1 = 0
        emission_2 = 0
        if revenue_emission_1 is None:
            return emission_1, emission_2  
        
        sector_data = RevenueEmissionFactorProvider.get_revenue_factors(sector)
        region_data = RevenueEmissionFactorProvider.get_region_revenue_multipliers(industry_region)


        if  (sector_data and region_data and len(sector_data) >= 2 and len(region_data) >= 2):
            emission_1 = self.financed_emission(float(sector_data[0])* float(region_data[0])* float(revenue_emission_1))
            emission_2 = self.financed_emission(float(sector_data[1])*float(region_data[0])* float(revenue_emission_1))

        return emission_1, emission_2

    def get_production_unit(self, sector):
        sector = sector.strip()
        units = {
            "Steel": "tonne",
            "Aluminium": "tonne",
            "Coal_Mining": "tonne",
            "Cement": "tonne",
            "Basic_Chemicals": "tonne",
            "Food_Processing": "tonne",
            "Textiles": "tonne",
            "Pharmaceuticals": "tonne",
            "Agriculture": "tonne",
            "Oil_Gas_Extraction": "barrel",
            "Electric_Power_Generation": "MWh",
            "Solar_Manufacturing": "MW_capacity",
            "Wind_Manufacturing": "MW_capacity",
            "Automotive": "vehicle",
            "Aviation": "aircraft",
            "Shipping": "vessel",
            "Construction": "m2_floor_area",
            "Forestry": "cubic_meter",
        }
        return units.get(sector)
