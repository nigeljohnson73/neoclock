import datetime
from colorsys import hsv_to_rgb
from PIL import Image, ImageDraw, ImageFont
from st7789 import ST7789
from _app.NjDisplay import NjDisplay

st7789 = False

def setupModule():
    global st7789
    if st7789 != False:
        return

    from st7789 import ST7789

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
#FONTSIZE=24
font24 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
font36 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 36)

r=0
rd=10
rmax=200
rmin=0


class PirateDisplay(NjDisplay):
    def __init__(self):
        super().__init__()
        print(f"Pirate Display enabled ({width}x{height}px)")
        setupModule()

    def loop(self):
        super().loop()

        global r, rd, rmin, rmax
        if r <= rmin or r >= rmax:
            rd= rd*-1
        r = min(rmax, max(rmin, r+rd))
        g = 0
        b = 0
        #print(f"r:{r}")
        draw.rectangle((0, 0, 240, 240), (r, g, b))

        t = datetime.datetime.now()
        tme = t.strftime("%H:%M")
        dte = t.strftime("%a %d %b %Y")

        font = font36
        text_left, text_top, text_right, text_bottom = draw.textbbox((0,0), text=tme, font=font)
        text_width, text_height = (text_right - text_left, text_bottom - text_top)
        d=(width//2 - text_width//2, height//2 - text_height)
        draw.text((width//2 - text_width//2, height//2 - text_height-1), tme, font=font, fill=(255,255,0))

        font = font24
        text_left, text_top, text_right, text_bottom = draw.textbbox((0,0), text=dte, font=font)
        text_width, text_height = (text_right - text_left, text_bottom - text_top)
        draw.text((width//2 - text_width//2, height//2 + text_height+1), dte, font=font, fill=(0,255,255))

        con = (255,0,0) if self.btConnected() else (0,0,0)
        draw.ellipse((0,0,10,10), fill=con, outline=(0,255,255))

        st7789.display(image)
