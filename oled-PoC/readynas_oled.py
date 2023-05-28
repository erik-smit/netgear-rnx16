import gpiod
import math
import time
from rnx16_font import rnx16_font as font

chip = gpiod.Chip('gpiochip0')

gpios = {
    "sdin": chip.get_line(54),
    "sclk": chip.get_line(52),
    "dc": chip.get_line(32),
    "cs": chip.get_line(50),
    "ctrl": chip.get_line(6),
    "reset": chip.get_line(7),
}

OLED_X_OFFSET = 4
OLED_COLS = 16
OLED_ROWS = 2

oled_row = 0
oled_col = 0

for _name, gpio in gpios.items():
    gpio.request(consumer="erik", type=gpiod.LINE_REQ_DIR_OUT)

def spi_send(c, cmd: bool):
    # print(f'0x{c:02x}')
    gpios["cs"].set_value(0)
    gpios["dc"].set_value(0 if cmd else 1)

    for bit in [7,6,5,4,3,2,1,0]:
        mask = 2**bit
        gpios["sclk"].set_value(0)
        gpios["sdin"].set_value(1 if (c & 2**bit) else 0)
        gpios["sclk"].set_value(1)

    gpios["cs"].set_value(1)
    gpios["dc"].set_value(1)

def spi_send_data(d):
    spi_send(d, False)

def spi_send_cmd(c):
    spi_send(c, True)

def clear_oled(sleepy: bool = False):
    spi_send_cmd(0x40) # Start position

    for page in range(0,4):
        gpios["cs"].set_value(0)
        gpios["dc"].set_value(0)
        spi_send_cmd(SSD1306_B0_SET_PAGE_START + page)
        spi_send_cmd(0x10)
        spi_send_cmd(OLED_X_OFFSET)
        gpios["dc"].set_value(1)

        for col in range(0,128):
            spi_send_data(0x0)

    oled_return_home()

def oled_return_home():
    oled_set_cursor_pos(0,0)

def oled_set_cursor_pos(row, col):
    global oled_row
    global oled_col
    oled_row = min(row, 1)
    oled_col = min(col, OLED_COLS)

def oled_data_write(c):
    global oled_row
    global oled_col

    cg = font[c]
    xpix = oled_col * 8 + OLED_X_OFFSET
    page = 0

    spi_send_cmd(SSD1306_A6_NORMAL_DISPLAY)
    spi_send_cmd(SSD1306_40_SET_START_LINE) # Start line

    # line1: page 0,1  line 2: page 2,3
    # one char takes 2 page 16 pbits height
    for page in [0,1]:
        gpios["cs"].set_value(0)
        gpios["dc"].set_value(0)

        spi_send_cmd(SSD1306_B0_SET_PAGE_START + oled_row * 2 + page)
        spi_send_cmd((xpix >> 4) | SSD1306_10_SET_HIGHER_COLUMN)
        spi_send_cmd( xpix & 0xf)

        gpios["dc"].set_value(1)

        for i in range(0, 8):
            raster = cg[page * 8 + i]
            # if (ord(c) != 0xff and (ord(c) & 0x80)):
            #     raster ^= ~0
            spi_send_data(raster)

    oled_shift_cursor(True)

def oled_shift_cursor(right: bool):
    global oled_row
    global oled_col

    if right:
        if (oled_col < OLED_COLS and oled_row < OLED_ROWS):
            oled_col += 1
            oled_row += math.floor(oled_col / OLED_COLS)
            oled_col %= OLED_COLS
    else:
        if (oled_col > 0):
            oled_col -= 1
        elif (oled_row > 0):
            oled_col = OLED_COLS - 1
            oled_row = 0


SSD1306_00_COMMAND = 0x00
SSD1306_C0_DATA = 0xC0
SSD1306_40_DATA_CONTINUE = 0x40

