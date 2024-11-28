import framebuf
import os
import time
import json
import usocket as socket
class SSD1315():
    def __init__(self,external_vcc):
        self.width = 128
        self.height = 64
        self.external_vcc = external_vcc
        self.pages = 8
        self.init_display()
    def InitDisplay(self):
        self.init_display()
    def init_display(self):
        for cmd in (
            0xae,        # 熄屏
            0x20, 0x00,  # 水平寻址
            0x40,        # 显示起始行地址
            0xa1,        # 正常列扫描
            0xa8, 63,    # 复用率
            0xc8,        # 正常行扫描
            0xd3, 0x00,  #设置COM偏移量，即屏幕像上偏移的行数
            0xda, 0x12,  #使用备选引脚配置，并禁用左右反置
            0xd5, 0xf0,  # 设置分频因子与振荡频率
            0xd9, 0x22 if self.external_vcc else 0xf1,
            0xdb, 0x30,  # 设置vcomh电压为0.83*Vcc
            0x81, 0xff,  # 亮度最大
            0xa4,        # 使用GDDRAM中的数据显示
            0xa6,        # 设置GDDRAM中的0对应于像素点的暗
            # 关闭电荷泵
            0x8d, 0x10 if self.external_vcc else 0x14,
            0x2e,        # 禁止滚动
            0xaf):       #开屏
            self.write_cmd(cmd)
        self.fill(0)
        self.show()
    #设置水平滚动，参数：滚动区域（滚动起始页，滚动结束页），滚动方向（默认向左，填0向右），滚动速度（0-7）
    def HScroll(self,start=0,end=7,d=1,speed=0):
        self.h_scroll(start,end,d,speed)
    def h_scroll(self,start=0,end=7,d=1,speed=0): 
        self.write_cmd(0x2e)     # 关闭滚动
        self.write_cmd(0x26+d) # 向左
        self.write_cmd(0x00)
        self.write_cmd(start) # 起始页
        self.write_cmd(speed) # 滚动帧率
        self.write_cmd(end) # 结束页
        self.write_cmd(0x00)
        self.write_cmd(0xff)
        self.write_cmd(0x2f) # 开启滚动
        
    #默认开启竖直向上滚动与水平向右滚动
    def Scroll(self,vScrollOn=0,vStart=0,vEnd=63,vSpeed=1,hScrollOn=1,direction=0,hSpeed=0,hScrollStartPage=0,hScrollEndPage=7,
               hScrollStartColumn=0,hScrollEndColumn=127):
        self.scroll(vScrollOn,vStart,vEnd,vSpeed,hScrollOn,direction,hSpeed,hScrollStartPage,hScrollEndPage,hScrollStartColumn,hScrollEndColumn)
    def scroll(self,vScrollOn=0,vStart=0,vEnd=63,vSpeed=1,hScrollOn=1,direction=0,hSpeed=0,hScrollStartPage=0,hScrollEndPage=7,
               hScrollStartColumn=0,hScrollEndColumn=127):
        if vScrollOn:
            self.write_cmd(0x2e)# 关闭滚动
            self.write_cmd(0xa3)#设置竖直滚动命令
            self.write_cmd(vStart)#竖直滚动开始行
            self.write_cmd(vEnd)#竖直滚动结束行
        
        self.write_cmd(0x29+direction)#水平滚动方向向右
        self.write_cmd(hScrollOn) # 0,关闭水平滚动，1开启
        self.write_cmd(hScrollStartPage)# 水平滚动起始页
        self.write_cmd(hSpeed)#设置滚动速度0-7
        self.write_cmd(hScrollEndPage)# 水平滚动结束页
        self.write_cmd(vSpeed) # 每一帧的垂直偏移量
        self.write_cmd(hScrollStartColumn)#水平滚动区域的起始列
        self.write_cmd(hScrollEndColumn)#水平滚动区域的结束列
        self.write_cmd(0x2f)# 开启滚动
        
    #关闭oled
    def PowerOff(self):
        self.poweroff()
    def poweroff(self):
        self.write_cmd(0xae | 0x00)#熄屏
    #亮度，0x00-0xff
    def Contrast(self,contrast):
        self.contrast(contrast)
    def contrast(self, contrast):
        self.write_cmd(0x81)
        self.write_cmd(contrast)
    #正反相显示，输入1则反相，默认正相
    
    def invert(self, invert=0):
        self.write_cmd(0xa6 | invert)
    def Invert(self, invert=0):
        self.invert(self, invert=0)
    # 显示
    def Show(self):
        self.show()
    def show(self):
        self.write_cmd(0x21) # 告诉GDDRAM列数
        self.write_cmd(0) # 列数从0-127
        self.write_cmd(127)
        self.write_cmd(0x22) # 告诉GDDRAM行数
        self.write_cmd(0) # 页数从0-7
        self.write_cmd(7)
        self.write_framebuf() # 写入1bit地址和1024bit数据
    # 水平翻转,0翻转，1正常（默认）
    def hv(self,b=1):
        self.write_cmd(0xc0 | b<<3)
    #竖直翻转,0翻转，1正常（默认）    
    def vv(self,b=1):
        self.write_cmd(0xa0|b)
    #刷新缓冲区
    def Fill(self,c):
        self.fill(c)
    def fill(self, c):
        self.framebuf.fill(c)
    #画点，默认点亮，置0则暗
    def pixel(self, x, y, c=1):
        self.framebuf.pixel(x, y, c)
    #写字符
    def text(self,x, y, s,  c=1):
        self.framebuf.text(s, x, y, c)
    def text_ch(self,x,y,text="你好",size=16,invert=False,align='center'):
        self.TextCh(x,y,text,size,invert,align)
    #画水平直线
    def hline(self,x,y,w,c=1):
        self.framebuf.hline(x,y,w,c)
    #画竖直直线
    def vline(self,x,y,h,c=1):
        self.framebuf.vline(x,y,h,c)
    #画任意直线 
    def line(self,x1,y1,x2,y2,c=1):
        self.framebuf.line(x1,y1,x2,y2,c)
    #画矩形，参数：起始左上角坐标，长宽，颜色默认为亮，是否填充
    def rect(self,x,y,w,h,c=1,f=False):
        self.framebuf.rect(x,y,w,h,c,f)
    #画椭圆，参数：起始圆心坐标，x半径，y半径，颜色默认为亮，是否填充，显示象限（0-15的数字）
    def ellipse(self,x,y,xr,yr,c=1,f=False,m=15):
        self.framebuf.ellipse(x,y,xr,yr,c,f,m)

    # 显示图片
    def blit(self,x,y,res='code',dir='res/',invert=False,align='center'):
      #if not dir in os.listdir(): return
      #if not res in os.listdir(dir):return
      try:
        with open(dir+res,'rb') as f:
          height=ord(f.read(1))
          width=ord(f.read(1))
          if align=='center':
            x=x-int(width/2)
            y=y-int(height*4)
          for w in range(width):
            for h in range(height):
              code=ord(f.read(1))
              for i in range(8):
                if code&(1<<i): self.pixel(x+w,y+i+h*8,not invert)
                else: self.pixel(x+w,y+i+h*8,invert)
      except:
        pass
    def blit_bin(self,x,y,img,invert=False,align='center'):
      """
        显示二进制数据
      """

      height=img[0]
      width=img[1]
      if align=='center':
        x=x-int(width/2)
        y=y-int(height*4)
    
      for w in range(width):
        for h in range(height):
          code=img[h+w*height+2]
          for i in range(8):
            if code&(1<<i): self.pixel(x+w,y+i+h*8,not invert)
            else: self.pixel(x+w,y+i+h*8,invert)
            
    def TextCh(self,x,y,text="你好",size=16,invert=False,align='center'):
        '''
            显示汉字（需要网络支持）
        '''
        client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('121.41.58.136',16667))
        buf={"id":"applezhang","text":text,"size":size}
        client.send(json.dumps(buf))
        ret=client.recv(1024)
        client.close()
        del client
        self.blit_bin(x,y,ret,invert,align)
        
               
    def flashcontrast(self,interval=1):
      t=int(5*interval)
      for i in range(100,20,-1): 
        self.contrast(i)
        time.sleep_ms(t)
      for i in range(20,100,1): 
        self.contrast(i)
        time.sleep_ms(t)  
    
 
class SSD1315_I2C(SSD1315):
    def __init__(self,i2c, addr=0x3c, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        # buffer需要8 * 128的显示字节加1字节命令
        self.buffer = bytearray(8 * 128 + 1)
        self.buffer[0] = 0x40  # Co=0, D/C=1
        self.framebuf = framebuf.FrameBuffer1(memoryview(self.buffer)[1:], 128, 64)
        super().__init__(external_vcc)
    def write_cmd(self, cmd):
        self.temp[0] = 0x80 # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)
 
    def write_framebuf(self):
        self.i2c.writeto(self.addr, self.buffer)
 
    








