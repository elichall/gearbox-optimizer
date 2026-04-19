from math import sqrt, tan, log, pow
from scipy.interpolate import RegularGridInterpolator, make_interp_spline
from constants import *
from tables import *
import numpy as np

# change to allow for initalization with only its ID then add parameters later in iteration

class Bearing:
    reliability = BEARING_RELIABILITY
    Ka = SHOCK_FACTOR
    L = STANDARD_LIFE
    angle = BEARING_ANGLE
    minWidth = MINIMUM_BEARING_WIDTH
    volPackingFactor = PACKING_FACTOR
    density = DENSITY_303A
    
    objectType = "bearing"
    
    # no torque on a frictionless bearing
    gravityForce = np.zeros([3]) # mass of bearing neglected
    # no torque on a frictionless bearing
    torque = np.zeros([3]) # torque applied on shaft
    
    deflection = np.zeros([3])
    
    moment = np.zeros([3])
    
    Lr = STANDARD_LIFE
    
    def __init__(self, id, shaftId):
        # ID
        self.id = id
        self.shaftId = shaftId
        
        # --- Create Space in Memory ---
        # bearing state parameters
        self.bore = None
        self.mass = None
        # forces and moments
        self.force = None # np.array([x, y, z])
        # strength and stress
        self.Kr = None
        self.Fe = None
        
        self.C = None
        
        # deflection
        self.angularDeflection = None # R^3
        
        # type of bearing
        self.basicNumber = None
        self.width = None
        
    def init(self):
        self.Kr = self.reliabilityFactor()
        
    def finalize(self, debug=False):
        self.Fe = self.effectiveForce()
        
        self.C = self.Ka * self.Fe * (self.L / (self.Kr * self.Lr)) ** (3/10)
        
        if debug:
            print(f"\n--- ⚙️ BEARING {self.id} SELECTION ---")
            print(f"  Bore: {self.bore} mm")
            print(f"  Radial Force (Fr): {sqrt(self.force[1]**2 + self.force[2]**2):.2f} N")
            print(f"  Axial Force (Ft): {self.force[0]:.2f} N")
            print(f"  Effective Force (Fe): {self.Fe:.2f} N")
            print(f"  Required Dynamic Load (C): {self.C:.2f} N ({self.C / 1000:.2f} kN)")
        
        self.basicNumber = self.pullBestBearing(debug=debug) # find if there is a bearing which meets specs
        
        if self.basicNumber == 0:
            self.width = 0.010 # dummy values for a failed bearing
            self.mass = 0.10 
            if debug: print(f"  ❌ FAILED: No bearing exists for this load/bore combination.")
        else:
            bearingInfo = dfBearings[dfBearings["basicNumber"] == self.basicNumber].iloc[0]
            
            self.width = bearingInfo["w"] / 1e3 # in m
            od         = bearingInfo["od"] / 1e3 # in m
            id         = self.bore / 1e3
            
            vol = PI / 4 * (od**2 - id**2) * self.width * self.volPackingFactor
            self.mass = self.density * vol
            
            if debug: 
                print(f"  ✅ Selected Bearing: {self.basicNumber}")
                print(f"  Width: {self.width*1000:.1f} mm")
                print(f"  OD: {od*1000:.1f} mm")
                print(f"  ID: {id*1000:.1f} mm")
                print(f"  Vol: {vol*(1e3)**3:.6f} mm^3")
                print(f"  Estimated Mass: {self.mass:.3f} kg")
                
        
    def reliabilityFactor(self):
        b = 1.483 
        kr = (log(1 / (self.reliability / 100)) / log(1 / 0.90)) ** (1 / b)
        return kr
    
    def effectiveForce(self):
        Fr = sqrt(self.force[1]**2 + self.force[2]**2)
        Ft = self.force[0]
        r = Ft/Fr
        if self.angle == 0:
            if r <= 0.35:
                Fe = Fr
            elif 0.35 < r <= 10:
                Fe = Fr * (1 + 1.115 * (Ft/Fr - 0.35))
            else:
                Fe = 1.176 * Ft
        elif self.angle == 25:
            if r <= 0.68:
                Fe = Fr
            elif 0.68 < r <= 10:
                Fe = Fr * (1 + 0.870 * (Ft/Fr - 0.68))
            else:
                Fe = 0.911 * Ft
        return Fe
    
    def pullBestBearing(self, debug=False):
        rank = {"xlt": 1, "lt": 2, "med": 3}
        
        C_kn = self.C / 1000
        
        matches = dfBearingLoads[
            (dfBearingLoads["bore"] == self.bore) & 
            (dfBearingLoads["loadCapacityKn"] >= C_kn)
            ].copy()
        
        if debug:
            catalog_max = dfBearingLoads[dfBearingLoads["bore"] == self.bore]["loadCapacityKn"].max()
            print(f"  Catalog Max Capacity for {self.bore}mm: {catalog_max} kN")
            print(f"  Found {len(matches)} matching bearings in catalog.")
        
        if matches.empty:
            return 0
        
        matches["rank"] = matches["seriesClass"].map(rank)
        sortedMatches = matches.sort_values(by=["rank", "loadCapacityKn"], ascending=[True, True])
        
        best_row = sortedMatches.iloc[0]
        series_num = str(best_row["seriesNumber"])
        
        # get prefix
        if series_num.startswith("L"): prefix = "L"
        elif series_num.startswith("2"): prefix = "2"
        elif series_num.startswith("3"): prefix = "3"
        else: prefix = "2" # safe fallback
        
        # get bore code
        if self.bore == 17:
            bore_code = "03"
        else:
            bore_code = f"{int(self.bore / 5):02d}"
            
        constructed_basic_number = f"{prefix}{bore_code}"
        
        return constructed_basic_number
    
    def printVerificationReport(self):
        print(f"\n  --- ⚙️ BEARING {self.id} (Shaft {self.shaftId}) ---")
        if getattr(self, 'basicNumber', 'DUMMY') == "DUMMY":
            print("      [OUT OF SCOPE - DUMMY BEARING]")
            return
            
        Fr = sqrt(self.force[1]**2 + self.force[2]**2)
        print(f"      Catalog Number:   {self.basicNumber}")
        print(f"      Bore:             {self.bore:.1f} mm")
        print(f"      Width:            {self.width*1000:.1f} mm")
        print(f"      Radial Load (Fr): {Fr:.2f} N")
        print(f"      Dynamic Load (C): {self.C/1000:.2f} kN")
        print(f"      Mass:             {self.mass:.3f} kg")

