from valuation_engine.vehicle_math import VehicleMathEngine

def verify():
    # Object: 7 years, 398,604 km
    i_obj = VehicleMathEngine.calculate_physical_wear(7, 398604)
    print(f"Object Wear: {i_obj:.4f} (Expected: 0.8482)")
    
    # Analog 1: 7 years, 210,000 km
    i_ana1 = VehicleMathEngine.calculate_physical_wear(7, 210000)
    print(f"Analog 1 Wear: {i_ana1:.4f} (Expected: 0.7062)")
    
    # K adjustment
    k = VehicleMathEngine.calculate_wear_adjustment(i_obj, i_ana1)
    print(f"K Adjustment: {k:.4f} (Expected: -0.2010)")

if __name__ == "__main__":
    verify()
