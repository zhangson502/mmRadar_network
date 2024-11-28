from machine import Pin, UART
import time
class Usart:
  
  def __init__(self,baudRate=115200,handler=None,timeout=1000):
    """初始化"""
    self.port=UART(1, baudrate=baudRate, tx=17, rx=16,timeout=timeout)
    if handler!=None:
      self.handler=handler
      Pin(16).irq(trigger=Pin.IRQ_RISING, handler=self.IRQ)
  def Send(self,dat):
    """发送数据"""
    self.port.write(dat)
    
  def Read(self,length=1024,strict=True):
    """读取数据"""
    cache=[]
    if not strict:
      while self.port.any() and len(cache)<length:
        cache.append(ord(self.port.read(1)))
    else:
      while len(cache)<length:
        tmp=self.port.read(1)
        if tmp!=None: 
          cache.append(ord(tmp))
    return cache
  
  def IRQ(self,pin):  
    """中断函数"""
    """接收过程中暂停中断"""
    Pin(16).irq(handler=None)
    ret=self.Read()
    Pin(16).irq(trigger=Pin.IRQ_RISING, handler=self.IRQ)
    """处理中断"""
    if len(ret)>0: self.handler(ret)
  


