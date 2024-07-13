import board
import digitalio
import time
import datetime
import neopixel
from nj.NjButton import NjButton
from nj.PirateDisplay import PirateDisplay
from nj.EinkDisplay import EinkDisplay
from nj.JoyDisplay import JoyDisplay

#################
## Neopixel gear
num_pixels = 60 # Can run on 24 neopixel rings
bri = 255  # Max brightness
toff = -26 # This is one pixel past 5 oclock (to allow for soldering)
pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)

def buttonPressed(label):
    print(f"{label} pressed")
    pass

def buttonReleased(label):
    print(f"{label} released")
    pass

package="Pirate"
buttons = []
display = False

def setPixel(n, mult, arr):
    for i in arr:
        #Scale pixels to expected 60
        sp = int(((toff + n + i[0]) % 60) * (num_pixels / 60))
        lb = round(i[1])
        pixels[sp]=(
            max(0, min(255, pixels[sp][0] + lb*mult[0])),
            max(0, min(255, pixels[sp][1] + lb*mult[1])),
            max(0, min(255, pixels[sp][2] + lb*mult[2])),
        )

def setup():
    global display, buttons

    if package == "InkyR":
        display = EinkDisplay(multicolor=True)
    elif package == "Inky":
        display = EinkDisplay()
    elif package == "Pirate":
        display = PirateDisplay()
        buttons = [ NjButton(board.D5, func_press=buttonPressed, func_release=buttonReleased, label="A"),
                    NjButton(board.D6, func_press=buttonPressed, label="B"),
                    NjButton(board.D16, func_press=buttonPressed, label="X"),
                    NjButton(board.D24, func_press=buttonPressed, label="Y"),
                ]
    elif package == "Joy":
        display = JoyDisplay()
        buttons = [ NjButton(board.D21,func_press=buttonPressed, label="KEY1"),
                    NjButton(board.D20,func_press=buttonPressed, label="KEY2"),
                    NjButton(board.D16,func_press=buttonPressed, label="KEY3"),
                    NjButton(board.D6,func_press=buttonPressed,  label="UP"),
                    NjButton(board.D19,func_press=buttonPressed, label="DOWN"),
                    NjButton(board.D5,func_press=buttonPressed,  label="LEFT"),
                    NjButton(board.D26,func_press=buttonPressed, label="RIGHT"),
                    NjButton(board.D13,func_press=buttonPressed, label="CENTER"),
                ]

def buttonLoop():
    for b in buttons:
        b.loop()

def loop():
    global display
    t = datetime.datetime.now().time()
    s = t.second
    m = t.minute
    h = int(((t.hour%12)+m/60+s/3600) * 5) # Allow for sweep within the hour

    pixels.fill((0,0,0))
    setPixel(h, (1,0,0), [[-1,bri/12], [0,bri], [1, bri/12]])
    setPixel(m, (0,1,0), [[0,bri]])
    setPixel(s, (0,0,1), [[-2,bri/23], [-1, bri/10], [0, bri/5]])
    pixels.show()

    buttonLoop()
    if display:
        display.loop();

last_s = 999
setup();
while True:
    loop()

    t = datetime.datetime.now().time()
    if last_s != t.second:
        last_s = t.second
        print(f"time: {t.hour:02d}:{t.minute:02d}:{t.second:02d}")
    #time.sleep(0.01)