SSD1306_81_SET_CONTRAST_CONTROL = 0x81
SSD1306_A4_DISPLAY_ALL_ON_RESUME = 0xA4
SSD1306_A5_DISPLAY_ALL_ON = 0xA5
SSD1306_A6_NORMAL_DISPLAY = 0xA6
SSD1306_A7_INVERT_DISPLAY = 0xA7
SSD1306_AE_DISPLAY_OFF = 0xAE
SSD1306_AF_DISPLAY_ON = 0xAF
SSD1306_E3_NOP = 0xE3
SSD1306_26_HORIZONTAL_SCROLL_RIGHT = 0x26
SSD1306_27_HORIZONTAL_SCROLL_LEFT = 0x27
SSD1306_29_HORIZONTAL_SCROLL_VERTICAL_AND_RIGHT = 0x29
SSD1306_2A_HORIZONTAL_SCROLL_VERTICAL_AND_LEFT = 0x2A
SSD1306_2E_DEACTIVATE_SCROLL = 0x2E
SSD1306_2F_ACTIVATE_SCROLL = 0x2F
SSD1306_A3_SET_VERTICAL_SCROLL_AREA = 0xA3
SSD1306_00_SET_LOWER_COLUMN = 0x00
SSD1306_10_SET_HIGHER_COLUMN = 0x10
SSD1306_20_MEMORY_ADDR_MODE = 0x20
SSD1306_21_SET_COLUMN_ADDR = 0x21
SSD1306_22_SET_PAGE_ADDR = 0x22
SSD1306_40_SET_START_LINE = 0x40
SSD1306_A0_SET_SEGMENT_REMAP = 0xA0
SSD1306_A8_SET_MULTIPLEX_RATIO = 0xA8
SSD1306_B0_SET_PAGE_START = 0xB0
SSD1306_C0_COM_SCAN_DIR_INC = 0xC0
SSD1306_C8_COM_SCAN_DIR_DEC = 0xC8
SSD1306_D3_SET_DISPLAY_OFFSET = 0xD3
SSD1306_DA_SET_COM_PINS = 0xDA
SSD1306_8D_CHARGE_PUMP = 0x8D
SSD1306_D5_SET_DISPLAY_CLOCK_DIV_RATIO = 0xD5
SSD1306_D9_SET_PRECHARGE_PERIOD = 0xD9
SSD1306_DB_SET_VCOM_DESELECT = 0xDB


def init_oled():
    oled_init_cmd = [
                SSD1306_AE_DISPLAY_OFF,   # Turn off display. */
                SSD1306_D5_SET_DISPLAY_CLOCK_DIV_RATIO,   # Display ClocDivide Ratio/Oscillator Frequency */
                0x71,   # to 105Hz. */
                SSD1306_A8_SET_MULTIPLEX_RATIO,   # Multiplex Ratio */
                0x1f,   # to 32mux. */
                SSD1306_D9_SET_PRECHARGE_PERIOD,   # Precharge period. */
                SSD1306_20_MEMORY_ADDR_MODE,   # Memory addressing mode. */
                0xa1,   # Seg re-map 127->0. */
                SSD1306_C8_COM_SCAN_DIR_DEC,   # COM scan direction COM(N-1)-->COM0. */
                SSD1306_DA_SET_COM_PINS,   # COM pins hardware configuration. */
                0xd8,   # Color_mode_set */
                0x00,   # to monochrome mode & normal power mode. */
                SSD1306_81_SET_CONTRAST_CONTROL,   # Contrast control. */
                SSD1306_B0_SET_PAGE_START,   # Page start address for page Addressing mode. */
                SSD1306_D3_SET_DISPLAY_OFFSET,   # Display offset. */
                0x00,
                SSD1306_21_SET_COLUMN_ADDR,   # Column address. */
                OLED_X_OFFSET,          # Colum address start. */
                0x7f+OLED_X_OFFSET,     # Colum address end. */
                SSD1306_22_SET_PAGE_ADDR,   # Page address. */
                0x00,   # Page address start. */
                0x03,   # Page address end. */
                SSD1306_10_SET_HIGHER_COLUMN,   # Higher column start addr for page addressing mode. */
                SSD1306_00_SET_LOWER_COLUMN,   # Lower column start addr for page addressing mode. */
                SSD1306_40_SET_START_LINE,   # Display start line */
                SSD1306_A6_NORMAL_DISPLAY,   # Normal (non-inverted). */
                SSD1306_A4_DISPLAY_ALL_ON_RESUME,   # Entire display Off. */
                SSD1306_DB_SET_VCOM_DESELECT,   # VCOMH Level */
                0x18,   # to 0.83*VCC 0x3c, change from 0x20 to 0x18 avoid power peek issue. */        
    ]

    gpios["reset"].set_value(0)
    time.sleep(0.1) # L pulse > 3us
    gpios["reset"].set_value(1)
    time.sleep(0.1)

    for cmd in oled_init_cmd:
        spi_send_cmd(cmd)

    clear_oled()
    gpios["ctrl"].set_value(1)

    oled_backlight_on(True)

