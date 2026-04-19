import numpy as np
import pandas as pd

# Surface Factor (Chap08_Lctr01 Slide 22)
SuMetric = np.array([0.414, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.793]) #GPa
CsMachined = np.array([0.80, 0.77, 0.74, 0.70, 0.66, 0.62, 0.56, 0.51])

# --- Shaft Data ---
diametersCatalog = np.array([17, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75]) # bores from bearings catalog

# --- BEARINGS DATA ---
# Bearing Dimensions (Chap14_Lctr01 Slide)
bearingCatalog = {
    "L03": {"bore": 17, "ball": {"od": 35, "w": 10, "r": 0.30, "ds": 19.8, "dh": 32.3}, "roller": {"od": 35, "w": 10, "r": 0.64, "ds": 20.8, "dh": 32.0}},
    "203": {"bore": 17, "ball": {"od": 40, "w": 12, "r": 0.64, "ds": 22.4, "dh": 34.8}, "roller": {"od": 40, "w": 12, "r": 0.64, "ds": 20.8, "dh": 36.3}},
    "303": {"bore": 17, "ball": {"od": 47, "w": 14, "r": 1.02, "ds": 23.6, "dh": 41.1}, "roller": {"od": 47, "w": 14, "r": 1.02, "ds": 22.9, "dh": 41.4}},
    
    "L04": {"bore": 20, "ball": {"od": 42, "w": 12, "r": 0.64, "ds": 23.9, "dh": 38.1}, "roller": {"od": 42, "w": 12, "r": 0.64, "ds": 24.4, "dh": 36.8}},
    "204": {"bore": 20, "ball": {"od": 47, "w": 14, "r": 1.02, "ds": 25.9, "dh": 41.7}, "roller": {"od": 47, "w": 14, "r": 1.02, "ds": 25.9, "dh": 42.7}},
    "304": {"bore": 20, "ball": {"od": 52, "w": 15, "r": 1.02, "ds": 27.7, "dh": 45.2}, "roller": {"od": 52, "w": 15, "r": 1.02, "ds": 25.9, "dh": 46.2}},
    
    "L05": {"bore": 25, "ball": {"od": 47, "w": 12, "r": 0.64, "ds": 29.0, "dh": 42.9}, "roller": {"od": 47, "w": 12, "r": 0.64, "ds": 29.2, "dh": 43.4}},
    "205": {"bore": 25, "ball": {"od": 52, "w": 15, "r": 1.02, "ds": 30.5, "dh": 46.7}, "roller": {"od": 52, "w": 15, "r": 1.02, "ds": 30.5, "dh": 47.0}},
    "305": {"bore": 25, "ball": {"od": 62, "w": 17, "r": 1.02, "ds": 33.0, "dh": 54.9}, "roller": {"od": 62, "w": 17, "r": 1.02, "ds": 31.5, "dh": 55.9}},
    
    "L06": {"bore": 30, "ball": {"od": 55, "w": 13, "r": 1.02, "ds": 34.8, "dh": 49.3}, "roller": {"od": 47, "w": 9, "r": 0.38, "ds": 33.3, "dh": 43.9}},
    "206": {"bore": 30, "ball": {"od": 62, "w": 16, "r": 1.02, "ds": 36.8, "dh": 55.4}, "roller": {"od": 62, "w": 16, "r": 1.02, "ds": 36.1, "dh": 56.4}},
    "306": {"bore": 30, "ball": {"od": 72, "w": 19, "r": 1.02, "ds": 38.4, "dh": 64.8}, "roller": {"od": 72, "w": 19, "r": 1.52, "ds": 37.8, "dh": 64.0}},
    
    "L07": {"bore": 35, "ball": {"od": 62, "w": 14, "r": 1.02, "ds": 40.1, "dh": 56.1}, "roller": {"od": 55, "w": 10, "r": 0.64, "ds": 39.4, "dh": 50.8}},
    "207": {"bore": 35, "ball": {"od": 72, "w": 17, "r": 1.02, "ds": 42.4, "dh": 65.0}, "roller": {"od": 72, "w": 17, "r": 1.02, "ds": 41.7, "dh": 65.3}},
    "307": {"bore": 35, "ball": {"od": 80, "w": 21, "r": 1.52, "ds": 45.2, "dh": 70.4}, "roller": {"od": 80, "w": 21, "r": 1.52, "ds": 43.7, "dh": 71.4}},
    
    "L08": {"bore": 40, "ball": {"od": 68, "w": 15, "r": 1.02, "ds": 45.2, "dh": 62.0}, "roller": {"od": 68, "w": 15, "r": 1.02, "ds": 45.7, "dh": 62.7}},
    "208": {"bore": 40, "ball": {"od": 80, "w": 18, "r": 1.02, "ds": 48.0, "dh": 72.4}, "roller": {"od": 80, "w": 18, "r": 1.52, "ds": 47.2, "dh": 72.9}},
    "308": {"bore": 40, "ball": {"od": 90, "w": 23, "r": 1.52, "ds": 50.8, "dh": 80.0}, "roller": {"od": 90, "w": 23, "r": 1.52, "ds": 49.0, "dh": 81.3}},
    
    "L09": {"bore": 45, "ball": {"od": 75, "w": 16, "r": 1.02, "ds": 50.8, "dh": 68.6}, "roller": {"od": 75, "w": 16, "r": 1.02, "ds": 50.8, "dh": 69.3}},
    "209": {"bore": 45, "ball": {"od": 85, "w": 19, "r": 1.02, "ds": 52.8, "dh": 77.5}, "roller": {"od": 85, "w": 19, "r": 1.52, "ds": 52.8, "dh": 78.2}},
    "309": {"bore": 45, "ball": {"od": 100, "w": 25, "r": 1.52, "ds": 57.2, "dh": 88.9}, "roller": {"od": 100, "w": 25, "r": 2.03, "ds": 55.9, "dh": 90.4}},
    
    "L10": {"bore": 50, "ball": {"od": 80, "w": 16, "r": 1.02, "ds": 55.6, "dh": 73.7}, "roller": {"od": 72, "w": 12, "r": 0.64, "ds": 54.1, "dh": 68.1}},
    "210": {"bore": 50, "ball": {"od": 90, "w": 20, "r": 1.02, "ds": 57.7, "dh": 82.3}, "roller": {"od": 90, "w": 20, "r": 1.52, "ds": 57.7, "dh": 82.8}},
    "310": {"bore": 50, "ball": {"od": 110, "w": 27, "r": 2.03, "ds": 64.3, "dh": 96.5}, "roller": {"od": 110, "w": 27, "r": 2.03, "ds": 61.0, "dh": 99.1}},
    
    "L11": {"bore": 55, "ball": {"od": 90, "w": 18, "r": 1.02, "ds": 61.7, "dh": 83.1}, "roller": {"od": 90, "w": 18, "r": 1.52, "ds": 62.0, "dh": 83.6}},
    "211": {"bore": 55, "ball": {"od": 100, "w": 21, "r": 1.52, "ds": 65.0, "dh": 90.2}, "roller": {"od": 100, "w": 21, "r": 2.03, "ds": 64.0, "dh": 91.4}},
    "311": {"bore": 55, "ball": {"od": 120, "w": 29, "r": 2.03, "ds": 69.8, "dh": 106.2}, "roller": {"od": 120, "w": 29, "r": 2.03, "ds": 66.5, "dh": 108.7}},
    
    "L12": {"bore": 60, "ball": {"od": 95, "w": 18, "r": 1.02, "ds": 66.8, "dh": 87.9}, "roller": {"od": 95, "w": 18, "r": 1.52, "ds": 67.1, "dh": 88.6}},
    "212": {"bore": 60, "ball": {"od": 110, "w": 22, "r": 1.52, "ds": 70.6, "dh": 99.3}, "roller": {"od": 110, "w": 22, "r": 2.03, "ds": 69.3, "dh": 101.3}},
    "312": {"bore": 60, "ball": {"od": 130, "w": 31, "r": 2.03, "ds": 75.4, "dh": 115.6}, "roller": {"od": 130, "w": 31, "r": 2.54, "ds": 72.9, "dh": 117.9}},
    
    "L13": {"bore": 65, "ball": {"od": 100, "w": 18, "r": 1.02, "ds": 71.9, "dh": 92.7}, "roller": {"od": 100, "w": 18, "r": 1.52, "ds": 72.1, "dh": 93.7}},
    "213": {"bore": 65, "ball": {"od": 120, "w": 23, "r": 1.52, "ds": 76.5, "dh": 108.7}, "roller": {"od": 120, "w": 23, "r": 2.54, "ds": 77.0, "dh": 110.0}},
    "313": {"bore": 65, "ball": {"od": 140, "w": 33, "r": 2.03, "ds": 81.3, "dh": 125.0}, "roller": {"od": 140, "w": 33, "r": 2.54, "ds": 78.7, "dh": 127.0}},
    
    "L14": {"bore": 70, "ball": {"od": 110, "w": 20, "r": 1.02, "ds": 77.7, "dh": 102.1}, "roller": {"od": 110, "w": 20, "r": None, "ds": None, "dh": None}},
    "214": {"bore": 70, "ball": {"od": 125, "w": 24, "r": 1.52, "ds": 81.0, "dh": 114.0}, "roller": {"od": 125, "w": 24, "r": 2.54, "ds": 81.8, "dh": 115.6}},
    "314": {"bore": 70, "ball": {"od": 150, "w": 35, "r": 2.03, "ds": 86.9, "dh": 134.4}, "roller": {"od": 150, "w": 35, "r": 3.18, "ds": 84.3, "dh": 135.6}},
    
    "L15": {"bore": 75, "ball": {"od": 115, "w": 20, "r": 1.02, "ds": 82.3, "dh": 107.2}, "roller": {"od": 115, "w": 20, "r": None, "ds": None, "dh": None}},
    "215": {"bore": 75, "ball": {"od": 130, "w": 25, "r": 1.52, "ds": 86.1, "dh": 118.9}, "roller": {"od": 130, "w": 25, "r": 2.54, "ds": 85.6, "dh": 120.1}},
    "315": {"bore": 75, "ball": {"od": 160, "w": 37, "r": 2.03, "ds": 92.7, "dh": 143.8}, "roller": {"od": 160, "w": 37, "r": 3.18, "ds": 90.4, "dh": 145.8}}
}
# Flatten the dictionary so Pandas can easily ingest it
flatData = []
for bId, data in bearingCatalog.items():
    # Append the ball bearing row
    flatData.append({
        "basicNumber": bId, "type": "ball", "bore": data["bore"],
        **data["ball"] # Unpacks od, w, r, ds, dh
    })
    # Append the roller bearing row
    flatData.append({
        "basicNumber": bId, "type": "roller", "bore": data["bore"],
        **data["roller"]
    })
