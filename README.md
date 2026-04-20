# Gearbox Design Optimizer: Genetic Algorithm

A Python-based physics engine and genetic algorithm built to autonomously design, simulate, and optimize a double-reduction gear train. The system minimizes total assembly weight while strictly enforcing kinematic targets, spatial boundaries, fatigue limits, and material constraints.

## Project Overview
This project was developed for a Machine Design course. The objective is to transmit 21 HP from an input shaft rotating at 1050 RPM to an output shaft rotating at 216 RPM. Instead of manually iterating through calculations to find a single viable design, this implementation's expanded scope encodes the physical and material parameters into a Genetic Algorithm (GA) that mathematically evolves the absolute lightest possible gearbox that survives all engineering constraints.

### Key Features
* Evolutionary Optimization: Evolves gear teeth combinations, shaft diameters, and physical mounting locations over multiple generations to find the global minimum weight.
* Rigorous Physics Engine: Calculates 3D static beam bending, torsional shear (Von Mises), and resulting equivalent stresses across all shafts.
* AGMA Gear Sizing: Dynamically calculates minimum required gear face widths for infinite fatigue life against tooth bending stress using standard AGMA geometry and velocity factors.
* Automated Bearing Selection: Resolves 3D reaction forces to calculate Required Dynamic Load (C) and automatically selects appropriately sized radial ball bearings from a digitized manufacturer catalog.
* Deflection and Resonance Filters: Calculates continuous deflection functions to verify angular deflection limits at bearings/gears, and checks critical speeds (using Rayleigh's method) to avoid system resonance.

## Engineering Assumptions
To bound the scope of the computational physics engine, the following standard machine design assumptions are integrated into the solver:
* Conservation of Energy: 100% efficiency in power transfer across all gear meshes (friction and thermal losses are neglected).
* Force Resolution: The meshing angles do not dynamically split the radial and tangential forces across complex 3D planes; instead, the resultant loads are felt directly by the shaft.
* Transverse Shear: Transverse shear stress is considered negligible compared to the bending moment stress (Transverse Shear << Bending Moment). This avoids computationally expensive calculus operations over the entire continuous shaft surface.
* Material Finish: The surface finish on all power-transmitting shafts is assumed to be "machined" for the purpose of calculating the Marin surface modification factor.
* Ideal Supports: Bearings are modeled as ideal simple supports (pin/roller) that carry radial loads but exert zero reaction moments on the shaft.

## Architecture
* main.py: The entry point. Initializes the system, triggers the GA, writes the convergence data to a CSV, and prints the final winning design.
* optimizer.py: Houses the Genetic Algorithm. Handles population generation, DNA expression, mutation, crossover, and the penalty filter.
* assembly.py: Contains the GearBox class. Manages the global kinematic relationships, total system mass, and coordinates the components.
* objects.py: Contains the actual physics objects (Shaft, Gear, Bearing). Handles internal load resolution, deflection formulas, factor of safety calculations, and catalog cross-referencing.
* constants.py: Stores all global system givens (Power, Target RPM, Material Properties, AGMA factors, spatial limits).
* tables.py: Contains digitized pandas DataFrames of standard bearing catalogs and AGMA geometry factor matrices.

## Execution and Convergence
Currently, the optimization loop runs for a user-defined, fixed number of generations (e.g., 1000). While this ensures a thorough search of the solution space, it can be easily modified to terminate based on a user-defined improvement metric. 

In a 1000-generation test run (lasting 20 minutes), the algorithm converged on its final, globally optimal solution at generation 184 (approximatly 4 minutes of runtime). The solution was highly optimized, pushing the intermediate shaft deflection to 97% of the absolute angular constraint limit. Because the solution space contains discrete boundaries (e.g., shaft diameters incrementing by 5mm based on the bearing catalog), the algorithm could not bridge the final 3% gap, and subsequent generations could not find a superior mutation that avoided the discrete penalty filters.

### Usage
1. Ensure you have Python installed along with numpy, pandas, and scipy.
2. Clone the repository and run the main script:
   `python main.py`
3. The script will run the genetic algorithm and output `evolution_curve.csv` containing the generational weight data, followed by a highly detailed System Verification Report in the terminal proving the math behind the winning design.

## Future Work
* Dynamic Mutation Rates (Simulated Annealing): Implementing a stagnation tracker. If the elite seed's fitness score does not improve for a set number of generations (e.g., 50 generations), the algorithm will massively scale up the mutation rate. This "thermal shock" will force the population to aggressively jump across discrete solution gaps to escape local minima.
* Intelligent Convergence: Implementing a robust, plateau-aware convergence condition so the optimizer autonomously determines when the global minimum has been found without relying on hardcoded generation counts.
* Removing Intelligent Design: The current GA jump-starts the population by seeding three known, conservative, viable bloodlines. Future iterations will aim to make this designer oversight obsolete, relying entirely on raw random initialization and natural selection.
* Dynamic DNA Structures: Transitioning the DNA array to simultaneously encode system configuration logic alongside physical parameters, allowing the GA to experiment with the number of reduction stages.
* Universal System Solver: Upgrading the hardcoded, class-specific high-level system code into an "any-configuration" smart solver utilizing dynamic pointer logic and graph theory. This would allow the engine to optimize infinitely complex gear trains, planetary systems, and branched power distributions.

## Note on AI Usage
While all core physics equations, logic architecture, and math code were initially written by hand using class resources and standard engineering textbooks, I utilized AI assistance during the development of this project. AI was used strictly for mathematical validation, code correction, and learning extracurricular programming concepts (such as bloodline seeding, elitism, and annealing). Additionally, AI was used to help generate the repetitive boilerplate for print debugging and the final validation reporting, as that work was tedious to format by hand and did not provide additional personal learning value.

## Author
* Elijah Hall
* Course: EGR 3323 - Machine Design (Spring 2026)
