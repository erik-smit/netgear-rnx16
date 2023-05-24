from readynas_oled import *

init_oled()

import time
#time.sleep(5)

for char in "Erik love Renata":
  oled_data_write(char)
  #time.sleep(1)

#clear_oled(True)

start_scroll_right()

# config = gpiod.line_request()
# config.consumer = "Erik"
# config.request_type = gpiod.line_request.DIRECTION_OUTPUT



