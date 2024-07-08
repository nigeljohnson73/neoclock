# neoclock

## Harware
I have a few Raspberry Pi zero W's lying about he place. While the LED strips will run from the PI power rails, my OCD would not let me use the USB socket on the PI as it was too off center... so I added a USB-C socket to the mix. How you wire up your PI is on you. The only real 'need' is to run the LED data line from GPIO 18 in code, but you can even change this. As well as your PI, and wires. You will need an LED strip. I use the 144/m strip as it makes the whole face printable on a single print bed.

* [144LED/m 5V](https://www.amazon.co.uk/dp/B088KJPXVB)
* [USB-C sockets](https://www.amazon.co.uk/dp/B0D2HJZ2V9)


## Setup
Once you have your raspberry pi on the network of your choice, you can run the setup as follows:

    curl https://raw.githubusercontent.com/nigeljohnson73/neoclock/main/setup.sh | sh

## What's going on
THe PI will power up, auto login and run the python clock.
