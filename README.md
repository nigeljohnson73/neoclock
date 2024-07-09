# neoclock
I have a few Raspberry Pi zero W's lying about the place and some LED strips from a WLED project, and that's why we can't have anything nice.

## Hardware
While the LED strips will run from the PI power rails, my OCD would not let me use the USB socket on the PI Zero W as it was too off-centre... so I added a USB-C socket to the mix. How you wire up your PI is on you. The only real 'need' is to run the LED data line from GPIO 18 in code, but you can even change this. As well as your PI, and wires. You will need an LED strip. I use the 144/m strip as it makes the whole face printable on a single print bed.

* [144LED/m 5V strip](https://www.amazon.co.uk/dp/B088KJPXVB)
* [USB-C breakout boards](https://www.amazon.co.uk/dp/B0D2HJZ2V9)
* [M2.6x6 self tapping screws](https://www.amazon.co.uk/dp/B087X76NXF)
* 26AWG silicone wire

You will need 60 LEDs. Cut the strip close to the last LED housing to give yourself a little solder wiggle room when assembling.

You will need 3 bits of wire about 125mm for the LED strip connection, and 2 about 65mm for the power.

## Wiring
There is nothing magical about the wiring, if you have headers, use them, if not, solder wires. I wired mine us as follows:

* USB +ve --> pin 2 (5V)
* USB -ve --> pin 9 (GND)
* LED +ve --> pin 4 (5V)
* LED data --> pin 12 (GPIO18)
* LED -ve --> pin 14 (GND)

You can solder the USB socket onto any ground/+5V you can find, and there are pads on the back of the PI under the USB power socket for this if you like.

## Software setup
You can use the Raspberry PI Imager and install Raspberry PI OS LITE (32-BIT). You should also attach it to your network and log in via SSH. You're looking at GitHub so I'm assuming that I don't need to go into too much detail here.

Once you have your Raspberry Pi on the network of your choice, you can run the setup as follows:

    curl https://raw.githubusercontent.com/nigeljohnson73/neoclock/main/setup.sh | sh

Reboot and all will be well in the world.

## What's going on
The PI will power up and run the Python clock in the background. It uses your local WiFi to get time and all that jazz.

## What about someone else's network?
Luckily the cunning folks at Raspberry Ing allow you to create a text file on the SD card and set up the new WiFi. [Click here](https://forums.raspberrypi.com/viewtopic.php?t=259894} for more information. But basically,

* Mount the SD card on your computer
* Create a file in the root partition called `wpa_supplicant.conf`
* Paste the following in, and update the SSID/PAssphrase, also check the country

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=GB

network={
	ssid="WiFi SSID"
	psk="WPA/WPA2 passphrase"
	key_mgmt=WPA-PSK
}
```
Reassemble, power up and wait for 10 minutes. Job jobbed.