class Shaft:
    L = SHAFT_LENGTH
    E = SHAFT_MODULUS
    Su = UTS_303A
    Sy = YS_303A
    density = SHAFT_DENSITY
    reliability = SHAFT_RELIABILITY
    
    # Constant Factors
    surfaceFactorInterpolator = make_interp_spline(SuMetric, CsMachined, k=2)
    Cs = surfaceFactorInterpolator(Su / 1e9)
    
    def __init__(self, id): 
        # ID
        self.id = id
        self.objectType = "shaft"
        self.scopeFlag = False
        
        # Containers
        self.mountedObjects = []
        
        # --- Shaft State Parameters ---
        self.diameter = None
        self.torque = None # R^3 np.array
        self.speed = None
        self.life = None
        
        # --- Calculated Values ---
        self.mass = None
        self.weight = None
        self.I = None
        self.J = None
        
        self.deflectionFunctions = [None, None]
        
        self.FOS = float('inf') # make largest possible float to make comparision loop work on first iteration
        
    def init(self):
        self.mass = self.density * (PI * self.diameter**2 * self.L / 4)
        self.weight = np.array([0, - self.mass * G, 0])
        
        self.I = PI * self.diameter**4 / 64
        self.J = PI * self.diameter**4 / 32
        
        self.Sn = self.findShaftStrength()
        
        for object in self.mountedObjects:
            object["component"].init()
            
    def finalize(self, debug=False):
        self.resolveReactionForces()
        
        for object in self.mountedObjects:
            comp = object["component"]
            
            if comp.objectType == "bearing":
                
                if not self.scopeFlag:
                    comp.basicNumber = "DUMMY"
                    comp.width = 0.010 # dummy width for spatial checks
                    if debug: print(f"  ⏭️ SKIPPED: Bearing on Shaft {self.id} is out of scope.")
                    continue
                
                comp.finalize(debug=debug)
            else:
                comp.finalize()
        
    def mountComponent(self, mountedObject, location):
        self.mountedObjects.append({
            "component": mountedObject,
            "location":  location
        }) 
        
    def resolveReactionForces(self):
        sortedMounts = sorted(self.mountedObjects, key=lambda item: item["location"])
        
        sumOfMoments = 0
        sumOfForces = 0
        for item in sortedMounts[1:-1]:
            r_vec = np.array([item["location"], 0, 0])
            force_vec = item["component"].force
            
            sumOfMoments += np.cross(r_vec, force_vec)
            sumOfForces += force_vec
        
        forceAtL = np.array([0, -sumOfMoments[2], sumOfMoments[1]]) / self.L # undo the cross product to solve for Reaction forces 
        forceAt0 = - sumOfForces - forceAtL
        
        sortedMounts[0]["component"].force = forceAt0 + self.weight / 2
        sortedMounts[-1]["component"].force = forceAtL + self.weight / 2
    
    def findShaftDeflection(self):
        if not self.scopeFlag:
            zero_vector = np.zeros(3)
            for object in self.mountedObjects:
                comp = object["component"]
                comp.deflection = zero_vector
                comp.angularDeflection = zero_vector
            
            # Return dummy functions that evaluate to 0 to prevent crashes
            return [lambda x: zero_vector, lambda x: zero_vector]
        
        individualDeflections = []
        individualAngularDeflections =[]
        
        for item in self.mountedObjects:
            a = item["location"]
            if a != 0 and a!= self.L:
                comp = item["component"]
                P = comp.force # R^3 vector but no expected x deflection
                b = self.L - a
    
                indvDeflectionFunct = lambda x, P=P, a=a, b=b: ( # must lock the values of P, a, and b or they change per eval
                    P * b * x * (self.L**2 - x**2 - b**2) if x < a 
                    else P * a * (self.L-x) * (self.L**2 - (self.L-x)**2 - a**2)
                )
                indvAngularDeflectionFunct = lambda x, P=P, a=a, b=b: ( # derivitive of deflection
                    P * b * (self.L**2 - b**2 - 3 * x**2) if x < a 
                    else -P * a * (self.L**2 - a**2 - 3 * (self.L - x)**2)
                )
                
                individualDeflections.append(indvDeflectionFunct)
                individualAngularDeflections.append(indvAngularDeflectionFunct)
                
        shaftWeightDeflection = lambda x, W=self.weight: (
            (W * x / 4) * (self.L**3 - 2 * self.L * x**2 + x**3)
        )
        shaftWeightAngularDeflection = lambda x, W=self.weight: (
            (W / 4) * (self.L**3 - 6 * self.L * x**2 + 4 * x**3)
        )
        
        individualDeflections.append(shaftWeightDeflection)
        individualAngularDeflections.append(shaftWeightAngularDeflection)
            
        deflectionFunct = lambda x: sum(f(x) for f in individualDeflections) / (6 * self.L * self.E * self.I)
        angularDeflectionFunct = lambda x: sum(f(x) for f in individualAngularDeflections) / (6 * self.L * self.E * self.I)
        
        # assign deflections for calculation
        for object in self.mountedObjects:
            comp = object["component"]
            loc = object["location"]

            comp.deflection = deflectionFunct(loc)
            comp.angularDeflection = angularDeflectionFunct(loc)
            
        return [deflectionFunct, angularDeflectionFunct]
    
    def findInternalLoads(self):
        sortedMounts = sorted(self.mountedObjects, key=lambda item: item["location"])
        
        internalLoads = []
        
        # all R^3 cartesian vectors
        runningShear = np.zeros(3) 
        runningMoment = np.zeros(3) # no need to tally torque as x comp of moment is torque

        previousX = 0
        
        distributedWeight = self.weight / self.L
        
        for item in sortedMounts:
            currentX = item["location"]
            comp = item["component"]
            
            deltax = currentX - previousX
            r_vec = np.array([deltax, 0, 0])
            
            # accounts for y and z moment interactions (bending stress) 
            # happens for both LHS and LHS of extrema
            runningMoment += np.cross(r_vec, runningShear) + np.cross(r_vec / 2, distributedWeight * deltax)
            
            internalLoads.append({
                "location": currentX,
                "side": "left",
                "shear": runningShear.copy(),
                "moment": runningMoment.copy()
            })
            
            # adds the shear and remaining x moment interaction (torque)
            # these are not felt by LHS of extrema but only by RHS
            runningShear += comp.force 
            runningMoment += comp.moment
            
            internalLoads.append({
                "location": currentX,
                "side": "right",
                "shear": runningShear.copy(),
                "moment": runningMoment.copy()
            })
            
            previousX = currentX
            
        return internalLoads
        
    def findShaftStress(self):
        
        if not self.scopeFlag:
            self.FOS = float('inf')
            return
        
        internalLoads = self.findInternalLoads()  
        # ignoring relatively small transverse shear as iterating through 360 degrees to find a maximum or solving the continuous defrivatives would be too taxing for the GA
        
        for extrema in internalLoads:
            # shearVec = extrema["shear"]
            momentVec = extrema["moment"]
            
            bendingMomentMag = sqrt( momentVec[1]**2 + momentVec[2]**2 )
            
            maxBendingStress = bendingMomentMag * self.diameter / self.I / 2
            
            torque = momentVec[0]
            
            torsionalShear = torque * self.diameter / self.J / 2
            
            # Von Mises Stress
            meanStress = sqrt(3*torsionalShear**2)
            alternatingStress = maxBendingStress
            
            total_stress = meanStress + alternatingStress
            if total_stress <= 1e-9: # catch stress being 0 or close to it causing div by zero error
                fatigueFOS = float('inf')
                yieldFOS = float('inf')
            else:
                fatigueFOS = ( alternatingStress / self.Sn + meanStress / self.Su )**(-1)
                yieldFOS = self.Sy / total_stress
            
            self.FOS = min([self.FOS, fatigueFOS, yieldFOS])
            
    def findShaftStrength(self):
        d = self.diameter * 39.3701 # in inches
        # Fatigue Factors (Chap08_Lctr01 Slide 21)
        
        # Gradient Factor
        if d < 0.4:
            Cg = 1
        else:
            Cg = 0.9
        
        Cr = 0.868 # hard code for 95% reliability
        
        Sn_prime = 0.5 * self.Su
        
        Sn = Sn_prime * self.Cs * Cg * Cr
        return Sn
    
    def resonanceCheck(self):
        if not self.scopeFlag:
            return True
        
        deltaFunct = self.deflectionFunctions[0]
        
        deltaShaft = abs(deltaFunct(self.L / 2)[1]) # only care about component of deflection in gravity's direction (turn into dot prod with vector for scaled up version)
        scalarShaftWeight = self.mass * G
        innerNumSum = scalarShaftWeight * deltaShaft # assumed point mass for shaft weight (conservative)
        innerDenSum = scalarShaftWeight * deltaShaft**2
        for object in self.mountedObjects:
            comp = object["component"]    
            if comp.objectType == "gear":
                loc = object["location"]              
                
                deltaComp = abs(deltaFunct(loc)[1])
                scalarCompWeight = comp.mass * G
                innerNumSum += scalarCompWeight * deltaComp
                innerDenSum += scalarCompWeight * deltaComp**2
        
        criticalSpeed = sqrt(G * innerNumSum / innerDenSum) # rad/s
        if criticalSpeed < 2 * np.linalg.norm(self.speed): # both in rad/s
            return False
        else:
            return True
    
    def initalValidMountCheck(self, debug=False):
        sortedMounts = sorted(self.mountedObjects, key=lambda item: item["location"])
        componentEdges = [] 
        
        if debug:
            print(f"\n--- 📏 SHAFT {self.id} INITIAL SPACING CHECK ---")
            print(f"Shaft Length: {self.L:.4f} m | Required Clearance: {COMPONENT_SPACING_LIMIT:.4f} m")
        
        i=0
        for item in sortedMounts:
            x = item["location"]
            comp = item["component"]
            
            # use minWidth for bearings in the initial check
            if comp.objectType == "bearing":
                width = comp.minWidth
            else:
                width = comp.width
            
            edgeLeft = x - width / 2
            edgeRight = x + width / 2
            componentEdges.append([edgeLeft, edgeRight])
            
            if debug:
                print(f"  [{i}] {comp.objectType.upper()}: Center={x:.4f} m | Width={width:.4f} m")
                print(f"      Edges: [{edgeLeft:.4f} m to {edgeRight:.4f} m]")
            
            if (i!=0):
                clearance = componentEdges[i][0] - componentEdges[i-1][1]
                if debug:
                    print(f"      Clearance to prev: {clearance:.4f} m")
                    
                if clearance < COMPONENT_SPACING_LIMIT:
                    if debug: 
                        print(f"      ❌ COLLISION! Needs {COMPONENT_SPACING_LIMIT:.4f} m, only has {clearance:.4f} m")
                    return False
            i+=1
        
        if debug: print(f"✅ Shaft {self.id} Initial Spacing Passed!")
        return True 
        
    def finalValidMountCheck(self, debug=False):
        sortedMounts = sorted(self.mountedObjects, key=lambda item: item["location"])
        componentEdges = [] 
        
        if debug:
            print(f"\n--- 📏 SHAFT {self.id} FINAL SPACING CHECK ---")
        
        i=0
        for item in sortedMounts:
            x = item["location"]
            comp = item["component"]
            width = comp.width
            
            # only fail if the bearing is IN-SCOPE and missing from the catalog
            if comp.objectType == "bearing":
                if not self.scopeFlag:
                    pass # Ignore catalog failures for the dummy bearings on out-of-scope shafts
                elif comp.basicNumber == 0:
                    if debug: 
                        print(f"      ❌ BEARING FAILED! No bearing in catalog with Bore={self.diameter}mm and C>={comp.C/1000:.2f}kN")
                    return False
            
            # enforce physical space for ALL components, including dummy bearings
            edgeLeft = x - width / 2
            edgeRight = x + width / 2
            componentEdges.append([edgeLeft, edgeRight])
            
            if debug:
                print(f"  [{i}] {comp.objectType.upper()}: Center={x:.4f} m | Width={width:.4f} m")
                print(f"      Edges: [{edgeLeft:.4f} m to {edgeRight:.4f} m]")

            if (i!=0):
                clearance = componentEdges[i][0] - componentEdges[i-1][1]
                if debug:
                    print(f"      Clearance to prev: {clearance:.4f} m")

                if clearance < COMPONENT_SPACING_LIMIT:
                    if debug: 
                        print(f"      ❌ COLLISION! Needs {COMPONENT_SPACING_LIMIT:.4f} m, only has {clearance:.4f} m")
                    return False
            i+=1
            
        if debug: print(f"✅ Shaft {self.id} Final Spacing Passed!")
        return True
          
    def printVerificationReport(self):
        print(f"\n  --- SHAFT {self.id} ---")
        if not self.scopeFlag:
            print("      [OUT OF SCOPE - ASSUMED RIGID]")
            return

        print(f"      Diameter:         {self.diameter * 1000:.1f} mm")
        print(f"      Length:           {self.L:.4f} m")
        print(f"      Operating Speed:  {np.linalg.norm(self.speed):.2f} rad/s")
        print(f"      Torque:           {np.linalg.norm(self.torque):.2f} Nm")
        print(f"      Mass:             {self.mass:.3f} kg")

        # Recalculate max stresses for reporting
        internalLoads = self.findInternalLoads()
        max_bend, max_torq = 0, 0
        min_fatigue_fos, min_yield_fos = float('inf'), float('inf')

        for extrema in internalLoads:
            momentVec = extrema["moment"]
            bendingMomentMag = sqrt( momentVec[1]**2 + momentVec[2]**2 )
            maxBendingStress = bendingMomentMag * self.diameter / self.I / 2
            
            torque = momentVec[0]
            torsionalShear = torque * self.diameter / self.J / 2

            meanStress = sqrt(3*torsionalShear**2)
            alternatingStress = maxBendingStress

            max_bend = max(max_bend, bendingMomentMag)
            max_torq = max(max_torq, abs(torque))

            fatigue_fraction = (alternatingStress / self.Sn) + (meanStress / self.Su)
            if fatigue_fraction > 1e-12:
                min_fatigue_fos = min(min_fatigue_fos, fatigue_fraction**(-1))

            total_stress = meanStress + alternatingStress
            if total_stress > 1e-12:
                min_yield_fos = min(min_yield_fos, self.Sy / total_stress)

        print(f"      Max Bending Mom:  {max_bend:.2f} Nm")
        print(f"      Max Torque:       {max_torq:.2f} Nm")
        print(f"      Fatigue FOS:      {min_fatigue_fos:.3f}")
        print(f"      Yield FOS:        {min_yield_fos:.3f}")
        print(f"      Overall Min FOS:  {self.FOS:.3f}")

        # Recalculate Resonance for reporting
        deltaFunct = self.deflectionFunctions[0]
        deltaShaft = abs(deltaFunct(self.L / 2)[1])
        scalarShaftWeight = self.mass * G
        innerNumSum = scalarShaftWeight * deltaShaft
        innerDenSum = scalarShaftWeight * deltaShaft**2
        for object in self.mountedObjects:
            comp = object["component"]
            if comp.objectType == "gear":
                loc = object["location"]
                deltaComp = abs(deltaFunct(loc)[1])
                scalarCompWeight = comp.mass * G
                innerNumSum += scalarCompWeight * deltaComp
                innerDenSum += scalarCompWeight * deltaComp**2

        criticalSpeed = sqrt(G * innerNumSum / innerDenSum)
        print(f"      Critical Speed:   {criticalSpeed:.2f} rad/s")

        # Bearing Deflections
        for object in self.mountedObjects:
            comp = object["component"]
            if comp.objectType == "bearing":
                ang_deg = np.linalg.norm(comp.angularDeflection) * 180 / PI
                print(f"      Bearing {comp.id} Ang Deflection: {ang_deg:.4f}° (Limit: {BEARING_ANGULAR_DEFLECTION_LIMIT * 180 / PI:.2f}°)")
    
