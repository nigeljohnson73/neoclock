import board
import digitalio
import time
import datetime
import neopixel
from colorsys import hsv_to_rgb
from PIL import Image, ImageDraw, ImageFont
from st7789 import ST7789
#from adafruit_rgb_display import st7789


#################
## Neopixel gear
num_pixels = 60 # Can run on 24 neopixel rings
bri = 255  # Max brightness
toff = -26 # This is one pixel past 5 oclock (to allow for soldering)
pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)

#################
## pirate audio gear
SPI_SPEED_MHZ = 80
st7789 = ST7789(
         rotation=90,  # Needed to display the right way up on Pirate Audio
         port=0,       # SPI port
         cs=1,         # SPI port Chip-select channel
         dc=9,         # BCM pin used for data/command
         backlight=13,
         spi_speed_hz=SPI_SPEED_MHZ * 1000 * 1000
         )
width=240
height=240
image = Image.new("RGB", (width, width), (0, 0, 0))
draw = ImageDraw.Draw(image)
FONTSIZE=24
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', FONTSIZE)

class NjButton():
    def __init__(self, pin, label=""):
        self.button = digitalio.DigitalInOut(pin)
        self.button.direction = digitalio.Direction.INPUT
        self.button.pull = digitalio.Pull.UP
        self.label = label
        self.state = self.button.value
        self.last_state = self.state

    def loop(self):
        self.state = self.button.value
        if self.state != self.last_state:
            print(f"Button {self.label}: change state to {not self.state}")
        self.last_state = self.state

buttons = [ NjButton(board.D5, "A"),
            NjButton(board.D6, "B"),
            NjButton(board.D16, "X"),
            NjButton(board.D24, "Y"),
          ]

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
    pass

def buttonLoop():
    for b in buttons:
        b.loop()

def loop():
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

    hue = (time.time()/10) % 255
    r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)]
    draw.rectangle((0, 0, 240, 240), (r, g, b))
    #disp.image(image)

    text = "Hello World!"
    text_left, text_top, text_right, text_bottom = draw.textbbox((0,0), text=text, font=font) 
    text_width, text_height = (text_right - text_left, text_bottom - text_top)
    draw.text((width//2 - text_width//2, height//2 - text_height//2), text, font=font, fill=(255, 255, 0))
    st7789.display(image)

last_s = 999
setup();
while True:
    loop()

    t = datetime.datetime.now().time()
    if last_s != t.second:
        last_s = t.second
        print(f"time: {t.hour:02d}:{t.minute:02d}:{t.second:02d}")
    #time.sleep(0.01)