dfBearings = pd.DataFrame(flatData)

bearingLoadCapacityMap = {
    10: {
        "radialBall": {"xlt_L00": 1.02, "lt_200": 1.42, "med_300": 1.90},
        "angularBall": {"xlt_L00": 1.02, "lt_200": 1.10, "med_300": 1.88},
        "roller": {"xlt_1000": None, "lt_1200": None, "med_1300": None}
    },
    12: {
        "radialBall": {"xlt_L00": 1.12, "lt_200": 1.42, "med_300": 2.46},
        "angularBall": {"xlt_L00": 1.10, "lt_200": 1.54, "med_300": 2.05},
        "roller": {"xlt_1000": None, "lt_1200": None, "med_1300": None}
    },
    15: {
        "radialBall": {"xlt_L00": 1.22, "lt_200": 1.56, "med_300": 3.05},
        "angularBall": {"xlt_L00": 1.28, "lt_200": 1.66, "med_300": 2.85},
        "roller": {"xlt_1000": None, "lt_1200": None, "med_1300": None}
    },
    17: {
        "radialBall": {"xlt_L00": 1.32, "lt_200": 2.70, "med_300": 3.75},
        "angularBall": {"xlt_L00": 1.36, "lt_200": 2.20, "med_300": 3.55},
        "roller": {"xlt_1000": 2.12, "lt_1200": 3.80, "med_1300": 4.90}
    },
    20: {
        "radialBall": {"xlt_L00": 2.25, "lt_200": 3.35, "med_300": 5.30},
        "angularBall": {"xlt_L00": 2.20, "lt_200": 3.05, "med_300": 5.80},
        "roller": {"xlt_1000": 3.30, "lt_1200": 4.40, "med_1300": 6.20}
    },
    25: {
        "radialBall": {"xlt_L00": 2.45, "lt_200": 3.65, "med_300": 5.90},
        "angularBall": {"xlt_L00": 2.65, "lt_200": 3.25, "med_300": 7.20},
        "roller": {"xlt_1000": 3.70, "lt_1200": 5.50, "med_1300": 8.50}
    },
    30: {
        "radialBall": {"xlt_L00": 3.35, "lt_200": 5.40, "med_300": 8.80},
        "angularBall": {"xlt_L00": 3.60, "lt_200": 6.00, "med_300": 8.80},
        "roller": {"xlt_1000": 2.40, "lt_1200": 8.30, "med_1300": 10.0}
    },
    35: {
        "radialBall": {"xlt_L00": 4.20, "lt_200": 8.50, "med_300": 10.6},
        "angularBall": {"xlt_L00": 4.75, "lt_200": 8.20, "med_300": 11.0},
        "roller": {"xlt_1000": 3.10, "lt_1200": 9.30, "med_1300": 13.1}
    },
    40: {
        "radialBall": {"xlt_L00": 4.50, "lt_200": 9.40, "med_300": 12.6},
        "angularBall": {"xlt_L00": 4.95, "lt_200": 9.90, "med_300": 13.2},
        "roller": {"xlt_1000": 7.20, "lt_1200": 11.1, "med_1300": 16.5}
    },
    45: {
        "radialBall": {"xlt_L00": 5.80, "lt_200": 9.10, "med_300": 14.8},
        "angularBall": {"xlt_L00": 6.30, "lt_200": 10.4, "med_300": 16.4},
        "roller": {"xlt_1000": 7.40, "lt_1200": 12.2, "med_1300": 20.9}
    },
    50: {
        "radialBall": {"xlt_L00": 6.10, "lt_200": 9.70, "med_300": 15.8},
        "angularBall": {"xlt_L00": 6.60, "lt_200": 11.0, "med_300": 19.2},
        "roller": {"xlt_1000": 5.10, "lt_1200": 12.5, "med_1300": 24.5}
    },
    55: {
        "radialBall": {"xlt_L00": 8.20, "lt_200": 12.0, "med_300": 18.0},
        "angularBall": {"xlt_L00": 9.00, "lt_200": 13.6, "med_300": 21.5},
        "roller": {"xlt_1000": 11.3, "lt_1200": 14.9, "med_1300": 27.1}
    },
    60: {
        "radialBall": {"xlt_L00": 8.70, "lt_200": 13.6, "med_300": 20.0},
        "angularBall": {"xlt_L00": 9.70, "lt_200": 16.4, "med_300": 24.0},
        "roller": {"xlt_1000": 12.0, "lt_1200": 18.9, "med_1300": 32.5}
    },
    65: {
        "radialBall": {"xlt_L00": 9.10, "lt_200": 16.0, "med_300": 22.0},
        "angularBall": {"xlt_L00": 10.2, "lt_200": 19.2, "med_300": 26.5},
        "roller": {"xlt_1000": 12.2, "lt_1200": 21.1, "med_1300": 38.3}
    },
    70: {
        "radialBall": {"xlt_L00": 11.6, "lt_200": 17.0, "med_300": 24.5},
        "angularBall": {"xlt_L00": 13.4, "lt_200": 19.2, "med_300": 29.5},
        "roller": {"xlt_1000": None, "lt_1200": 23.6, "med_1300": 44.0}
    },
    75: {
        "radialBall": {"xlt_L00": 12.2, "lt_200": 17.0, "med_300": 25.5},
        "angularBall": {"xlt_L00": 13.8, "lt_200": 20.0, "med_300": 32.5},
        "roller": {"xlt_1000": None, "lt_1200": 23.6, "med_1300": 45.4}
    },
    80: {
        "radialBall": {"xlt_L00": 14.2, "lt_200": 18.4, "med_300": 28.0},
        "angularBall": {"xlt_L00": 16.6, "lt_200": 22.5, "med_300": 35.5},
        "roller": {"xlt_1000": 17.3, "lt_1200": 26.2, "med_1300": 51.6}
    }
}
flatLoadData = []
# Flatten the nested dictionary
for boreSize, types in bearingLoadCapacityMap.items():
    for bearingType, seriesData in types.items():
        for seriesPrefix, loadValue in seriesData.items():
            # seriesPrefix looks like 'xlt_L00', we can split it to be cleaner
            seriesClass, seriesNumber = seriesPrefix.split('_')
            
            flatLoadData.append({
                "bore": boreSize,
                "bearingType": bearingType,
                "seriesClass": seriesClass,   # e.g., 'xlt', 'lt', 'med'
                "seriesNumber": seriesNumber, # e.g., 'L00', '200', '1300'
                "loadCapacityKn": loadValue
            })
