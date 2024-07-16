import datetime
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


width = 240
height = 240
image = Image.new("RGB", (width, width), (0, 0, 0))
draw = ImageDraw.Draw(image)
font_name = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font_locn = ImageFont.truetype(font_name, 22)
font_temp = ImageFont.truetype(font_name, 16)
font_date = ImageFont.truetype(font_name, 24)
font_time = ImageFont.truetype(font_name, 64)


class PirateDisplay(NjDisplay):
    def __init__(self):
        super().__init__()
        print(f"PirateDisplay::PirateDisplay(({width},{height}))")
        setupModule()

    def loop(self):
        super().loop()

        global image, draw, width, height
        # background bluer if BT connected
        bgcol = (0, 0, 52) if self.btConnected() else 0
        draw.rectangle((0, 0, width, height), bgcol)

        # Show the delineation of the display
        if False:
            lcol = (127, 127, 127)
            draw.rectangle([(0, 0), (width-1, 10)],
                           fill=(0, 0, 0), outline=lcol)
            draw.rectangle([(0, 10), (width/2, 10+64)],
                           fill=(0, 0, 0), outline=lcol)
            draw.rectangle([(width/2, 10), (width-1, 10+64)],
                           fill=(0, 0, 0), outline=lcol)
            draw.rectangle([(0, 10+64), (width-1, 10+64+20)],
                           fill=(0, 0, 0), outline=lcol)
            draw.rectangle([(0, 10+64+20), (width-1, height-1)],
                           fill=(0, 0, 0), outline=lcol)

        # Bleutooth indicator
        # con = (255, 0, 0) if self.btConnected() else (0, 0, 0)
        # draw.ellipse((0, 0, 10, 10), fill=con, outline=(0, 255, 255))

        t = datetime.datetime.now()
        tme = t.strftime("%H:%M")
        dte = t.strftime("%a %d %b %Y")

        # Time as large - cuz we have an HD display
        cy = 140
        yo = 12
        font = font_time
        text_left, text_top, text_right, text_bottom = draw.textbbox(
            (0, 0), text=tme, font=font)
        text_width, text_height = (
            text_right - text_left, text_bottom - text_top)
        tp = (width//2-text_width//2, cy+((height-cy)//2)-text_height-1-yo)
        draw.text(tp, tme, font=font, fill=(255, 255, 0))

        # Date
        yo = 5
        font = font_date
        text_left, text_top, text_right, text_bottom = draw.textbbox(
            (0, 0), text=dte, font=font)
        text_width, text_height = (
            text_right - text_left, text_bottom - text_top)
        tp = (width//2-text_width//2, cy+((height-cy)//2)+5-yo)
        draw.text(tp, dte, font=font, fill=(0, 255, 255))

        fc = getForecast()
        if len(fc):
            self.forecast_current_img = fc["now"].get("condition_img", None)
            self.forecast_next_img = fc["next"].get("condition_img", None)

            y = 0  # Image location
            cy = 0+64+2  # Text location
            if self.forecast_current_img:
                x = int(1*image.width/4 - self.forecast_current_img.width/2)
                image.paste(self.forecast_current_img,
                            (x, y), self.forecast_current_img)

            if self.forecast_next_img:
                x = int(3*image.width/4 - self.forecast_next_img.width/2)
                image.paste(self.forecast_next_img,
                            (x, y), self.forecast_next_img)

            # Do the current temp/humidity
            tmp = ""
            if len(str(fc["now"]["temp_c"])):
                tmp = f'{round(fc["now"]["temp_c"])}C'
            if len(str(fc["now"]["humidity"])):
                if len(tmp):
                    tmp = f"{tmp} / "
                tmp = f'{tmp}{round(fc["now"]["humidity"])}%'
            font = font_temp
            text_left, text_top, text_right, text_bottom = draw.textbbox(
                (0, 0), text=tmp, font=font)
            text_width, text_height = (
                text_right - text_left, text_bottom - text_top)
            tp = (1*width//4-text_width//2, cy)
            draw.text(tp, tmp, font=font, fill=(0, 255, 255))

            # Do the min/max temp for tomorrow
            tmp = ""
            if len(str(fc["next"]["mintemp_c"])):
                tmp = f'{round(fc["next"]["mintemp_c"])}C'
            if len(str(fc["next"]["maxtemp_c"])):
                if len(tmp):
                    tmp = f"{tmp} / "
                tmp = f'{tmp}{round(fc["next"]["maxtemp_c"])}C'
            font = font_temp
            text_left, text_top, text_right, text_bottom = draw.textbbox(
                (0, 0), text=tmp, font=font)
            text_width, text_height = (
                text_right - text_left, text_bottom - text_top)
            tp = (3*width//4-text_width//2, cy)
            draw.text(tp, tmp, font=font, fill=(0, 255, 255))

            cy = 0+64+2+20
            tmp = fc["location"]["name"]
            font = font_locn
            text_left, text_top, text_right, text_bottom = draw.textbbox(
                (0, 0), text=tmp, font=font)
            text_width, text_height = (
                text_right - text_left, text_bottom - text_top)
            tp = (width//2-text_width//2, cy)
            draw.text(tp, tmp, font=font, fill=(0, 255, 255))

        st7789.display(image)
