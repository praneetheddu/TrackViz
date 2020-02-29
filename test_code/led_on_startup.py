from pynq.lib import Button, LED
from pynq.overlays.base import BaseOverlay

base = BaseOverlay("base.bit")
print("setup")
base.rgbleds_gpio.write(0, 0x5)
print("done")
