# -*- coding: utf-8 -*-
"""
Read functions for measurement values of the EE895 Sensor via I2c interface.

Copyright 2022 E+E Elektronik Ges.m.b.H.

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


# pylint: disable=E0401
from smbus2 import SMBus, i2c_msg
import numpy as np
# pylint: enable=E0401
CRC16_ONEWIRE_START = 0xFFFF


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
        for _ in range(8,0,-1):
            if (crc & 0x0001) != 0:
                crc = crc >> 1
                crc ^= 0xA001
            else:
                crc = crc >> 1
    buf.pop(0)
    return crc


def convert_to_number(m):
    """convert the binary code to a float"""
    count = -1
    mantissa = 0
    for i in range(22, 0, -1):
        mantissa += (((m >> i) & 0x01) * pow(2, count))
        count -= 1
    return (mantissa + 1)


def IEEE754(buf):
    """convert IEEE754 standard to a float"""
    s = buf[2] >> 7
    if(s):
        s = -1
    else:
        s = 1
    E = (((buf[2] & 0x7F) << 1) + (buf[3] >> 7))
    B = 127
    e = E - B
    m = (buf[3] & 0x7F) * 65536 + buf[0] * 256 + buf[1]
    m = convert_to_number(m)
    x = s * m * pow(2, e)
    return x


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
        i2c_response = self.wire_write_read([0x03, 0x03, 0xEA, 0x00, 0x02, 0xE8, 0xC5], 8)
        crc_check = i2c_response[7] * 256 + i2c_response[6]
        if (crc_check - calc_crc16(i2c_response, 7)) == 0:
            temperature = IEEE754([i2c_response[2], i2c_response[3], i2c_response[4], i2c_response[5]])
            return temperature
        else:
            raise Warning(get_status_string(2))

    def get_temp_f(self):
        """get the temperature in fahrenheit"""
        i2c_response = self.wire_write_read([0x03, 0x03, 0xEC, 0x00, 0x02, 0x08, 0xC4], 8)
        crc_check = i2c_response[7] * 256 + i2c_response[6]
        if crc_check - calc_crc16(i2c_response, 7) == 0:
            temperature = IEEE754([i2c_response[2], i2c_response[3], i2c_response[4], i2c_response[5]])
            return temperature
        else:
            raise Warning(get_status_string(2))

    def get_temp_K(self):
        """get the temperature in Kelvin"""
        i2c_response = self.wire_write_read([0x03, 0x03, 0xF0, 0x00, 0x02, 0xC9, 0x02], 8)
        crc_check = i2c_response[7] * 256 + i2c_response[6]
        if crc_check - calc_crc16(i2c_response, 7) == 0:
            temperature = IEEE754([i2c_response[2], i2c_response[3], i2c_response[4], i2c_response[5]])
            return temperature
        else:
            raise Warning(get_status_string(2))

    def get_co2_aver_with_pc(self):
        """get the co2 value in average mode with pressure compenstaion"""
        i2c_response = self.wire_write_read([0x03, 0x04, 0x24, 0x00, 0x02, 0x88, 0x4E], 8)
        crc_check = i2c_response[7] * 256 + i2c_response[6]
        if crc_check == calc_crc16(i2c_response, 7):
            co2 = IEEE754([i2c_response[2], i2c_response[3], i2c_response[4], i2c_response[5]])
            return co2
        else:
            raise Warning(get_status_string(2))

    def get_co2_raw_with_pc(self):
        """get the co2 value raw with pressure compenstaion"""
        i2c_response = self.wire_write_read([0x03, 0x04, 0x26, 0x00, 0x02, 0x29, 0x8E], 8)
        crc_check = i2c_response[7] * 256 + i2c_response[6]
        if crc_check == calc_crc16(i2c_response, 7):
            co2 = IEEE754([i2c_response[2], i2c_response[3], i2c_response[4], i2c_response[5]])
            return co2
        else:
            raise Warning(get_status_string(2))

    def get_co2_aver_with_npc(self):
        """get the co2 value in average mode with no pressure compenstaion"""
        i2c_response = self.wire_write_read([0x03, 0x04, 0x28, 0x00, 0x02, 0x48, 0x4D], 8)
        crc_check = i2c_response[7] * 256 + i2c_response[6]
        if crc_check == calc_crc16(i2c_response, 7):
            co2 = IEEE754([i2c_response[2], i2c_response[3], i2c_response[4], i2c_response[5]])
            return co2
        else:
            raise Warning(get_status_string(2))

    def get_co2_raw_with_npc(self):
        """get the co2 value raw with no pressure compenstaion"""
        i2c_response = self.wire_write_read([0x03, 0x04, 0x2A, 0x00, 0x02, 0xE9, 0x8D], 8)
        crc_check = i2c_response[7] * 256 + i2c_response[6]
        if crc_check == calc_crc16(i2c_response, 7):
            co2 = IEEE754([i2c_response[2], i2c_response[3], i2c_response[4], i2c_response[5]])
            return co2
        else:
            raise Warning(get_status_string(2))

    def get_pressure_mbar(self):
        """get the pressure value in mbar"""
        i2c_response = self.wire_write_read([0x03, 0x04, 0xB0, 0x00, 0x02, 0xC9, 0xA2], 8)
        crc_check = i2c_response[7] * 256 + i2c_response[6]
        if crc_check == calc_crc16(i2c_response, 7):
            pressure = IEEE754([i2c_response[2], i2c_response[3], i2c_response[4], i2c_response[5]])
            return pressure
        else:
            raise Warning(get_status_string(2))

    def get_pressure_psi(self):
        """get the pressure value in psi"""
        i2c_response = self.wire_write_read([0x03, 0x04, 0xB2, 0x00, 0x02, 0x68, 0x62], 8)
        crc_check = i2c_response[7] * 256 + i2c_response[6]
        if crc_check == calc_crc16(i2c_response, 7):
            pressure = IEEE754([i2c_response[2], i2c_response[3], i2c_response[4], i2c_response[5]])
            return pressure
        else:
            raise Warning(get_status_string(2))

    def read_serial_number(self):
        """get the serial number"""
        i2c_response = self.wire_write_read([0x03, 0x00, 0x00, 0x00, 0x08, 0x49, 0x72], 20)
        crc_check = i2c_response[19] * 256 + i2c_response[18]
        if crc_check == calc_crc16(i2c_response, 19):
            i2c_response.pop(0)
            i2c_response.pop(0)
            i2c_response.pop(17)
            i2c_response.pop(16)
            return i2c_response
        else:
            raise Warning(get_status_string(2))

    def read_firmware_version(self):
        """get the firmware version"""
        i2c_response = self.wire_write_read([0x03, 0x00, 0x08, 0x00, 0x01, 0x08, 0xB6], 6)
        crc_check = i2c_response[5] * 256 + i2c_response[4]
        if crc_check == calc_crc16(i2c_response, 5):
            i2c_response.pop(0)
            i2c_response.pop(0)
            i2c_response.pop(3)
            i2c_response.pop(2)
            return i2c_response
        else:
            raise Warning(get_status_string(2))

    def read_sensor_name(self):
        """get the sensor name"""
        i2c_response = self.wire_write_read([0x03, 0x00, 0x09, 0x00, 0x08, 0x99, 0x70], 20)
        crc_check = i2c_response[19] * 256 + i2c_response[18]
        if crc_check == calc_crc16(i2c_response, 19):
            i2c_response.pop(0)
            i2c_response.pop(0)
            i2c_response.pop(17)
            i2c_response.pop(16)
            return i2c_response
        else:
            raise Warning(get_status_string(2))

    def read_measuring_mode(self):
        """read the measuring mode, 0 => continuous mode, 1 => single shot"""
        i2c_response = self.wire_write_read([0x03, 0x01, 0xF8, 0x00, 0x01, 0x09, 0x79], 6)
        crc_check = i2c_response[5] * 256 + i2c_response[4]
        if crc_check == calc_crc16(i2c_response, 5):
            return (i2c_response[3] & 0x01)
        else:
            raise Warning(get_status_string(2))

    def change_measuring_mode(self, measuring_mode):
        """change the measuring mode, 0 => continuous mode, 1 => single shot"""
        sendByte = measuring_mode
        command = [0x06, 0x01, 0xF8, 0x00, sendByte]
        crc = calc_crc16(command, 6)
        command.append(crc & 0xFF)
        command.append(crc >> 8)
        i2c_response = self.wire_write_read(command, 7)
        if command == i2c_response:
            return
        else:
            raise Warning(get_status_string(3))

    def data_ready(self):
        """shows if the data is ready to be read"""
        i2c_response = self.wire_write_read([0x03, 0x01, 0xF9, 0x00, 0x01, 0x58, 0xB9], 6)
        crc_check = i2c_response[5] * 256 + i2c_response[4]
        if crc_check == calc_crc16(i2c_response, 5):
            return (i2c_response[3] & 0x01)
        else:
            raise Warning(get_status_string(2))

    def trigger_ready(self):
        """shows if the trigger is ready"""
        i2c_response = self.wire_write_read([0x03, 0x01, 0xF9, 0x00, 0x01, 0x58, 0xB9], 6)
        crc_check = i2c_response[5] * 256 + i2c_response[4]
        if crc_check == calc_crc16(i2c_response, 5):
            return ((i2c_response[3] & 0x02) >> 1)
        else:
            raise Warning(get_status_string(2))

    def trigger_new_measurement(self):
        """triggers a new measuremnet, but only in single shot mode"""
        command = [0x06, 0x01, 0xFA, 0x00, 0x01, 0x64, 0xB9]
        i2c_response = self.wire_write_read(command, 7)
        if (command == i2c_response):
            return
        else:
            raise Warning(get_status_string(3))

    def status_details(self):
        """ Bit 0 = Co2 measurment too high, Bit 1 = Co2 measurment too low,
        Bit 2 = T measurement too high, Bit 3 = T measurement too low
        Bit 6 = p measurement too high, Bit 7 p measurement too low"""
        i2c_response = self.wire_write_read([0x03, 0x02, 0x58, 0x00, 0x01, 0x09, 0x1F],6)
        crc_check = i2c_response[5] * 256 + i2c_response[4]
        if crc_check == calc_crc16(i2c_response, 5):
            return i2c_response[3]
        else:
            raise Warning(get_status_string(2))

    def change_co2_measuring_interval(self, measuring_interval):
        """change the measuring interval of the sensor in continuous mode"""
        if 36001 > measuring_interval & measuring_interval > 99:
            sendByte0 = np.uint8(measuring_interval / 256)
            sendByte1 = np.uint8(measuring_interval % 256)
            command = [0x06, 0x14, 0x50, sendByte0, sendByte1]
            crc = calc_crc16(command, 6)
            command.append(crc & 0xFF)
            command.append(crc >> 8)
            i2c_response = self.wire_write_read(command, 7)
            if command == i2c_response:
                return
            else:
                raise Warning(get_status_string(3))
        else:
            raise Warning(get_status_string(4))

    def read_co2_measuring_interval(self):
        """read the measuring interval of the sensor in continuous mode"""
        i2c_response = self.wire_write_read([0x03, 0x14, 0x50, 0x00, 0x01, 0x8C, 0x95], 6)
        crc_check = i2c_response[5] * 256 + i2c_response[4]
        if crc_check == calc_crc16(i2c_response, 5):
            return ((i2c_response[2] << 8) + i2c_response[3])
        else:
            raise Warning(get_status_string(2))

    def change_co2_filter_coefficient(self, filter_coefficient):
        """change the filter coefficient of the sensor"""
        if 21 > filter_coefficient & filter_coefficient > 0:
            command = [0x06, 0x14, 0x51, 0x00, filter_coefficient]
            crc = calc_crc16(command, 6)
            command.append(crc & 0xFF)
            command.append(crc >> 8)
            i2c_response = self.wire_write_read(command, 7)
            if (command == i2c_response):
                return
            else:
                raise Warning(get_status_string(3))
        else:
            raise Warning(get_status_string(5))

    def read_co2_filter_coefficient(self):
        """read the filter coefficient of the sensor"""
        i2c_response = self.wire_write_read([0x03, 0x14, 0x51, 0x00, 0x01, 0xDD, 0x55], 6)
        crc_check = i2c_response[5] * 256 + i2c_response[4]
        if crc_check == calc_crc16(i2c_response, 5):
            return ((i2c_response[2] << 8) + i2c_response[3])
        else:
            raise Warning(get_status_string(2))

    def change_co2_custom_offset(self, custom_offset):
        """change the customer offset of the sensor for co2"""
        buf = np.uint16(custom_offset)
        sendByte0 = np.uint8(buf / 256)
        sendByte1 = np.uint8(buf % 256)
        command = [0x06, 0x14, 0x52, sendByte0, sendByte1]
        crc = calc_crc16(command, 6)
        command.append(crc & 0xFF)
        command.append(crc >> 8)
        i2c_response = self.wire_write_read(command, 7)
        if (command == i2c_response):
            return
        else:
            raise Warning(get_status_string(3))

    def read_co2_custom_offset(self):
        """read the customer offset of the sensor for co2"""
        i2c_response = self.wire_write_read([0x03, 0x14, 0x52, 0x00, 0x01, 0x2D, 0x55], 6)
        crc_check = i2c_response[5] * 256 + i2c_response[4]
        if crc_check == calc_crc16(i2c_response, 5):
            buf = np.int16((i2c_response[2] << 8) + i2c_response[3])
            return buf
        else:
            raise Warning(get_status_string(2))

    def change_customer_Register1(self, customer_Register):
        """since firmware version 1.1.1, registers reserved
        for any customer use, e.g. serial number, traceability, etc."""
        """change the customer register of the sensor for co2"""
        sendByte0 = customer_Register / 256
        sendByte1 = customer_Register % 256
        command = [0x06, 0x16, 0xA8, sendByte0, sendByte1]
        crc = calc_crc16(command, 6)
        command.append(crc & 0xFF)
        command.append(crc >> 8)
        i2c_response = self.wire_write_read(command, 7)
        if command == i2c_response:
            return
        else:
            raise Warning(get_status_string(3))

    def read_customer_Register1(self):
        """since firmware version 1.1.1, registers reserved
        for any customer use, e.g. serial number, traceability, etc."""
        i2c_response = self.wire_write_read([0x03, 0x16, 0xA8, 0x00, 0x01, 0xC0, 0xDC], 6)
        crc_check = i2c_response[5] * 256 + i2c_response[4]
        if crc_check == calc_crc16(i2c_response, 5):
            return ((i2c_response[2] << 8) + i2c_response[3])
        else:
            raise Warning(get_status_string(2))

    def change_customer_Register2(self, customer_Register):
        """since firmware version 1.1.1, registers reserved
        for any customer use, e.g. serial number, traceability, etc."""
        sendByte0 = customer_Register / 256
        sendByte1 = customer_Register % 256
        command = [0x06, 0x16, 0xA9, sendByte0, sendByte1]
        crc = calc_crc16(command, 6)
        command.append(crc & 0xFF)
        command.append(crc >> 8)
        i2c_response = self.wire_write_read(command, 7)
        if command == i2c_response:
            return
        else:
            raise Warning(get_status_string(3))

    def read_customer_Register2(self):
        """since firmware version 1.1.1, registers reserved
        for any customer use, e.g. serial number, traceability, etc."""
        i2c_response = self.wire_write_read([0x03, 0x16, 0xA9, 0x00, 0x01, 0x91, 0x1C], 6)
        crc_check = i2c_response[5] * 256 + i2c_response[4]
        if crc_check == calc_crc16(i2c_response, 5):
            return ((i2c_response[2] << 8) + i2c_response[3])
        else:
            raise Warning(get_status_string(2))

    def wire_write_read(self,  buf, receiving_bytes):
        """write a command to the sensor to get different answers like temperature values,..."""
        write_command = i2c_msg.write(self.i2c_address, buf)
        read_command = i2c_msg.read(self.i2c_address, receiving_bytes)
        with SMBus(1) as ee895_communication:
            ee895_communication.i2c_rdwr(write_command, read_command)
        return list(read_command)

    def wire_write(self, buf):
        """write to the sensor"""
        write_command = i2c_msg.write(self.i2c_address, buf)
        with SMBus(1) as ee895_communication:
            ee895_communication.i2c_rdwr(write_command)
