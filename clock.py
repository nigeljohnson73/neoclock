import board
import time
import datetime
import neopixel
import math

num_pixels = 60 # CAn run on 24 neopixel rings
bri = 255  # Max brightness
toff = -26 # This is one pixel past 5 oclock (to allow for soldering)
pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)

def setPixel(n, mult, arr):
    for i in arr:
        #Scale pixels to expected 60
        sp = int(((toff + n + i[0]) % 60) * (num_pixels / 60))
        lb = round(i[1])
        #print(f"n:{n}, sp:{sp}/{num_pixels}, l:{lb}")
        pixels[sp]=(
            max(0, min(255, pixels[sp][0] + lb*mult[0])),
            max(0, min(255, pixels[sp][1] + lb*mult[1])),
            max(0, min(255, pixels[sp][2] + lb*mult[2])),
        )

while True:
    t = datetime.datetime.now().time()
    s = t.second
    m = t.minute
    h = int(((t.hour%12)+m/60+s/3600) * 5) # Allow for sweep within the hour

    #print(f"time: {t.hour:02d}:{t.minute:02d}:{t.second:02d} - pixels: {h}:{m}:{s}")

    pixels.fill((0,0,0))
    setPixel(h, (1,0,0), [[-1,bri/12], [0,bri], [1, bri/12]])
    setPixel(m, (0,1,0), [[0,bri]])
    setPixel(s, (0,0,1), [[-2,bri/23], [-1, bri/10], [0, bri/5]])
    pixels.show()
    time.sleep(0.1)
