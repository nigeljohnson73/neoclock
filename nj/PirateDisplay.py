import datetime
from colorsys import hsv_to_rgb
from PIL import Image, ImageDraw, ImageFont
from st7789 import ST7789
from nj.NjDisplay import NjDisplay


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

r=0
rd=10
rmax=200
rmin=0


class PirateDisplay(NjDisplay):
    def __init__(self):
        super().__init__()
        print("Pirate Display enabled")
        pass

    def loop(self):
        super().loop()

        global r, rd, rmin, rmax
        #hue = (time.time()/10) % 255
        #r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)]
        #r = int((r+1) % 255)
        if r <= rmin or r >= rmax:
            rd= rd*-1
        r = min(rmax, max(rmin, r+rd))
        g = 0
        b = 0
        #print(f"r:{r}")
        draw.rectangle((0, 0, 240, 240), (r, g, b))
        #text = "Hello World!"
        t = datetime.datetime.now().time()
        text = f"{t.hour:02d}:{t.minute:02d}:{t.second:02d}"
        text_left, text_top, text_right, text_bottom = draw.textbbox((0,0), text=text, font=font)
        text_width, text_height = (text_right - text_left, text_bottom - text_top)
        draw.text((width//2 - text_width//2, height//2 - text_height//2), text, font=font, fill=(255, 255, 0))
        st7789.display(image)
