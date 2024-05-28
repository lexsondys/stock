# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 14:34:20 2020

@author: shenlei
"""
import datetime
import os
import numpy as np

fileName = "e:\\workspace\\temp\\sh600089.day"

TDXRS = 32;

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

def readStockList():
    stockFileName = "D:\\tdx_swzd\\T0002\\export\\沪深Ａ股20200729.txt"
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

def readClosePrice(stockCode, mDate):
    tdxShDayDir = "D:\\tdx_swzd\\vipdoc\\sh\\lday"
    SzDayDir = "D:\\tdx_swzd\\vipdoc\\sz\\lday"
#    tDateTime = datetime.datetime.strptime(dateStr,'%Y%m%d')
#    objectDate = tDateTime.date()
    objectDate = mDate
    if objectDate.isoweekday() == 6 or objectDate.isoweekday() == 7:
        return 0
    if int(stockCode) >= 600000 :
        fileName="{}\\sh{}.day".format(tdxShDayDir,stockCode)
    else:
        fileName="{}\\sz{}.day".format(SzDayDir,stockCode)
    try: 
        fsize = os.path.getsize(fileName)
    except FileNotFoundError:
#        print(stockCode,' file not found!')
        return 0
    srcFile = open(fileName, "rb")
    oneRow = srcFile.read(TDXRS)
    if len(oneRow) <=0 :
        print(stockCode," error 0!")
    launchDayInfo = dayInfo()
    launchDayInfo.read(oneRow)
    
    offset = objectDate.__sub__(launchDayInfo.m_date).days
    if offset < 0 :
        return 0
    offset = int(offset*4.5/7)
    while offset*TDXRS >= fsize:
        offset -= 1
    srcFile.seek(offset*TDXRS)
    oneRow = srcFile.read(TDXRS)
    if len(oneRow) <=0 :
        print(stockCode," error 1!")
    tmpDayInfo = dayInfo()
    tmpDayInfo.read(oneRow)
    while objectDate.__sub__(tmpDayInfo.m_date).days < 0:
        offset = srcFile.tell() - 10*TDXRS
        if offset < 0:
            offset = 0
        try :
            srcFile.seek(offset)
        except OSError:
            print(stockCode,offset)
        oneRow = srcFile.read(TDXRS)
        if len(oneRow) <=0 :
            print(stockCode," error 2!")
        tmpDayInfo = dayInfo()
        tmpDayInfo.read(oneRow)
#        print("| ",tmpDayInfo.m_date)
    findFlag = True
    while not tmpDayInfo.m_date.__eq__(objectDate):
        oneRow = srcFile.read(TDXRS)
        if len(oneRow) <=0 :
            findFlag = False
            break
#            return 0
        tmpDayInfo = dayInfo()
        tmpDayInfo.read(oneRow)
#        print(tmpDayInfo.m_date)
        if objectDate.__sub__(tmpDayInfo.m_date).days < 0:
            findFlag = False
            break
    srcFile.close()
    if findFlag:
#        print(tmpDayInfo.m_date, tmpDayInfo.m_closePrice)
        return tmpDayInfo.m_closePrice
    else:
#        print(stockCode,' Data of this date not found!')
        return 0

def statisticStockPrice(stockList,mDay):
    statisticResult = np.zeros((21))
    stockCount = 0
    for stockCode in stockList:
        price = readClosePrice(stockCode,mDay)
        if price <= 0.1 :
            continue
        stockCount += 1
        pIndex = int(price/5)
        if pIndex >= 20:
            pIndex = 20
#        if pIndex == 0:
#            print(stockCode,";",end = "")
        statisticResult[pIndex] += 1
#    statisticResult = statisticResult 
    if stockCount > 0:
        statisticResult = statisticResult / stockCount 
    return statisticResult,stockCount
    
def statisticPeriodPrice(startDateStr,endDateStr):
    dstFileName = "e:\\workspace\\temp\\stockprice.txt"

    tDateTime = datetime.datetime.strptime(startDateStr,'%Y%m%d')
    startDate = tDateTime.date()
    tDateTime = datetime.datetime.strptime(endDateStr,'%Y%m%d')
    endDate = tDateTime.date()
    dstFile = open(dstFileName,"w",encoding='gbk')
    dstFile.write("日期\t[0,5)\t[5,10)\t[10,15)\t[15,20)\t[20,25)\t[25,30)\t[30,35)\t[35,40)")
    dstFile.write("\t[40,45)\t[45,50)\t[50,55)\t[55,60)\t[60,65)\t[65,70)\t[70,75)\t[75,80)")    
    dstFile.write("\t[80,85)\t[85,90)\t[90,95)\t[95,100)\t[100,)\t个数\n")
    
    stockList=readStockList()
    while endDate.__sub__(startDate).days >= 0:
        result,stockCount = statisticStockPrice(stockList,startDate)
        if stockCount < 10:
            startDate += datetime.timedelta(1)
            continue
        dstFile.write(startDate.isoformat())
        for ratio in result:
            dstFile.write("\t{:.2f}%".format(ratio*100))
        dstFile.write("\t{}\n".format(stockCount))    
        print(startDate.isoformat(),end=";")
        startDate += datetime.timedelta(1)
    dstFile.close()