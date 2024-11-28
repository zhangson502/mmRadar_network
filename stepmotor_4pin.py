from machine import Pin
import time

class StepMotor_4Pin:
    '''
    4线步进电机驱动
    '''
    def __init__(self,A=2,B=4,C=17,D=16):
        '''
        定义引脚
        '''
        self.Pins=[Pin(A, Pin.OUT),Pin(B, Pin.OUT),Pin(C, Pin.OUT),Pin(D, Pin.OUT)]
        #引脚缓存状态
        self.motor_states = [
            [1, 0, 0, 1], # 第1象限
            [1, 1, 0, 0], # 第2象限
            [0, 1, 1, 0], # 第3象限
            [0, 0, 1, 1], # 第4象限
        ]
        self.stop_state=[0,0,0,0]
        self.distance=0.0
        self.step_id=0
        
    def SetState(self,states=[1,0,0,1]):
        '''
        设置4个驱动脚状态
        '''
        for i in range(4):
            self.Pins[i].value(states[i])
            
    def TransPhase(self,direction=1,interval=5):
        '''
        变更相位
        '''
        phase=self.step_id%4
        self.SetState(self.motor_states[phase])
        time.sleep_ms(interval)
        self.step_id+=direction
    
    def Move(self,steps=100,direction=1,interval=7):
        '''
        转动步进电机
        '''
        for i in range(steps):
            self.TransPhase(direction,interval)
    
    def Free(self):
        '''
        释放步进电机
        '''
        self.SetState(self.stop_state)
    
    
        