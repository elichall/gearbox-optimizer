from enum import Enum

class Axis(Enum):
    X = 0
    Y = 1
    Z = 2

# System Specifications
LIFE_REQUIRED_IN = 3.6e8 # revolutions
SYS_POWER = 21 * 745.7 # power input in watts
INPUT_SPEED = 1050 # rpm
OUTPUT_SPEED = 216 # rpm

# Global Constants
G = 9.81 # m/s^2
PI = 3.141592653589793

# Gear Constants
PITCH = 10
PRESURE_ANGLE = 25 # deg
OVERLOAD_CORRECTION_FACTOR = 1.25 # moderate shock with uniform power
UTS_303A = 690 * 1e6 # Pa
YS_303A = 450 * 1e6 # Pa
LOADING_FACTOR = 1 # bending stress
TEMPERATURE_FACTOR = 1 # temperature is STP
LOADING_PATTERN_FACTOR = 1.4 # all driven or driving gears
GEAR_RELIABILITY = 95 # percents
DENSITY_303A = 8027 # kg/m^3
GEAR_ANGULAR_DEFLECTION_LIMIT = 0.03 * PI / 180 # degrees
SEPERATION_DEFLECTION_LIMIT = 0.005 / 39.3701 # linear seperation limit between gears

# Bearing Constants
BEARING_RELIABILITY = 95
SHOCK_FACTOR = 2.0 # moderate to heavy ball bearing
STANDARD_LIFE= 90e6
BEARING_ANGLE = 0 # radial bearings
MINIMUM_BEARING_WIDTH = 0.010 # m 
BEARING_ANGULAR_DEFLECTION_LIMIT = 0.04 * PI / 180 # degrees
PACKING_FACTOR = 0.85

# Shaft Constants
SHAFT_LENGTH = 9 / 39.3701 # length of shafts (meters)
COMPONENT_SPACING_LIMIT = 1 / 39.3701 # length between bearings and gears on shaft
SHAFT_MODULUS = 200e9 # modulus for average steel (may change to a table of options later for optimization)
SHAFT_DENSITY = 7850 # kg/m^3
SHAFT_RELIABILITY = 95 