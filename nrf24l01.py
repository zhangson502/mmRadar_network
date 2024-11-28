"""NRF24L01 driver for MicroPython
"""

from micropython import const
from machine import Pin, SPI
import utime
import machine

# nRF24L01+ registers
CONFIG = const(0x00)
EN_RXADDR = const(0x02)
SETUP_AW = const(0x03)
SETUP_RETR = const(0x04)
RF_CH = const(0x05)
RF_SETUP = const(0x06)
STATUS = const(0x07)
RX_ADDR_P0 = const(0x0A)
TX_ADDR = const(0x10)
RX_PW_P0 = const(0x11)
FIFO_STATUS = const(0x17)
DYNPD = const(0x1C)

# CONFIG register
EN_CRC = const(0x08)  # enable CRC
CRCO = const(0x04)  # CRC encoding scheme; 0=1 byte, 1=2 bytes
PWR_UP = const(0x02)  # 1=power up, 0=power down
PRIM_RX = const(0x01)  # RX/TX control; 0=PTX, 1=PRX

# RF_SETUP register
POWER_0 = const(0x00)  # -18 dBm
POWER_1 = const(0x02)  # -12 dBm
POWER_2 = const(0x04)  # -6 dBm
POWER_3 = const(0x06)  # 0 dBm
SPEED_1M = const(0x00)
SPEED_2M = const(0x08)
SPEED_250K = const(0x20)

# STATUS register
RX_DR = const(0x40)  # RX data ready; write 1 to clear
TX_DS = const(0x20)  # TX data sent; write 1 to clear
MAX_RT = const(0x10)  # max retransmits reached; write 1 to clear

# FIFO_STATUS register
RX_EMPTY = const(0x01)  # 1 if RX FIFO is empty

# constants for instructions
R_RX_PL_WID = const(0x60)  # read RX payload width
R_RX_PAYLOAD = const(0x61)  # read RX payload
W_TX_PAYLOAD = const(0xA0)  # write TX payload
FlushTx = const(0xE1)  # flush TX FIFO
FlushRx = const(0xE2)  # flush RX FIFO
NOP = const(0xFF)  # use to read STATUS register
MAX_ATTEMPTS=const(6)
RETRANSMIT_LATENCY=8


