# netgear-rnx16

Here is some bits and bobs about my use of a Netgear RN516 with Proxmox.  
Mostly involves how to use the non-standard components under Linux.

[oled-PoC](oled-PoC) is my proof-of-concept for the oled in the frontpanel  
[zfs-zed.d-script](zfs-zed.d-script) interfaces zfs zed.d with ledmon  
[lcdproc-RNx16](https://github.com/erik-smit/lcdproc-RNx16) contains my driver for LCDproc for the SSD1306 OLED panel

# oled

| SPI  | GPIO | MUX |
|------|------|-----|
| SDIN | GPIO54 | REQ3# |
| SCLK | GPIO52 | REQ2# |
| DC | GPIO32 | NO |
| CS | GPIO50 | REQ1# |
| CTRL | GPIO6 | TACH2 |
| RESET | GPIO7 | TACH3 |
