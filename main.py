#   digital rothko
#   January 15, 2019
#   J. Blake Harris
#   Display two colors on a string of neopixels based
#   on sound and light sensors
#   on the Adafruit Playground Express

from simpleio import map_range
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull
import array
import audiobusio
import board
import neopixel
import math
import time

SHERBET = (127, 20, 0)
SALMON = (80, 0, 20)
POMENGRANITE = (127, 0, 2)
TOMATO = (208, 8, 8)
LEMON = (127, 80, 0)
PERIWINKLE = (2, 0, 80)
AQUA = (0, 80, 20)
MARINE = (0, 80, 40)
MIDNIGHT = (20, 0, 127)
LIME = (20, 127, 0)

TOP_COLORS = [LIME, MIDNIGHT, MARINE, POMENGRANITE, PERIWINKLE, TOMATO, LEMON, AQUA, SHERBET,LIME, LIME]
BTM_COLORS = [MIDNIGHT, AQUA, LEMON, SALMON, POMENGRANITE, LEMON, SHERBET, LEMON, POMENGRANITE, AQUA, AQUA]

# light meter -------------------------------------------------------------
analogLight = AnalogIn(board.LIGHT)

# microphone --------------------------------------------------------------
# Exponential scaling factor.
# Should probably be in range -10 .. 10 to be reasonable.
CURVE = 2
SCALE_EXPONENT = math.pow(10, CURVE*-0.1)
# Number of samples to read at once.
NUM_SAMPLES = 160

# Restrict value to be between floor and ceiling.
def constrain(value, floor, ceiling):
    return max(floor, min(value, ceiling))

# Scale input_value to be between output_min and output_max, in an exponential way.
def log_scale(input_value, input_min, input_max, output_min, output_max):
    normalized_input_value = (input_value - input_min) / (input_max - input_min)
    return output_min + math.pow(normalized_input_value, SCALE_EXPONENT) * (output_max - output_min)

# Remove DC bias before computing RMS.
def normalized_rms(values):
    minbuf = int(mean(values))
    return math.sqrt(sum(float((sample-minbuf)*(sample-minbuf)) for sample in values)/len(values))

def mean(values):
    return (sum(values) / len(values))

mic = audiobusio.PDMIn(board.MICROPHONE_CLOCK, board.MICROPHONE_DATA, sample_rate=16000, bit_depth=16)
# Record an initial sample to calibrate. Assume it's quiet when we start.
samples = array.array('H', [0] * NUM_SAMPLES)
mic.record(samples, len(samples))
# Set lowest level to expect, plus a little.
input_floor = normalized_rms(samples) + 10
# OR: used a fixed floor
# input_floor = 50

# You might want to print the input_floor to help adjust other values.
# print(input_floor)

# Corresponds to sensitivity: lower means more pixels light up with lower sound
# Adjust this as you see fit.
input_ceiling = input_floor + 10

peak = 0

# on-board neopixels ------------------------------------------------------
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, auto_write=0, brightness=0.3)
pixels.fill(POMENGRANITE)
pixels.show()

# pin neopixels
pin = neopixel.NeoPixel(board.A7, 120)

while True:
    # read light meter ----------------------------------------------------
    # light value remapped to 0 - 9
    lightReading = map_range(analogLight.value, 2000, 100000, 0, 10)
    print("light:")
    print(int(lightReading))
    if lightReading > 10:
        lightReading = 10

    # read microphone ----------------------------------------------------
    mic.record(samples, len(samples))
    magnitude = normalized_rms(samples)
    # You might want to print this to see the values.
    # print(magnitude)

    # Compute scaled logarithmic reading in the range 0 to 8
    soundReading = log_scale(constrain(magnitude, input_floor, input_ceiling), input_floor, input_ceiling, 0, 100)
    print("sound:")
    soundReading = soundReading/10
    if soundReading > 10:
        soundReading = 10
    print(int(soundReading))
    finalReading = int((lightReading + soundReading)/2)
    print("final:")
    print(int(finalReading))
    print("-----------------")

    for i in range(0, 5):
        pixels[i] = TOP_COLORS[int(finalReading)]
        pixels.show()
        time.sleep(0.05)

    for i in range(5, 10):
        pixels[i] = BTM_COLORS[int(finalReading)]
        pixels.show()
        time.sleep(0.05)

    for i in range(0, 30):
        pin[i] = BTM_COLORS[int(finalReading)]
        pin.show()
        time.sleep(0.01)

    for i in range(30, 60):
        pin[i] = TOP_COLORS[int(finalReading)]
        pin.show()
        time.sleep(0.01)
