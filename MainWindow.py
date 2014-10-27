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
from PyQt4 import QtCore, QtGui

from Ui_MainWindow import Ui_Dialog
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
def GetSimpleStrFromLabelStr( LabelStr):     
    retStr = ''
    if re.search(r'\<([A-Za-z0-9]+)[^\>]*>([\s\S]*?)\</(\1)\>', LabelStr) == None:
        retStr = LabelStr
        return retStr.strip()
    else:
        SubLabelStrs = re.findall(r'\<([A-Za-z0-9]+)[^\>]*>([\s\S]*?)\</(\1)\>', LabelStr)
        i = 0
        for ch in LabelStr.strip():
            if ch == '<':
                retStr += LabelStr[0:i]
                break;
            i += 1
        for i in range(len(SubLabelStrs)):
            #print retStr
            #print GetSimpleStrFromLabelStr(SubLabelStrs[i][1].strip())           
            retStr += GetSimpleStrFromLabelStr(SubLabelStrs[i][1].strip())
            print retStr
        i = len(LabelStr.strip()) - 1
        while (LabelStr[i] != '>'):
            i -= 1
        retStr += LabelStr[i + 1: len(LabelStr.strip()) ]
    return retStr
class Dialog(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    tabID = 1
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
    def QTout(self, tmp):
        self.teExctData.append(unicode(tmp, 'utf-8', 'ignore'))
        
    #init keyword type 1
    def InitKeyWordType1(self, reptns):
        reptns.append(r'([^"]*[Ii][Nn][Ff][Oo][^"]*)')
        reptns.append(r'([^"]*[Gg][oO][oO][Dd][Ss][^"]*)')
        reptns.append(r'([^"]*[Ii][Tt][Ee][Mm][^"]*)')
        reptns.append(r'([^"]*[Pp][Rr][Oo][Dd][^"]*)')
        reptns.append(r'([^"]*[Ll][Ii][Ss][Tt][^"]*)')
        
  
    #get Soups with keywords
    def MakeSoupLists(self,  extTstLists, reptns, soup):
        for tmpreptn in reptns:
            extTstLists.append(soup.findAll('div', re.compile(tmpreptn)))
    
    #find most freqency class
    def FindMostFreqCls(self, reptns, extTstLists, hashval):
        mfreqcls = ''
        maxv = 0
        for i in range(len(reptns)):
            for tmpTst in extTstLists[i]:
                tmpStr = unicode(tmpTst)
                tmpKey = re.search(reptns[i], tmpStr).group()
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
        return mfreqcls
    
     #find possible cols    
    def FindPossibleCols(self, extResList, hashval, resCols, resCols2):
        for tmpRes in extResList:
            tmpStr = unicode(tmpRes)
            tmpColRePtnResList = re.findall(r'''\s([A-Za-z][^\s]*)=["']([^'"]*)['"]''', tmpStr)
            tmpColRePtnResList2 = re.findall(r'''\<([^\s]*)\s+[^\>]*class=['"]([^\>"']*)['"][^\>]*\>([^\>\<]*?)\</(?:\1)\>|\<([^\s]*)\s+[^\>]*id=['"]([^\>'"]*)['"][^\>]*\>([^\>\<]*?)\</(?:\4)\>''', tmpStr)
            #tmpColRePtnResList3 = re.findall(r'''\<a[^\>]*\>([^\<\>]*?)\</a\>''',  tmpStr)
            #find identical cols Type 1
            for tmpColRePtnRes in tmpColRePtnResList:
                if hashval.has_key(tmpColRePtnRes[0]):
                    hashval[tmpColRePtnRes[0]] += 1
                else:
                    hashval[tmpColRePtnRes[0]] = 1
                    if tmpColRePtnRes[0] != 'class':
                        resCols.append(tmpColRePtnRes[0])
            #find identical cols Type 2            
            for tmpColRePtnRes in tmpColRePtnResList2:
                tmplist = [1, 4]
                for idkey in tmplist:
                    if tmpColRePtnRes[idkey].strip() != '':
                        if hashval.has_key(tmpColRePtnRes[idkey]):
                            hashval[tmpColRePtnRes[idkey]] += 1
                        else:
                            hashval[tmpColRePtnRes[idkey]] = 1      
                            if tmpColRePtnRes[idkey+1].strip() != "":
                                resCols2.append(tmpColRePtnRes[idkey])
    
    #fill the super table  and return row, col
    def MakeSuperTab(self, extResList, superTab, resCols, resCols2, hashval):
        row = 0
        col = 0
        for tmpRes in extResList:
            tmpStr = unicode(tmpRes)
            superTab.append([])
            #assign with way 1
            for curCol in resCols:
                if curCol.find('(') != -1 or curCol.find(')') != -1:
                    continue; #invalid expression
                
                if hashval.has_key(curCol) :
                    #print curCol+r'="([^"]*)"'
                    #print re.search(curCol+r'="([^"]*)"', tmpStr)
                    if re.search(curCol+r'''=["']([^'"]*)['"]''', tmpStr) != None:
                        superTab[row].append(re.search(curCol+r'''=["']([^'"]*)['"]''', tmpStr).group(1))
                    else:
                        superTab[row].append('')
                        #print tmpStr
                        print curCol+r'="([^"]*)"'
                    col += 1
            #assign with way 2
            for curCol in resCols2:
                if hashval.has_key(curCol) :
                    if re.search(r'''\<([^\s]*)\s+[^\>]*class=['"]''' + curCol+ r'''['"][^\>]*\>([^\>\<]*?)\</(?:\1)\>''', tmpStr) != None:
                        superTab[row].append(re.search(r'''\<([^\s]*)\s+[^\>]*class=['"]''' + curCol+ r'''['"][^\>]*\>([^\>\<]*?)\</(?:\1)\>''', tmpStr) .group(2))
                    else:
                        #print tmpStr
                        superTab[row].append('')
                        print curCol+r'="([^"]*)"'
                    if re.search(r'''\<([^\s]*)\s+[^\>]*id=['"]''' + curCol + r'''['"][^\>]*\>([^\>\<]*?)\</(?:\1)\>''', tmpStr) != None:
                        superTab[row].append(re.search(r'''\<([^\s]*)\s+[^\>]*id=['"]''' + curCol + r'''['"][^\>]*\>([^\>\<]*?)\</(?:\1)\>''', tmpStr) .group(2))
                    else:
                        #print tmpStr
                        superTab[row].append('')
                        print curCol+r'="([^"]*)"'
                    col += 1
            row += 1
        if row != 0:
            col /= row
        return row, col
        
    def UpdateTableWidget(self, tableWidget, row, col, resCols, resCols2, superTab):
        tableWidget.setRowCount(row)
        tableWidget.setColumnCount(col)
        tableWidget.setHorizontalHeaderLabels(resCols + resCols2)
        #update Tabel Widget
        for i in range(row):
            for j in range(col):
                self.newItem = QTableWidgetItem(unicode(superTab[i][j].strip().encode('utf-8'), 'utf-8', 'ignore'))    
                tableWidget.setItem(i, j, self.newItem)
                self.QTout(superTab[i][j].encode('utf-8') )
    #Exact Web Page Type 1        
    def ExctType1(self, doc, soup): 
        # find the most frequent class
        reptns = []
        self.InitKeyWordType1(reptns)  
        
        extTstLists =[]
        self.MakeSoupLists(extTstLists, reptns, soup) 
        
        hashval = {}  
        mfreqcls = self.FindMostFreqCls(reptns, extTstLists, hashval)  
        
        #use the most frequent class to work
        extResList = soup.findAll('div', {'class' : mfreqcls})
        
        
        resCols = []
        resCols2 = []           
        hashval = {}
        self.FindPossibleCols(extResList, hashval, resCols, resCols2)    
        #assign the suiperTab[0...row-1][0...col-1]
        superTab = []
        row, col = self.MakeSuperTab(extResList, superTab, resCols, resCols2, hashval)              
        
        self.UpdateTableWidget(self.tableWidget, row, col, resCols, resCols2, superTab)
        
        """
        self.tab_3 = PyQt4.QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.tableWidget2 = QtGui.QTableWidget(self.tab_3)
        self.tableWidget2.setGeometry(QtCore.QRect(0, 0, 821, 221))
        self.tableWidget2.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget2.setColumnCount(3)
        self.tableWidget2.setRowCount(3)
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("Dialog", "Tab 3", None))
        """
    
    def updateTabWidgetType2(self, superTable2, superTable2Name, extTableHeadsLists):
        i = 0
        for curTable in superTable2:
            self.curTab = PyQt4.QtGui.QWidget()
            self.curTab.setObjectName(_fromUtf8(superTable2Name[i]))
            self.curTableWidget = QtGui.QTableWidget(self.curTab)
            self.curTableWidget.setGeometry(QtCore.QRect(10, 10, 751, 181))
            self.curTableWidget.setObjectName(_fromUtf8("tableWidget"+superTable2Name[i]))
            self.curTableWidget.setColumnCount(len(superTable2[i][0]))
            self.curTableWidget.setRowCount(len(superTable2[i]))
            
            
            self.curTableWidget.setHorizontalHeaderLabels(extTableHeadsLists[i])
            #update Tabel Widget
            for k in range(len(superTable2[i])):
                for j in range(len(superTable2[i][0])):
                    self.newItem = QTableWidgetItem(unicode(superTable2[i][k][j].strip().encode('utf-8'), 'utf-8', 'ignore'))    
                    self.curTableWidget.setItem(k, j, self.newItem)
                    self.QTout(superTable2[i][k][j].encode('utf-8') )
                    
                    
            self.tabWidget.addTab(self.curTab, _fromUtf8(""))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.curTab), _translate("Dialog", superTable2Name[i], None))
            
            i += 1
    
    def ExctType2(self, doc, soup):
        extTableObjs = []

        extTableObjs = soup.findAll('table')
        extTableHeadsLists = []  #2d tid, col
        i = 0
        extTableValidId = []
        superTable2 = [] #3d      tid,row, col
        superTable2Name = [] #1d tid
        for extTableObj in extTableObjs:
            ##########
            TableFg = 0
            curHead = []
            if  extTableObj.find('tr') !=None:
                extTableStr = unicode(extTableObj)               
                curTable = []
                j = 0
                if extTableObj.find('tr') != None:
                    extTRObjs = extTableObj.findAll('tr')
                    fst = 1
                    for extTRObj in extTRObjs:
                        if fst == 1:
                            type = 0
                            extTRStr = unicode (extTRObj)
                            extCurTHTDs = re.findall(r'\<th[^\>]*>([\s\S]*?)\</th\>|\<td[^\>]*>([\s\S]*?)\</td\>', extTRStr)
                            i = 0
                            for extCurTHTD in extCurTHTDs:
                                tmp = extCurTHTD[0] + extCurTHTD[1]
                                if tmp != '':
                                    curHead.append(GetSimpleStrFromLabelStr(tmp))
                                else:
                                    curHead.append(str(i+1))
                                i += 1
                            '''
                            if extTRObj.find('th') != None:
                                extCurTHs = extTRObj.findAll('th')
                                type = 1
                            else:
                                extCurTHs = extTRObj.findAll('td')
                                type = 2
                            i = 0
                            for extCurTH in extCurTHs:
                                extCurStr = unicode(extCurTH)
                                if type == 1 and re.search(r'\<th[^\>]*>([\s\S]*?)\</th\>', extCurStr) != None:
                                        tmp = GetSimpleStrFromLabelStr(re.search(r'\<th[^\>]*>([\s\S]*?)\</th\>', extCurStr).group(1))
                                        curHead.append(tmp)  #添加单元格
                                elif type == 2 and re.search(r'\<td[^\>]*>([\s\S]*?)\</td\>', extCurStr) != None:
                                        tmp = GetSimpleStrFromLabelStr(re.search(r'\<td[^\>]*>([\s\S]*?)\</td\>', extCurStr).group(1))
                                        curHead.append(tmp)  #添加单元格
                                else:
                                    curHead.append(str(i + 1))
                                i += 1
                                
                            '''
                            fst = 0
                        else:
                            TableFg = 1
                            curTable.append([])
                            #extCurTDs = extTRObj.findAll('td')
                            i = 0
                            extTRStr = unicode(extTRObj)
                            extCurTHTDs = re.findall(r'\<th[^\>]*>([\s\S]*?)\</th\>|\<td[^\>]*>([\s\S]*?)\</td\>', extTRStr)
                            for extCurTHTD in extCurTHTDs:
                                tmp = extCurTHTD[0] + extCurTHTD[1]
                                if tmp != '':
                                    curTable[j].append(GetSimpleStrFromLabelStr(tmp))
                                else:
                                    curTable[j].append('')
                                i += 1
                            while (len(curHead) > i):
                                curTable[j].append('')
                                i += 1
                            '''
                            for i in range(len(curHead)):
                            #for extCurTD in extCurTDs:
                                if i < len(extCurTDs):
                                    extCurStr = unicode(extCurTDs[i])
                                    if re.search(r'\<td[^\>]*>([\s\S]*?)\</td\>|\<th[^\>]*>([\s\S]*?)\</th\>', extCurStr) != None:
                                        tmpre = re.search(r'\<td[^\>]*>([\s\S]*?)\</td\>|\<th[^\>]*>([\s\S]*?)\</th\>', extCurStr)
                                        tmp = GetSimpleStrFromLabelStr(tmpre[0]+tmpre[1])
                                        curTable[j].append(tmp)  #添加单元格
                                    else:
                                        curTable[j].append('')
                                else:
                                    curTable[j].append('')
                            '''
                            j += 1
                extTableValidId.append(i)
                
                '''
                #######
                if extTableObj.find('thead') != None:
                    blkTHead = extTableObj.find('thead')
                    extCurTableHead = blkTHead.find('tr')
                    extCurTHs = extCurTableHead.findAll('th')
                else:
                    blkTHead = extTableObj.find('tbody')
                    extCurTableHead = blkTHead.find('tr')
                    if extCurTableHead.findAll('th') != None:
                        extCurTHs = extCurTableHead.findAll('th')
                    else:
                        extCurTHs = extCurTableHead.findAll('td')
                curHead = []
                for extCurTH in extCurTHs:
                    if extCurTH.contents != []:
                        curHead.append(unicode(extCurTH.contents[0]))
                    else:
                        curHead.append('')
                extTableHeadsLists.append(curHead)
                #extTableHeadsLists.append(self.ExctTableHeads(extTableObs))
                extTableValidId.append(i)
                blkTBody = extTableObj.find('tbody')                
                extCurTableRows = blkTBody.findAll('tr')
                '''
                
                #for extCurTableRow in extCurTableRows:
                if  TableFg != 0:
                    superTable2.append(curTable)
                    extTableHeadsLists.append(curHead)
                    if re.search(r'''\<table[^\>]+class=["']([^'"]+)["'][^\>]*\>''', extTableStr) != None:
                        tmpStr = re.search(r'''\<table[^\>]+class=["']([^'"]+)["'][^\>]*\>''', extTableStr).group(1)
                        superTable2Name.append(tmpStr)
                    else:
                        superTable2Name.append('table' + str(self.tabID))
                    self.tabID += 1
                i += 1
        #print superTable2
        self.updateTabWidgetType2(superTable2, superTable2Name, extTableHeadsLists)
    
    def DoExct(self, doc):
        soup = bs4.BeautifulSoup(doc)   #get soup from HTML code
        
        #fake table
        self.ExctType1(doc, soup)
        
        #real table
        self.ExctType2(doc, soup)       
        
        file = open('webdata.txt', 'w')
        file = file.write(doc)
    @pyqtSignature("")
    def on_btnExct_clicked(self):
        """
        Exact Web Page
        """
        self.teExctData.setText("")
        qsurl = self.leURL.text()
        url = unicode (qsurl) 
        if re.match(r'http://[^\s]*', url) == None:
            url = r'http://' + url
        req = urllib2.Request(url)
        con = urllib2.urlopen(req)
        doc = con.read()
        con.close()
        #docuni = unicode(doc,'UTF-8')
        self.DoExct(doc)
        
        
    
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
