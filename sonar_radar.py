from machine import Pin, time_pulse_us
import time

class Sonar:
    def __init__(self, trig_pin=4, echo_pin=2):
        self.trigger = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)

    def Distance(self):
        # 发送超声波脉冲
        self.trigger.value(1)
        time.sleep_us(10)
        self.trigger.value(0)
        
        # 等待回声
        pulse_time = time_pulse_us(self.echo, 1, 40000)  # 超时设为30毫秒
        
        # 将回声时间转换为距离（单位：厘米）
        distance = pulse_time * 0.000343 / 2  # 声波在空气中的传播速度约为343米/秒
        return distance




