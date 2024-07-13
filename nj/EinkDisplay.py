import threading
import os
import datetime
from PIL import Image,ImageDraw,ImageFont
from nj.NjDisplay import NjDisplay

epd = False
def setupModule():
    global epd
    if epd != False:
        return

    print("EInk module setup")
    from nj.epd2in13b_V4 import EPD
    epd = EPD()


libdir = os.path.dirname(os.path.realpath(__file__))
picdir = os.path.dirname(os.path.realpath(__file__))
#if os.path.exists(libdir):
#    sys.path.append(libdir)

font72 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 72)
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)

display_updating = False
def drawEinkDisplay(multicolor):
    global epd, display_updating
    if display_updating:
        print(f"drawEinkDisplay(): Skipping double update")
        return

    display_updating = True
    print(f"drawEinkDisplay(multicolor: {multicolor})")
    epd.init()
    #width = epd.width
    #height = epd.height
    width = epd.height
    height = epd.width

    imgb = Image.new('1', (epd.height, epd.width), 255)  # 250*122
    #imgc = Image.new('1', (epd.height, epd.width), 255)  # 250*122
    imgc = Image.new('1', (epd.height, epd.width), 255) if multicolor else imgb
    drawb = ImageDraw.Draw(imgb)
    drawc = ImageDraw.Draw(imgc) if multicolor else drawb

    #tme = f"{t.hour:02d}:{t.minute:02d}:{t.second:02d}"

    t = datetime.datetime.now()
    tme = t.strftime("%H:%M")
    dte = t.strftime("%a %d %B %Y")

    font = font72
    text_left, text_top, text_right, text_bottom = drawb.textbbox((0,0), text=tme, font=font)
    text_width, text_height = (text_right - text_left, text_bottom - text_top)
    d=(width//2 - text_width//2, height//2 - text_height)
    drawb.text((width//2 - text_width//2, height//2 - text_height-1), tme, font=font, fill=0)

    #print(f"dim:({width},{height}), txt: ({text_width},{text_height}), drw:{d}")
    font = font24
    text_left, text_top, text_right, text_bottom = drawc.textbbox((0,0), text=dte, font=font)
    text_width, text_height = (text_right - text_left, text_bottom - text_top)
    drawc.text((width//2 - text_width//2, height//2 + text_height+1), dte, font=font, fill=0)

    #drawb.text((10, 0), tme, font = font24, fill = 0)
    #drawc.text((10, 30), dte, font = font24, fill = 0)

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
    

    def loop(self):
        super().loop()

        t = datetime.datetime.now().time()
        if self.last_minute != t.minute:
            self.last_minute = t.minute
            print("e-ink: Starting update thread")
            thread = threading.Thread(target=drawEinkDisplay, args=(self.multicolor,))
            thread.start()

