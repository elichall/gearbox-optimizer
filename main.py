from src.assembly import GearBox
from src.constants import SYS_POWER, INPUT_SPEED, OUTPUT_SPEED, LIFE_REQUIRED_IN
from src.optimizer import gearBoxGeneticAlgorithm, gearBoxFitnessScore
import csv
from pathlib import Path
from copy import deepcopy
import time

startTime = time.perf_counter()

sysConfigArray = [[0, 1, [[1,1]]], [1, 2, [[0,0],[2,0]]], [1, 1, [[1,0]]]]

gearBox = GearBox(SYS_POWER, INPUT_SPEED, OUTPUT_SPEED, LIFE_REQUIRED_IN, sysConfigArray)

gearBox.initSystem()

# change the number of evaluated generations
numGens = 100

[dna, bestWeight, weights] = gearBoxGeneticAlgorithm(gearBox, numGens, debug=False)

N_B, N_C, N_D, N_E, LL, LR, d_b, d_c = dna

# Console Output Dashboard
print("\n" + "="*55)
print(" GEARBOX OPTIMIZATION COMPLETE")
print("="*55)
print(f"  Optimal System Weight:     {bestWeight:.2f} N")
print("-" * 55)
print("  [FINAL SYSTEM DNA]")
print(f"    Stage 1 - Gear B (Input):  {int(N_B):>3} teeth")
print(f"    Stage 1 - Gear D (Driven): {int(N_D):>3} teeth")
print(f"    Stage 2 - Gear C (Driver): {int(N_C):>3} teeth")
print(f"    Stage 2 - Gear E (Output): {int(N_E):>3} teeth")
print("-" * 55)
print("  [SPATIAL LAYOUT & GEOMETRY]")
print(f"    Gear C Position (LL):      {LL:>5.3f} in")
print(f"    Gear D Position (LR):      {LR:>5.3f} in")
print(f"    Shaft b Diameter:          {d_b:>5.1f} mm")
print(f"    Shaft c Diameter:          {d_c:>5.1f} mm")
print("="*55 + "\n")

# CSV export
PROJECT_ROOT = Path(__file__).resolve().parent

DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

csv_filename = DOCS_DIR / "evolution_curve.csv"
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Generation', 'Best Weight (N)'])
    for gen, weight in enumerate(weights):
        clean_weight = round(float(weight), 4) 
        writer.writerow([gen, clean_weight])

print(f"Success: Saved evolution curve to {csv_filename}")

endTime = time.perf_counter()
print(endTime - startTime)