import time
import board
import digitalio

class NjButton():
    def __init__(self, pin, func_press, func_release=False, label=""):
        self.button = digitalio.DigitalInOut(pin)
        self.button.direction = digitalio.Direction.INPUT
        self.button.pull = digitalio.Pull.UP

        self.debounce_delay = 1/100
        self.func_press = func_press
        self.func_release = func_release
        self.label = label
        self.state = self.button.value
        self.last_state = self.state
        self.last_state_time = time.time()

        print(f"NjButton({self.label}): added: {self.state}")

    def loop(self):
        self.state = self.button.value
        if self.state != self.last_state:
            print(f"NjButton({self.label}): {self.state}")
            now = time.time()
            if (now - self.last_state_time) > self.debounce_delay:
                # pull up resistor means buton is pressed when state is low
                if not self.state:
                    self.func_press(self.label)
                elif self.func_release:
                    self.func_release(self.label)
                self.last_state_time = now
            self.last_state = self.state
