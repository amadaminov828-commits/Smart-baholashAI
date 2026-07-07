import math
from datetime import datetime

class VehicleMathEngine:
    """
    15-son MBS asosidagi avtotransport vositalarini baholash matematik dvigateli.
    """
    
    # Konstantalar (yengil avtomobillar uchun odatiy)
    A_CONST = 0.07
    B_CONST = 0.0035
    
    # Texnik holat shkalasi (MBS-15 asosida)
    TECHNICAL_CONDITION_SCALE = {
        "Yangi": 5.0,           # 0-10 o'rtachasi
        "Juda yaxshi": 22.5,    # 10-35 o'rtachasi
        "Yaxshi": 42.5,         # 35-50 o'rtachasi
        "Qoniqarli": 55.0,       # 50-60 o'rtachasi
        "Shartli-yaroqli": 65.0, # 60-70 o'rtachasi
        "Qoniqarsiz": 75.0,      # 70-80 o'rtachasi
        "Cheklangan holat": 85.0 # 80-90 o'rtachasi
    }

    @staticmethod
    def calculate_physical_wear(age_years, mileage_km):
        """
        Jismoniy eskirish (I) hisoblash: I = 1 - e^-(a*Df + b*Pf)
        Pf - ming km da.
        """
        Df = float(age_years)
        Pf = float(mileage_km) / 1000.0
        
        omega = (VehicleMathEngine.A_CONST * Df) + (VehicleMathEngine.B_CONST * Pf)
        wear = 1 - math.exp(-omega)
        return wear

    @staticmethod
    def calculate_wear_adjustment(i_object, i_analog):
        """
        Jismoniy eskirishga tuzatish koeffisiyenti (K): K = (Iana - Iobj) / (1 - Iana)
        """
        if i_analog >= 1.0: 
            return 0.0
        return (i_analog - i_object) / (1.0 - i_analog)

    @staticmethod
    def calculate_age(manufacturing_year, valuation_date=None):
        """
        Xronologik yoshni hisoblash.
        """
        if valuation_date is None:
            valuation_date = datetime.now()
        elif isinstance(valuation_date, str):
            # Formats: 21/10/2025 or 2025-10-21
            for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
                try:
                    valuation_date = datetime.strptime(valuation_date, fmt)
                    break
                except ValueError:
                    continue
        
        return max(0, valuation_date.year - int(manufacturing_year))

    @staticmethod
    def calculate_weights(analogs_adjustments):
        """
        Analoglar uchun vaznlarni hisoblash. 
        Mantiq: Tuzatishlar yig'indisi qancha kichik bo'lsa, vazn shuncha katta.
        analogs_adjustments: list of absolute sum of percentage adjustments for each analog.
        """
        if not analogs_adjustments:
            return []
            
        # 1. Teskari qiymatlarni hisoblash (Inverse values)
        # Agar tuzatish 0 bo'lsa, kichik son qo'shamiz
        inverses = [1.0 / (abs(a) + 0.001) for a in analogs_adjustments]
        total_inverse = sum(inverses)
        
        # 2. Normallashtirish (Vaznlar yig'indisi 1 bo'lishi kerak)
        weights = [inv / total_inverse for inv in inverses]
        return weights

    @staticmethod
    def get_scale_wear(technical_condition):
        """
        Texnik holat shkalasi bo'yicha eskirishni olish.
        """
        return VehicleMathEngine.TECHNICAL_CONDITION_SCALE.get(technical_condition, 50.0)

    @staticmethod
    def calculate_aggregate_wear(act_wear, scale_wear, formula_wear):
        """
        Jamlangan (agregatlangan) jismoniy eskirishni hisoblash.
        (Method1 + Method2 + Method3) / 3
        """
        # Formula_wear typically 0-1 range, others 0-100. Normalize all to 0-100.
        f_wear = formula_wear * 100.0 if formula_wear <= 1.0 else formula_wear
        
        return (float(act_wear) + float(scale_wear) + float(f_wear)) / 3.0

    @staticmethod
    def calculate_residual_value(replacement_cost, aggregate_wear_percent):
        """
        Qoldiq qiymatni aniqlash: Cqold = Ctikl * (1 - Ijam)
        """
        return float(replacement_cost) * (1 - (float(aggregate_wear_percent) / 100.0))

    @staticmethod
    def calculate_final_weighted_value(comparative_value, cost_value, comparative_score=12, cost_score=0):
        """
        Yondashuvlarni vaznlar bo'yicha birlashtirish.
        Misol: Comparative=12 ball, Cost=0 ball -> Vazn 1.0 vs 0.0
        """
        total_score = float(comparative_score) + float(cost_score)
        if total_score == 0: return float(comparative_value)
        
        comp_weight = float(comparative_score) / total_score
        cost_weight = float(cost_score) / total_score
        
        return (float(comparative_value) * comp_weight) + (float(cost_value) * cost_weight)

    @staticmethod
    def calculate_robust_price(prices):
        """
        Narxlarni barqarorlashtirish (Median yoki Truncated Mean).
        O'ta baland yoki past narxlarni ta'sirini kamaytiradi.
        """
        if not prices: return 0.0
        
        sorted_prices = sorted([float(p) for p in prices])
        n = len(sorted_prices)
        
        if n >= 5:
            # Agar 5 tadan ko'p bo'lsa, eng chetki 20% ni olib tashlaymiz (Trimmed Mean)
            trim = max(1, n // 5)
            trimmed = sorted_prices[trim:-trim]
            return sum(trimmed) / len(trimmed)
        else:
            # Agar kam bo'lsa, Median
            if n % 2 == 1:
                return sorted_prices[n // 2]
            else:
                return (sorted_prices[n // 2 - 1] + sorted_prices[n // 2]) / 2.0

    @staticmethod
    def round_to_nearest_thousand(value):
        """
        Qiymatni minglikkacha yaxlitlash.
        """
        return round(float(value) / 1000.0) * 1000
