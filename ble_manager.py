import bluetooth
import time



class Ble:
    
    def __init__(self,name='AppleZhang Device',perihp_key='Q36',auto_connect=True,callback=None):
        '''初始化'''
        self.ble = bluetooth.BLE()
        self.name=name
        self.callback=callback
        self.periph_key=perihp_key
        self.auto_connect=auto_connect
        self.dev_list=[]
        self.dat=[]
        self.conn=None
        self.Config()
        
    def active(self,status):
        '''开启关闭蓝牙'''
        self.ble.active(status)
        
    def Config(self):
        '''配置蓝牙'''
        self.active(True)
        self.ble.config(gap_name=self.name)
        self.ble.irq(self.Handler)
        
    def ScanDev(self,duration=8000):
        '''扫描设备'''
        self.dev_list=[]
        self.ble.gap_scan(duration)
        
    def Advertise(self,interval=100,connectable=True,stop=False):
        '''开始广播'''
        payload=b'\x02\x01\x06' # 0x02: 2字节，0x01:标志位，0x06: 普通蓝牙
        payload+=b'\x03\x03\x05\x18' # 3字节，设备类型，1805表示人机接口设备
        payload+=bytearray([len(self.name)+1])
        payload+=b'\x09'
        payload+=self.name.encode('utf-8')
        print(payload)
        self.ble.gap_advertise(interval*1000, adv_data=payload)
        
    def Connect(self,addr):
        '''连接设备'''
        self.ble.gap_connect(0x00,addr)
        
        
        
    def Handler(self, event, data):
        '''事件处理函数'''
        if event == 1:
            #连接到设备
            #print("已连接到设备")
            pass
        elif event == 2:
            #断开连接设备
            #print("已断开连接")
            # 重新开始广播
            pass
            #ble.advertise()
        elif event==3:
            #print(data)
            pass
        elif event ==4:
            #print(data)
            pass
        
        elif event == 5:
            #扫描结果
            addr_type=data[0]
            dev={}
            if addr_type==0:
                dev['addr']=bytes(data[1])
                dev['adv']=bytes(data[4])
                if self.periph_key in dev['adv']:
                    if self.auto_connect:
                        self.Connect(dev['addr'])
                    else:
                        self.dev_list.append(dev)
                    
        elif event==6:
            pass
            #print("扫描完成")
        
        elif event ==7:
            self.conn,_,_=data
            self.ble.gap_pair(self.conn)
            #print("已连接到外设")
        elif event==18:
            self.dat=list(bytes(data[2]))
            
            
    
        
    
        

        
            
        
