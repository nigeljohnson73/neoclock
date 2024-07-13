import board
import digitalio

class NjButton():
    def __init__(self, pin, label=""):
        self.button = digitalio.DigitalInOut(pin)
        self.button.direction = digitalio.Direction.INPUT
        self.button.pull = digitalio.Pull.UP
        self.label = label
        self.state = self.button.value
        self.last_state = self.state

    def loop(self):
        self.state = self.button.value
        if self.state != self.last_state:
            print(f"Button {self.label}: change state to {not self.state}")
        self.last_state = self.state

# Pirate Audio board
buttons = [ NjButton(board.D5, "A"),
            NjButton(board.D6, "B"),
           NjButton(board.D16, "X"),
            NjButton(board.D24, "Y"),
          ]

ws_buttons = [ NjButton(board.D21, "KEY1"),
               NjButton(board.D20, "KEY2"),
               NjButton(board.D16, "KEY3"),
               NjButton(board.D6, "UP"),
               NjButton(board.D19, "DOWN"),
               NjButton(board.D5, "LEFT"),
               NjButton(board.D26, "RIGHT"),
               NjButton(board.D13, "PRESS"),
          ]


