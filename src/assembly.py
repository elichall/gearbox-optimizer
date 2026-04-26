from src.objects import Shaft, Gear, Bearing
from src.constants import *
import numpy as np
from math import sqrt

class GearBox:
    shaftContainer = []
    gearContainer = []
    bearingContainer = []

    systemIndex = [] # may not need
    
    def __init__(self, power, inputSpeed, outputSpeed, lifeIn, systemConfig):
        self.shaftContainer = []
        self.gearContainer = []
        self.bearingContainer = []
        
        # system specifications
        self.power = power # scaler net power input (input in W) 
        self.inputSpeed = np.array([inputSpeed * 1/60 * 2*PI, 0, 0]) #R^3 np.array(rpm to rad/s)
        self.inputShaftLife = lifeIn # revs
        
        self.outputSpeed = np.array([outputSpeed * 1/60 * 2*PI, 0, 0]) # R^3 np.array (rpm to rad/s)
        
        # calculated values
        scalarTorque = self.power / self.inputSpeed[0] 
        self.inputTorque = np.array([scalarTorque, 0, 0])
        
        # nested list, length of list is number of shafts
        # index 0 of internal list is flag for if the shaft is in design scope (if its stresses matter)
        # index 1 is logic for if the shaft is input/output or intermediate (1 gear or 2 for this project scope)
        # index 2 is the input output logic which tells the shaft which gears are meshing with which other external gears on other shafts [shaft id, gear id on that shaft]
        # for this project systemConfig = [[0, 1, [[1,1]]],[1, 2, [[0,0],[2,0]]],[1, 1, [[1,0]]]
        self.systemArray = systemConfig 
        
    def initSystem(self):
        runningShaftId = 0
        runningBearingId = 0
        runningGearId = 0
              
        for shaftConfig in self.systemArray:
            shaft = Shaft(runningShaftId)
            
            shaft.scopeFlag = bool(shaftConfig[0]) # is the shaft being considered for optimization
            
            # bearing generation
            bearingIndex = runningBearingId 
            for j in range(0,2):
                bearing = Bearing(bearingIndex + j, runningShaftId) # create bearing object
                
                self.bearingContainer.append(bearing) # store it
                shaft.mountComponent(self.bearingContainer[bearingIndex + j], shaft.L * j) # mount bearings
                
                runningBearingId += 1
            
            # gear generation
            gearIndex = runningGearId
            for j in range(0,shaftConfig[1]): # how many gears
                
                # need a hash function for the system to find the global index values given the local shaft config
                meshingIndex = 0 
                meshingGearShaftIndex, localMeshingGearIndex = shaftConfig[2][j] 
                for k in range(0,meshingGearShaftIndex): # 0 until the shaft index of the meshing gear
                    meshingIndex += self.systemArray[k][1]  
                meshingIndex += localMeshingGearIndex
                    
                gear = Gear(gearIndex + j, meshingIndex, runningShaftId) # create gear object, tell it the id of the meshing gear
                
                self.gearContainer.append(gear) # store it
                shaft.mountComponent(self.gearContainer[gearIndex + j], None)
                runningGearId += 1
            
            self.shaftContainer.append(shaft)
            runningShaftId += 1
    
    def expressDNA(self, DNA):
        # Unpack DNA 
        N0, N1, N2, N3, LL, LR, b_diam, c_diam = DNA
        
        dummy_diameter = 1 # mm
        diameterMap = {0:dummy_diameter / 1e3, 1:b_diam / 1e3, 2:c_diam / 1e3}
        teethMap = {0:N0, 1:N1, 2:N2, 3:N3}
        locationMap ={0:SHAFT_LENGTH - LR, 1:LL, 2:SHAFT_LENGTH - LR, 3:LL}
        for shaft in self.shaftContainer:
            shaft.diameter = diameterMap[shaft.id]
            
            for object in shaft.mountedObjects:
                comp = object["component"]
                if comp.objectType == "bearing":
                    comp.bore = shaft.diameter * 1e3 # pass to bearings in mm for the catalouge lookup
                    
                elif comp.objectType == "gear":
                    comp.N = teethMap[comp.id]
                    comp.N_mating = teethMap[comp.meshingId]
                    object["location"] = locationMap[comp.id]
               
    def setupFilter(self, debug=False):
        # Check Kinematics
        if self.gearTrainCheck(debug=debug) != True:
            if debug: 
                print(f"DEBUG: ❌ Kinematics Failed.")
                print(f"  -> Target: {self.outputSpeed}, Actual: {self.shaftContainer[-1].speed}")
            return False

        # Check Spacing
        for shaft in self.shaftContainer:
            shaft.init()
            if shaft.initalValidMountCheck(debug=debug) != True:
                if debug: 
                    print(f"DEBUG: ❌ Spacing Failed on Shaft {shaft.id}.")
                return False
                     
        return True
                     
    def gearTrainCheck(self, debug=False): # hardcoded relationships
        shaftIn = self.shaftContainer[0]
        shaft01 = self.shaftContainer[1]
        shaftOut = self.shaftContainer[-1]
        
        if debug:
            print("\n--- ⚙️ KINEMATICS CHECK ---")
            print(f"Input Speed:  {self.inputSpeed} rad/s")
            print(f"Input Torque: {self.inputTorque} Nm")
        
        shaftIn.speed = self.inputSpeed
        shaftIn.torque = self.power * self.inputSpeed / sum(self.inputSpeed**2)
        shaftIn.life = self.inputShaftLife
        
        self.gearContainer[0].speed = self.inputSpeed
        self.gearContainer[0].torque = shaftIn.torque
        self.gearContainer[0].life = shaftIn.life
        
        inTo01Ratio = self.gearContainer[0].N / self.gearContainer[2].N # Driving / Driven
        shaft01Speed = - inTo01Ratio * self.inputSpeed
        shaft01Life = inTo01Ratio * self.inputShaftLife
        
        if debug:
            print(f"Stage 1 Ratio: {self.gearContainer[0].N}T / {self.gearContainer[2].N}T = {inTo01Ratio:.4f}")
            print(f"Shaft 1 Speed: {shaft01Speed} rad/s")
        
        shaft01.speed = shaft01Speed
        shaft01.torque = self.power * shaft01Speed / sum(shaft01Speed**2)
        shaft01.life = shaft01Life
        
        self.gearContainer[2].speed = shaft01Speed
        self.gearContainer[2].torque = shaft01.torque
        self.gearContainer[2].life = shaft01.life
        self.bearingContainer[2].L = shaft01.life
        self.bearingContainer[3].L = shaft01.life
        
        self.gearContainer[1].speed = shaft01Speed
        self.gearContainer[1].torque = - shaft01.torque
        self.gearContainer[1].life = shaft01.life
        
        S01ToOutRatio = self.gearContainer[1].N / self.gearContainer[3].N # Driving / Driven
        shaftOutSpeed = - S01ToOutRatio * shaft01Speed
        
        error_mag = np.linalg.norm(shaftOutSpeed - self.outputSpeed)
        if debug:
            print(f"Stage 2 Ratio: {self.gearContainer[1].N}T / {self.gearContainer[3].N}T = {S01ToOutRatio:.4f}")
            print(f"Target Output: {self.outputSpeed} rad/s")
            print(f"Actual Output: {shaftOutSpeed} rad/s")
            print(f"Error Mag:     {error_mag:.6f}")
            
        if error_mag < 1e-4: # account for unit conversion and rounding differences
            if debug: print("✅ Kinematics Passed!")
            
            shaftOut.speed = shaftOutSpeed
            shaftOut.torque = self.power * self.outputSpeed / sum(self.outputSpeed**2)
            shaftOut.life = S01ToOutRatio * shaft01Life
            
            self.gearContainer[3].speed = shaftOutSpeed
            self.gearContainer[3].torque = shaftOut.torque
            self.gearContainer[3].life = shaftOut.life
            self.bearingContainer[4].L = shaftOut.life
            self.bearingContainer[5].L = shaftOut.life
            return True
        else:
            if debug: print("❌ Kinematics Failed!")
            return False
        
    def deflectionCheck(self):
        for bearing in self.bearingContainer:
            if np.linalg.norm(bearing.angularDeflection) >= BEARING_ANGULAR_DEFLECTION_LIMIT:
                return False
        
        accountedForGears =[]
        for gear in self.gearContainer:
            if np.linalg.norm(gear.angularDeflection) >= GEAR_ANGULAR_DEFLECTION_LIMIT:
                return False
            if gear.id not in accountedForGears:
                id = gear.id
                meshingId = gear.meshingId
                accountedForGears.append([id, meshingId])
            
                meshingGear = self.gearContainer[meshingId]
                
                totalDeltaOrigins = gear.deflection + meshingGear.deflection
                
                totalSeperation = np.linalg.norm(totalDeltaOrigins)
                if totalSeperation >= SEPERATION_DEFLECTION_LIMIT:
                    return False
        
    def findSystemWeight(self): # fitness score after checking constraints 
        runningMass = 0
        
        for shaft in self.shaftContainer:
            if shaft.scopeFlag:
                runningMass += shaft.mass
                
        for bearing in self.bearingContainer:
            shaftId = bearing.shaftId
            
            if self.shaftContainer[shaftId].scopeFlag:
                runningMass += bearing.mass
                
        for gear in self.gearContainer:
            runningMass += gear.mass
            
        return runningMass * G
    
    def wipeState(self):
        # Reset any system-level flags
        
        for shaft in self.shaftContainer:
            # Reset the Factor of Safety
            shaft.FOS = float('inf') 