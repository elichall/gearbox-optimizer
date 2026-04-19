from assembly import GearBox
from copy import deepcopy
import numpy as np
from tables import N_teethCataloge, diametersCatalog
from constants import *

MUTATION_CHANCE = 0.03 
POPULATION_SIZE = 100 
CULL_PERCENT = 0.5 
TOTAL_GENERATIONS = 20

safe_LL = SHAFT_LENGTH * 0.33
safe_LR = SHAFT_LENGTH * 0.33
thickest_shaft = diametersCatalog[-1]


rng = np.random.default_rng()

def gearBoxGeneticAlgorithm(gearBox, debug=False):
    
    if debug:
        print("\n--- RUNNING KNOWN PASSING SEED TO DEBUG CODE  ---")
        testBox = deepcopy(gearBox)
        
        # done by hand math to find a working seed
        seedDNA = [60, 72, 140, 150, 0.0754, 0.0754, 50, 40] 
        
        gearBoxFitnessScore(testBox, seedDNA, debug=True)
        print("--- DIAGNOSTIC COMPLETE ---\n")
        import sys; sys.exit()

    population = []
    bestScoresPerPop = []
    
    # create intial population
    for i in range(POPULATION_SIZE):
        indvGearBox = deepcopy(gearBox)
        
        indvDNA = generateRandomDNA()
        
        # seed bloodlines that pass gear train check (intelligent designer)
        if i == 0:
            # Bloodline A
            indvDNA = [72, 72, 140, 180, safe_LL, safe_LR, thickest_shaft, thickest_shaft]
        elif i == 1:
            # Bloodline B
            indvDNA = [60, 72, 140, 150, safe_LL, safe_LR, thickest_shaft, thickest_shaft]
        elif i == 2:
            # Bloodline C
            indvDNA = [64, 90, 140, 200, safe_LL, safe_LR, thickest_shaft, thickest_shaft]
        
        indv = {
            "gearbox": indvGearBox,
            "dna":     indvDNA,
            "score":   None
            }
        
        population.append(indv)
        
    # while loop ideally with a last gen to new gen score change condition
    for i in range(TOTAL_GENERATIONS):
        # Express Genes and score response
        for indv in population:
            indvGearBox = indv["gearbox"]
            indvDNA =     indv["dna"]
            
            fitnessScore = gearBoxFitnessScore(indvGearBox, indvDNA, debug=False)
            
            indv["score"] = fitnessScore
            
        # Sort for score and cull for dead members
        population.sort(key=lambda indv: indv["score"])    
        survivors = [indv for indv in population if indv['score'] < 999999]
        
        # fallback just in case of total extinction
        if len(survivors) > 0:
            oldGen = survivors
        else:
            oldGen = population[0 : int(POPULATION_SIZE * 0.1)]
        
        # store best of generations weight
        bestScoresPerPop.append(population[0]["score"])
        
        # Populate new generation with DNA of the survivors
        newGenDNA = generateDNA(oldGen, POPULATION_SIZE)
        i=0
        for indv in population:
            indv["gearbox"].wipeState()
            indv["dna"] = newGenDNA[i]
            indv["score"] = None
            i += 1

    # express DNA of the last generation
    for indv in population:
        indvGearBox = indv["gearbox"]
        indvDNA =     indv["dna"]
        
        fitnessScore = gearBoxFitnessScore(indvGearBox, indvDNA, debug=debug)
        
        indv["score"] = fitnessScore
    
    # sort for best
    population.sort(key=lambda indv: indv["score"])
    finalWeight = population[0]["score"]
    bestScoresPerPop.append(finalWeight)
    supremeDNA = population[0]["dna"]
    return [supremeDNA, finalWeight, bestScoresPerPop]

def generateRandomDNA():
    N0 = np.random.choice(N_teethCataloge)
    N1 = np.random.choice(N_teethCataloge)
    N2 = np.random.choice(N_teethCataloge)
    N3 = np.random.choice(N_teethCataloge)
    
    LL = ( rng.random() * (SHAFT_LENGTH - 2 * COMPONENT_SPACING_LIMIT) + COMPONENT_SPACING_LIMIT)
    LR = ( rng.random() * (SHAFT_LENGTH - 2 * COMPONENT_SPACING_LIMIT) + COMPONENT_SPACING_LIMIT)
    
    b_diam = np.random.choice(diametersCatalog)
    c_diam = np.random.choice(diametersCatalog)
    
    return [N0, N1, N2, N3, LL, LR, b_diam, c_diam]

def generateDNA(oldGen, size):
    newGenDNA = []
    
    # protect the best Genes so you never go backwards
    bestDNA = oldGen[0]["dna"]
    newGenDNA.append(bestDNA)
    
    # inheritance from parents to children
    while len(newGenDNA) < size:
        idxA = rng.integers(0, len(oldGen))
        idxB = rng.integers(0, len(oldGen))
        
        parentA = oldGen[idxA]["dna"]
        parentB = oldGen[idxB]["dna"]
        
        childDNA = []
        
        for i in range(8):
            if rng.random() > 0.5:
                childDNA.append(parentA[i])
            else:
                childDNA.append(parentB[i])
                
        # mutation chance for each gene is MUTATION_CHANCE
        for i in range(4):
            if rng.random() < MUTATION_CHANCE:
                childDNA[i] = np.random.choice(N_teethCataloge)
                
        for i in range(4, 6):
            if rng.random() < MUTATION_CHANCE:
                childDNA[i] = (rng.random() * (SHAFT_LENGTH - 2 * COMPONENT_SPACING_LIMIT) + COMPONENT_SPACING_LIMIT)
                
        for i in range(6, 8):
            if rng.random() < MUTATION_CHANCE:
                childDNA[i] = np.random.choice(diametersCatalog)
        
        newGenDNA.append(childDNA)
    
    return newGenDNA

def gearBoxFitnessScore(gearBox, DNA_array, debug=False, verification=False):
    gearBox.expressDNA(DNA_array)

    if gearBox.setupFilter(debug=debug) != True:
        if debug: print("DEBUG: ❌ Failed setupFilter() (Kinematics didn't match 216 RPM, or Gears Overlapped)")
        return 999999

    for shaft in gearBox.shaftContainer:
        shaft.finalize(debug=debug)
        if shaft.finalValidMountCheck() == False:
            if debug: print(f"DEBUG: ❌ Failed finalValidMountCheck() on Shaft {shaft.id}")
            return 999999
        
        shaft.findShaftStress()
        
        if shaft.FOS < 1: 
            if debug: print(f"DEBUG: ❌ Failed Factor of Safety on Shaft {shaft.id}. FOS = {shaft.FOS}")
            return 999999
        
        shaft.deflectionFunctions = shaft.findShaftDeflection()
        
        resonance = shaft.resonanceCheck()
        if resonance == False: # Or whatever your specific penalty check is here
            if debug: print(f"DEBUG: ❌ Failed Resonance Check on Shaft {shaft.id}. Value: {resonance}")
            return 999999

    if gearBox.deflectionCheck() == False: 
        if debug: print("DEBUG: ❌ Failed Global Deflection Check (Bearings angled > 0.04 deg, or Gear separation > limit)")
        return 999999
        
    weight = gearBox.findSystemWeight()
    if debug: print(f"DEBUG: ✅ SEED SURVIVED! Weight: {weight}")
    
    if verification: gearBox.printVerificationReport() # only for the final selected DNA
    
    return weight