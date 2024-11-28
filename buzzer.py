from machine import Pin, PWM
import time

class Buzzer:
    def __init__(self, pin, inverse=False):
        """ 初始化蜂鸣器，设置PWM引脚 """
        self.free_val=0
        if inverse: self.free_val=1023
        self.buzzer = PWM(Pin(pin), freq=250000, duty=512)  # 默认频率1000Hz，占空比50%
        self.buzzer.duty(self.free_val)

    def Beep(self, freq=1000, always=False,duration=0.5):
        """ 发出指定频率和持续时间的声音 """
        self.buzzer.freq(freq)  # 设置频率
        self.buzzer.duty(512)         # 设置占空比为50%
        if not always:
            time.sleep(duration)          # 持续时间
            self.Stop()           # 停止声音

    def Stop(self):
        """ 停止蜂鸣器发声 """
        self.buzzer.freq(250000)
        self.buzzer.duty(self.free_val)

    def Melody(self, melody):
        """ 播放指定的音符列表 """
        for frequency, duration,interval  in melody:
            self.Beep(frequency, False, duration)
            time.sleep(interval)  # 音符之间的间隔

# 示例用法
if __name__ == "__main__":
    # 创建Buzzer对象，连接到GPIO 23
    my_buzzer = Buzzer(23)

    # 定义一个简单的旋律 (频率, 持续时间)
    melody = [
        (440, 0.5, 0.2),  # A4
        (523, 0.5, 0.2),  # C5
        (587, 0.5, 0.2),  # D5
        (659, 0.5, 0.2),  # E5
    ]

