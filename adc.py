from machine import ADC, Pin
import time

class ADCReader:
    '''
    封装ADC检测
    '''
    CONFIG={"1.1v":ADC.ATTN_0DB,"1.5v":ADC.ATTN_2_5DB,"2.2v":ADC.ATTN_6DB,"3.9v":ADC.ATTN_11DB}
    LIMIT={"1.1v":1.1,"1.5v":1.5,"2.2v":2.2,"3.9v":3.9}
    def __init__(self,pin=33,v_range='3.9v'):
        
        self.adc=ADC(pin)
        self.SetRange(v_range)
    
    def SetRange(self,v_range='1.5v'):
        '''
        设置量程
        '''
        self.adc.atten(ADCReader.CONFIG[v_range])
        self.adc.width(ADC.WIDTH_12BIT)
        self.v_range=ADCReader.LIMIT[v_range]
    
    def ReadVoltage(self,amp=3.0):
        '''
        读取电压值
        '''
        raw=self.adc.read()
        return raw*amp*self.v_range/4096
        
        
        
        