import datetime
from colorsys import hsv_to_rgb
from PIL import Image, ImageDraw, ImageFont
from _app.NjDisplay import NjDisplay

disp = False

def setupModule():
    global disp, r, rd, rmin, rmax, image, draw,width,height
    if disp != False:
        return
    print("Joypad module setup")

    import _app.LCD_1in44 as LCD_1in44
    disp = LCD_1in44.LCD()
    Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
    disp.LCD_Init(Lcd_ScanDir)
    disp.LCD_Clear()

    width=disp.width
    height=disp.height
    image = Image.new("RGB", (width, width), (0, 0, 0))
    draw = ImageDraw.Draw(image)

font24 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
font36 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)

r=0
rd=10
rmax=200
rmin=0

class JoyDisplay(NjDisplay):
    def __init__(self):
        super().__init__()
        setupModule()
        print(f"Joypad Display enabled ({disp.width}x{disp.height}px)")

    def loop(self):
        super().loop()

        global disp, r, rd, rmin, rmax, image, draw,width,height
        if r <= rmin or r >= rmax:
            rd= rd*-1
        r = min(rmax, max(rmin, r+rd))
        g = 0
        b = 0
        #print(f"r:{r}")
        draw.rectangle((0, 0, width, height), (r, g, b))

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

        disp.LCD_ShowImage(image,0,0)

