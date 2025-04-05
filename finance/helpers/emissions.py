from ..services.fuel_factor_data import FuelEmissionFactorProvider
from ..services.asset_factor_data import AssetEmissionFactorProvider
from ..services.electricity_factor_data import ElectricityEmissionFactorProvider

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
    
    # formatting to 4 decimals 
    @staticmethod
    def format_or_na(value):
        return "{:.4f}".format(value) if isinstance(value, (int, float)) else "NA"
    
    # industry sector
    @staticmethod
    def prepare_industry_sector_factor(sector):
        return {
            "Steel": 2.5,
            "Aluminium": 1.7,
            "Thermal": 10,
            "Solar": 0.1,
        }.get(sector, 1)
    
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
        total_emission=0
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
                    total_emission += self.financed_emission(scope1 * float(fuel_key)) 
                except Exception as e:
                    print(f"Error in fuel_{i + 1} row {row}: {e}")
                    continue

        return total_emission

    # asset emissions
    def assetbased(self, industry_region, sector):
        emission_1 = 0
        emission_2 = 0

        data = AssetEmissionFactorProvider.get_factors(sector)
        values = data.get(industry_region)

        if values and len(values) >= 2:
            emission_1 = self.financed_emission(float(values[0]))
            emission_2 = self.financed_emission(float(values[1]))

        return emission_1, emission_2