dfBearingLoads = pd.DataFrame(flatLoadData)

# --- GEARS DATA ---
# gear reliability factor (Chap15_Lctr02 Slide 15)
reliabilityPct = np.array([50, 90, 99, 99.9, 99.99, 99.999])
krFactor = np.array([1.000, 0.897, 0.814, 0.753, 0.702, 0.659])

# Geometry Factor Graph (Chap15_Lctr02 Slide 11)
teeth = np.array([12, 15, 17, 20, 24, 30, 35, 40, 45, 50, 60, 80, 125, 275])
matingTeeth = np.array([17, 25, 50, 85, 1000])
J_matrix = np.matrix([
    [0.325, 0.325, 0.325, 0.335, 0.345],  # N=12
    [0.325, 0.332, 0.345, 0.355, 0.365],  # N=15
    [0.330, 0.340, 0.355, 0.365, 0.375],  # N=17
    [0.340, 0.350, 0.365, 0.378, 0.390],  # N=20
    [0.355, 0.365, 0.385, 0.395, 0.410],  # N=24
    [0.375, 0.385, 0.405, 0.420, 0.435],  # N=30
    [0.390, 0.400, 0.422, 0.435, 0.450],  # N=35
    [0.402, 0.415, 0.435, 0.450, 0.465],  # N=40
    [0.413, 0.425, 0.445, 0.460, 0.475],  # N=45
    [0.422, 0.435, 0.455, 0.470, 0.485],  # N=50
    [0.440, 0.450, 0.470, 0.485, 0.500],  # N=60
    [0.465, 0.475, 0.495, 0.510, 0.525],  # N=80
    [0.500, 0.510, 0.530, 0.545, 0.565],  # N=125
    [0.542, 0.555, 0.575, 0.590, 0.605]   # N=275
])

# Teeth Subset Table
N_teethCataloge = np.array([60, 64, 70, 72, 75, 80, 84, 90, 96, 100, 120, 140, 150, 180, 200])