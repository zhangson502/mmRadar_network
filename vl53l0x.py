from machine import Pin, I2C
import time

class VL53L0X:

    _I2C_ADDR = 0x29

    # 寄存器地址
    _REG_SYSRANGE_START = 0x00
    _REG_RESULT_RANGE_STATUS = 0x14
    _REG_TIME_BUDGET=0x51
    _REG_MEASURE_MODE=0x4b
    def __init__(self, i2c):
        self.i2c = i2c
        self.InivDev()
        self.distance=0.0
        print(self.Distance())
    def InivDev(self):
        # 启动测量
        self.i2c.writeto(self._I2C_ADDR, bytearray([self._REG_MEASURE_MODE, 0x00]))
        self.i2c.writeto(self._I2C_ADDR, bytearray([self._REG_SYSRANGE_START, 0x01]))
    def SetAccu(self,t=100):
        #数值越大测量越准，但是时间花费越长
        val1=int(t*1000)&0xff00>>8;val2=int(t*1000)&0xff
        self.i2c.writeto_mem(self._I2C_ADDR, self._REG_TIME_BUDGET,bytearray([ val1, val2]))
    def Distance(self,min=0.03):
        # 等待测量完成
        dat=0.0
        while dat<min:
          self.InivDev()
          #time.sleep_ms(100)
          while True:
              status = self.i2c.readfrom_mem(self._I2C_ADDR, self._REG_RESULT_RANGE_STATUS, 1)[0]
              if status & 0x01:
                  break
              time.sleep_ms(10)
          
          # 读取测量结果
          distance = self.i2c.readfrom_mem(self._I2C_ADDR, 0x14, 12)
          dat=((distance[10] << 8) + distance[11])/1000.0
        self.distance=dat
        return dat







