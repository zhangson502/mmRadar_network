import network
import usocket as socket
import time
import ujson as json
from machine import Pin
from firmware.file_manager import Memory
from firmware.algorithm import RandomString
#coding=utf-8
import urandom
class Wifi:
    def __init__(self, default_ssid="CodPi-", default_password="12345678", config_file="wifi_config.json"):
        """
          初始化过程，开启一个AP，并禁用STA
        """
        self.staConnected=False
        self.ssid=default_ssid+RandomString()
        self.static_ssid=default_ssid
        self.passwd=default_password
        self.config_file = config_file
        self.ap = network.WLAN(network.AP_IF)
        self.sta=network.WLAN(network.STA_IF)
        self.sta.active(True)
        
    def DecodeUrl(self,url):
        url = url.replace("+", " ")
        parts = url.split('%')
        
        if len(parts) == 1:
            return url
        result = bytes(parts[0].encode('utf-8'))
                       
        for item in parts[1:]:
            char = bytes.fromhex(item[:2])
            char+=item[2:]
            print(item,char)
            result+=char
        return result
    
    def SetAP(self,active=True):
      """
        AP开关
      """
      self.ap.active(active)
    
    def ConnectSTA(self,ssid, password,attemps=60,relay=100):
        """
          连接到STA网络
        """
        self.sta.active(True)
        self.sta.connect(ssid, password)
        for i in range(attemps):
          time.sleep_ms(relay)
          if self.sta.isconnected():
           self.staConnected=True
           return True
        self.staConnected=False
        return False
        
    def Scan(self):
        """
          扫描附近网络
        """
        self.sta.active(True)
        ssid_list = [ssid.decode('utf-8') for ssid,_,_,_,_,_ in self.sta.scan()]
        ret_list=[]
        # 去除空表
        for i in range(len(ssid_list)): 
          if ssid_list[i] !='': 
            ret_list.append(ssid_list[i])
        #self.sta.active(False)
        return ret_list

    def ManualConnect(self):
        """
          手动连接STA
        """
        self.SetAP(True)
        self.sta.active(False)
        self.ap.config(essid=self.ssid, password=self.passwd)
        time.sleep_ms(2000)
        self.staConnected=False
        self.apServer= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.html = Memory().Read("/firmware/connect_wifi.ht")
        self.html_ok=Memory().Read("/firmware/wifi_connected.ht")
        self.html_fail=Memory().Read("/firmware/wifi_fail.ht")
        self.apServer.bind(('192.168.4.1', 80))
        self.apServer.listen(5)
        while not self.staConnected:
            client, addr = self.apServer.accept()
            self.HttpHandler(client)
        time.sleep_ms(1000)
        self.apServer.close()
        self.ap.active(False)
    
    def AutoConnectSTA(self,cache='wifi_config.json'):
        """
          自动连接STA
        """
        if self.sta.isconnected(): return True 
        try:
            with open(cache,"r") as f:
                info = json.load(f)
                return self.ConnectSTA(info['ssid'],info['passwd'])
        except:
            return False
            
    def HttpHandler(self, client_socket):
        """
        手动联网服务
        """
        def Return(client_socket,ret):
          client_socket.sendall(ret)
          client_socket.close()
        ret=b"HTTP/1.1 200 OK\n\n"
        request = client_socket.recv(1024)
        request = str(request)
        ssid_start = request.find("ssid=") + 5
        ssid_end = request.find("&", ssid_start)
        ssid = request[ssid_start:ssid_end]
        
        if "connectwifi" in request:
            try:
                password_start = request.find("password=") + 9
                password_end = request.find(" ", password_start)
                password = request[password_start:password_end]
                ssid=self.DecodeUrl(ssid)
                print(ssid, password)
                if self.ConnectSTA(ssid, password): 
                  Return(client_socket,self.html_ok)
                  print("连接成功！")
                  with open(self.config_file, 'w+') as f:
                      json.dump({'ssid':ssid,'passwd':password},f)
                  self.staConnected=True
                  return
                else:
                    ret+=self.html_fail
            except Exception as e:
                ret+=self.html_fail
        elif "/scan" in request:
            ssid_list = self.Scan()
            ssid_options = ""
            for ssid in ssid_list:
                ssid_options += '<option value="{}">{}</option>'.format(ssid, ssid)
            ret+=self.html.format(ssid_options)
        else:
            ret+=self.html.format('')
        Return(client_socket,ret)   
        
    """
      WIFI下衍生的类
    """
    def UDPBroadCaster(self):
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
      return sock
      
    def UDPReceiver(self,iport=8889):
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      sock.bind(("0.0.0.0", iport))
      return sock
        
    def TCPServer(self,iport=8889):
      server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      server_socket.bind(('', iport)) 
      return server_socket
      
    def TCPClient(self):
      return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def BroadCastAddr(self,mode='sta'):
      if mode=='ap': ip=self.ap.ifconfig()[0]
      else: ip=self.sta.ifconfig()[0]
      ip_parts = ip.split('.')
      ip_parts[-1] = '255'
      return'.'.join(ip_parts)







