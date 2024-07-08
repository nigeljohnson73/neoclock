import board
import time
import datetime
import neopixel
import math

# setup the pixels
num_pixels=60
pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)
bri=255
toff=-26 # 25 if you get spot on 5 oclock entry

def setPixel(n, mult, arr):
    for i in arr:
        sp = (toff + n + i[0]) % num_pixels
        lb = i[1]
        pixels[sp]=(
                    min(255, pixels[sp][0] + lb*mult[0]),
                    min(255, pixels[sp][1] + lb*mult[1]),
                    min(255, pixels[sp][2] + lb*mult[2]),
                    )


# while forever
while True:
    t = datetime.datetime.now().time()
    h = (t.hour%12)*5
    m = t.minute
    s = t.second
    print(f"{t.hour:02d}:{t.minute:02d}:{t.second:02d} - {h}:{m}:{s}")

    pixels.fill((0,0,0))
    setPixel(h, (1,0,0), [[-1,bri/12], [0,bri], [1, bri/12]])
    setPixel(m, (0,1,0), [[0,bri]])
    setPixel(s, (0,0,1), [[-2,bri/20], [-1,bri/8], [0, bri]])
    pixels.show()
    time.sleep(0.1)
