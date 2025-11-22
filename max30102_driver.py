# max30102_driver.py

import smbus
import time

class MAX30102:
    DEFAULT_I2C_ADDR = 0x57

    REG_INTR_STATUS_1   = 0x00
    REG_INTR_STATUS_2   = 0x01
    REG_INTR_ENABLE_1   = 0x02
    REG_INTR_ENABLE_2   = 0x03
    REG_FIFO_WR_PTR     = 0x04
    REG_OVF_COUNTER     = 0x05
    REG_FIFO_RD_PTR     = 0x06
    REG_FIFO_DATA       = 0x07
    REG_FIFO_CONFIG     = 0x08
    REG_MODE_CONFIG     = 0x09
    REG_SPO2_CONFIG     = 0x0A
    REG_LED1_PA         = 0x0C
    REG_LED2_PA         = 0x0D

    MODE_HRONLY         = 0x02
    MODE_SPO2           = 0x03

    def __init__(self, address=DEFAULT_I2C_ADDR, bus=1):
        self.address = address
        self.bus = smbus.SMBus(bus)

        # 리셋
        self._write_reg(self.REG_MODE_CONFIG, 0x40)
        time.sleep(0.1)

        # FIFO 초기화
        self._write_reg(self.REG_FIFO_WR_PTR, 0x00)
        self._write_reg(self.REG_OVF_COUNTER, 0x00)
        self._write_reg(self.REG_FIFO_RD_PTR, 0x00)

        # 모드 설정: HR ONLY
        self._write_reg(self.REG_MODE_CONFIG, self.MODE_HRONLY)

        # SPO2 설정
        self._write_reg(self.REG_SPO2_CONFIG, 0x27)   # 예: sample rate 100Hz, pulse width 411us
        # LED 파워 설정
        self._write_reg(self.REG_LED1_PA, 0x1F)       # LED1 (RED) amplitude
        self._write_reg(self.REG_LED2_PA, 0x1F)       # LED2 (IR) amplitude

        # FIFO 설정: sample average = 4, FIFO roll over 등 설정
        self._write_reg(self.REG_FIFO_CONFIG, 0x4F)

    def _write_reg(self, reg, val):
        self.bus.write_byte_data(self.address, reg, val)

    def _read_reg(self, reg):
        return self.bus.read_byte_data(self.address, reg)

    def read_fifo(self):
        # FIFO 데이터 6바이트: RED(3바이트) + IR(3바이트)
        data = self.bus.read_i2c_block_data(self.address, self.REG_FIFO_DATA, 6)

        red = (data[0] << 16) | (data[1] << 8) | data[2]
        ir  = (data[3] << 16) | (data[4] << 8) | data[5]

        # 상위 18비트 유효
        red &= 0x03FFFF
        ir  &= 0x03FFFF

        return ir, red
