# -*- coding: utf-8 -*-
"""
Read functions for measurement values of the EE895 Sensor via I2c interface.

Copyright 2023 E+E Elektronik Ges.m.b.H.

Disclaimer:
This application example is non-binding and does not claim to be complete with
regard to configuration and equipment as well as all eventualities. The
application example is intended to provide assistance with the EE895 sensor
module design-in and is provided "as is".You yourself are responsible for the
proper operation of the products described. This application example does not
release you from the obligation to handle the product safely during
application, installation, operation and maintenance. By using this application
example, you acknowledge that we cannot be held liable for any damage beyond
the liability regulations described.

We reserve the right to make changes to this application example at any time
without notice. In case of discrepancies between the suggestions in this
application example and other E+E publications, such as catalogues, the content
of the other documentation takes precedence. We assume no liability for
the information contained in this document.
"""


# pylint: disable=E0401
from smbus2 import SMBus, i2c_msg
import numpy as np
# pylint: enable=E0401
CRC16_ONEWIRE_START = 0xFFFF
FUNCTION_CODE_READ_REGISTER = 0x03
FUNCTION_CODE_WRITE_REGISTER = 0x06
READ_ALL_MEASUREMENTS = 0x00
USER_REGISTER_1 = 0x16A8
USER_REGISTER_2 = 0x16A9
REGISTER_TEMPERATURE_CELSIUS = 0x03EA
REGISTER_TEMPERATURE_FAHRENHEIT = 0x03EC
REGISTER_TEMPERATURE_KELVIN = 0x03F0
REGISTER_CO2_AVERAGE_PC = 0x0424  # PC = pressure compensated
REGISTER_CO2_RAW_PC = 0x0426  # PC = pressure compensated
REGISTER_CO2_AVERAGE_NPC = 0x0428  # NPC = no pressure compensated
REGISTER_CO2_RAW_NPC = 0x042A  # NPC = no pressure compensated
REGISTER_PRESSURE_MBAR = 0x04B0
REGISTER_PRESSURE_PSI = 0x04B2
REGISTER_SERIAL_NUMBER = 0x0000
REGISTER_FIRMWARE_VERSION = 0x0008
REGISTER_SENSORNAME = 0x0009
REGISTER_MEASURING_MODE = 0x01F8
REGISTER_MEASURING_STATUS = 0x01F9
REGISTER_MEASURING_TRIGGER = 0x01FA
REGISTER_DETAILED_STATUS = 0x0258
REGISTER_CO2_MEASURING_INTERVAL = 0x1450
REGISTER_CO2_FILTER_COEFFICIENT = 0x1451
REGISTER_CO2_CUSTOMER_OFFSET = 0x1452


def get_status_string(status_code):
    """Return string from status_code."""
    status_string = {
        0: "Success",
        1: "Not acknowledge error",
        2: "Checksum error",
        3: "something went wrong when changing the register",
        4: "error wrong input for change_co2_measuring_interval",
        5: "error wrong input for change_co2_filter_coefficient",
    }

    if status_code < len(status_string):
        return status_string[status_code]
    return "Unknown error"


def calc_crc16(buf, end):
    ''' calculate crc16 checksum  '''
    buf.insert(0, 0x5F)
    crc = CRC16_ONEWIRE_START
    for j in range(end):
        crc ^= buf[j]
        for _ in range(8, 0, -1):
            if (crc & 0x0001) != 0:
                crc = crc >> 1
                crc ^= 0xA001
            else:
                crc = crc >> 1
    buf.pop(0)
    return crc


def convert_to_number(number):
    """convert the binary code to a float"""
    count = -1
    mantissa = 0
    for i in range(22, 0, -1):
        mantissa += (((number >> i) & 0x01) * pow(2, count))
        count -= 1
    return mantissa + 1


