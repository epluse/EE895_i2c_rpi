# -*- coding: utf-8 -*-
"""
Example script reading measurement values from the EE895 sensor via I2C interface.

Copyright 2023 E+E Elektronik Ges.m.b.H.

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

import time
from ee895_i2c_library import EE895

CSV_DELIMETER = ","

EE_895 = EE895()


try:
    # read device serial number
    print("serial number: " + ''.join('{:02x}'.format(x) for x in EE_895.read_serial_number()))
    # read device Firmware Version
    print("Firmware Version: " + '.'.join('{:01d}'.format(x) for x in EE_895.read_firmware_version()))
    # read device name
    print("Sensor name: " + ''.join('{:c}'.format(x) for x in EE_895.read_sensor_name())) 
    # change Measuring mode
    EE_895.change_measuring_mode(1)
    # read Measuring mode
    print("Measuring mode: " + str(EE_895.read_measuring_mode()))
    # change Custom offset
    EE_895.change_co2_custom_offset(0)
    # read Custom offset mode
    print("Custom co2 offset: " + str(EE_895.read_co2_custom_offset()))

except Warning as exception:
    print("Exception: " + str(exception))

# print a header
print("temperarture",CSV_DELIMETER,"CO2",CSV_DELIMETER,"pressure")
time.sleep(1)

for i in range(30):
    try:
        EE_895.trigger_new_measurement()
        temperature = EE_895.get_temp_c()
        co2 = EE_895.get_co2_aver_with_pc()
        pressure = EE_895.get_pressure_mbar()
        print('%0.2f °C' % temperature, CSV_DELIMETER, end="")
        print('%0.0f ppm' % co2, CSV_DELIMETER, end="")
        print('%0.1f mbar' % pressure)
    except Warning as exception:
        print("Exception: " + str(exception))

    finally:
        time.sleep(15)
