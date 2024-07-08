# neoclock
I have a few Raspberry Pi zero W's lying about the place and some LED strips from a WLED project, and that's why we can't have anything nice.

## Hardware
While the LED strips will run from the PI power rails, my OCD would not let me use the USB socket on the PI Zero W as it was too off center... so I added a USB-C socket to the mix. How you wire up your PI is on you. The only real 'need' is to run the LED data line from GPIO 18 in code, but you can even change this. As well as your PI, and wires. You will need an LED strip. I use the 144/m strip as it makes the whole face printable on a single print bed.

* [144LED/m 5V](https://www.amazon.co.uk/dp/B088KJPXVB) You will need 60. Cut the strip close to the last LED housing.
* [USB-C sockets](https://www.amazon.co.uk/dp/B0D2HJZ2V9)
* The boards mound with M2.6x6

## Setup
Once you have your raspberry pi on the network of your choice, you can run the setup as follows:

    curl https://raw.githubusercontent.com/nigeljohnson73/neoclock/main/setup.sh | sh

You should then reboot and all will be well in the world.

## What's going on
The PI will power up, auto login and run the python clock.
