# Vehicle Specifications Catalog Database

# Detailed catalog mapping standard vehicle models to their manufacturer factory-certified specifications.
# Fits Uzbekistan's popular models and a wide range of global automobile brands.
# Parameters:
# - engine_capacity: volume in cubic centimeters (cm³)
# - engine_horsepower: power in horsepower (ot kuchi)
# - seats_count: passenger capacity including driver (o'rindiqlar soni)
# - empty_weight: mass of vehicle in service without load (yuksiz vazni in kg)
# - full_weight: maximum permissible weight under full load (to'la vazni in kg)
# - fuel_type: fuel class (Benzin, Dizel, Elektr, Gaz, Benzin/Gaz, GBASNG)
# - transmission_type: default transmission (Mexanika, Avtomat, Variator, Robot)

VEHICLE_SPECS_CATALOG = {
    # === UZBEKISTAN DOMESTIC / UZAUTO MOTORS MODELS ===
    'DAMAS': {
        'engine_capacity': 796,
        'engine_horsepower': 38,
        'seats_count': 7,
        'empty_weight': 850,
        'full_weight': 1353,
        'fuel_type': 'GBASNG',
        'engine_prefix': 'F8CB',
        'transmission_type': 'Mexanika'
    },
    'LABO': {
        'engine_capacity': 796,
        'engine_horsepower': 38,
        'seats_count': 2,
        'empty_weight': 740,
        'full_weight': 1190,
        'fuel_type': 'GBASNG',
        'engine_prefix': 'F8CB',
        'transmission_type': 'Mexanika'
    },
    'COBALT': {
        'engine_capacity': 1485,
        'engine_horsepower': 106,
        'seats_count': 5,
        'empty_weight': 1190,
        'full_weight': 1620,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'GENTRA': {
        'engine_capacity': 1485,
        'engine_horsepower': 106,
        'seats_count': 5,
        'empty_weight': 1300,
        'full_weight': 1660,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'LACETTI': {
        'engine_capacity': 1485,
        'engine_horsepower': 106,
        'seats_count': 5,
        'empty_weight': 1300,
        'full_weight': 1660,
        'fuel_type': 'Benzin',
        'transmission_type': 'Mexanika'
    },
    'SPARK': {
        'engine_capacity': 1249,
        'engine_horsepower': 85,
        'seats_count': 5,
        'empty_weight': 950,
        'full_weight': 1280,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'NEXIA 3': {
        'engine_capacity': 1485,
        'engine_horsepower': 106,
        'seats_count': 5,
        'empty_weight': 1085,
        'full_weight': 1520,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'NEXIA 2': {
        'engine_capacity': 1498,
        'engine_horsepower': 80,
        'seats_count': 5,
        'empty_weight': 1025,
        'full_weight': 1430,
        'fuel_type': 'Benzin',
        'transmission_type': 'Mexanika'
    },
    'NEXIA 1': {
        'engine_capacity': 1498,
        'engine_horsepower': 75,
        'seats_count': 5,
        'empty_weight': 1025,
        'full_weight': 1430,
        'fuel_type': 'Benzin',
        'transmission_type': 'Mexanika'
    },
    'NEXIA': {
        'engine_capacity': 1485,
        'engine_horsepower': 106,
        'seats_count': 5,
        'empty_weight': 1085,
        'full_weight': 1520,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'TRACKER': {
        'engine_capacity': 999,
        'engine_horsepower': 116,
        'seats_count': 5,
        'empty_weight': 1260,
        'full_weight': 1710,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'ONIX': {
        'engine_capacity': 1199,
        'engine_horsepower': 132,
        'seats_count': 5,
        'empty_weight': 1120,
        'full_weight': 1530,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'MALIBU': {
        'engine_capacity': 1490,
        'engine_horsepower': 166,
        'seats_count': 5,
        'empty_weight': 1420,
        'full_weight': 1950,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'MONZA': {
        'engine_capacity': 1498,
        'engine_horsepower': 113,
        'seats_count': 5,
        'empty_weight': 1260,
        'full_weight': 1680,
        'fuel_type': 'Benzin',
        'transmission_type': 'Robot'
    },
    'CAPTIVA': {
        'engine_capacity': 2997,
        'engine_horsepower': 249,
        'seats_count': 7,
        'empty_weight': 1860,
        'full_weight': 2505,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'ORLANDO': {
        'engine_capacity': 1796,
        'engine_horsepower': 141,
        'seats_count': 7,
        'empty_weight': 1528,
        'full_weight': 2160,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'EPICA': {
        'engine_capacity': 1993,
        'engine_horsepower': 143,
        'seats_count': 5,
        'empty_weight': 1500,
        'full_weight': 1985,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'EQUINOX': {
        'engine_capacity': 1998,
        'engine_horsepower': 252,
        'seats_count': 5,
        'empty_weight': 1715,
        'full_weight': 2200,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'TRAVERSE': {
        'engine_capacity': 3564,
        'engine_horsepower': 318,
        'seats_count': 7,
        'empty_weight': 2014,
        'full_weight': 2800,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'TAHOE': {
        'engine_capacity': 6162,
        'engine_horsepower': 426,
        'seats_count': 7,
        'empty_weight': 2548,
        'full_weight': 3311,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },

    # === BYD (BUILD YOUR DREAMS) MODELS ===
    'BYD CHAZOR': {
        'engine_capacity': 1498,
        'engine_horsepower': 110,
        'seats_count': 5,
        'empty_weight': 1500,
        'full_weight': 1875,
        'fuel_type': 'Benzin/Gaz', # PHEV Hybrid
        'transmission_type': 'Variator'
    },
    'BYD SONG': {
        'engine_capacity': 1498,
        'engine_horsepower': 110,
        'seats_count': 5,
        'empty_weight': 1700,
        'full_weight': 2075,
        'fuel_type': 'Benzin/Gaz', # PHEV Hybrid
        'transmission_type': 'Variator'
    },
    'BYD HAN': {
        'engine_capacity': 1998,
        'engine_horsepower': 494,
        'seats_count': 5,
        'empty_weight': 2100,
        'full_weight': 2540,
        'fuel_type': 'Elektr',
        'transmission_type': 'Avtomat'
    },
    'BYD TANG': {
        'engine_capacity': 1998,
        'engine_horsepower': 517,
        'seats_count': 7,
        'empty_weight': 2360,
        'full_weight': 2860,
        'fuel_type': 'Elektr',
        'transmission_type': 'Avtomat'
    },
    'BYD YUAN': {
        'engine_capacity': 0,
        'engine_horsepower': 204,
        'seats_count': 5,
        'empty_weight': 1625,
        'full_weight': 2000,
        'fuel_type': 'Elektr',
        'transmission_type': 'Avtomat'
    },
    'BYD SEAGULL': {
        'engine_capacity': 0,
        'engine_horsepower': 75,
        'seats_count': 4,
        'empty_weight': 1160,
        'full_weight': 1460,
        'fuel_type': 'Elektr',
        'transmission_type': 'Avtomat'
    },
    'BYD DOLPHIN': {
        'engine_capacity': 0,
        'engine_horsepower': 95,
        'seats_count': 5,
        'empty_weight': 1405,
        'full_weight': 1780,
        'fuel_type': 'Elektr',
        'transmission_type': 'Avtomat'
    },
    'BYD QIN': {
        'engine_capacity': 1498,
        'engine_horsepower': 110,
        'seats_count': 5,
        'empty_weight': 1500,
        'full_weight': 1875,
        'fuel_type': 'Benzin/Gaz',
        'transmission_type': 'Variator'
    },
    'BYD DESTROYER': {
        'engine_capacity': 1498,
        'engine_horsepower': 110,
        'seats_count': 5,
        'empty_weight': 1500,
        'full_weight': 1875,
        'fuel_type': 'Benzin/Gaz',
        'transmission_type': 'Variator'
    },

    # === LADA (AVTOVAZ) MODELS ===
    'LADA VESTA': {
        'engine_capacity': 1596,
        'engine_horsepower': 106,
        'seats_count': 5,
        'empty_weight': 1230,
        'full_weight': 1670,
        'fuel_type': 'Benzin',
        'transmission_type': 'Mexanika'
    },
    'LADA GRANTA': {
        'engine_capacity': 1596,
        'engine_horsepower': 90,
        'seats_count': 5,
        'empty_weight': 1075,
        'full_weight': 1560,
        'fuel_type': 'Benzin',
        'transmission_type': 'Mexanika'
    },
    'LADA NIVA': {
        'engine_capacity': 1690,
        'engine_horsepower': 83,
        'seats_count': 5,
        'empty_weight': 1285,
        'full_weight': 1610,
        'fuel_type': 'Benzin',
        'transmission_type': 'Mexanika'
    },
    'NIVA LEGEND': {
        'engine_capacity': 1690,
        'engine_horsepower': 83,
        'seats_count': 5,
        'empty_weight': 1285,
        'full_weight': 1610,
        'fuel_type': 'Benzin',
        'transmission_type': 'Mexanika'
    },
    'NIVA TRAVEL': {
        'engine_capacity': 1690,
        'engine_horsepower': 80,
        'seats_count': 5,
        'empty_weight': 1485,
        'full_weight': 1860,
        'fuel_type': 'Benzin',
        'transmission_type': 'Mexanika'
    },
    'LADA LARGUS': {
        'engine_capacity': 1596,
        'engine_horsepower': 106,
        'seats_count': 7,
        'empty_weight': 1260,
        'full_weight': 1850,
        'fuel_type': 'Benzin',
        'transmission_type': 'Mexanika'
    },

    # === KIA MODELS ===
    'KIA K5': {
        'engine_capacity': 1999,
        'engine_horsepower': 150,
        'seats_count': 5,
        'empty_weight': 1410,
        'full_weight': 1920,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'KIA SPORTAGE': {
        'engine_capacity': 1999,
        'engine_horsepower': 150,
        'seats_count': 5,
        'empty_weight': 1500,
        'full_weight': 2050,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'KIA SELTOS': {
        'engine_capacity': 1999,
        'engine_horsepower': 149,
        'seats_count': 5,
        'empty_weight': 1375,
        'full_weight': 1800,
        'fuel_type': 'Benzin',
        'transmission_type': 'Variator'
    },
    'KIA CERATO': {
        'engine_capacity': 1591,
        'engine_horsepower': 128,
        'seats_count': 5,
        'empty_weight': 1230,
        'full_weight': 1720,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'KIA CARNIVAL': {
        'engine_capacity': 3470,
        'engine_horsepower': 272,
        'seats_count': 7,
        'empty_weight': 2090,
        'full_weight': 2740,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'KIA SORENTO': {
        'engine_capacity': 2497,
        'engine_horsepower': 180,
        'seats_count': 7,
        'empty_weight': 1780,
        'full_weight': 2430,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'KIA RIO': {
        'engine_capacity': 1396,
        'engine_horsepower': 100,
        'seats_count': 5,
        'empty_weight': 1050,
        'full_weight': 1560,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'KIA K8': {
        'engine_capacity': 3470,
        'engine_horsepower': 300,
        'seats_count': 5,
        'empty_weight': 1640,
        'full_weight': 2190,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'KIA EV6': {
        'engine_capacity': 0,
        'engine_horsepower': 325,
        'seats_count': 5,
        'empty_weight': 2015,
        'full_weight': 2530,
        'fuel_type': 'Elektr',
        'transmission_type': 'Avtomat'
    },

    # === HYUNDAI MODELS ===
    'HYUNDAI ACCENT': {
        'engine_capacity': 1396,
        'engine_horsepower': 100,
        'seats_count': 5,
        'empty_weight': 1050,
        'full_weight': 1560,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'HYUNDAI ELANTRA': {
        'engine_capacity': 1591,
        'engine_horsepower': 128,
        'seats_count': 5,
        'empty_weight': 1230,
        'full_weight': 1720,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'HYUNDAI SONATA': {
        'engine_capacity': 2497,
        'engine_horsepower': 180,
        'seats_count': 5,
        'empty_weight': 1485,
        'full_weight': 1980,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'HYUNDAI TUCSON': {
        'engine_capacity': 1999,
        'engine_horsepower': 150,
        'seats_count': 5,
        'empty_weight': 1500,
        'full_weight': 2050,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'HYUNDAI SANTA FE': {
        'engine_capacity': 2497,
        'engine_horsepower': 180,
        'seats_count': 7,
        'empty_weight': 1820,
        'full_weight': 2510,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'HYUNDAI PALISADE': {
        'engine_capacity': 3470,
        'engine_horsepower': 277,
        'seats_count': 7,
        'empty_weight': 2020,
        'full_weight': 2680,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'HYUNDAI CRETA': {
        'engine_capacity': 1591,
        'engine_horsepower': 123,
        'seats_count': 5,
        'empty_weight': 1260,
        'full_weight': 1720,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'HYUNDAI IONIQ': {
        'engine_capacity': 0,
        'engine_horsepower': 225,
        'seats_count': 5,
        'empty_weight': 1910,
        'full_weight': 2430,
        'fuel_type': 'Elektr',
        'transmission_type': 'Avtomat'
    },

    # === TOYOTA MODELS ===
    'TOYOTA CAMRY': {
        'engine_capacity': 2487,
        'engine_horsepower': 203,
        'seats_count': 5,
        'empty_weight': 1520,
        'full_weight': 2030,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'TOYOTA COROLLA': {
        'engine_capacity': 1598,
        'engine_horsepower': 122,
        'seats_count': 5,
        'empty_weight': 1280,
        'full_weight': 1765,
        'fuel_type': 'Benzin',
        'transmission_type': 'Variator'
    },
    'TOYOTA RAV4': {
        'engine_capacity': 2487,
        'engine_horsepower': 199,
        'seats_count': 5,
        'empty_weight': 1585,
        'full_weight': 2130,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'TOYOTA PRADO': {
        'engine_capacity': 2694,
        'engine_horsepower': 163,
        'seats_count': 7,
        'empty_weight': 2100,
        'full_weight': 2850,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'LAND CRUISER': {
        'engine_capacity': 3445,
        'engine_horsepower': 415,
        'seats_count': 7,
        'empty_weight': 2520,
        'full_weight': 3230,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'TOYOTA HIGHLANDER': {
        'engine_capacity': 2487,
        'engine_horsepower': 246,
        'seats_count': 7,
        'empty_weight': 2020,
        'full_weight': 2680,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'TOYOTA PRIUS': {
        'engine_capacity': 1797,
        'engine_horsepower': 98,
        'seats_count': 5,
        'empty_weight': 1360,
        'full_weight': 1790,
        'fuel_type': 'Benzin', # Hybrid
        'transmission_type': 'Variator'
    },

    # === TESLA MODELS ===
    'TESLA MODEL 3': {
        'engine_capacity': 0,
        'engine_horsepower': 283,
        'seats_count': 5,
        'empty_weight': 1611,
        'full_weight': 2060,
        'fuel_type': 'Elektr',
        'transmission_type': 'Avtomat'
    },
    'TESLA MODEL Y': {
        'engine_capacity': 0,
        'engine_horsepower': 347,
        'seats_count': 5,
        'empty_weight': 1910,
        'full_weight': 2300,
        'fuel_type': 'Elektr',
        'transmission_type': 'Avtomat'
    },
    'TESLA MODEL S': {
        'engine_capacity': 0,
        'engine_horsepower': 670,
        'seats_count': 5,
        'empty_weight': 2069,
        'full_weight': 2530,
        'fuel_type': 'Elektr',
        'transmission_type': 'Avtomat'
    },
    'TESLA MODEL X': {
        'engine_capacity': 0,
        'engine_horsepower': 670,
        'seats_count': 7,
        'empty_weight': 2300,
        'full_weight': 2820,
        'fuel_type': 'Elektr',
        'transmission_type': 'Avtomat'
    },

    # === CHERY MODELS ===
    'TIGGO 7': {
        'engine_capacity': 1498,
        'engine_horsepower': 147,
        'seats_count': 5,
        'empty_weight': 1439,
        'full_weight': 1888,
        'fuel_type': 'Benzin',
        'transmission_type': 'Variator'
    },
    'TIGGO 8': {
        'engine_capacity': 1598,
        'engine_horsepower': 186,
        'seats_count': 7,
        'empty_weight': 1600,
        'full_weight': 2135,
        'fuel_type': 'Benzin',
        'transmission_type': 'Robot'
    },
    'TIGGO 4': {
        'engine_capacity': 1498,
        'engine_horsepower': 113,
        'seats_count': 5,
        'empty_weight': 1300,
        'full_weight': 1680,
        'fuel_type': 'Benzin',
        'transmission_type': 'Variator'
    },
    'ARRIZO 6': {
        'engine_capacity': 1498,
        'engine_horsepower': 147,
        'seats_count': 5,
        'empty_weight': 1344,
        'full_weight': 1744,
        'fuel_type': 'Benzin',
        'transmission_type': 'Variator'
    },

    # === HAVAL MODELS ===
    'HAVAL JOLION': {
        'engine_capacity': 1497,
        'engine_horsepower': 143,
        'seats_count': 5,
        'empty_weight': 1445,
        'full_weight': 1845,
        'fuel_type': 'Benzin',
        'transmission_type': 'Robot'
    },
    'HAVAL H6': {
        'engine_capacity': 1998,
        'engine_horsepower': 204,
        'seats_count': 5,
        'empty_weight': 1685,
        'full_weight': 2085,
        'fuel_type': 'Benzin',
        'transmission_type': 'Robot'
    },
    'HAVAL DARGO': {
        'engine_capacity': 1998,
        'engine_horsepower': 192,
        'seats_count': 5,
        'empty_weight': 1700,
        'full_weight': 2150,
        'fuel_type': 'Benzin',
        'transmission_type': 'Robot'
    },

    # === GEELY MODELS ===
    'GEELY MONJARO': {
        'engine_capacity': 1998,
        'engine_horsepower': 238,
        'seats_count': 5,
        'empty_weight': 1865,
        'full_weight': 2265,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'GEELY COOLRAY': {
        'engine_capacity': 1477,
        'engine_horsepower': 150,
        'seats_count': 5,
        'empty_weight': 1340,
        'full_weight': 1640,
        'fuel_type': 'Benzin',
        'transmission_type': 'Robot'
    },
    'GEELY TUGELLA': {
        'engine_capacity': 1998,
        'engine_horsepower': 238,
        'seats_count': 5,
        'empty_weight': 1815,
        'full_weight': 2115,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },

    # === NISSAN MODELS ===
    'NISSAN PATROL': {
        'engine_capacity': 5552,
        'engine_horsepower': 400,
        'seats_count': 7,
        'empty_weight': 2695,
        'full_weight': 3500,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'NISSAN X-TRAIL': {
        'engine_capacity': 2488,
        'engine_horsepower': 171,
        'seats_count': 5,
        'empty_weight': 1610,
        'full_weight': 2130,
        'fuel_type': 'Benzin',
        'transmission_type': 'Variator'
    },
    'NISSAN LEAF': {
        'engine_capacity': 0,
        'engine_horsepower': 150,
        'seats_count': 5,
        'empty_weight': 1580,
        'full_weight': 2020,
        'fuel_type': 'Elektr',
        'transmission_type': 'Avtomat'
    },

    # === HONDA MODELS ===
    'HONDA CR-V': {
        'engine_capacity': 1498,
        'engine_horsepower': 190,
        'seats_count': 5,
        'empty_weight': 1590,
        'full_weight': 2130,
        'fuel_type': 'Benzin',
        'transmission_type': 'Variator'
    },
    'HONDA ACCORD': {
        'engine_capacity': 1498,
        'engine_horsepower': 192,
        'seats_count': 5,
        'empty_weight': 1470,
        'full_weight': 1980,
        'fuel_type': 'Benzin',
        'transmission_type': 'Variator'
    },
    'HONDA CIVIC': {
        'engine_capacity': 1498,
        'engine_horsepower': 180,
        'seats_count': 5,
        'empty_weight': 1330,
        'full_weight': 1785,
        'fuel_type': 'Benzin',
        'transmission_type': 'Variator'
    },

    # === PREMIUM GERMAN BRANDS (MERCEDES-BENZ, BMW, AUDI) ===
    'MERCEDES-BENZ E-CLASS': {
        'engine_capacity': 1991,
        'engine_horsepower': 197,
        'seats_count': 5,
        'empty_weight': 1730,
        'full_weight': 2360,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'MERCEDES-BENZ C-CLASS': {
        'engine_capacity': 1496,
        'engine_horsepower': 170,
        'seats_count': 5,
        'empty_weight': 1625,
        'full_weight': 2265,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'MERCEDES-BENZ S-CLASS': {
        'engine_capacity': 2999,
        'engine_horsepower': 367,
        'seats_count': 5,
        'empty_weight': 2015,
        'full_weight': 2690,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'MERCEDES-BENZ G': { # G-Class Gelendvagen
        'engine_capacity': 3982,
        'engine_horsepower': 422,
        'seats_count': 5,
        'empty_weight': 2429,
        'full_weight': 3200,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'BMW 5': { # BMW 5 Series
        'engine_capacity': 1998,
        'engine_horsepower': 184,
        'seats_count': 5,
        'empty_weight': 1610,
        'full_weight': 2230,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'BMW 3': { # BMW 3 Series
        'engine_capacity': 1998,
        'engine_horsepower': 184,
        'seats_count': 5,
        'empty_weight': 1500,
        'full_weight': 2085,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'BMW 7': { # BMW 7 Series
        'engine_capacity': 2998,
        'engine_horsepower': 381,
        'seats_count': 5,
        'empty_weight': 2075,
        'full_weight': 2700,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'BMW X5': {
        'engine_capacity': 2998,
        'engine_horsepower': 340,
        'seats_count': 5,
        'empty_weight': 2100,
        'full_weight': 2860,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'BMW X7': {
        'engine_capacity': 2998,
        'engine_horsepower': 381,
        'seats_count': 7,
        'empty_weight': 2415,
        'full_weight': 3215,
        'fuel_type': 'Benzin',
        'transmission_type': 'Avtomat'
    },
    'AUDI A6': {
        'engine_capacity': 1984,
        'engine_horsepower': 190,
        'seats_count': 5,
        'empty_weight': 1680,
        'full_weight': 2240,
        'fuel_type': 'Benzin',
        'transmission_type': 'Robot'
    },
    'AUDI Q5': {
        'engine_capacity': 1984,
        'engine_horsepower': 245,
        'seats_count': 5,
        'empty_weight': 1720,
        'full_weight': 2380,
        'fuel_type': 'Benzin',
        'transmission_type': 'Robot'
    },
}
