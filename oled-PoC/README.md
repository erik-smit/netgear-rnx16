#

This is a Proof-of-Concept to see if I can interface with the RNx16 OLED display from Linux.

# Kernel
```
[    1.170446] ACPI Warning: SystemIO range 0x0000000000000500-0x000000000000052F conflicts with OpRegion 0x0000000000000500-0x0000000000000563 (\GPIO) (20210730/utaddress-204)
[    1.170451] ACPI: OSL: Resource conflict; ACPI support missing from driver?
[    1.170452] lpc_ich: Resource conflict(s) found affecting gpio_ich
```

Needed to add `acpi_enforce_resources=lax` to kernel

# Usage
```
# python3 test.py "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef"
#
```

# Example
![Alt text](rnx16-oled-small.jpg?raw=true "rnx16 frontpanel oled")
