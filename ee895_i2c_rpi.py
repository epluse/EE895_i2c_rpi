# -*- coding: utf-8 -*-
"""
Example script reading measurement values from the EE895 sensor via I2C interface.

Copyright 2021 E+E Elektronik Ges.m.b.H.

Disclaimer:
This application example is non-binding and does not claim to be complete with regard
to configuration and equipment as well as all eventualities. The application example
is intended to provide assistance with the EE895 sensor module design-in and is provided "as is".
You yourself are responsible for the proper operation of the products described.
This application example does not release you from the obligation to handle the product safely
during application, installation, operation and maintenance. By using this application example,
you acknowledge that we cannot be held liable for any damage beyond the liability regulations
described.

We reserve the right to make changes to this application example at any time without notice.
In case of discrepancies between the suggestions in this application example and other E+E
publications, such as catalogues, the content of the other documentation takes precedence.
We assume no liability for the information contained in this document.
"""

from smbus2 import SMBus, i2c_msg

ADDRESS = 0x5E
CSV_DELIMETER = ","

# print a header
print("temperarture",CSV_DELIMETER,"CO2",CSV_DELIMETER,"pressure")

write_command = i2c_msg.write(ADDRESS, [0x00])
read_command = i2c_msg.read(ADDRESS, 8)

with SMBus(1) as ee895:                   #creating an I2C instance and opening the bus
    ee895.i2c_rdwr(write_command)         #Command obtain data for temperature and humidity
    ee895.i2c_rdwr(read_command)          #for more information check data sheet
    reading = list(read_command)

    temperature = ((reading[2] << 8) + reading[3]) / 100
    print('%0.2f °C' % temperature, CSV_DELIMETER, end="")
    co2 = (reading[0] << 8) + reading[1]
    print('%0.0f ppm' % co2, CSV_DELIMETER, end="")
    pressure = ((reading[6] << 8) + reading[7]) / 10
    print('%0.1f mbar' % pressure)
