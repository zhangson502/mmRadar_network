import time
from machine import Pin

class Button:
  
  def __init__(self,port=0):
    self.btn=Pin(port,Pin.IN,Pin.PULL_UP)
    
  def Pressed(self):
    return not self.btn.value()
    
  def IRQ(self,trigger=Pin.IRQ_RISING,handler=None):
    self.btn.irq(trigger=trigger, handler=handler)
    
    
  def LongPress(self,t=400):
      last=time.ticks_ms()
      while self.Pressed():
          pass
      if time.ticks_ms()-last < t:
          return False
      return True
      
