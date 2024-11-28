from machine import I2C, Pin
import time

class TCS34725:
    TCS34725_ADDRESS = 0x29
    
    COMMAND_BIT = 0x80
    
    ENABLE = 0x00
    ENABLE_AIEN = 0x10
    ENABLE_WEN = 0x08
    ENABLE_AEN = 0x02
    ENABLE_PON = 0x01
    
    ATIME = 0x01
    CONTROL = 0x0F
    
    CDATA = 0x14
    RDATA = 0x16
    GDATA = 0x18
    BDATA = 0x1A
    
    INTEGRATIONTIME_2_4MS = 0xFF
    INTEGRATIONTIME_24MS = 0xF6
    INTEGRATIONTIME_101MS = 0xD5
    TIME_CONFIG={"low":0xFF,"med":0xF6,"high":0xD5}
    GAIN_1X = 0x00
    GAIN_4X=0x01
    GAIN_16X=0x02
    GAIN_CONFIG={"low":0x00,"med":0x01,"high":0x02}
    
    def __init__(self, i2c):
        self.i2c = i2c
        
        self.InitSensor()
    def SetSensory(self,time_mode="med",amp_mode="med"):
        '''
        设置传感器的灵敏度
        '''
        self.i2c.writeto_mem(self.TCS34725_ADDRESS, self.COMMAND_BIT | self.ATIME, bytearray([self.TIME_CONFIG[time_mode]]))
        self.i2c.writeto_mem(self.TCS34725_ADDRESS, self.COMMAND_BIT | self.CONTROL, bytearray([self.TIME_CONFIG[amp_mode]]))
        
        
    def InitSensor(self):
        # 使能电源
        self.i2c.writeto_mem(self.TCS34725_ADDRESS, self.COMMAND_BIT | self.ENABLE, bytearray([self.ENABLE_PON]))
        time.sleep(0.003)
        self.i2c.writeto_mem(self.TCS34725_ADDRESS, self.COMMAND_BIT | self.ENABLE, bytearray([self.ENABLE_PON | self.ENABLE_AEN]))

    def ReadColor(self):
        # 读取颜色数据
        clear = self.i2c.readfrom_mem(self.TCS34725_ADDRESS, self.COMMAND_BIT | self.CDATA, 2)
        red = self.i2c.readfrom_mem(self.TCS34725_ADDRESS, self.COMMAND_BIT | self.RDATA, 2)
        green = self.i2c.readfrom_mem(self.TCS34725_ADDRESS, self.COMMAND_BIT | self.GDATA, 2)
        blue = self.i2c.readfrom_mem(self.TCS34725_ADDRESS, self.COMMAND_BIT | self.BDATA, 2)
        
        clear = int.from_bytes(clear, 'little')
        red = int.from_bytes(red, 'little')
        green = int.from_bytes(green, 'little')
        blue = int.from_bytes(blue, 'little')
        
        return (red, green, blue, clear)

