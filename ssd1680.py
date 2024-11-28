import utime as time
from machine import Pin,SPI
import framebuf

class EPaper(framebuf.FrameBuffer):
    '''
    电纸书驱动
    '''
    def __init__(self,spi,pin_rst=4,pin_dc=5,pin_cs=18,pin_busy=19,horizontal=True,invert=False):
        '''
        初始化
        '''
        self.spi=spi
        self.pin_rst=Pin(pin_rst,Pin.OUT,Pin.PULL_UP)
        self.pin_dc=Pin(pin_dc,Pin.OUT,Pin.PULL_UP)
        self.pin_cs=Pin(pin_cs,Pin.OUT,Pin.PULL_UP)
        self.pin_busy=Pin(pin_busy,Pin.IN)
        
        # 横屏竖屏配置
        self.horizontal=horizontal
        self.invert=invert
        self.width = 296 if horizontal else 176
        self.height = 176 if horizontal else 296
        mode = framebuf.MONO_VLSB if self.horizontal else framebuf.MONO_HLSB
        # 缓存数据
        self._buffer = bytearray(self.height * self.width // 8)
        self._mvb = memoryview(self._buffer)
        self.busy=False
        
        #初始化
        super().__init__(self._buffer,self.width,self.height,mode)
        self.Initialize()
        
    def Command(self, command, data=None):
        '''
        发送指令
        '''
        self.WaitReady()
        self.pin_cs(0)
        self.pin_dc(0)
        self.spi.write(bytes(command))
        self.pin_dc(1)
        if data is not None:
            self.TxData(bytes(data))
        self.pin_cs(1)
            
    def TxData(self,data):
        '''
        发送数据
        '''
        self.pin_cs(0)
        self.pin_dc(1)
        self.spi.write(data)
        self.pin_cs(1)
        self.pin_dc(0)
        
    def HwReset(self):
        '''
        初始化墨水屏幕
        '''
        self.pin_rst(1)
        time.sleep_ms(200)
        self.pin_rst(0)
        time.sleep_ms(200)
        self.pin_rst(1)
        self.WaitReady()
        
    def Initialize(self):
        '''
        初始化
        '''
        self.HwReset()
        self.pin_dc(0)
        self.pin_cs(1)
        
        self.Command(b'\x12') #软件复位
        
        
        # 设置扫描控制
        self.Command(b'\x01', [0x27,1,0])
        # 设置扫描方向
        self.Command(b'\x11', [0x07] if self.horizontal else [0x03] )
        # 设置反向
        
        # 设置RAM-X
        self.Command(b'\x44', [0x00,0x15])
        # 设置RAM-Y
        self.Command(b'\x45', [0x00,0x00,0x27,0x01])
        # 设置边框显示波形
        self.Command(b'\x3c', b'\x05')
        # 设置刷新特征(正常模式)
        self.Command(b'\x21', [00 if self.invert else 88, 00])
        # 初始化X-Y起始地址
        self.Command(b'\x4e', b'\x00')
        self.Command(b'\x4F', b'\x00\x00')
        # 设置内部温度传感器
        self.Command(b'\x18', b'\x80')
       
        
    def DeepSleep(self,mode=0x01):
        '''
        深度睡眠模式
        '''
        self.Command(b'\x10', bytes([mode]))
        
    def WaitReady(self):
        '''
        等待完成
        '''
        time.sleep_ms(50)
        while self.pin_busy():
            time.sleep_ms(50)
        
        
    def Show(self,fast_refresh=False):
        '''
        显示水墨界面
        '''
        self.Command(b'\x4e', [0])
        self.Command(b'\x4F', b'\x00\x00')
        self.Command(b'\x24',self._buffer)
        
                
        if fast_refresh:
            self.Command(b'\x22', b'\xFF')
        else:
            self.Command(b'\x22', b'\xF7')
            
        time.sleep_us(20)
        self.Command(b'\x20')
        
        self.WaitReady()
        
if __name__=='__main__':
    
    spi0 = SPI(1, baudrate=1000000, polarity=0, phase=0)
    e=EPaper(spi0,horizontal=True)
    e.fill(0)
    e.Show()       
    e.line(0,0,180,180,1)
    e.Show()