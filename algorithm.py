import math
import urandom

def RandomString(length=4):
    random_bytes = urandom.getrandbits(8 * length).to_bytes(length, 'little')
    random_string = ''.join(['{:02x}'.format(byte) for byte in random_bytes])
    return random_string

class KalmanFilter:
    def __init__(self, procCov=0.1, monitorCov=0.1):
        self.procCov = procCov
        self.monitorCov = monitorCov
        self.predictVal = 0.0
        self.predictErr = 1.0
        self.K=0.0

    def Update(self, measuredVal=0.0):
        # 预测步骤
        predictVal = self.predictVal
        predictErr = self.predictErr

        # 更新步骤
        self.K = predictErr / (predictErr + self.monitorCov)
        self.predictVal = predictVal + self.K * (measuredVal - predictVal)
        self.predictErr = (1 - self.K) * predictErr
        return self.predictVal

    def Predict(self,transVal=0.0):
        # 预测下一个状态
        self.predictVal = self.predictVal+transVal
        self.predictErr = self.predictErr + self.procCov


