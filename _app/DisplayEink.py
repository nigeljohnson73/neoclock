import os
import datetime
from PIL import Image, ImageDraw, ImageFont
from _app.DisplayBase import DisplayBase
from _app.KillableThread import KillableThread
from _app.WeatherApi import getForecast
from _app.AppLog import AppLog


'''
Stop clashes of setups by only setting this module up if it's needed
It's kinda like a singleton pattern, but badly implemented, cuz I hate python
'''
epd = None
picdir = os.path.dirname(os.path.realpath(__file__))
font_time = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 72)
font_date = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font_temp = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 20)
display_updating = False


def setupModule():
    global epd
    if epd != None:
        return

    AppLog.log("DisplayEink::setupModule()")
    from _app.epd2in13b_V4 import EPD
    epd = EPD()


def drawEinkDisplay(display, multicolor):
    global epd, display_updating
    if display_updating:
        AppLog.log(f"DisplayEink::drawEinkDisplay(): Skipping double update")
        return

    display_updating = True
    epd.init()
    width = epd.height  # for some reason the directions are reversed
    height = epd.width
    AppLog.log(
        f"DisplayEink::drawEinkDisplay(({width}, {height}), multicolor: {multicolor})")

    # Create a the black and contrast images. Basically the same image if mono screen
    imgb = Image.new('1', (width, height), 255)  # 250*122
    imgc = Image.new('1', (width, height), 255) if multicolor else imgb
    drawb = ImageDraw.Draw(imgb)
    drawc = ImageDraw.Draw(imgc) if multicolor else drawb

    # # Bluetooth connection indicator - useless for e-ink - delete this shortly
    # drawb.arc((0, 0, 10, 10),  0, 360, fill=0)
    # if display.btConnected():
    #     drawc.ellipse((1, 1, 9, 9), fill=0)

    # Draw the date near the bottom of the dispaly
    t = datetime.datetime.now()
    dte = t.strftime("%a %d %B %Y")
    font = font_date
    text_left, text_top, text_right, text_bottom = drawc.textbbox(
        (0, 0), text=dte, font=font)
    text_width, text_height = (text_right - text_left, text_bottom - text_top)
    drawc.text((width//2 - text_width//2, height -
               text_height-5), dte, font=font, fill=0)

    # Forecast images and text
    fc = getForecast()
    if len(fc):
        forecast_current_img = fc["now"].get("condition_img", None)
        forecast_next_img = fc["next"].get("condition_img", None)

        y = 0  # Image at the top of the screen (64px big)
        cy = 64  # Text directly under the image
        if forecast_current_img:
            x = int(1*imgb.width/4 - forecast_current_img.width/2)
            imgb.paste(forecast_current_img, (x, y), forecast_current_img)

        if forecast_next_img:
            x = int(3*imgb.width/4 - forecast_next_img.width/2)
            y = 0
            imgb.paste(forecast_next_img, (x, y), forecast_next_img)

        tmp = ""
        if len(str(fc["now"]["temp_c"])):
            tmp = f'{round(fc["now"]["temp_c"])}C'
        if len(str(fc["now"]["humidity"])):
            if len(tmp):
                tmp = f"{tmp} / "
            tmp = f'{tmp}{round(fc["now"]["humidity"])}%'
        font = font_temp
        text_left, text_top, text_right, text_bottom = drawb.textbbox(
            (0, 0), text=tmp, font=font)
        text_width, text_height = (
            text_right - text_left, text_bottom - text_top)
        tp = (1*width//4-text_width//2, cy)
        drawb.text(tp, tmp, font=font, fill=0)

        tmp = ""
        if len(str(fc["next"]["mintemp_c"])):
            tmp = f'{round(fc["next"]["mintemp_c"])}C'
        if len(str(fc["next"]["maxtemp_c"])):
            if len(tmp):
                tmp = f"{tmp} / "
            tmp = f'{tmp}{round(fc["next"]["maxtemp_c"])}C'
        font = font_temp
        text_left, text_top, text_right, text_bottom = drawb.textbbox(
            (0, 0), text=tmp, font=font)
        text_width, text_height = (
            text_right - text_left, text_bottom - text_top)
        tp = (3*width//4-text_width//2, cy)
        drawb.text(tp, tmp, font=font, fill=0)

    # Draw the images (for mono, the second arg is ignored)
    epd.display(epd.getbuffer(imgb), epd.getbuffer(imgc))
    epd.sleep()

    # Done updating
    display_updating = False
    print(f"drawEinkDisplay(): complete")


'''
Due to the delay it takes to update an e-ink display, this class does it in a separate 
thread. The module is set up the first time an object is instantiated, and each loop
processes the update loop in a backgound thread
'''


class DisplayEink(DisplayBase):
    def __init__(self, multicolor=False):
        super().__init__()
        setupModule()
        AppLog.log(f"DisplayEink::DisplayEink(multicolor: {multicolor})")
        self.multicolor = multicolor
        self.last_minute = -1

    def __del__(self):
        AppLog.log("DisplayEink::~DisplayEink()")
        self.thread.kill()
        self.thread.join()

    def loop(self):
        super().loop()

        t = datetime.datetime.now().time()
        if self.last_minute != t.minute:
            self.last_minute = t.minute
            AppLog.log("DisplayEink::loop()")
            self.thread = KillableThread(
                target=drawEinkDisplay, args=(self, self.multicolor,))
            self.thread.start()
