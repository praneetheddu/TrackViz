import cv2 as cv
import numpy as numpy
import time
import serial 
import adafruit_gps
import plotly.graph_objects as go
import matplotlib.pyplot as plt

from pynq.lib import Button, LED
from pynq.overlays.base import BaseOverlay
from pynq.lib.video import *



#Load the base overlay
base = BaseOverlay("base.bit")
print("Modules and Peripherals are setup")

# Setup UART
uart = serial.Serial('/dev/ttyUSB0', baudrate=9600)

# Setup GPS
gps = adafruit_gps.GPS(uart, debug=False)
gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
gps.send_command(b'PMTK220,1000')


print("done")
base.rgbleds_gpio.write(0, 0x2)
# Setup HDMI
print("HDMI setting up ... ")
hdmi_in = base.video.hdmi_in
print('HDMI in is setup')
hdmi_out = base.video.hdmi_out
print("HDMI out is setup")

# Configure the HDMI output to the same resolution as the HDMI input
hdmi_in.configure(PIXEL_BGR)
hdmi_out.configure(hdmi_in.mode, PIXEL_BGR)
print("HDMI is setup and configured with mode: ", hdmi_in.mode)
base.rgbleds_gpio.write(0, 0x3)

def start_HDMI():
    # Start the HDMI interfaces
    hdmi_in.start()
    hdmi_out.start()
    print("HDMI started")


start_HDMI()
base.rgbleds_gpio.write(0, 0x4)
init = False
last_print = time.monotonic()
speed_mph = 0

# overlays go here
gauge = cv.imread('/home/xilinx/jupyter_notebooks/TrackViz/Contents/pooe.png', -1)
gps_map = cv.imread('/home/xilinx/jupyter_notebooks/TrackViz/gps_plots/out.png')
start_screen_menu = cv.imread('Contents/record.png')

# Offset from top left of screen in pixels
gauge_x_offset=20
gauge_y_offset= 500
gps_x_offset = 800
gps_y_offset = 50
start_x_offset=start_y_offset=0


start_screen_mode = 0

# Matplot lib initialize
#fig = plt.figure(frameon=False)
base.rgbleds_gpio.write(0, 0x5)
# Start Screen
while base.buttons[1].read() == 0:
    new_frame = hdmi_in.readframe()
    new_frame[start_y_offset:start_y_offset+start_screen_menu.shape[0], start_x_offset:start_x_offset+start_screen_menu.shape[1]] = start_screen_menu
    hdmi_out.writeframe(new_frame)

#     # Wait till button press 
#     button_pressed = False
    
#     while button_pressed == False: 
#         for i in range(0, 3):
#             if base.buttons[i].read() == 1:
#                 button_pressed = True
#                 break
           
    if base.buttons[2].read() == 1:
        new_frame = hdmi_in.readframe()
        start_screen_mode = start_screen_mode + 1 
        time.sleep(0.1)
    elif base.buttons[3].read() == 1:
        start_screen_mode = start_screen_mode - 1
        time.sleep(0.1)
    start_screen_mode = start_screen_mode % 4 
    
    if start_screen_mode == 0:
        start_screen_menu = cv.imread('Contents/record.png')
    elif start_screen_mode == 1:
        start_screen_menu = cv.imread('Contents/Review.png')
    elif start_screen_mode == 2:
        start_screen_menu = cv.imread('Contents/settings.png')
    elif start_screen_mode == 3:
        start_screen_menu = cv.imread('Contents/restart.png')
    
print("going to main screen")
time.sleep(0.1)

lattitude = []
longitude = []
gps_count = 0

while True:
    gps.update()
    gps_map = cv.imread('gps_plots/out.png')
    current = time.monotonic()
    if current - last_print >= 0.2:
        last_print = current
    
    if not gps.has_fix:
        # Try again if we don't have a fix yet.
        print('Waiting for fix...')
        #continue
    
    # Shut down the stream when button 0 is pressed
    if base.buttons[0].read() == 1:
        print('Closing HDMI ...')
        hdmi_out.close()
        hdmi_in.close()
        print("Closed HDMI. Deleting HDMI ...")
        del hdmi_out, hdmi_in
        break

    new_frame = hdmi_in.readframe()    

    if gps.speed_knots is not None:
        speed_mph = round(gps.speed_knots * 1.151, 3)


    #GPS modules
    lattitude.append(gps.latitude)
    longitude.append(gps.longitude)
    
    # Update GPS plot every 60th iteration. Put this in a thread later
    gps_count = gps_count + 1
    if gps_count % 60 == 0:
        plt.clf()
        plt.plot(lattitude, longitude, color='#1f07d9', linewidth=3)
        if gps.latitude == None and gps.longitude == None:
            continue
        else:
            plt.plot(gps.latitude, gps.longitude, marker='o', markerfacecolor='red', markersize=12)
        plt.axis('off')
        fig.savefig('gps_plots/out.png', bbox_inches='tight',transparent=True, pad_inches=0)
    
    print('after if')
    y1, y2 = gauge_y_offset, gauge_y_offset + gauge.shape[0]
    x1, x2 = gauge_x_offset, gauge_x_offset + gauge.shape[1]
    
    # Take out the unwanted black background pixels 
    alpha_s = gauge[:, :, 3] / 255.0
    alpha_l = 1.0 - alpha_s
    for c in range(0, 3):
        new_frame[y1:y2, x1:x2, c] = (alpha_s * gauge[:, :, c] + alpha_l * new_frame[y1:y2, x1:x2, c])
    
    # Update frames with overlays
    new_frame[gps_y_offset:gps_y_offset+gps_map.shape[0], gps_x_offset:gps_x_offset+gps_map.shape[1]] = gps_map
    write_frame = cv.putText(new_frame, str(speed_mph), (200, 550),fontFace=cv.FONT_ITALIC, fontScale=1, color=(2, 154, 242))
    hdmi_out.writeframe(write_frame)
    
    if not init:
        init = True
        print("Frames are ready")   

print("Break out the loop")
