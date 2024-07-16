# Neo-clock
I have a few Raspberry Pi zero W's lying about the place and some LED strips from an old WLED project, and that's why we can't have anything nice.

Oh, Python is not my first langfuage, and we are in a pretty rough place relationship wise, so please bear with us while we work through our differences.

## Hardware
While the LED strips will run from the PI power rails, my OCD would not let me use the USB socket on the PI Zero W as it was too off-centre... so I added a USB-C socket to the mix. How you wire up your PI is on you. The only real 'need' is to run the LED data line from GPIO 18 in code, but you can even change this. As well as your PI, and wires. You will need an LED strip. I use the 144/m strip as it makes the whole face printable on a single print bed.

* [144LED/m 5V strip](https://www.amazon.co.uk/dp/B088KJPXVB) (60 long)
* [USB-C breakout boards](https://www.amazon.co.uk/dp/B0D2HJZ2V9) (1x)
* [M2.6x6 self tapping screws](https://www.amazon.co.uk/dp/B087X76NXF) (6x)
* 26AWG silicone wire
   * 3x 125mm for LED strip
   * 2x 65mm for USB power

Cut the LED strip close to the last LED housing to give yourself a little solder wiggle room when assembling.

## Wiring
There is nothing magical about the wiring, if you have headers, use them, if not, solder wires. I wired mine us as follows:

* LED +ve --> pin 2 (5V)
* LED -ve --> pin 6 (GND)
* LED data --> pin 12 (GPIO18)
* USB +ve --> Top USB port pad or GPIO pin 2 (5V)
* USB -ve --> Bottom USB port pad or GPIO pin 9 (GND)

You can solder the USB socket onto any ground/+5V you can find, and there are pads on the back of the PI under the USB power socket for this if you like.

### USB-C
So QC and PD3.0 or PD3.1 - just solder a 5k1 pull-up resistor onto the CC pin on the socket bearkout board and all will be good... THat all sounded like gibberish? no worries, some USB-C power supplies might not work if they are labelled "Quick Charge" (QC) or "Power Delivery" (PD). The resistor signals to the power supply that you just want a little bit of 5V.

### USB-micro
You can use a [usb-micro breakout](https://www.amazon.co.uk/dp/B08DCZRXXS) instead if you like, but that won't fit on the 3D print yet. I've built the model, but not tested or released it yet. Get with the 21st century though :) Lightening connector? awww, you're cute.

## Software setup
You can use the Raspberry PI Imager and install Raspberry PI OS LITE (32-BIT). You should also attach it to your network and log in via SSH. You're looking at GitHub so I'm assuming that I don't need to go into too much detail here.

Log in as the `pi` user and run the setup as follows:

    curl https://raw.githubusercontent.com/nigeljohnson73/neoclock/main/setup.sh | sh

Reboot and all will be well in the world.

If you want to use the advanced version with the displays and bluetooth etc, use this on:

    curl https://raw.githubusercontent.com/nigeljohnson73/neoclock/main/setup_adv.sh | sh

## Display packages
I have a couple of displays and things that need adding into the config file:

* [Pimoroni Pirate Audio hat](https://shop.pimoroni.com/products/pirate-audio-mini-speaker?variant=31189753692243) ('Pirate')
* [Waveshare 2.13" Mono e-ink display](https://www.amazon.co.uk/dp/B07J3FHJVP) ('Inky')
* [Waveshare 2.13" Mono and red/yellow e-ink display](https://www.amazon.co.uk/dp/B075FR81WL) ('InkyR')
* [Waveshare 1.44" hat with joypad and stuff](https://www.amazon.co.uk/dp/B077YK8161) ('Joypad')

These work to display the weather integration bits. You will need a free account setup in [WeatherAPI.com](https://www.weatherapi.com/). The key stuff goes into the config file as well. A comma separated list of locations can be set as well. To switch between them, press the top left button (`KEY3` on the joypad (cuz it's mounted upside down) or `A` on the pirate display)

## Bluetooth
The advanced setup allows for a bleutooth serial connection. On Android, I use '[Serial Bluetooth Terminal](https://play.google.com/store/apps/details?id=de.kai_morich.serial_bluetooth_terminal)' to send configuration commands over the serial port. It's all text, and it will probably turn into an App at some point. On Apple? You're on your own for a while. There really should be more documentation, but when you connect you are told what commands are available.

## What about someone else's network?
Well, use the built-in bluetooth connector to set the WiFi up. It's currently untested, but the folk at Raspberry have purposely broken the old way of configuring WiFi the cool way and use the network manager exclusively now.

## Helping out
I'd love some help. Get in touch!!!! I'm in need of Phone apps to control things over bluetooth serial, python coding skills, and more ideas on how to make the displays better if there is no weather integration... etc...
