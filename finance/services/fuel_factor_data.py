class FuelEmissionFactorProvider:
    @staticmethod
    def get_factors(mode):
        if mode == "Amount":
            return {
                "fuel_1": [
                    ["North America", 7],
                    ["Asia", 5],
                    ["Europe", 8],
                ],
                "fuel_2": [
                    ["North America", 5],
                    ["Asia", 6],
                    ["Europe", 4],
                ],
                "fuel_3": [
                    ["North America", 9],
                    ["Asia", 9],
                    ["Europe", 10],
                ]
            }
        elif mode == "Quantity":
            return {
                "fuel_1": [
                    ["North America", 30],
                    ["Asia", 2],
                    ["Europe", 33],
                ],
                "fuel_2": [
                    ["North America", 25],
                    ["Asia", 8],
                    ["Europe", 23],
                ],
                "fuel_3": [
                    ["North America", 45],
                    ["Asia", 3],
                    ["Europe", 23],
                ]
            }
        else:
            return {}
