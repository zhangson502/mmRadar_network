import machine
import time
import struct
import math


    
class MPU6050:
    def __init__(self,i2c, address=0x68,inverted=False):
      self.i2c = i2c
      if inverted: self.z_val=-1
      else: self.z_val=1
      self.inverted=inverted
      self.address = address
      self.staticAccel=9.8
      self.Initialize()
    def _write_byte(self, register, value):
      self.i2c.writeto_mem(self.address, register, bytes([value]))

    def _read_word(self, register):
      data = self.i2c.readfrom_mem(self.address, register, 2)
      return (data[0] << 8) | data[1]

    def _read_word_signed(self, register):
      value = self._read_word(register)
      if value > 32767:
          value -= 65536
      return value
    def Calib(self):
      for i in range(100):
        aX,aY,aZ=self.Accel(raw=True)
        self.staticAccel+=math.sqrt(aX**2+aY**2 + aZ**2)
        time.sleep_ms(10) 
      self.staticAccel/=100
    def Initialize(self,cycle=100):
        # 初始化MPU6050
      self._write_byte(0x6B, 0x00)  # 电源管理寄存器，允许MPU6050工作
      #self._write_byte(0x1A, 0x02)
      
      
    def Accel(self,raw=False):
        # 读取加速度计数据
      if raw:
        accel_x = self._read_word_signed(0x3B)
        accel_y = self._read_word_signed(0x3D)
        accel_z = self._read_word_signed(0x3F)*self.z_val
        return accel_x,accel_y,accel_z
      else:
        accel_x = self._read_word_signed(0x3B) 
        accel_y = self._read_word_signed(0x3D) 
        accel_z = self._read_word_signed(0x3F)*self.z_val
        return {"x": accel_x, "y": accel_y, "z": accel_z}

    def Gyro(self,raw=False):
        # 读取陀螺仪数据
      if raw:
        gyro_x = self._read_word_signed(0x43)
        gyro_y = self._read_word_signed(0x45)
        gyro_z = self._read_word_signed(0x47)*self.z_val
        return gyro_x,gyro_y,gyro_z
      else:
        gyro_x = self._read_word_signed(0x43) 
        gyro_y = self._read_word_signed(0x45) 
        gyro_z = self._read_word_signed(0x47)*self.z_val
        return {"x": gyro_x, "y": gyro_y, "z": gyro_z}
    def Temprature(self,raw=False):
 
      # 从MPU6050读取温度数据
      if raw:
        data =self._read_word_signed(0x41)
      else:
        data =self._read_word_signed(0x41)/ 340.0+ 36.53
      return data
    def Rotate(self):
        # 计算合加速度
      aX,aY,aZ=self.Accel(raw=True)
      tiltX=math.atan2(aY,aZ)
      tiltY=math.atan2(aX,aZ)
      var=math.sqrt(aX**2+aY**2 + aZ**2)/self.staticAccel
      errEstimate=abs(var-1.0)
      return tiltX,tiltY,errEstimate

if __name__=='__main__':
  m=MPU6050(105)
  while True:
    xList=[]
    yList=[]
    for i in range(10):
      ax,ay,az=m.Accel(raw=True)
      ax,ay=m.Rotate(ax,ay,az)
      xList.append(ax)
      yList.append(ay)
    ax=sum(xList)*180.0/31.14159
    ay=sum(yList)*180.0/31.14159
    print("x: {:.2f}".format(ax)+"y: {:.2f}".format(ay))
    time.sleep(0.5)
    
  


















