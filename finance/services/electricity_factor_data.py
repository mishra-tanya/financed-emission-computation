class ElectricityEmissionFactorProvider:
    @staticmethod
    def get_factors(mode):
        if mode == "Amount":
            return [
                ["North America", 2],
                ["Asia", 3],
                ["Europe", 3],
            ]
        elif mode == "Quantity":
            return [
                ["North America", 3],
                ["Asia", 4],
                ["Europe", 2],
            ]
        return []
