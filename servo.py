
import machine
import time
import utime
# 设置舵机A和B的GPIO引脚
class Servo:
  '''
    定义舵机类型
  '''
  def __init__(self,pin=19):
    '''
      定义引脚
    '''
    self.sPin = machine.Pin(pin, machine.Pin.OUT)
    self.servo = machine.PWM(self.sPin,freq=50)
    self.lastVal=0.01

  def SetAngle(self,val=0.0):
    '''
      设置单个舵机的角度
    '''
    if -110.0<val<110.0:
        if abs(self.lastVal-val)<0.1: return
        realVal=1500000-int(val*11111.11)
        self.servo.duty_ns(realVal)
        self.lastVal=val
      


if __name__=='__main__':
  s=Servo()
  s.SetAngle(0)
  for i in range(-80,80,1):
    s.SetAngle(i)
    time.sleep_ms(50)



















