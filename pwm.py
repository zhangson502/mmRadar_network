
import machine
import time
import utime
# 设置舵机A和B的GPIO引脚
class PWM:
  '''
    定义舵机类型
  '''
  def __init__(self,pin=19,freq=10000,power=0.0):
    '''
      定义引脚
    '''
    self.sPin = machine.Pin(pin, machine.Pin.OUT)
    self.pwm = machine.PWM(self.sPin,freq=freq)
    self.SetPower(power)

  def SetPower(self,val=0.0):
    '''
      设置单个舵机的角度
    '''
    realVal=int(val*1023)
    self.pwm.duty(realVal)
      





