class NRF24L01:
    '''
    NRF24L01驱动程序
    '''
    def __init__(self, spi, cs_pin=18, ce_pin=19, irq_pin=27, channel=46, address=[0,0,0,0,1], payload_size=16):
        
        assert payload_size <= 32  #保证数据不溢出
        self.payload_size = payload_size
        self.buf = bytearray(1)

        self.spi = spi
        self.cs = machine.Pin(cs_pin,machine.Pin.OUT)
        self.ce = machine.Pin(ce_pin,machine.Pin.OUT)
        self.irq=machine.Pin(irq_pin,machine.Pin.IN)
        #self.irq.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.RecvIRQ)
        

        #初始化引脚： CE=0 待机模式  CS=1 非选中模式
        self.ce(0)
        self.cs(1)
        
        self.pipe0_read_addr = bytes(address)
        utime.sleep_ms(5)

        # 设置地址长度
        self.WriteReg(SETUP_AW, 0b11)
        if self.ReadReg(SETUP_AW) != 0b11:
            raise OSError("nRF24L01+ Hardware not responding")

        # 禁用动态负载长度
        self.WriteReg(DYNPD, 0)

        # 设置重发次数和延迟
        self.WriteReg(SETUP_RETR, (MAX_ATTEMPTS << 4) | RETRANSMIT_LATENCY)

        # 设置无线电频率和传输速度
        self.SetRadio(POWER_3, SPEED_250K)  # Best for point to point links

        # 设置CRC长度
        self.ConfigCRC(2)

        # 清除状态标志
        self.WriteReg(STATUS, RX_DR | TX_DS | MAX_RT)

        # 设置通信通道
        self.SetChannel(channel)

        # flush buffers
        self.FlushRx()
        self.FlushTx()
        
    def RecvIRQ(self,pin):
        '''接收中断'''
        pass
    

    def ReadReg(self, reg):
        self.cs(0)
        self.spi.readinto(self.buf, reg)
        self.spi.readinto(self.buf)
        self.cs(1)
        return self.buf[0]

    def WriteReg_bytes(self, reg, buf):
        self.cs(0)
        self.spi.readinto(self.buf, 0x20 | reg)
        self.spi.write(buf)
        self.cs(1)
        return self.buf[0]

    def WriteReg(self, reg, value):
        self.cs(0)
        self.spi.readinto(self.buf, 0x20 | reg)
        ret = self.buf[0]
        self.spi.readinto(self.buf, value)
        self.cs(1)
        return ret

    def FlushRx(self):
        self.cs(0)
        self.spi.readinto(self.buf, FlushRx)
        self.cs(1)

    def FlushTx(self):
        self.cs(0)
        self.spi.readinto(self.buf, FlushTx)
        self.cs(1)

    def SetRadio(self, power, speed):
        '''
        设置无线发射器的功率和无线传输速度
        '''
        setup = self.ReadReg(RF_SETUP) & 0b11010001
        self.WriteReg(RF_SETUP, setup | power | speed)

    # length in bytes: 0, 1 or 2
    def ConfigCRC(self, length):
        '''
        配置CRC校验
        '''
        config = self.ReadReg(CONFIG) & ~(CRCO | EN_CRC)
        if length == 0:
            pass
        elif length == 1:
            config |= EN_CRC
        else:
            config |= EN_CRC | CRCO
        self.WriteReg(CONFIG, config)

    def SetChannel(self, channel):
        '''
        设置通信信道
        同一个网络信道必须一致
        [0] 2.400-2.401GHz
        [1] 2.401-2.402GHz
        ...
        [125] 2.525-2.526GHz
        '''
        self.WriteReg(RF_CH, min(channel, 125))


    def SetTxAddr(self, address):
        '''
        设置作为发送端的地址
        '''
        assert len(address) == 5
        self.WriteReg_bytes(RX_ADDR_P0, address)
        self.WriteReg_bytes(TX_ADDR, address)
        self.WriteReg(RX_PW_P0, self.payload_size)


    def SetRxAddr(self, pipe_id, address):
        '''
        设置作为接收端的地址
        '''
        assert len(address) == 5
        assert 0 <= pipe_id <= 5
        if pipe_id == 0:
            self.pipe0_read_addr = address
        if pipe_id < 2:
            self.WriteReg_bytes(RX_ADDR_P0 + pipe_id, address)
        else:
            self.WriteReg(RX_ADDR_P0 + pipe_id, address[0])
        self.WriteReg(RX_PW_P0 + pipe_id, self.payload_size)
        self.WriteReg(EN_RXADDR, self.ReadReg(EN_RXADDR) | (1 << pipe_id))

    def RxMode(self):
        '''
        接收数据
        '''
        self.WriteReg(CONFIG, self.ReadReg(CONFIG) | PWR_UP | PRIM_RX)
        self.WriteReg(STATUS, RX_DR | TX_DS | MAX_RT)

        if self.pipe0_read_addr is not None:
            self.WriteReg_bytes(RX_ADDR_P0, self.pipe0_read_addr)

        self.FlushRx()
        self.FlushTx()
        self.ce(1)
        utime.sleep_us(130)

    def StopMode(self):
        '''
        停止发送接收
        '''
        self.ce(0)
        self.FlushTx()
        self.FlushRx()

    # returns True if any data available to Recv
    def any(self):
        return not bool(self.ReadReg(FIFO_STATUS) & RX_EMPTY)

    def Recv(self):
        '''
        接收数据
        '''
        self.cs(0)
        self.spi.readinto(self.buf, R_RX_PAYLOAD)
        buf = self.spi.read(self.payload_size)
        self.cs(1)
        # clear RX ready flag
        self.WriteReg(STATUS, RX_DR)
        return buf
    
    def SendTo(self,addr,buffer,ack=True,timeout=100):
        '''
        向某个地址发送数据
        '''
        self.SetTxAddr(bytes(addr));self.SetRxAddr(0,bytes(addr)) #地址跳转到接收端
        ret=self.Send(buffer,ack,timeout)
        self.RxMode()
        return ret
        
        
    
    def WaitData(addr,pipe_id=0):
        '''
        阻塞式等待数据
        '''
        pass

    def Send(self, buf, ack=False, timeout=500):
        '''
        发送数据
        '''
        self.SendBuffer(buf)
        if ack:
            start = utime.ticks_ms()
            result = None
            while result is None and utime.ticks_diff(utime.ticks_ms(), start) < timeout:
                result = self.CheckTxStatus()  # 1 == success, 2 == fail
            if result == 1:
                return True
            return False
        return False


    def SendBuffer(self, buf):
        '''
        发送一组buffer，bytes形式的
        '''
        # power up
        self.WriteReg(CONFIG, (self.ReadReg(CONFIG) | PWR_UP) & ~PRIM_RX)
        utime.sleep_us(150)
        # Send the data
        self.cs(0)
        self.spi.readinto(self.buf, W_TX_PAYLOAD)
        self.spi.write(buf)
        if len(buf) < self.payload_size:
            self.spi.write(b"\x00" * (self.payload_size - len(buf)))  # pad out data
        self.cs(1)

        # enable the chip so it can Send the data
        self.ce(1)
        utime.sleep_us(15)  # needs to be >10us
        self.ce(0)

    def CheckTxStatus(self):
        '''
        检测发送状态
        '''
        if not (self.ReadReg(STATUS) & (TX_DS | MAX_RT)):
            return None  # tx not finished

        # either finished or failed: get and clear status flags, power down
        status = self.WriteReg(STATUS, RX_DR | TX_DS | MAX_RT)
        self.WriteReg(CONFIG, self.ReadReg(CONFIG) & ~PWR_UP)
        return 1 if status & TX_DS else 2
    
    
if __name__=='__main__':
    spi0 = SPI(1, baudrate=1000000, polarity=0, phase=0)
    spi0.init(
        baudrate=1000000,  # 速率
        polarity=0,        # 时钟极性
        phase=0,           # 时钟相位
        bits=8,            # 每个字节的位数
        firstbit=SPI.MSB, # 最先发送高位
        sck=machine.Pin(14),           # SCK 引脚
        mosi=machine.Pin(13),         # MOSI 引脚
        miso=machine.Pin(12)          # MISO 引脚
    )
    n=NRF24L01(spi0)
