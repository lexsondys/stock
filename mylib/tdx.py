# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 16:26:52 2021

@author: Administrator
"""
import datetime
import os
import numpy as np
from copy import deepcopy
import re

TDXRS = 32;
dayRootDir = "E:\\workspace\\temp\\港澳资讯F10"

class dayInfo:
    m_date = datetime.date(1990,1,1)
    m_openPrice = 0.0
    m_highPrice = 0.0
    m_lowPrice = 0.0
    m_closePrice = 0.0
    m_money = 0
    m_volume = 0
    def __init__(self):
        self.m_date = datetime.date(1990,1,1)
        self.m_openPrice = 0.0
        self.m_highPrice = 0.0
        self.m_lowPrice = 0.0
        self.m_closePrice = 0.0
        self.m_money = 0
        self.m_volume = 0        
    def read(self,oneRow):
        tmpInt = oneRow[3]*256*256*256 + oneRow[2]*256*256 + oneRow[1]*256+oneRow[0] #one int compose by 4 char
        nYear = int(tmpInt/10000)
        tmpInt = tmpInt%10000
        nMon = int(tmpInt/100)
        nDay = int(tmpInt%100)
        self.m_date = datetime.date(nYear,nMon,nDay)
        self.m_closePrice = (oneRow[19]*256*256+oneRow[18]*256*256+oneRow[17]*256+oneRow[16])/100 #1000.0f;
        self.m_openPrice = (oneRow[7]*256*256*256+oneRow[6]*256*256+oneRow[5]*256+oneRow[4])/100
        self.m_highPrice = (oneRow[11]*256*256*256+oneRow[10]*256*256+oneRow[9]*256+oneRow[8])/100
        self.m_lowPrice = (oneRow[15]*256*256*256+oneRow[14]*256*256+oneRow[13]*256+oneRow[12])/100
        self.m_closePrice = (oneRow[19]*256*256+oneRow[18]*256*256+oneRow[17]*256+oneRow[16])/100
        self.m_money = oneRow[23]*256*256*256+oneRow[22]*256*256+oneRow[21]*256+oneRow[20]
        self.m_volume = oneRow[27]*256*256*256+oneRow[26]*256*256+oneRow[25]*256+oneRow[24]

def readStockList(stockFileName):
    stockList = set()
    stockFile = open(stockFileName,"r",encoding='gbk')
    line = stockFile.readline() #跳过标题行
    line = stockFile.readline()
    while line:
        if len(line.strip()) == 0:
            line = stockFile.readline()
            continue
        oneRow  = line.split("\t")
        if len(oneRow) <= 5:
            line = stockFile.readline()
            continue
        stockList.add(oneRow[0])
        line = stockFile.readline()
    return stockList

'''
    titleInfo = {'code':{'title':'代码'},
                 'name':{'title':'名称'},
                 'cirMktVle':{'title':'流通市值'},
                 'per':{'title':'市盈(动)'},
                 'pbr':{'title':'市净率'},
                 'trade':{'title':'细分行业'}}
    retrun:{'code':'300399','name':'润和软件','cirMktVle':'90',
                 'per':'40','pbr':'3','trade':'软件'}
'''    
def readStockInfoList(stockListFileName, titleInfo):
    stockList = list()
    try:
        stockFile = open(stockListFileName,"r",encoding='gbk')
    except Exception as e:
        print(e)
        return None
    line = stockFile.readline() #跳过标题行
    oneRow = line.split("\t")
    keyList = list(titleInfo.keys())
    fCount = 0
    for key in keyList:
        posi = 0
        for titleStr in oneRow:
            titleStr = titleStr.strip()
            if titleInfo[key]['title'] == titleStr:
                titleInfo[key]['posi'] = posi
                fCount += 1
                break
            posi += 1
    if fCount < len(keyList):
        print("read title in {} error!".format(stockListFileName))
        return None
    line = stockFile.readline()
    stockInfo = dict.fromkeys(keyList)
    while line:
        if len(line.strip()) == 0:
            line = stockFile.readline()
            continue
        oneRow  = line.split("\t")
        if len(oneRow) <= 10:
            line = stockFile.readline()
            continue
        for key in keyList:
            stockInfo[key] = oneRow[titleInfo[key]['posi']]
        tempStock = deepcopy(stockInfo)
        stockList.append(tempStock)
        line = stockFile.readline()
    return stockList


def readClosePrice(stockCode, startDate,endDate):
#    dayRootDir = "D:\\tdx_swzd\\vipdoc"
    tdxShDayDir = os.path.join(dayRootDir,"sh\\lday")
    tdxSzDayDir = os.path.join(dayRootDir,"sz\\lday")
#    tDateTime = datetime.datetime.strptime(dateStr,'%Y%m%d')
#    objectDate = tDateTime.date()

    days = endDate.__sub__(startDate).days
    priceList = np.zeros((days+1))

    if int(stockCode) >= 600000 :
        fileName="{}\\sh{}.day".format(tdxShDayDir,stockCode)
    else:
        fileName="{}\\sz{}.day".format(tdxSzDayDir,stockCode)
    try: 
        fsize = os.path.getsize(fileName)
    except FileNotFoundError:
#        print(stockCode,' file not found!')
        return priceList
    srcFile = open(fileName, "rb")
    oneRow = srcFile.read(TDXRS)
    if len(oneRow) <=0 :
        print(stockCode," error 0!")
    launchDayInfo = dayInfo()
    launchDayInfo.read(oneRow)
    offset = startDate.__sub__(launchDayInfo.m_date).days
    if offset < 0 :
        offset = 0
    offset = int(offset*4.5/7)
    while offset*TDXRS >= fsize:
        offset -= 1
    srcFile.seek(offset*TDXRS)
    oneRow = srcFile.read(TDXRS)
    if len(oneRow) <=0 :
        print(stockCode," error 1!")
    tmpDayInfo = dayInfo()
    tmpDayInfo.read(oneRow)
    while startDate.__sub__(tmpDayInfo.m_date).days < 0: #过头了，往回找
        offset = srcFile.tell() - 10*TDXRS
        if offset < 0:
            offset = 0
            srcFile.seek(offset)
            break
        srcFile.seek(offset)
        oneRow = srcFile.read(TDXRS)
        if len(oneRow) <=0 :
            print(stockCode," error 2!")
            break
        tmpDayInfo = dayInfo()
        tmpDayInfo.read(oneRow)
#        print("| ",tmpDayInfo.m_date)
    findFlag = True
    while tmpDayInfo.m_date.__sub__(startDate).days < 0:
        oneRow = srcFile.read(TDXRS)
        if len(oneRow) <=0 :  #文件读完了
            findFlag = False
            break
        tmpDayInfo = dayInfo()
        tmpDayInfo.read(oneRow)
    if findFlag:
        while endDate.__sub__(tmpDayInfo.m_date).days >= 0:
            index = tmpDayInfo.m_date.__sub__(startDate).days
            priceList[index] = tmpDayInfo.m_closePrice
            oneRow = srcFile.read(TDXRS)
            if len(oneRow) <=0 :
                break
            tmpDayInfo = dayInfo()
            tmpDayInfo.read(oneRow)
    srcFile.close()
    return priceList

def getPriceChangeRate(stockCode, startDate,endDate):
    priceList = readClosePrice(stockCode, startDate,endDate)
    for closePrice in priceList:
        if closePrice > 0.0 :
            startPrice = closePrice
            break
    for closePrice in reversed(priceList):
        if closePrice > 0.0 :
            endPrice = closePrice
            break
    if closePrice > 0.0:
        return (endPrice - startPrice)/startPrice
    else:
        return -2.0