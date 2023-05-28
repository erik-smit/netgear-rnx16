from readynas_oled import *
import sys
import time

init_oled()

output = " ".join(sys.argv[1:])

for char in output:
  oled_data_write(char)

#start_scroll_right()

# config = gpiod.line_request()
# config.consumer = "Erik"
# config.request_type = gpiod.line_request.DIRECTION_OUTPUT



