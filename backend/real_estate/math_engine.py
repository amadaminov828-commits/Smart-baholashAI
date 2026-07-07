import math
import datetime

class RealEstateMathEngine:
    """
    Real Estate valuation math engine incorporating:
    - Comparative adjustment matrix & robust weighting
    - Cost approach: Physical wear (Actual/Normative) & Indexation
    - Income approach: NOI Chain & Cumulative Cap Rate
    """

    @staticmethod
    def calculate_physical_wear(actual_age, normative_life=100):
        """
        I_f = (T_haqiqiy / T_normativ) * 100%
        """
        if normative_life <= 0: return 0
        return min(100, (float(actual_age) / float(normative_life)) * 100.0)

    @staticmethod
    def calculate_income_value(unit_rent, area, vacancy_rate=0.07, opex_rate=0.15, cap_rate=0.12):
        """
        PGI -> EGI -> NOI -> Value
        """
        pgi = float(unit_rent) * float(area) * 12
        egi = pgi * (1 - float(vacancy_rate))
        noi = egi * (1 - float(opex_rate))
        value = noi / float(cap_rate) if cap_rate > 0 else 0
        return {
            'pgi': pgi,
            'egi': egi,
            'noi': noi,
            'value': value
        }

    @staticmethod
    def calculate_cap_rate(risk_free=0.08, risk1=0.02, risk2=0.01, liquidity_risk=0.01):
        """
        R = R_bezrisk + R_risk1 + R_risk2 + R_likvidlik
        """
        return float(risk_free) + float(risk1) + float(risk2) + float(liquidity_risk)

    @staticmethod
    def calculate_robust_average(prices, weights=None):
        """
        Sum(Price_i * Weight_i)
        """
        if not prices: return 0
        if not weights or len(weights) != len(prices):
            # Equal weighting if not provided
            return sum(prices) / len(prices)
        
        # Normalize weights to sum to 1.0
        total_w = sum(weights)
        if total_w == 0: return sum(prices) / len(prices)
        
        norm_weights = [w / total_w for w in weights]
        return sum(p * w for p, w in zip(prices, norm_weights))

    @staticmethod
    def calculate_reproduction_cost(base_cost, area_or_vol, indexation=1.0):
        """
        ShNQ * Volume * Index
        """
        return float(base_cost) * float(area_or_vol) * float(indexation)

    @staticmethod
    def calculate_comparative_adjustment(base_price_m2, location_adj=1.0, repair_adj=1.0, floor_adj=1.0, utilities_adj=1.0):
        """
        Adjusted Price = Base * Product(Coefficients)
        """
        return float(base_price_m2) * location_adj * repair_adj * floor_adj * utilities_adj
