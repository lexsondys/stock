# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 14:34:20 2020

@author: shenlei
统计股票价格的分布区间
"""
import datetime
import os
import numpy as np
import mylib.tdx as tdx

fileName = "e:\\workspace\\temp\\sh600089.day"


def statisticStockPrice(stockList,mDay):
    statisticResult = np.zeros((21))
    stockCount = 0
    for stockCode in stockList:
        price = tdx.readClosePrice(stockCode,mDay)
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
    stockFileName = "D:\\tdx_swzd\\T0002\\export\\沪深Ａ股20200729.txt"

    dstFileName = "e:\\workspace\\temp\\stockprice1.txt"

    tDateTime = datetime.datetime.strptime(startDateStr,'%Y%m%d')
    startDate = tDateTime.date()
    tDateTime = datetime.datetime.strptime(endDateStr,'%Y%m%d')
    endDate = tDateTime.date()
    dstFile = open(dstFileName,"w",encoding='gbk')
    dstFile.write("日期\t[0,5)\t[5,10)\t[10,15)\t[15,20)\t[20,25)\t[25,30)\t[30,35)\t[35,40)")
    dstFile.write("\t[40,45)\t[45,50)\t[50,55)\t[55,60)\t[60,65)\t[65,70)\t[70,75)\t[75,80)")    
    dstFile.write("\t[80,85)\t[85,90)\t[90,95)\t[95,100)\t[100,)\t个数\n")

    days = endDate.__sub__(startDate).days + 1
    statisticResultList = np.zeros((days, 21))    
    stockList=tdx.readStockList(stockFileName)
    stockCountList = np.zeros((days))
    for stockCode in stockList:
        print(stockCode,end=";")
        priceList = tdx.readClosePrice(stockCode,startDate,endDate)
        for index in range(days):
            if priceList[index] > 0 :
                pIndex = int(priceList[index]/5)
                if pIndex >= 20:
                    pIndex = 20
                statisticResultList[index,pIndex] += 1
                stockCountList[index] += 1

    for index in range(days):
        if stockCountList[index] < 10:
            continue
        tempDate = startDate + datetime.timedelta(index)
        dstFile.write(tempDate.isoformat())
        statisticResultList[index] = statisticResultList[index] / stockCountList[index] 
        for ratio in statisticResultList[index]:
            dstFile.write("\t{:.2f}%".format(ratio*100))
        dstFile.write("\t{}\n".format(int(stockCountList[index])))    
    dstFile.close()