def IEEE754(buf):
    """convert IEEE754 standard to a float"""
    sign = buf[2] >> 7
    if sign:
        sign = -1
    else:
        sign = 1
    biased_exponent = (((buf[2] & 0x7F) << 1) + (buf[3] >> 7))
    bias_value = 127
    exponent = biased_exponent - bias_value
    mantissa = (buf[3] & 0x7F) * 65536 + buf[0] * 256 + buf[1]
    mantissa = convert_to_number(mantissa)
    result = sign * mantissa * pow(2, exponent)
    return result


class EE895():
    """Implements communication with EE895 over i2c with a specific address."""

    def __init__(self):
        self.i2c_address = 0x5F
    
    def get_all_measurements(self):
        """get allt the Measurments from the Sensor with i2c simplified"""
        write_command = i2c_msg.write(0x5E, [0x00])
        read_command = i2c_msg.read(0x5E, 8)
        with SMBus(1) as ee895_communication:
            ee895_communication.i2c_rdwr(write_command, read_command)
        i2c_response = list(read_command)
        temperature = ((i2c_response[2] << 8) + i2c_response[3]) / 100
        co2 = (i2c_response[0] << 8) + i2c_response[1]
        pressure = ((i2c_response[6] << 8) + i2c_response[7]) / 10
        return temperature, co2, pressure
    
    def get_temp_c(self):
        """get the temperature in celsius"""
        i2c_response = self.read_bytes_from_register(REGISTER_TEMPERATURE_CELSIUS,
                                                0x02, 8)
        temperature = IEEE754([i2c_response[2], i2c_response[3],
                               i2c_response[4], i2c_response[5]])
        return temperature

    def get_temp_f(self):
        """get the temperature in fahrenheit"""
        i2c_response = self.read_bytes_from_register(
            REGISTER_TEMPERATURE_FAHRENHEIT, 0x02, 8)
        temperature = IEEE754([i2c_response[2], i2c_response[3],
                               i2c_response[4], i2c_response[5]])
        return temperature

    def get_temp_k(self):
        """get the temperature in Kelvin"""
        i2c_response = self.read_bytes_from_register(
            REGISTER_TEMPERATURE_KELVIN, 0x02, 8)
        temperature = IEEE754([i2c_response[2], i2c_response[3],
                               i2c_response[4], i2c_response[5]])
        return temperature

    def get_co2_aver_with_pc(self):
        """get the co2 value in average mode with pressure compenstaion"""
        i2c_response = self.read_bytes_from_register(
            REGISTER_CO2_AVERAGE_PC, 0x02, 8)
        co2 = IEEE754([i2c_response[2], i2c_response[3],
                       i2c_response[4], i2c_response[5]])
        return co2

    def get_co2_raw_with_pc(self):
        """get the co2 value raw with pressure compenstaion"""
        i2c_response = self.read_bytes_from_register(
            REGISTER_CO2_RAW_PC, 0x02, 8)
        co2 = IEEE754([i2c_response[2], i2c_response[3],
                       i2c_response[4], i2c_response[5]])
        return co2

    def get_co2_aver_with_npc(self):
        """get the co2 value in average mode with no pressure compenstaion"""
        i2c_response = self.read_bytes_from_register(
            REGISTER_CO2_AVERAGE_NPC, 0x02, 8)
        co2 = IEEE754([i2c_response[2], i2c_response[3],
                       i2c_response[4], i2c_response[5]])
        return co2

    def get_co2_raw_with_npc(self):
        """get the co2 value raw with no pressure compenstaion"""
        i2c_response = read_bytes_from_register(
            REGISTER_CO2_RAW_NPC, 0x02, 8)
        co2 = IEEE754([i2c_response[2], i2c_response[3],
                       i2c_response[4], i2c_response[5]])
        return co2

    def get_pressure_mbar(self):
        """get the pressure value in mbar"""
        i2c_response = self.read_bytes_from_register(
            REGISTER_PRESSURE_MBAR, 0x02, 8)
        pressure = IEEE754([i2c_response[2], i2c_response[3],
                            i2c_response[4], i2c_response[5]])
        return pressure

    def get_pressure_psi(self):
        """get the pressure value in psi"""
        i2c_response = self.read_bytes_from_register(
            REGISTER_PRESSURE_PSI, 0x02, 8)
        pressure = IEEE754([i2c_response[2], i2c_response[3],
                            i2c_response[4], i2c_response[5]])
        return pressure

    def read_serial_number(self):
        """get the serial number"""
        i2c_response = self.read_bytes_from_register(
            REGISTER_SERIAL_NUMBER, 0x08, 20)
        i2c_response.pop(0)
        i2c_response.pop(0)
        i2c_response.pop(17)
        i2c_response.pop(16)
        return i2c_response

    def read_firmware_version(self):
        """get the firmware version"""
        i2c_response = self.read_bytes_from_register(
            REGISTER_FIRMWARE_VERSION, 0x01, 6)
        i2c_response.pop(0)
        i2c_response.pop(0)
        i2c_response.pop(3)
        i2c_response.pop(2)
        return i2c_response

    def read_sensor_name(self):
        """get the sensor name"""
        i2c_response = self.read_bytes_from_register(
            REGISTER_SENSORNAME, 0x08, 20)
        i2c_response.pop(0)
        i2c_response.pop(0)
        i2c_response.pop(17)
        i2c_response.pop(16)
        return i2c_response

    def read_measuring_mode(self):
        """read the measuring mode, 0 => continuous mode, 1 => single shot"""
        i2c_response = self.read_bytes_from_register(
            REGISTER_MEASURING_MODE, 0x01, 6)
        return i2c_response[3] & 0x01

    def change_measuring_mode(self, measuring_mode):
        """change the measuring mode, 0 => continuous mode, 1 => single shot"""
        self.write_to_register(REGISTER_MEASURING_MODE, [0x00, measuring_mode])

    def data_ready(self):
        """shows if the data is ready to be read"""
        i2c_response = self.read_bytes_from_register(
            REGISTER_MEASURING_STATUS, 0x01, 6)
        return i2c_response[3] & 0x01

    def trigger_ready(self):
        """shows if the trigger is ready"""
        i2c_response = self.read_bytes_from_register(
            REGISTER_MEASURING_STATUS, 0x01, 6)
        return (i2c_response[3] & 0x02) >> 1

    def trigger_new_measurement(self):
        """triggers a new measuremnet, but only in single shot mode"""
        self.write_to_register(REGISTER_MEASURING_TRIGGER, [0x00, 0x01])

    def status_details(self):
        """ Bit 0 = Co2 measurment too high, Bit 1 = Co2 measurment too low,
        Bit 2 = T measurement too high, Bit 3 = T measurement too low
        Bit 6 = p measurement too high, Bit 7 p measurement too low"""
        i2c_response = self.read_bytes_from_register(
            REGISTER_DETAILED_STATUS, 0x01, 6)
        return i2c_response[3]

    def change_co2_measuring_interval(self, measuring_interval):
        """change the measuring interval of the sensor in continuous mode"""
        if 36001 > measuring_interval & measuring_interval > 99:
            self.write_to_register(REGISTER_CO2_MEASURING_INTERVAL,
                              [np.uint8(measuring_interval / 256),
                               np.uint8(measuring_interval % 256)])
        else:
            raise Warning(get_status_string(4))

    def read_co2_measuring_interval(self):
        """read the measuring interval of the sensor in continuous mode"""
        i2c_response = self.read_bytes_from_register(
            REGISTER_CO2_MEASURING_INTERVAL, 0x01, 6)
        return (i2c_response[2] << 8) + i2c_response[3]

    def change_co2_filter_coefficient(self, filter_coefficient):
        """change the filter coefficient of the sensor"""
        if 21 > filter_coefficient & filter_coefficient > 0:
            self.write_to_register(REGISTER_CO2_FILTER_COEFFICIENT,
                              [0x00, filter_coefficient])
        else:
            raise Warning(get_status_string(5))

    def read_co2_filter_coefficient(self):
        """read the filter coefficient of the sensor"""
        i2c_response = self.read_bytes_from_register(
            REGISTER_CO2_FILTER_COEFFICIENT, 0x01, 6)
        return (i2c_response[2] << 8) + i2c_response[3]

    def change_co2_custom_offset(self, custom_offset):
        """change the customer offset of the sensor for co2"""
        buf = np.uint16(custom_offset)
        self.write_to_register(REGISTER_CO2_CUSTOMER_OFFSET,
                          [np.uint8(buf / 256), np.uint8(buf % 256)])

    def read_co2_custom_offset(self):
        """read the customer offset of the sensor for co2"""
        i2c_response = self.read_bytes_from_register(
            REGISTER_CO2_CUSTOMER_OFFSET, 0x01, 6)
        buf = np.int16((i2c_response[2] << 8) + i2c_response[3])
        return buf

    def change_customer_register1(self, customer_register):
        """since firmware version 1.1.1, registers reserved
        for any customer use, e.g. serial number, traceability, etc."""
        self.write_to_register(USER_REGISTER_1, [(customer_register >> 8),
                                            (customer_register and 0xFF)])

    def read_customer_register1(self):
        """since firmware version 1.1.1, registers reserved
        for any customer use, e.g. serial number, traceability, etc."""
        i2c_response = self.read_bytes_from_register(USER_REGISTER_1, 0x01, 6)
        return (i2c_response[2] << 8) + i2c_response[3]

    def change_customer_register2(self, customer_register):
        """since firmware version 1.1.1, registers reserved
        for any customer use, e.g. serial number, traceability, etc."""
        self.write_to_register(USER_REGISTER_2, [(customer_register >> 8),
                                            (customer_register and 0xFF)])

    def read_customer_register2(self):
        """since firmware version 1.1.1, registers reserved
        for any customer use, e.g. serial number, traceability, etc."""
        i2c_response = self.read_bytes_from_register(USER_REGISTER_2, 0x01, 6)
        return (i2c_response[2] << 8) + i2c_response[3]

    def read_bytes_from_register(self, register_address, register_to_read, bytes_to_read):
        """ read bytes from the register addrdss"""
        command = [FUNCTION_CODE_READ_REGISTER, (register_address >> 8),
                   (register_address & 0xFF), (register_to_read >> 8),
                   (register_to_read & 0xFF)]
        crc = calc_crc16(command, 6)
        command.append(crc & 0xFF)
        command.append(crc >> 8)
        i2c_response = self.wire_write_read(command, bytes_to_read)
        crc_check = i2c_response[bytes_to_read - 1] * 256 + i2c_response[bytes_to_read - 2]
        if (crc_check - calc_crc16(i2c_response, (bytes_to_read - 1))) == 0:
            return i2c_response
        else:
            raise Warning(get_status_string(2))

    def write_to_register(self, register_address, bytes_to_write):
        """writes 2 uint8_t to the register address"""
        command = [FUNCTION_CODE_WRITE_REGISTER, (register_address >> 8),
                   (register_address & 0xFF), (bytes_to_write[0]),
                   (bytes_to_write[1])]
        crc = calc_crc16(command, 6)
        command.append(crc & 0xFF)
        command.append(crc >> 8)
        i2c_response = self.wire_write_read(command, 7)
        if command == i2c_response:
            return
        else:
            raise Warning(get_status_string(3))

    def wire_write_read(self,  buf, receiving_bytes):
        """write a command to the sensor to get different answers like temperature values,..."""
        write_command = i2c_msg.write(self.i2c_address, buf)
        read_command = i2c_msg.read(self.i2c_address, receiving_bytes)
        with SMBus(1) as ee895_communication:
            ee895_communication.i2c_rdwr(write_command, read_command)
        return list(read_command)
