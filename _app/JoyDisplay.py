import datetime
from colorsys import hsv_to_rgb
from PIL import Image, ImageDraw, ImageFont
from _app.NjDisplay import NjDisplay
from _app.WeatherApi import getForecast

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

font_date = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
font_time = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
font_temp = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 10)

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

        global disp, image, draw, width, height
        draw.rectangle((0, 0, width, height), 0)

        if True:
            t = datetime.datetime.now()
            tme = t.strftime("%H:%M")
            dte = t.strftime("%a %d %b %Y")

            cy=64+10
            '''
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
            '''

            font = font_date
            yo=5
            text_left, text_top, text_right, text_bottom = draw.textbbox((0,0), text=dte, font=font)
            text_width, text_height = (text_right - text_left, text_bottom - text_top)
            tp=(width//2-text_width//2, cy+((height-cy)//2)+5-yo)
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


        rimage = image.rotate(180)
        disp.LCD_ShowImage(rimage,0,0)