class Gear:
    # givens
    pitch = PITCH 
    pressureAngle = PRESURE_ANGLE * (PI / 180) # given
    Ko = OVERLOAD_CORRECTION_FACTOR
    Su = UTS_303A
    Sn_prime = 0.5 * Su
    Cl = LOADING_FACTOR 
    kt = TEMPERATURE_FACTOR 
    kms = LOADING_PATTERN_FACTOR 
    reliability = GEAR_RELIABILITY
    
    density = DENSITY_303A

    # table interpolators
    jInterpolator = RegularGridInterpolator((teeth, matingTeeth), J_matrix, bounds_error=False, fill_value=None)
    surfaceFactorInterpolator = make_interp_spline(SuMetric, CsMachined, k=2)
    reliabilityFactorInterpolator = make_interp_spline(reliabilityPct, krFactor, k=1)
    
    def __init__(self, id, idMeshing, shaftId):
        # ID
        self.objectType = "gear"
        self.id = id
        self.meshingId = idMeshing
        self.shaftId = shaftId
        
        self.Cs = self.surfaceFactorInterpolator(self.Su / 1e9)
        self.kr = self.reliabilityFactorInterpolator(self.reliability)
        self.Cg = self.gradientFactor()
        
        # create space in memory
        # --- Gear State Parameters ---
        self.N = None
        self.N_mating = None
        
        self.d = None
        self.speed = None
        self.torque = None
        self.mass = None
        self.life = None

        # tangential force
        self.Ft = None
        
        # Strength and Stress
        self.Kv = None
        self.J = None
        
        self.Sn = None
        self.width = None 
        
        # net vectors
        self.gravityForce = None
        self.force = None
        self.moment = None
        
        # deflections
        self.deflection = None
        self.angularDeflection = None
        
    def init(self):
        self.d = self.N / self.pitch / 39.3701
        self.J = self.jInterpolator(np.array([self.N, self.N_mating]))[0]
        
        self.Ft = 2 * np.linalg.norm(self.torque) / self.d
        self.Kv = self.velocityFactor()
        
        # strength needed to balancing stress equation for width
        self.Sn = self.findGearStrength()
        
        # required width for each gear needed to validate spacial constaints
        self.width = self.findGearWidth()
        
        # find the mass (approximate) and gravity force
        self.mass = self.density * self.width * PI / 4 * self.d**2
        self.gravityForce = np.array([0, -self.mass * G, 0])
        
        # set the force and moment it reflects back at the shaft for deflections and shaft stress
        self.force = self.Ft * np.array([0, tan(self.pressureAngle), 1]) + self.gravityForce
        self.moment = self.torque
        
    def finalize(self, debug=False):
        None
    
    def findGearStrength(self):
        if self.life < 1e3:
            Sn_temp = 0.9 * self.Su
        elif self.life < 1e6: 
            expr = log(0.9 * self.Su) + ( log(self.life) - log(1e3) ) * ( log(self.Sn_prime) - log(0.9 * self.Su) ) / ( log(1e6) - log(1e3) )
            Sn = pow(10, expr)
        else:
            Sn_temp = self.Sn_prime
        
        Sn = Sn_temp * self.Cl * self.Cg * self.Cs * self.kr * self.kms * self.kt
        return Sn
        
    def findGearWidth(self):
        b = 0 # width in inches
        b_old = 10 # establish first look inequality
        
        currentMountingFactor = self.mountingFactor(b)
        
        while currentMountingFactor != self.mountingFactor(b_old):
            b_old = b
            
            Ft_lbf = self.Ft * 0.224809
            Sn_psi = self.Sn * 0.000145038
            
            b = Ft_lbf * self.pitch / self.J / Sn_psi * self.Kv * self.Ko * currentMountingFactor
            currentMountingFactor = self.mountingFactor(b)
        
        return b / 39.3701
    
    # stress functions
    def velocityFactor(self):
        rpm = np.linalg.norm(self.speed) * 30 / PI
        v = PI * rpm * self.d * 39.3701 / 12
        Kv = (50 + sqrt(v))/50
        return Kv
    
    def mountingFactor(self, b_inches):
        if 0 <= b_inches < 2:
            Km = 1.3
        elif 2 <= b_inches < 6: 
            Km = 1.4 
        elif 6 <= b_inches <= 9:
            Km = 1.5
        else:
            Km = 1.8
        return Km
    
    # strength functions
    def gradientFactor(self):
        if self.pitch <= 5:
            Cg = 0.85
        else:
            Cg = 1
        return Cg
    
    def printVerificationReport(self):
        print(f"\n  --- ⚙️ GEAR {self.id} (Meshes with Gear {self.meshingId}) ---")
        print(f"      Teeth (N):        {self.N}")
        print(f"      Pitch Diam (d):   {self.d * 39.3701:.2f} in ({self.d * 1000:.1f} mm)")
        print(f"      Face Width (b):   {self.width * 39.3701:.3f} in ({self.width * 1000:.1f} mm)")
        print(f"      Tangential (Ft):  {self.Ft:.2f} N")
        print(f"      Geometry (J):     {self.J:.3f}")
        print(f"      Velocity (Kv):    {self.Kv:.3f}")
        print(f"      Strength (Sn):    {self.Sn / 1e6:.2f} MPa")
        print(f"      Mass:             {self.mass:.3f} kg")