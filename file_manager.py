import uos
import gc
import os
import urequests as requests
class Memory:
  
  def __init__(self):
    pass
  
  def IsFile(self,path):
    try:
      stat = uos.stat(path)
      return stat[0] & 0x4000 == 0
    except OSError as e:
        return False

# 检查路径是否是文件夹
  def IsDir(self,path):
    try:
      stat = uos.stat(path)
      return stat[0] & 0x4000 != 0
    except OSError as e:
        return False
        
  def GetSize(self,file_path):
    try:
        file_stat = uos.stat(file_path)
        return file_stat[6]  # 索引6对应文件大小
    except OSError as e:
        return 0    
        
  def ListFiles(self,dir=''):
    # 列举所有文件
    ret={}
    for file in os.listdir(dir):
      if self.IsDir(file): ret[file]=self.ListFiles(file+'/')
      else: ret[file]=self.GetSize(dir+file)
    return ret
  def CheckFile(self,file,path):
    if file in os.listdir(path): return True
    return False
    
  def Save(self,dat,file):
    try:
      with open(file, 'w+') as f:
        f.write(dat)
        return True
    except:
      return False
  def Read(self,file):
    #try:
    with open(file, 'rb') as f:
        content = f.read()
    return content
    #except:
    #  return ""

  def DiskFree(self):
    disk_stat = uos.statvfs('/')
    disk_free = disk_stat[0] * disk_stat[3]  # 块大小 * 剩余块数
    return disk_free
  
  def MemFree(self):
    return gc.mem_free()
    
  def DiskUsage(self):
    return 1.0-self.DiskFree()/2097152.0
      
  def MemUsage(self):
    return gc.mem_alloc()*1.0/(gc.mem_free() + gc.mem_alloc())
  
  def ShowUsage(self,oled=None):
    if oled==None: return
    dUsage=int(self.DiskUsage()*100.0)
    mUsage=int(self.MemUsage()*100.0)
    oled.fill(0)
    oled.text(s="Mem & Disk Usage",x=0,y=4)
    oled.text(s="C: {:d}% {}K".format(dUsage,int(self.DiskFree()/1024)),x=10,y=20)
    oled.rect(14,30,100,5)
    oled.text(s="Mem:{:d}% {}K".format(mUsage,int(self.MemFree()/1024)),x=10,y=42)
    oled.rect(14,52,100,5)
    oled.rect(14,30,dUsage,5,f=True)
    oled.rect(14,52,mUsage,5,f=True)
    oled.show()
    
  def DeleteFolder(self,folder):
    # 获取文件夹中的所有项目
    if not folder in os.listdir(): return
    items = os.listdir(folder)
    for item in items:
        # 构建项目的完整路径
        item_path = folder+'/'+item
        os.remove(item_path)
    # 删除空文件夹
    os.rmdir(folder) 
  
  def MoveFile(self,source_path,destination_path,oled=None):
    # 移动文件
    if oled!=None:
      oled.fill(0)
      oled.text(s="Loading...",x=20,y=20)
      oled.rect(14,40,100,5)
      oled.show()
    source_size = os.stat(source_path)[6]
    with open(source_path, 'rb') as source_file:
      with open(destination_path, 'wb+') as destination_file:
          total_written = 0
          while True:
              data = source_file.read(1024)  # 读取512字节块
              if not data:
                  break
              destination_file.write(data)  # 写入到目标文件
              total_written += len(data)
              progress = int(total_written / source_size* 100)
              if oled!=None:
                oled.rect(14,40,progress,5,f=True)
                oled.show()
  def MoveFolder(self,source, destination):
    if destination in os.listdir(): self.DeleteFolder(destination)
    os.mkdir(destination)
    for item in os.listdir(source):
      source_path = source+'/'+item
      destination_path = destination+'/'+item
      self.MoveFile(source_path,destination_path) 
  
  def DownloadFile(self, url, local_filename):
    """
      把网络文件下载到本地
    """
    response = requests.get(url, stream=True)
    with open(local_filename, 'wb+') as f:
      while True:
        try:
          content_byte = response.raw.read(1024)
          f.write(content_byte)
          if len(content_byte) == 0: break
        except Exception as e:
          return False
    response.close()
    return True

  def ReadNet(self,file,path='http://www.seafishpi.com/resources/tunapi'):
    """
        下载小型网络资源
    """
    return requests.get(path+file).content





