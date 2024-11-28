def SplitJsonStr(jsonStr):
    '''
    鎷嗗垎绮樺寘鐨刯son鏁版嵁
    :param jsonStr:
    :return:
    '''
    ret=[]
    while True:
        index = jsonStr.find('}{')
        if index != -1:
            ret.append(jsonStr[0:index+1])
            jsonStr=jsonStr[index+1:]
        else:
            if '{' in jsonStr:
                ret.append(jsonStr)
            return ret
