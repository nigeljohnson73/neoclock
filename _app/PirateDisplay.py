import datetime
import time
from colorsys import hsv_to_rgb
from PIL import Image, ImageDraw, ImageFont
from st7789 import ST7789
from _app.NjDisplay import NjDisplay
from _app.WeatherApi import getForecast

from io import BytesIO
from PIL import Image
import requests

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
font_temp = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
font_date = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
font_time = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 64)

r=0
rd=10
rmax=200
rmin=0


class PirateDisplay(NjDisplay):
    def __init__(self):
        super().__init__()
        print(f"Pirate Display enabled ({width}x{height}px)")
        setupModule()
        self.last_forecast = 0
        self.forecast_update = 50
        self.forecast_current_img = None
        self.forecast_next_img = None

    def loop(self):
        super().loop()

        global r, rd, rmin, rmax
        if r <= rmin or r >= rmax:
            rd= rd*-1
        #r = min(rmax, max(rmin, r+rd))
        #g = 0
        #b = 0
        #draw.rectangle((0, 0, 240, 240), (r, g, b))
        draw.rectangle((0, 0, 240, 240), 0)

        if False:
            lcol=(127,127,127)
            draw.rectangle([(0,0), (width-1, 10)], fill=(0,0,0), outline=lcol)
            draw.rectangle([(0,10), (width/2, 10+64)], fill=(0,0,0), outline=lcol)
            draw.rectangle([(width/2,10), (width-1, 10+64)], fill=(0,0,0), outline=lcol)
            draw.rectangle([(0,10+64), (width-1, 10+64+20)], fill=(0,0,0), outline=lcol)
            draw.rectangle([(0,10+64+20), (width-1, height-1)], fill=(0,0,0), outline=lcol)
            #print(f"(x,y):{width}x{height}")
        if True:
            t = datetime.datetime.now()
            tme = t.strftime("%H:%M")
            dte = t.strftime("%a %d %b %Y")

            #tp=(width//2, 74+((height-74)//2))
            #draw.ellipse((tp[0]-5,tp[1]-5,tp[0]+5,tp[1]+5), fill=(52,52,52), outline=(255,0,0))

            cy=120
            font = font_time
            yo=12
            text_left, text_top, text_right, text_bottom = draw.textbbox((0,0), text=tme, font=font)
            text_width, text_height = (text_right - text_left, text_bottom - text_top)
            tp=(width//2-text_width//2, cy+((height-cy)//2)-text_height-1-yo)
            if False:
                draw.ellipse((tp[0]-5,tp[1]+yo-5,tp[0]+5,tp[1]+yo+5), fill=(52,52,52), outline=(0,255,0))
                draw.rectangle(
                    (tp[0]+text_left, 
                     tp[1]+text_top, 
                     tp[0]+text_right, 
                     tp[1]+text_bottom,
                     ), 
                     fill=(52,52,52), outline=(0,255,0))
            draw.text(tp, tme, font=font, fill=(255,255,0))


            font = font_date
            yo=5
            text_left, text_top, text_right, text_bottom = draw.textbbox((0,0), text=dte, font=font)
            text_width, text_height = (text_right - text_left, text_bottom - text_top)
            tp=(width//2-text_width//2, cy+((height-cy)//2)+5-yo)
            if False:
                draw.ellipse((tp[0]-5,tp[1]+yo-5,tp[0]+5,tp[1]+yo+5), fill=(52,52,0), outline=(0,0,255))
                draw.rectangle(
                    (tp[0]+text_left, 
                     tp[1]+text_top, 
                     tp[0]+text_right, 
                     tp[1]+text_bottom,
                     ), 
                     fill=(52,52,52), outline=(0,0,255))
            draw.text(tp, dte, font=font, fill=(0,255,255))

        con = (255,0,0) if self.btConnected() else (0,0,0)
        draw.ellipse((0,0,10,10), fill=con, outline=(0,255,255))

        fc = getForecast()
        if len(fc):
            self.forecast_current_img = fc["now"]["condition_img"]
            self.forecast_next_img = fc["next"]["condition_img"]

            tmp = f'{round(fc["now"]["temp_c"])}C / {round(fc["now"]["humidity"])}%'
            font = font_temp
            cy=10+64+2
            text_left, text_top, text_right, text_bottom = draw.textbbox((0,0), text=tmp, font=font)
            text_width, text_height = (text_right - text_left, text_bottom - text_top)
            tp=(1*width//4-text_width//2, cy)
            draw.text(tp, tmp, font=font, fill=(0,255,255))

            tmp = f'{round(fc["next"]["mintemp_c"])}C / {round(fc["next"]["maxtemp_c"])}C'
            font = font_temp
            cy=10+64+2
            text_left, text_top, text_right, text_bottom = draw.textbbox((0,0), text=tmp, font=font)
            text_width, text_height = (text_right - text_left, text_bottom - text_top)
            tp=(3*width//4-text_width//2, cy)
            draw.text(tp, tmp, font=font, fill=(0,255,255))

        else:
            self.forecast_current_img = None
            self.forecast_next_img = None

        if self.forecast_current_img:
            x = int(1*image.width/4 - self.forecast_current_img.width/2) 
            y = 10 #(image.height - self.forecast_current_img.height) // 2
            image.paste(self.forecast_current_img, (x, y), self.forecast_current_img)

        if self.forecast_next_img:
            x = int(3*image.width/4 - self.forecast_next_img.width/2) 
            y = 10 #(image.height - self.forecast_next_img.height) // 2
            image.paste(self.forecast_next_img, (x, y), self.forecast_next_img)

        st7789.display(image)
