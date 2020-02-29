from pynq.lib import Button, LED
from pynq.overlays.base import BaseOverlay
import time

base = BaseOverlay("base.bit")
print("setup")

while base.buttons[1].read() == 0:
    base.rgbleds_gpio.write(0, 0x5)
    print("done")
    time.sleep(2)
    base.rgbleds_gpio.write(0, 0x3)
    time.sleep(2)
    
base.rgbleds_gpio.write(0, 0x0)