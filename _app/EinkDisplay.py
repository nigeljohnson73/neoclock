import threading
import os
import datetime
from PIL import Image,ImageDraw,ImageFont
from _app.NjDisplay import NjDisplay
from _app.KillableThread import KillableThread
from _app.WeatherApi import getForecast

epd = False
def setupModule():
    global epd
    if epd != False:
        return

    print("EInk module setup")
    from _app.epd2in13b_V4 import EPD
    epd = EPD()


libdir = os.path.dirname(os.path.realpath(__file__))
picdir = os.path.dirname(os.path.realpath(__file__))
#if os.path.exists(libdir):
#    sys.path.append(libdir)

font_time = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 72)
font_date = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font_temp = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 20)

display_updating = False
def drawEinkDisplay(display, multicolor):
    global epd, display_updating
    if display_updating:
        print(f"drawEinkDisplay(): Skipping double update")
        return

    display_updating = True
    epd.init()
    #width = epd.width
    #height = epd.height
    width = epd.height
    height = epd.width
    print(f"drawEinkDisplay(dim: ({width}, {height}), multicolor: {multicolor})")

    imgb = Image.new('1', (epd.height, epd.width), 255)  # 250*122
    imgc = Image.new('1', (epd.height, epd.width), 255) if multicolor else imgb
    drawb = ImageDraw.Draw(imgb)
    drawc = ImageDraw.Draw(imgc) if multicolor else drawb

    t = datetime.datetime.now()
    tme = t.strftime("%H:%M")
    dte = t.strftime("%a %d %B %Y")

    '''
    font = font_time
    text_left, text_top, text_right, text_bottom = drawb.textbbox((0,0), text=tme, font=font)
    text_width, text_height = (text_right - text_left, text_bottom - text_top)
    d=(width//2 - text_width//2, height//2 - text_height)
    drawb.text((width//2 - text_width//2, height//2 - text_height-1), tme, font=font, fill=0)

    #print(f"dim:({width},{height}), txt: ({text_width},{text_height}), drw:{d}")
    '''
    font = font_date
    text_left, text_top, text_right, text_bottom = drawc.textbbox((0,0), text=dte, font=font)
    text_width, text_height = (text_right - text_left, text_bottom - text_top)
    drawc.text((width//2 - text_width//2, height - text_height-5), dte, font=font, fill=0)

    fc = getForecast()
    forecast_current_img = None
    forecast_next_img = None
    if len(fc):
        forecast_current_img = fc["now"]["condition_img"]
        forecast_next_img = fc["next"]["condition_img"]

        tmp = f'{round(fc["now"]["temp_c"])}C / {round(fc["now"]["humidity"])}%'
        font = font_temp
        cy=64
        text_left, text_top, text_right, text_bottom = drawb.textbbox((0,0), text=tmp, font=font)
        text_width, text_height = (text_right - text_left, text_bottom - text_top)
        tp=(1*width//4-text_width//2, cy)
        drawb.text(tp, tmp, font=font, fill=0)

        tmp = f'{round(fc["next"]["mintemp_c"])}C / {round(fc["next"]["maxtemp_c"])}C'
        font = font_temp
        cy=64
        text_left, text_top, text_right, text_bottom = drawb.textbbox((0,0), text=tmp, font=font)
        text_width, text_height = (text_right - text_left, text_bottom - text_top)
        tp=(3*width//4-text_width//2, cy)
        drawb.text(tp, tmp, font=font, fill=0)

    if forecast_current_img:
        x = int(1*imgb.width/4 - forecast_current_img.width/2)
        y = 0 #(image.height - self.forecast_current_img.height) // 2
        imgb.paste(forecast_current_img, (x, y), forecast_current_img)

    if forecast_next_img:
        x = int(3*imgb.width/4 - forecast_next_img.width/2)
        y = 0 #(image.height - self.forecast_next_img.height) // 2
        imgb.paste(forecast_next_img, (x, y), forecast_next_img)

    drawb.arc((0,0,10,10),  0, 360, fill=0)
    if display.btConnected():
        #print("Display says BT is connected")
        drawc.ellipse((1,1,9,9), fill=0)
    #else:
        #print("Display says BT is DISConnected")
        #pass

    epd.display(epd.getbuffer(imgb), epd.getbuffer(imgc))
    epd.sleep()
    display_updating = False
    print(f"drawEinkDisplay(): complete")

class EinkDisplay(NjDisplay):
    def __init__(self, multicolor=False):
        super().__init__()
        setupModule()
        print(f"E-Ink Display enabled (multicolor: {multicolor})")
        self.multicolor=multicolor
        self.last_minute = -1
    
    def __del__(self):
        print("EinkDisplay::__del__()")
        self.thread.kill()
        self.thread.join()

    def loop(self):
        super().loop()

        t = datetime.datetime.now().time()
        if self.last_minute != t.minute:
            self.last_minute = t.minute
            print("e-ink: Starting update thread")
            #thread = threading.Thread(target=drawEinkDisplay, args=(self, self.multicolor,))
            self.thread = KillableThread(target=drawEinkDisplay, args=(self, self.multicolor,))
            self.thread.start()

