
from machine import I2S,Pin
import urequests as requests
import time
class Mouth:
  
  def __init__(self):
    pass
  def InitSound(self,rate=16000,buf=10000):
    self.i2s = I2S(1, sck=Pin(12), ws=Pin(14), sd=Pin(13), mode=I2S.TX, bits=16, format=I2S.MONO, rate=rate, ibuf=buf)
    
  def PlaySound(self,file,rate=16000):
    self.InitSound(rate=rate)
    with open(file,'rb') as f:
      f.seek(44) 
      wav_samples = bytearray(1024)
      wav_samples_mv = memoryview(wav_samples)
      #并将其写入I2S DAC
      while True:
        try:
          num_read = f.readinto(wav_samples_mv)
          if num_read == 0: 
            break
          num_written = 0
          while num_written < num_read:
            num_written += self.i2s.write(wav_samples_mv[num_written:num_read])
        except:
          self.i2s.deinit()
          return False
    self.i2s.deinit()
    return True
  def tPlaySound(self,file,rate=16000):
    import _thread
    _thread.start_new_thread(self.PlaySound,(file,rate))
  def tPlayNetSound(self,file,rate=16000):
    import _thread
    _thread.start_new_thread(self.PlayNetSound,(file,rate))  
    
  def PlayNetSound(self,url,rate=16000):
    self.InitSound(rate=rate)
    response = requests.get(url, stream=True)
    response.raw.read(44)
    while True:
      try:
          content_byte = response.raw.read(256)  # 每次读取1024个字节
          # 判断WAV文件是否结束
          if len(content_byte) == 0: 
              break
          # 调用I2S对象播放音频
          self.i2s.write(content_byte) 
      except Exception as ret:
         
          response.close()
          return False
    time.sleep(0.5)
    self.i2s.deinit()
    response.close()
    return True




