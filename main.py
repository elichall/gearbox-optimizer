from assembly import GearBox
from constants import SYS_POWER, INPUT_SPEED, OUTPUT_SPEED, LIFE_REQUIRED_IN
from optimizer import gearBoxGeneticAlgorithm, gearBoxFitnessScore
import csv
from copy import deepcopy

sysConfigArray = [[0, 1, [[1,1]]], [1, 2, [[0,0],[2,0]]], [1, 1, [[1,0]]]]

gearBox = GearBox(SYS_POWER, INPUT_SPEED, OUTPUT_SPEED, LIFE_REQUIRED_IN, sysConfigArray)

gearBox.initSystem()

[[N0, N1, N2, N3, LL, LR, b_diam, c_diam], bestWeight, weights] = gearBoxGeneticAlgorithm(gearBox, debug=False)

# CSV export
csv_filename = "evolution_curve.csv"
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Generation', 'Best Weight (N)'])
    for gen, weight in enumerate(weights):
        clean_weight = round(float(weight), 4) # the weight is a numpy object so cast it into standasrd float
        writer.writerow([gen, clean_weight])

# output the final selected seeds weight and DNA

print("GEARBOX OPTIMIZATION COMPLETE")
print("_"*50)

print(f"OPTIMAL SYSTEM WEIGHT: {bestWeight:.2f} N")
print(f"Convergence data saved to: {csv_filename}")

print("\n--- OPTIMIZED GEAR TEETH ---")
print(f"  First Reduction:  {N0}T driving {N2}T")
print(f"  Second Reduction: {N1}T driving {N3}T")

print("\n--- OPTIMIZED GEOMETRY ---")
print(f"  Mounting Left (LL):  {LL:.4f} m")
print(f"  Mounting Right (LR): {LR:.4f} m")

print("\n--- OPTIMIZED SHAFTS ---")
print(f"  Intermediate Shaft (b): {b_diam} mm")
print(f"  Output Shaft (c):       {c_diam} mm")
print("_"*50 + "\n")

# run the final seed with a verification flag to print out all final intermediate calculated values for report

print("\n" + "="*50)
print("GENERATING FINAL ENGINEERING REPORT DATA")
print("="*50)

testBox = deepcopy(gearBox)
gearBoxFitnessScore(testBox, [N0, N1, N2, N3, LL, LR, b_diam, c_diam], debug=False, verification=True)