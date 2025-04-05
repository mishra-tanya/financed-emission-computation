class AssetEmissionFactorProvider:
    @staticmethod
    def get_factors(sector):
        sector = sector.lower()
        if sector == "steel":
            return {
                "North America": [23, 34],
                "Asia": [33, 32],
                "Europe": [43, 53],
            }
        elif sector == "aluminium":
            return {
                "North America": [10, 20],
                "Asia": [5, 15],
                "Europe": [8, 18],
            }
        elif sector == "thermal":
            return {
                "North America": [12, 22],
                "Asia": [6, 16],
                "Europe": [9, 19],
            }
        elif sector == "solar":
            return {
                "North America": [2, 3],
                "Asia": [1, 2],
                "Europe": [1.5, 2.5],
            }
        else:
            return {}
