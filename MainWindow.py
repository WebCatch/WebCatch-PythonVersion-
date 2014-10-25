# -*- coding: utf-8 -*-

"""
Module implementing Dialog.
"""
import PyQt4, PyQt4.QtGui,  sys
import urllib2
import re
import bs4
from PyQt4.QtGui import QDialog
from PyQt4.QtCore import pyqtSignature
import sip
from PyQt4.QtGui  import *  
from PyQt4.QtCore import *

from Ui_MainWindow import Ui_Dialog

class Dialog(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
    def QTout(self, tmp):
        self.teExctData.append(unicode(tmp, 'utf-8', 'ignore'))
    def ExctType1(self, doc, soup):
        #Exact Web Page Type 1         
        # find the most frequent class
        extTstList = soup.findAll('div', {'class' : re.compile(r'[^"]*info[^"]*')})
        hashval = {}
        mfreqcls = ''
        maxv = 0
        for tmpTst in extTstList:
            tmpStr = unicode(tmpTst)
            tmpKey = re.search(r'[^"]*info[^"]*', tmpStr).group()
            if hashval.has_key(tmpKey):
                hashval[tmpKey] += 1
                tmpv = hashval[tmpKey]
                if tmpv > maxv:
                    maxv = tmpv
                    mfreqcls = tmpKey
            else:
                hashval[tmpKey] = 1
                if 1 > maxv:
                    maxv = 1
                    mfreqcls = tmpKey
        #use the most frequent class to work
        extResList = soup.findAll('div', {'class' : mfreqcls})
        #saleprice = []
        #skuname = []
        #skucode = []
        superTab = []
        resCols = []
        #find possible cols
        col = 0
        hashval = {}
        for tmpRes in extResList:
            tmpStr = unicode(tmpRes)
            tmpColRePtnResList = re.findall(r'([^ ]*)="([^"]*)"', tmpStr)
            #find identical cals
            for tmpColRePtnRes in tmpColRePtnResList:
                if hashval.has_key(tmpColRePtnRes[0]):
                    hashval[tmpColRePtnRes[0]] += 1
                else:
                    hashval[tmpColRePtnRes[0]] = 1
                    if tmpColRePtnRes[0] != 'class':
                        resCols.append(tmpColRePtnRes[0])
                        col += 1
            break
        row = 0
        for tmpRes in extResList:
            #saleprice="(\d*\.\d*)"
            #print tmpRes
            tmpStr = unicode(tmpRes)
            #print tmpStr
            #saleprice.append(re.search(r'salesprice="([^"]*)"', tmpStr).group(1))
            superTab.append([])
            for curCol in resCols:
                if hashval.has_key(curCol) and hashval[curCol] == 1:
                    superTab[row].append(re.search(curCol+r'="([^"]*)"', tmpStr).group(1))
            #skuname.append(re.search(r'([^ ]*)="([^"]*)"', tmpStr).group(2))
            #skucode.append(re.search(r'([^ ]*)="([^"]*)"', tmpStr).group(2))
            row += 1
            #skuname="([^"]*)"
            #skucode="([^"]*)"
        #resdata = '\n'.join(tsstr.encode('utf-8') in skuname)
        #resdata = skuname[0].encode('utf-8')
        self.tableWidget.setRowCount(row)
        self.tableWidget.setColumnCount(col)
        self.tableWidget.setHorizontalHeaderLabels(resCols)
        #fuc  = "中国\n中国"
        for i in range(row):
            #print saleprice[i].encode('UTF-8')
            #print skuname[i].encode('UTF-8')
            for j in range(col):
                self.newItem = QTableWidgetItem(unicode(superTab[i][j].encode('utf-8'), 'utf-8', 'ignore'))
                self.QTout(superTab[i][j].encode('utf-8') )
                self.tableWidget.setItem(i, j, self.newItem)
                #resdata = resdata + fuc # + skuname[i].encode('utf-8')
            #print skucode[i].encode('UTF-8')
        #print resdata
        #self.teExctData.setText(resdata.encode('gbk', 'ignore'))
        #tmp1 = resdata.encode('utf-8', 'ignore')
        #tmp2 = unicode(resdata.encode('utf-8', 'ignore'), 'utf-8', 'ignore')
        #tmp3 = '中文'
        #self.teExctData.setText(unicode(resdata.encode('utf-8', 'ignore'), 'utf-8', 'ignore'))
        #self.teExctData.setText(unicode(resdata, 'utf-8', 'ignore'))
    @pyqtSignature("")
    def on_btnExct_clicked(self):
        """
        Exact Web Page
        """
        qsurl = self.leURL.text()
        url = unicode (qsurl) 
        req = urllib2.Request(url)
        con = urllib2.urlopen(req)
        doc = con.read()
        con.close()
        #docuni = unicode(doc,'UTF-8')
        soup = bs4.BeautifulSoup(doc)   #get soup from HTML code
        
        self.ExctType1(doc, soup)
       
        file = open('webdata.txt', 'w')
        file = file.write(doc)
        
        
    
    @pyqtSignature("")
    def on_btnConnect_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_btnSave_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
if __name__ == "__main__":
    app = PyQt4.QtGui.QApplication(sys.argv)

    dlg = Dialog()

    dlg.show()

    sys.exit(app.exec_())