def cont_vert_scroll():
    oled_scroll_cmd = [
        SSD1306_29_HORIZONTAL_SCROLL_VERTICAL_AND_RIGHT,
        0x00, # dummy
        0x00, # start page
        0x00, # time interval
        0x01, # page f end

        0x01, # vertical scrolling
#        0xff,
        SSD1306_2F_ACTIVATE_SCROLL
    ]

    for cmd in oled_scroll_cmd:
        spi_send_cmd(cmd)

def horizontal_scroll():
    oled_scroll_cmd = [
        SSD1306_26_HORIZONTAL_SCROLL_RIGHT,
        0x00, # dummy
        0x00, # start page
        0x06, # time interval
        0x07, # page end
        0x00, # dummy
        0xff, # dummy
        SSD1306_2F_ACTIVATE_SCROLL
    ]

    for cmd in oled_scroll_cmd:
        spi_send_cmd(cmd)

def reset_oled():
    gpios["reset"].set_value(0)
    time.sleep(0.1) # L pulse > 3us
    gpios["reset"].set_value(1)
    time.sleep(0.1)

def oled_backlight_on(on: bool):
    spi_send_cmd(0xaf if on else 0xae)

import gpiod

class OLEDController:
    def __init__(self):
        self.gpios = {}
        self.oled_row = 0
        self.oled_col = 0
        self.font = {
            ' ': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            '!': [0x00, 0x00, 0x00, 0xf8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x33, 0x30, 0x00, 0x00, 0x00],
            # ...
            # Add remaining characters from the font dictionary here
            # ...
        }
        self._initialize_gpios()

    def _initialize_gpios(self):
        chip = gpiod.Chip('gpiochip0')
        gpio_lines = {
            "sdin": 54,
            "sclk": 52,
            "dc": 32,
            "cs": 50,
            "ctrl": 6,
            "reset": 7,
        }
        for name, line_number in gpio_lines.items():
            line = chip.get_line(line_number)
            line.request(consumer="erik", type=gpiod.LINE_REQ_DIR_OUT)
            self.gpios[name] = line

    def spi_send(self, c, cmd):
        # print(f'0x{c:02x}')
        self.gpios["cs"].set_value(0)
        self.gpios["dc"].set_value(0 if cmd else 1)

        for bit in [7, 6, 5, 4, 3, 2, 1, 0]:
            mask = 2 ** bit
            self.gpios["sclk"].set_value(0)
            self.gpios["sdin"].set_value(1 if (c & mask) else 0)
            self.gpios["sclk"].set_value(1)

        self.gpios["cs"].set_value(1)
        self.gpios["dc"].set_value(1)

    def spi_send_data(self, d):
        self.spi_send(d, False)

    def spi_send_cmd(self, c):
        self.spi_send(c, True)

    def clear_oled(self, sleepy=False):
        spi_send_cmd(0x40)  # Start position

        for page in range(0, 4):
            self.gpios["cs"].set_value(0)
            self.gpios["dc"].set_value(0)
            spi_send_cmd(SSD1306_B0_SET_PAGE_START + page)
            spi_send_cmd(0x10)
            spi_send_cmd(OLED_X_OFFSET)
            self.gpios["dc"].set_value(1)

            for col in range(0, 128):
                spi_send_data(0x0)

        self.oled_return_home()

    def oled_return_home(self):
        self.oled_set_cursor_pos(0, 0)

    def oled_set_cursor_pos(self, row, col):
        self.oled_row = min(row, 1)
        self.oled_col = min(col, OLED_COLS)