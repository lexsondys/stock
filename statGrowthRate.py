# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 14:54:33 2021

@author: Administrator
从F10材料中统计业绩增长率
"""

import datetime
import os
import re
import mylib.tdx as tdx  

f10RootDirName = "D:\\workspace\\港澳资讯F10"
stockListFileName = "D:\\workspace\\全部A股20240205.txt"

def readGrowthRate(stockCode):
    patStr1 = '｜(.*)每股资本公积:(.*)营业收入\(万元\):(.*)同比增(.*)｜'
    patStr2 = '｜(.*)每股未分利润:(.*)净利润\(万元\):(.*)同比增(.*)｜'
    patStr3 = '｜(.*)｜(.*)｜(.*)｜(.*)｜(.*)｜(.*)｜'
    patStr4 = '｜(.*)｜(.*)｜(.*)｜(.*)｜(.*)｜'
    result = {'Date':'','capital':'','revenue':'','profit':''}
    curProfitList = []
    lastProfitList = []
    fCount = 0
    if stockCode.isdecimal():
        if int(stockCode) >= 600000:
            f10FileName = os.path.join(f10RootDirName,"SHASE\\base")
        else:
            f10FileName = os.path.join(f10RootDirName,"SZNSE\\base")
        f10FileName = os.path.join(f10FileName,"{}.txt".format(stockCode))
    else: 
        return None
    try:
        f10File = open(f10FileName,"r",encoding='gb18030')
    except Exception as e:
        print(e)
        return None
    line = f10File.readline()
    CountFlag = False
    lCount = 0
    while line:
        matchObj = re.match(patStr1, line, re.M | re.I)
        if matchObj:
            result['Date'] = matchObj.group(1).strip()
            result['revenue'] = matchObj.group(4).strip()
            fCount += 1
        matchObj = re.match(patStr2, line, re.M | re.I)
        if matchObj:
            result['profit'] = matchObj.group(4).strip()
            fCount += 1
        matchObj = re.match(patStr3, line, re.M | re.I)
        if matchObj:
            if matchObj.group(1).find("流通A股(亿股)") >= 0:
                result['capital'] = matchObj.group(2).strip()
                fCount += 1
        if line.find(" ★近五年每股收益对比：") >= 0:
            CountFlag = True
        if CountFlag:
            lCount += 1
        if lCount == 5:
            matchObj = re.match(patStr4, line, re.M | re.I)
            if matchObj:
                for i in range(4):
                    curProfitList.insert(i,matchObj.group(i+2).strip())
            else:
                print("读取近五年每股收益对比错误")
        if lCount == 6:
            matchObj = re.match(patStr4, line, re.M | re.I)
            if matchObj:
                for i in range(4):
                    lastProfitList.insert(i,matchObj.group(i+2).strip())
            else:
                print("读取近五年每股收益对比错误")
        if fCount>=103 :
            break
        try:
            line = f10File.readline()
        except Exception as e:
            print(e)
            break            
    if fCount>=3:
#        growthStr = "{}\t{}\t{}\t{}".format(stockCode, result['Date'], 
#                     result['income'], result['profit'])
        return result
    else:
        return None



'''
读取近5年和近5个季度的的净利润增长率(%)
'''
def readProfiltGrowthRate(stockCode):
    patStr1 = '｜净利润增长率       ｜(.*)｜(.*)｜(.*)｜(.*)｜(.*)｜(.*)｜'
    fiveYearsProfitGrowthRate = ()
    fiveQuartersProfitGrowthRate = ()
    fCount = 0
    if stockCode.isdecimal():
        if int(stockCode) >= 800000:
            return None
        if int(stockCode) >= 600000:
            f10FileName = os.path.join(f10RootDirName,"SHASE\\base")
        else:
            f10FileName = os.path.join(f10RootDirName,"SZNSE\\base")
        f10FileName = os.path.join(f10FileName,"{}.txt".format(stockCode))
    else: 
        return None
    try:
        f10File = open(f10FileName,"r",encoding='gb18030')
    except Exception as e:
        print(e)
        return None
    line = f10File.readline()
    while line:
        line = line.replace('(%)','')
        matchObj = re.match(patStr1, line, re.M | re.I)
        if matchObj:
            if fCount == 0:
                fiveYearsProfitGrowthRate = matchObj.groups()
            else :
                fiveQuartersProfitGrowthRate = matchObj.groups()
            fCount += 1
        if fCount > 1 :
            break
        try:
            line = f10File.readline()
        except Exception as e:
            print(e)
            break            
    if fCount > 1:
        return fiveYearsProfitGrowthRate,fiveQuartersProfitGrowthRate
    else:
        return None

def statGrowthRate():
    tilteInfo = {'code':{'title':'代码'},
                 'name':{'title':'名称'},
                 'cirMktVle':{'title':'流通市值'},
                 'per':{'title':'市盈(动)'},
                 'pbr':{'title':'市净率'},
                 'trade':{'title':'细分行业'}}
    stockList = tdx.readStockInfoList(stockListFileName, tilteInfo)
    if stockList is None:
        return
    dstFileName =  dstFileName = "e:\\workspace\\temp\\growthrate0115.txt"
    dstFile = open(dstFileName,"w",encoding='gbk')
    dstFile.write("代码\t名称\t去年涨幅\t市盈率\t市净率\t日期\t流通股本\t流通市值\t营收增长率\t利率增长率\t细分行业\n")
    for stockInfo in stockList:
        print(stockInfo["code"],end=";")
        growthRate = readGrowthRate(stockInfo["code"])
        startDate = datetime.date(2020,1,1)
        endDate = datetime.date(2020,12,31)
        priceChangeRate = tdx.getPriceChangeRate(stockInfo["code"], startDate,endDate)
        if growthRate is not None and priceChangeRate > -2.0 :
            dstFile.write("{}\t{}\t{}%\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(stockInfo["code"], 
                          stockInfo["name"], format(priceChangeRate*100,'.2f'), 
                          stockInfo["per"], stockInfo["pbr"],growthRate['Date'],
                          growthRate['capital'], stockInfo["cirMktVle"],
                          growthRate['revenue'], growthRate['profit'], 
                          stockInfo["trade"]))
    dstFile.close()
    return

def getPredict(stockCode):
    patStr = '预计2020年'
    if stockCode.isdecimal():
        if int(stockCode) >= 600000:
            f10FileName = os.path.join(f10RootDirName,"SHASE\\base")
        else:
            f10FileName = os.path.join(f10RootDirName,"SZNSE\\base")
        f10FileName = os.path.join(f10FileName,"{}.txt".format(stockCode))
    else: 
        return None
    try:
        f10File = open(f10FileName,"r",encoding='gb18030')
    except Exception as e:
        print(e)
        return None
    line = f10File.readline()
    fFlag = False
    lCount = 0
    while line:
        if line.find(patStr) >= 0:
            fFlag = True
            break
        if lCount>=100 :
            break
        try:
            line = f10File.readline()
            lCount += 1
        except Exception as e:
            print(e)
            break            
    return fFlag

def statPredict():
    stockList = tdx.readStockList(stockListFileName)
    if stockList is None:
        return
    dstFileName =  dstFileName = "e:\\workspace\\temp\\predict0115.txt"
    dstFile = open(dstFileName,"w",encoding='gbk')
    for stockCode in stockList:
        print(stockCode,end=";")
        if getPredict(stockCode) :
            dstFile.write("{}\n".format(stockCode))
    dstFile.close()
    return

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
            
'''
寻找利润增长的公司
'''
titleInfo = {'code':{'title':'代码'},
                 'name':{'title':'名称'},
                 'cirMktVle':{'title':'流通市值'},
                 'per':{'title':'市盈(动)'},
                 'pbr':{'title':'市净率'},
                 'trade':{'title':'细分行业'}}
def findGrowCorp():
    stockInfoList=tdx.readStockInfoList(stockListFileName, titleInfo)
    if stockInfoList is None:
        return
    dstFileName =  dstFileName = "d:\\workspace\\profitgrowcrop0206.txt"
    dstFile = open(dstFileName,"w",encoding='gbk')
    count = 0
    for stockInfo in stockInfoList:
        score1 = 0
        score2 = 0
        try :
            fiveYearsProfitGrowthRate,fiveQuartersProfitGrowthRate = readProfiltGrowthRate(stockInfo['code'])
            if fiveYearsProfitGrowthRate and fiveQuartersProfitGrowthRate:
                for profitGrowthRate in fiveYearsProfitGrowthRate:
                    profitGrowthRate = profitGrowthRate.replace('(P)','')
                    profitGrowthRate = profitGrowthRate.replace('(L)','')
                    if is_float(profitGrowthRate) :
                        if float(profitGrowthRate) > 5.0:
                            score1 += 1
                for profitGrowthRate in fiveQuartersProfitGrowthRate :
                    profitGrowthRate = profitGrowthRate.replace('(P)','')
                    profitGrowthRate = profitGrowthRate.replace('(L)','')
                    if is_float(profitGrowthRate) :
                        if float(profitGrowthRate) > 5.0 :
                            # print(profitGrowthRate)
                            score2 += 1
        except Exception as e:
            print(stockInfo['code'])
        if score2 >= 5 :
            dstFile.write("{}\t{}\t{}\t{}\n".format(stockInfo['code'],stockInfo['name'],score1,score2))
        count += 1
        # if count > 2000:
        #     break
    dstFile.close()
    