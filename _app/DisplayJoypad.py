import datetime
from colorsys import hsv_to_rgb
from PIL import Image, ImageDraw, ImageFont
from _app.DisplayBase import DisplayBase
from _app.WeatherApi import getForecast

'''
Stop clashes of setups by only setting this module up if it's needed
It's kinda like a singleton pattern, but badly implemented, cuz I hate python
'''
disp = None
font_name = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font_locn = ImageFont.truetype(font_name, 14)
font_date = ImageFont.truetype(font_name, 13)
font_time = ImageFont.truetype(font_name, 24)
font_temp = ImageFont.truetype(font_name, 10)


def setupModule():
    global disp, image, draw, width, height
    if disp != None:
        return

    print("DisplayJoypad::setupModule()")

    import _app.LCD_1in44 as LCD_1in44
    disp = LCD_1in44.LCD()
    Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  # SCAN_DIR_DFT = D2U_L2R
    disp.LCD_Init(Lcd_ScanDir)
    disp.LCD_Clear()

    width = disp.width
    height = disp.height
    image = Image.new("RGB", (width, width), (0, 0, 0))
    draw = ImageDraw.Draw(image)


class DisplayJoypad(DisplayBase):
    def __init__(self):
        super().__init__()
        setupModule()
        print(f"DisplayJoypad::DisplayJoypad(({width}, {height}))")

    def loop(self):
        super().loop()

        global disp, image, draw, width, height

        # background bluer if BT connected
        bgcol = (0, 0, 52) if self.btConnected() else 0
        draw.rectangle((0, 0, width, height), bgcol)

        if True:
            t = datetime.datetime.now()
            tme = t.strftime("%H:%M")
            dte = t.strftime("%a %d %b %Y")

            cy = height - 18  # 64+10
            font = font_date
            text_left, text_top, text_right, text_bottom = draw.textbbox(
                (0, 0), text=dte, font=font)
            text_width, text_height = (
                text_right - text_left, text_bottom - text_top)
            tp = (width//2-text_width//2, cy)
            draw.text(tp, dte, font=font, fill=(0, 255, 255))

            #con = (255, 0, 0) if self.btConnected() else (0, 0, 0)
            #draw.ellipse((0, 0, 10, 10), fill=con, outline=(0, 255, 255))

            fc = getForecast()
            if len(fc):
                self.forecast_current_img = fc["now"].get(
                    "condition_img", None)
                self.forecast_next_img = fc["next"].get("condition_img", None)

                y = 0  # (image.height - self.forecast_next_img.height) // 2
                cy = 0+64+2
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

        rimage = image.rotate(180)
        disp.LCD_ShowImage(rimage, 0, 0)
