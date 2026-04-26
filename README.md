# Gearbox Design Optimizer: Genetic Algorithm

A Python-based physics engine and genetic algorithm built to autonomously design, simulate, and optimize a double-reduction gear train. The system minimizes total assembly weight while strictly enforcing kinematic targets, spatial boundaries, fatigue limits, and material constraints.

## Project Overview
This project was developed for a Machine Design course. The objective is to transmit power from an input shaft rotating at 1050 RPM to an output shaft rotating at 216 RPM. Instead of manually iterating through calculations to find a single viable design, this implementation's expanded scope encodes the physical and material parameters into a Genetic Algorithm (GA) that mathematically evolves the absolute lightest possible gearbox that survives all engineering constraints.

### Key Features
* **Evolutionary Optimization:** Evolves gear teeth combinations, shaft diameters, and physical mounting locations over multiple generations to find the global minimum weight.
* **Robust Genetic Operators:** * **Dynamic Penalty Fitness:** Uses a weighted fitness function that heavily penalizes constraint violations (like deflection or fatigue failure) while rewarding mass reduction, smoothly guiding the population toward viable spaces.
  * **Elitism & Bloodlines:** Preserves the highest-performing "elite" configurations across generations to prevent regression, while utilizing selective crossover to blend successful traits.
  * **Adaptive Mutation:** Incorporates a stagnation tracker that temporarily spikes the mutation rate when fitness plateaus. This prevents premature convergence and helps the population navigate discrete catalog boundaries (like bearing bore increments).
* **Rigorous Physics Engine:** Calculates 3D static beam bending, torsional shear (Von Mises), and resulting equivalent stresses across all shafts using exact continuous singularity (Macaulay) functions.
* **AGMA Gear Sizing:** Dynamically calculates minimum required gear face widths for infinite fatigue life against tooth bending stress using standard AGMA geometry and velocity factors.
* **Automated Bearing Selection:** Resolves 3D reaction forces to calculate Required Dynamic Load (C) and automatically selects appropriately sized radial ball bearings from a digitized manufacturer catalog.
* **Deflection and Resonance Filters:** Calculates continuous deflection functions to verify angular deflection limits at bearings/gears, and checks critical speeds (using Rayleigh's method) to avoid system resonance.

## Engineering Assumptions
To bound the scope of the computational physics engine, the following standard machine design assumptions are integrated into the solver:
* **Conservation of Energy:** 100% efficiency in power transfer across all gear meshes (friction and thermal losses are neglected).
* **Force Resolution:** The meshing angles do not dynamically split the radial and tangential forces across complex 3D planes; instead, the resultant loads are felt directly by the shaft.
* **Transverse Shear:** Transverse shear stress is considered negligible compared to the bending moment stress (Transverse Shear << Bending Moment). This avoids computationally expensive calculus operations over the entire continuous shaft surface.
* **Material Finish:** The surface finish on all power-transmitting shafts is assumed to be "machined" for the purpose of calculating the Marin surface modification factor.
* **Ideal Supports:** Bearings are modeled as ideal simple supports (pin/roller) that carry radial loads but exert zero reaction moments on the shaft.

## Architecture
* `main.py`: The entry point. Initializes the system, triggers the GA, writes the convergence data to a CSV, and prints the final winning design.
* `optimizer.py`: Houses the Genetic Algorithm. Handles population generation, DNA expression, mutation, crossover, adaptive mutation logic, and the penalty filter.
* `assembly.py`: Contains the `GearBox` class. Manages the global kinematic relationships, total system mass, and coordinates the components.
* `objects.py`: Contains the actual physics objects (`Shaft`, `Gear`, `Bearing`). Handles internal load resolution, deflection formulas, factor of safety calculations, and catalog cross-referencing.
* `constants.py`: Stores all global system givens (Power, Target RPM, Material Properties, AGMA factors, spatial limits).
* `tables.py` (or `data/` directory): Contains digitized pandas DataFrames of standard bearing catalogs and AGMA geometry factor matrices.

## Execution and Convergence
Currently, the optimization loop runs for a user-defined, fixed number of generations (e.g., 1000). Thanks to a balanced combination of elitism, crossover, and adaptive mutation, the engine efficiently navigates discrete boundary conditions to ensure the true global minimum is found.

In recent test runs (completing in roughly 7 to 9.5 minutes), the algorithm consistently converged on a globally optimal system weight of **423.85 N (43.21 kg)**. The program converged on its final design at the 155th iteration. Despite boosted mutation rates, it could never escape this final value.

**The Limiting Constraint:**
While the AGMA gear widths were perfectly optimized to a Factor of Safety of 1.0, the absolute bottleneck of the entire system proved to be the **angular misalignment at Bearing C** (the left bearing on the intermediate shaft). The algorithm drove this value to **0.0391°**, sitting right on the edge of the **0.040°** hard physical constraint. The remaining difference could not be made up as much of the system's parameters relied on discreet catalouge sizes.

To achieve this minimum weight, the optimizer purposefully selected a thin 40mm shaft to save mass. To prevent this thin shaft from bending past the 0.040° bearing limit under load, the algorithm intelligently pushed the heaviest radial and tangential loads (Gear D) as close to the bearing support as physically possible, minimizing the peak internal bending moment. If the shaft were any thinner, or the heavy gear positioned any closer to the center span, the angular deflection would have failed the system.

### Usage
1. Ensure you have Python installed along with `numpy`, `pandas`, `matplotlib`, and `scipy`.
2. Clone the repository and activate your virtual environment.
3. Run the main script:

       python main.py

4. The script will run the genetic algorithm, output `evolution_curve.csv` containing the generational weight data, and display a highly detailed System Verification Report in the terminal proving the statics and fatigue math behind the winning design.

## Future Work
* **Intelligent Convergence:** Implementing a robust, plateau-aware convergence condition so the optimizer autonomously determines when the global minimum has been found without relying on hardcoded generation counts.
* **Removing Intelligent Design:** The current GA jump-starts the population by seeding known, conservative, viable bloodlines. Future iterations will aim to make this designer oversight obsolete, relying entirely on raw random initialization and natural selection.
* **Dynamic DNA Structures:** Transitioning the DNA array to simultaneously encode system configuration logic alongside physical parameters, allowing the GA to experiment with the number of reduction stages (e.g., evolving a triple-reduction vs. double-reduction box).
* **Universal System Solver:** Upgrading the hardcoded, class-specific high-level system code into an "any-configuration" smart solver utilizing dynamic pointer logic and graph theory. This would allow the engine to optimize infinitely complex gear trains, planetary systems, and branched power distributions.

## Note on AI Usage
While all core physics equations, logic architecture, and math code were initially written by hand using class resources and standard engineering textbooks, I utilized AI assistance during the development of this project. AI was used strictly for mathematical validation (e.g., building an independent forward-solving script to verify optimizer outputs against continuous beam functions), code syntax correction, and learning extracurricular algorithmic concepts (such as bloodline seeding, elitism, and simulated annealing). Additionally, AI was used to help generate the repetitive boilerplate for print debugging and automated formatting for the final validation reports, allowing me to focus entirely on the core mechanical physics and computational logic.

## Author
* **Elijah Hall**
* Course: EGR 3323 - Machine Design (Spring 2026)