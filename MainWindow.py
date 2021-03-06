# -*- coding:utf-8 -*-

"""
Module implementing Dialog.
"""
import PyQt4, PyQt4.QtGui,  sys
import urllib2
import re
import bs4
import DBmodel
from PyQt4.QtGui import QDialog
from PyQt4.QtCore import pyqtSignature
import sip
from PyQt4.QtGui  import *  
from PyQt4.QtCore import *
from PyQt4 import QtCore, QtGui
import SQLmodel
import DBmodel
#import qdarkstyle
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
        return retStr.strip().replace('&nbsp;', '')
    else:
        SubLabelStrs = re.findall(r'\<([A-Za-z0-9]+)[^\>]*>([\s\S]*?)\</(\1)\>', LabelStr)
        i = 0
        for ch in LabelStr.strip():
            if ch == '<':
                retStr += LabelStr[0:i].replace('&nbsp;', '')
                break;
            i += 1
        for i in range(len(SubLabelStrs)):
            #print retStr
            #print GetSimpleStrFromLabelStr(SubLabelStrs[i][1].strip())   
            print retStr
            if len(retStr) == 0 or (len(retStr) != 0 and retStr[len(retStr) - 1] != ' '):
                retStr += ' '
            retStr += GetSimpleStrFromLabelStr(SubLabelStrs[i][1].strip())
            print retStr
        i = len(LabelStr) - 1
        while (LabelStr[i] != '>'):
            i -= 1
        retStr += LabelStr[i + 1: len(LabelStr) ].replace('&nbsp;', '')
    return retStr
class Dialog(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    tabID = 1
    conn = None
    tabBuf = []
    tableBuf = []
    extracted = 0
    specialTableHeadsList = [
                    ["dealtime", "number last-item", "shopname", "amount","trade_status",
                    "baobei_name", "price", "quantity", "item_operate","trade_operate"
                      ]      
                                    ]
    specialTableNames = [("TaobaoBuyList")]
    specialList = [r"""<\s*tbody\s+data-isarchive=[^\s]+\s+data-orderid="[^"]*"\s+data-status="[^"]*"\s+class="[^"]*"\s*>([\s\S]*?)</tbody>"""]
    
    def initSpecialTables(self):
        i = 0
        j = 0
        for tableItem in self.specialTableHeadsList:
            for headItem in tableItem:                
                self.specialTableHeadsList[i][j] = unicode(self.specialTableHeadsList[i][j])
                j += 1
            i += 1
        i = 0
        for tableItem in self.specialTableNames:
            self.specialTableNames[i] = unicode (self.specialTableNames[i])
            i += 1
    
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.initSpecialTables()
    def QTout(self, tmp):
        self.teExctData.append(unicode(tmp, 'utf-8', 'ignore'))
        
    #init keyword type 1
    def InitKeyWordType1(self, reptns):
        reptns.append(r'([^"]*[Ii][Nn][Ff][Oo][^"]*)')
        reptns.append(r'([^"]*[Gg][oO][oO][Dd][Ss][^"]*)')
        reptns.append(r'([^"]*[Ii][Tt][Ee][Mm][^"]*)')
        reptns.append(r'([^"]*[Pp][Rr][Oo][Dd][^"]*)')
        reptns.append(r'([^"]*[Ll][Ii][Ss][Tt][^"]*)')
        reptns.append(r'([^"]*[Ss][Hh][Oo][Ww][^"]*)')
        reptns.append(r'([^"]*[Ss][Uu][Mm][Mm][Aa][Rr][Yy][^"]*)')
        reptns.append(r'([^"]*[Vv][Ii][Dd][Ee][Oo][^"]*)')
        
  
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
    def FindPossibleCols(self, extResList, hashval, resCols, resCols2, resCols3):
        for tmpRes in extResList:
            tmpStr = unicode(tmpRes)
            tmpColRePtnResList = re.findall(r'''\s([A-Za-z][^\s]*)=["']([^'"]*)['"]''', tmpStr)
            tmpColRePtnResList2 = re.findall(r'''\<([^\s]*)\s+[^\>]*class=['"]([^\>"']*)['"][^\>]*\>([^\>\<]*?)\</(?:\1)\>|\<([^\s]*)\s+[^\>]*id=['"]([^\>'"]*)['"][^\>]*\>([^\>\<]*?)\</(?:\4)\>''', tmpStr)

            #tmpColRePtnResList3 = re.findall(r'''<a[^\>]*class="([^"]*)"[^\>]*>([\s\S]*?)</a>''', tmpStr)
            #tmpColRePtnResList3 = re.findall(r'''\<a[^\>]*\>([^\<\>]*?)\</a\>''',  tmpStr)
            #find identical cols Type 1
            for tmpColRePtnRes in tmpColRePtnResList:
                if hashval.has_key(tmpColRePtnRes[0]):
                    hashval[tmpColRePtnRes[0]] += 1
                else:
                    hashval[tmpColRePtnRes[0]] = 1
                    if tmpColRePtnRes[0] != 'class' and tmpColRePtnRes[0]  != 'alt' and tmpColRePtnRes[0]  != 'src' and tmpColRePtnRes[0] != 'target':
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
            """
            for tmpColRePtnRes in tmpColRePtnResList3:
                if hashval.has_key(tmpColRePtnRes[0]):
                    hashval[tmpColRePtnRes[0]] += 1
                else:
                    hashval[tmpColRePtnRes[0]] = 1
                    resCols3.append(tmpColRePtnRes[0]) """
    
    #fill the super table  and return row, col
    def MakeSuperTab(self, extResList, superTab, resCols, resCols2, resCols3, hashval):
        row = 0
        col = 0
        print len(extResList)
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
                        #superTab[row].append(re.search(r'''\<([^\s]*)\s+[^\>]*class=['"]''' + curCol+ r'''['"][^\>]*\>([^\>\<]*?)\</(?:\1)\>''', tmpStr) .group(2))
                        tmpItemStr = ""
                        tmpReRes = re.findall(r'''\<([^\s]*)\s+[^\>]*class=['"]''' + curCol+ r'''['"][^\>]*\>([^\>\<]*?)\</(?:\1)\>''', tmpStr) 
                        for curReRes in tmpReRes:
                            if len(tmpItemStr) > 0 and tmpItemStr[len(tmpItemStr) - 1] != ' ':
                                tmpItemStr += ' '
                            tmpItemStr += curReRes[1];
                        superTab[row].append(tmpItemStr)
                    #else:
                        #print tmpStr
                       # superTab[row].append('')
                        #print curCol+r'="([^"]*)"'
                    elif re.search(r'''\<([^\s]*)\s+[^\>]*id=['"]''' + curCol + r'''['"][^\>]*\>([^\>\<]*?)\</(?:\1)\>''', tmpStr) != None:
                        #superTab[row].append(re.search(r'''\<([^\s]*)\s+[^\>]*id=['"]''' + curCol + r'''['"][^\>]*\>([^\>\<]*?)\</(?:\1)\>''', tmpStr) .group(2))
                        tmpItemStr = ""
                        tmpReRes = re.findall(r'''\<([^\s]*)\s+[^\>]*id=['"]''' + curCol + r'''['"][^\>]*\>([^\>\<]*?)\</(?:\1)\>''', tmpStr) 
                        for curReRes in tmpReRes:
                            if len(tmpItemStr) > 0 and tmpItemStr[len(tmpItemStr) - 1] != ' ':
                                tmpItemStr += ' '
                            tmpItemStr += curReRes[1];
                        superTab[row].append(tmpItemStr)
                    else:
                        #print tmpStr
                        superTab[row].append('')
                        print curCol+r'="([^"]*)"'
                    col += 1
            """
            for curCol in resCols3:
                if hashval.has_key(curCol) :
                    if re.search(r'''<a[^\>]*class="([^"]*)"[^\>]*>([\s\S]*?)</a>''', tmpStr) != None:
                        tmpItemStr = ""
                        tmpReRes = re.findall(r'''<a[^\>]*class="([^"]*)"[^\>]*>([\s\S]*?)</a>''', tmpStr) 
                        for curReRes in tmpReRes:
                            if len(tmpItemStr) > 0 and tmpItemStr[len(tmpItemStr) - 1] != ' ':
                                tmpItemStr += ' '
                            tmpItemStr += curReRes[1];
                        superTab[row].append(tmpItemStr)
                        #superTab[row].append(re.search(r'''<a[^\>]*class="([^"]*)"[^\>]*>([\s\S]*?)</a>''', tmpStr) .group(2))
                    else:
                        #print tmpStr
                        superTab[row].append('')
                        print curCol+r'="([^"]*)"'
                    col += 1
            """

            row += 1
        if row != 0:
            col /= row
        return row, col
        
    def UpdateTableWidget(self, resCols, resCols2, resCols3, superTab):
        if len(resCols + resCols2 + resCols3) == 0 :
            return
        
        #updateTabWidgetType2(self, superTable2, superTable2Name, extTableHeadsLists):
        superTable2 = []
        superTable2Name = []
        extTableHeadsLists = []
        extTableHeadsLists.append(resCols + resCols2 + resCols3)
        superTable2Name.append('table0')
        superTable2.append(superTab)
        self.updateTabWidgetType2( superTable2, superTable2Name, extTableHeadsLists)
        
        """
        self.tabBuf.append(self.tab)
        self.tableBuf.append(self.tableWidget)
        tableWidget.setRowCount(row)
        tableWidget.setColumnCount(col)      
        tableWidget.setHorizontalHeaderLabels([unicode(str(i + 1)) for i in range(len(resCols + resCols2))])
        #update Tabel Widget
        for i in range(col):
            if i < len(resCols):
                self.newItem = QTableWidgetItem(unicode(resCols[i].strip().encode('utf-8'), 'utf-8', 'ignore'))
                self.QTout(resCols[i].encode('utf-8') )
            else:
                self.newItem = QTableWidgetItem(unicode(resCols2[i-len(resCols)].strip().encode('utf-8'), 'utf-8', 'ignore'))
                self.QTout(resCols2[i-len(resCols)].encode('utf-8') )
            tableWidget.setItem(0, i, self.newItem)
            
        for i in range(row):
            for j in range(col):
                self.newItem = QTableWidgetItem(unicode(superTab[i][j].strip().encode('utf-8'), 'utf-8', 'ignore'))    
                tableWidget.setItem(i + 1, j, self.newItem)
                self.QTout(superTab[i][j].encode('utf-8') )
        """
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
        if mfreqcls != '':
            extResList = soup.findAll('div', {'class' : mfreqcls})
        else :
            extResList = []
        
        resCols = []
        resCols2 = []    
        resCols3 = []       
        hashval = {}
        #DBmodel.ReplaceSpace(resCols)
        #DBmodel.ReplaceSpace(resCols2)
        self.FindPossibleCols(extResList, hashval, resCols, resCols2, resCols3)    
        #assign the suiperTab[0...row-1][0...col-1]
        superTab = []
        row, col = self.MakeSuperTab(extResList, superTab, resCols, resCols2, resCols3, hashval)              
        
        self.UpdateTableWidget( resCols, resCols2, resCols3, superTab)
        
        
    
    def updateTabWidgetType2(self, superTable2, superTable2Name, extTableHeadsLists):
        i = 0
        for curTable in superTable2:
            if len(extTableHeadsLists[i]) == 0:
                continue
            self.curTab = PyQt4.QtGui.QWidget()
            self.tabBuf.append(self.curTab)
            self.curTab.setObjectName(_fromUtf8(superTable2Name[i]))
            self.curTableWidget = QtGui.QTableWidget(self.curTab)
            self.tableBuf.append(self.curTableWidget)
            self.curTableWidget.setGeometry(QtCore.QRect(10, 10, 751, 300))
            self.curTableWidget.setObjectName(_fromUtf8("tableWidget"+superTable2Name[i]))
            self.curTableWidget.setColumnCount(len(superTable2[i][0]))
            self.curTableWidget.setRowCount(len(superTable2[i])+1)
            #DBmodel.RemoveSpace(extTableHeadsLists)
            #self.curTableWidget.setHorizontalHeaderLabels(extTableHeadsLists[i])
            self.curTableWidget.setHorizontalHeaderLabels([unicode(str(j + 1)) for j in range(len(extTableHeadsLists[i])) ])
            #update Tabel Widget
            for j in range(len(superTable2[i][0])):
                self.newItem = QTableWidgetItem(unicode(extTableHeadsLists[i][j].strip().encode('utf-8'), 'utf-8', 'ignore'))    
                self.curTableWidget.setItem(0, j, self.newItem)
                self.QTout(extTableHeadsLists[i][j].encode('utf-8') )
            for k in range(len(superTable2[i])):
                for j in range(len(superTable2[i][0])):
                    self.newItem = QTableWidgetItem(unicode(superTable2[i][k][j].strip().encode('utf-8'), 'utf-8', 'ignore'))    
                    self.curTableWidget.setItem(k + 1, j, self.newItem)
                    self.QTout(superTable2[i][k][j].encode('utf-8') )
                    
                    
            self.tabWidget.addTab(self.curTab, _fromUtf8(""))           
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.curTab), _translate("Dialog", superTable2Name[i], None))
            i += 1
    
    def ExctType2(self, doc, soup):
        extTableObjs = []

        #extTableObjs2 = soup.findAll('table')
        #soupStr = unicode(soup)
        extTableObjs = re.findall(r'(\<table[^\>]*\>[\s\S]*?\</table\>)', unicode(doc, 'utf-8', 'ignore'))
        #extTableObjs.extend(extNeedtoEx)
        extTableHeadsLists = []  #2d tid, col
        i = 0
        extTableValidId = []
        superTable2 = [] #3d      tid,row, col
        superTable2Name = [] #1d tid
        for extTableObj in extTableObjs:
            ##########
            TableFg = 0
            curHead = []
            extTableStr = unicode(extTableObj) 
            if  extTableObj.find('tr') !=None:                              
                curTable = []
                j = 0               
                #extTRObjs = extTableObj.findAll('tr')
                extTRObjs = re.findall(r'\<tr[^\>]*\>([\s\S]*?)\</tr\>', extTableStr)                
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
                            tmp = GetSimpleStrFromLabelStr(tmp)
                            if tmp != '':
                                curTable[j].append((tmp))
                            else:
                                curTable[j].append('')
                            i += 1
                        while (len(curHead) > i):
                            curTable[j].append('')
                            i += 1
                        j += 1
                extTableValidId.append(i)
                
                #for extCurTableRow in extCurTableRows:
                if  TableFg != 0 and len(curTable) * len(curTable[0]) >= int(unicode(self.leThreshold.text())):
                    superTable2.append(curTable)
                    extTableHeadsLists.append(curHead)
                    if re.search(r'''\<table[^\>]+class=["']([^'"]+)["'][^\>]*\>''', extTableStr) != None:
                        tmpStr = re.search(r'''\<table[^\>]+class=["']([^'"]+)["'][^\>]*\>''', extTableStr).group(1)
                        #superTable2Name.append(DBmodel.ReplaceSpace(tmpStr))
                        superTable2Name.append(tmpStr)
                    else:
                        superTable2Name.append('table' + str(self.tabID))
                    self.tabID += 1
                i += 1
        #for i in range(len(extTableHeadsLists)):
            #DBmodel.ReplaceSpace(extTableHeadsLists[i])
        #print superTable2
        self.updateTabWidgetType2(superTable2, superTable2Name, extTableHeadsLists)
    
    @pyqtSignature("")
    def on_btnDisConnect_clicked(self):    
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        #ConnectMySQL(hostaddr, username, password, portstr, dbname):
        try:
            self.conn.close()     
            self.lbState.setText(unicode('Unconnected'))
        except:
            QtGui.QMessageBox.warning( self, "WebExt", "Please connect first!:)", QtGui.QMessageBox.Ok )
            self.conn = None
        
       # conn = SQLmodel.ConnectMySQL()
    
    def MatchReItem(self, specialItem, doc):
        
        if re.search(specialItem, doc) != None :
            return 1        
        else :
            return 0
        
    def addItemfromRePtns(self, tmpHd, tmpRePtns, strItem):
        for tmpRePtn in tmpRePtns:
                curReRes = re.findall(tmpRePtn, strItem)
                if len(curReRes) == 0:
                    tmpHd.append("")
                else:
                    tmpHd.append(GetSimpleStrFromLabelStr((curReRes[0])))
        
    def addItemfromHdandSubRePtns(self, curTable, tmpHd, tmpSubItem, tmpSubRePtns):
        curRow = []
        for hdItem in tmpHd:
           curRow.append(hdItem)
        for tmpSubRePtn in tmpSubRePtns:
            curReRes = re.findall(tmpSubRePtn, tmpSubItem)
            if len(curReRes) == 0:
                curRow.append("")
            else:
                curRow.append(GetSimpleStrFromLabelStr((curReRes[0])))
        curTable.append(curRow)
        
    def ExctSpecial(self, idx, doc):
        doc = unicode(doc, "utf8", "ignore")
        superTable2 =[]
        curTable = []
        superTable2Name = []
        extTableHeadsLists = []       
        superTable2Name.append(self.specialTableNames[idx])
        extTableHeadsLists.append(self.specialTableHeadsList[idx])    
        reResItems = re.findall(self.specialList[idx], doc) 
        strItems = []
        for reResItem in reResItems:
                strItems.append(reResItem)
        if idx == 0:         
            for strItem in strItems:
                tmpHd = []
                tmpHdRePtns = [
                    r"""<span class="dealtime" title="[^"]*">([\s\S]*?)</span>""",
                    r"""<span class="number last-item"\s*>([\s\S]*?)</span>""",                      
                    r"""<a target="_blank" class="shopname[^"]*" title="([^"]*)" href="[^"]*" data-point-url="[^"]*" data-spm-anchor-id="[^"]*">[\s\S]*?</a>""", 
                    r"""<td class="amount"[^\>]*>([\s\S]*?)</td>""", 
                    r"""<td class="trade-status[^"]*"[^\>]*>([\s\S]*?)</td>""", 
                    
                        ]
                self.addItemfromRePtns(tmpHd,tmpHdRePtns, strItem)
                tmpSubReRes = re.findall(r"""<tr id="[^"]*" class="order-bd[^"]*"\s*>([\s\S]*?)</tr>""", strItem)
                tmpSubStrItem = []
                tmpSubRePtns = [
                    r"""<a\s*target="_blank"\s*href="[^"]*"\s*class="J_MakePoint"\s*data-point-url="[^"]*"\s*data-spm-anchor-id="[^"]*"\s*>([\s\S]*?)</a>""", 
                    r"""<td class="price" title="[^"]*">([\s\S]*?)</td>""", 
                    r"""<td class="quantity" title="[^"]*">([\s\S]*?)</td>""", 
                    r"""<td class="item-operate"[^\>]*>([\s\S]*?)</td>""", 
                    r"""<td class="trade-operate"[^\>]*>([\s\S]*?)</td>"""
                        ]
                for tmpSubReResItem in tmpSubReRes:
                    tmpSubStrItem.append(tmpSubReResItem)
                    self.addItemfromHdandSubRePtns(curTable, tmpHd, tmpSubReResItem, tmpSubRePtns)
            
        superTable2.append(curTable) 
        self.updateTabWidgetType2(superTable2, superTable2Name, extTableHeadsLists)
    
    def DoExct(self, doc):
        soup = bs4.BeautifulSoup(doc)   #get soup from HTML code
        
        #fake table
        self.ExctType1(doc, soup)
        
        #real table
        self.ExctType2(doc, soup)       
        i = 0
        
        for specialItem in self.specialList:
            if self.MatchReItem(specialItem, doc) == 1:
                self.ExctSpecial(i, doc)
            i += 1
            
        file = open('webdata.txt', 'w')
        file = file.write(doc)


    def GetCurTable(self):
        tablename = unicode(self.tabWidget.tabText(self.tabWidget.indexOf(self.tabBuf[self.tabWidget.currentIndex()])))
        tableheads = []
        tabledata = []
        tmpQTableObj = self.tableBuf[self.tabWidget.currentIndex()]
        for i in range(tmpQTableObj.rowCount()):
            if i !=0:
                tabledata.append([])
            for j in range(tmpQTableObj.columnCount()):
                if i == 0:
                    tableheads.append(unicode(tmpQTableObj.item(i, j).text()))
                else:
                    tabledata[i - 1].append(unicode(tmpQTableObj.item(i, j).text()))
        return tablename,tableheads,tabledata

    def ReplaceCurTableWidget(self,tablename,tableheads,tabledata):
        curTableWidget = self.tableBuf[self.tabWidget.currentIndex()]
        curTableWidget.clear()
        curTableWidget.setColumnCount(len(tableheads))
        curTableWidget.setRowCount(len(tabledata) +1)
        curTableWidget.setHorizontalHeaderLabels([unicode(str(j + 1)) for j in range(len(tableheads)) ])
        for j in range(len(tableheads)):
            self.newItem = QTableWidgetItem(unicode(tableheads[j].strip().encode('utf-8'), 'utf-8','ignore' ) )
            curTableWidget.setItem(0, j, self.newItem)
        for k in range(len(tabledata) ):
            for j in range(len(tableheads) ):
                self.newItem = QTableWidgetItem(unicode(tabledata[k][j].strip().encode('utf-8'), 'utf-8', 'ignore'))
                curTableWidget.setItem(k + 1, j, self.newItem)


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
        try:
            req = urllib2.Request(url)
            con = urllib2.urlopen(req)
            doc = con.read()
            con.close()
            #docuni = unicode(doc,'UTF-8')
            self.DoExct(doc)
            self.extracted = 1
        except:
            QtGui.QMessageBox.warning( self, "WebExt", "Page not found! o.O", QtGui.QMessageBox.Ok )

    @pyqtSignature("")
    def on_btnDeleteTable_clicked(self):
        tablename = unicode(self.leDTableName.text())
        #DelTablefromMySQL(tablename, conn):
        try:
            SQLmodel.DelTablefromMySQL(tablename, self.conn)
            self.on_btnShowTables_clicked()
            QtGui.QMessageBox.warning( self, "WebExt", "Successfully! :)", QtGui.QMessageBox.Ok )
        except:
            QtGui.QMessageBox.warning( self, "WebExt", "Failed! o.O", QtGui.QMessageBox.Ok )
    @pyqtSignature("")
    def on_btnExtfromCode_clicked(self):
        """
        Slot documentation goes here.
        """
        doc = unicode(self.teHTMLCode.toPlainText())
        doc = doc.encode('utf-8')
        print doc        
        self.DoExct(doc)
        self.extracted = 1
    
    @pyqtSignature("")
    def on_btnConnect_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        #ConnectMySQL(hostaddr, username, password, portstr, dbname):
        hostaddr = unicode(self.leHost.text())
        username = unicode(self.leUsername.text())
        password = unicode(self.lePassword.text())
        try:
            portstr = int(unicode(self.lePort.text()))            
        except:
            pass
        dbname = unicode(self.leDBName.text())
        if dbname == '':
            QtGui.QMessageBox.warning( self, "WebExt", "Failed. :(", QtGui.QMessageBox.Ok )
            self.lbState.setText(unicode('Unconnected'))
            return
        try:
            self.conn = SQLmodel.ConnectMySQL(hostaddr, username, password, portstr, dbname)
            self.lbState.setText(unicode('Connected'))
        except:
            QtGui.QMessageBox.warning( self, "WebExt", "Failed. :(", QtGui.QMessageBox.Ok )
            self.lbState.setText(unicode('Unconnected'))
        
       # conn = SQLmodel.ConnectMySQL()

    def GetDelorAddListandOthers(self,fg):
        ids = {}
        if fg == 0:
            rawunistr = unicode(self.leRowId.text())
        else:
            rawunistr = unicode(self.leColId.text())
        sections = rawunistr.split(',')
        for section in sections:
            oneortwo = section.split('-')
            if len(oneortwo) == 1:
                ids[(int(oneortwo[0]) )] = 1
            elif len(oneortwo) == 2 :
                for i in range(int(oneortwo[0]),int(oneortwo[1])+1):
                    ids[i] = 1
            else:
                raise

        id_list = []
        for id in ids:
            id_list.append(id)
        id_list.sort()
        tablename,tableheads,tabledata = self.GetCurTable()
        return id_list,tablename,tableheads,tabledata

    def AddRoworCol(self,fg):
        add_id_list,tablename,tableheads,tabledata = self.GetDelorAddListandOthers(fg)
        for i in range(len(add_id_list) - 1, -1 , -1 ):
            if fg == 0:
                tabledata.insert( add_id_list[i] - 2,[])
                for j in range(len(tableheads)):
                    tabledata[add_id_list[i] - 2].append('')
            elif fg == 1:
                tableheads.insert(add_id_list[i]-1,'')
                for item in tabledata:
                    item.insert(add_id_list[i] - 1,'')
            else:
                raise
        self.ReplaceCurTableWidget( tablename,tableheads,tabledata)

    def DelRoworCol(self,fg):

        del_id_list,tablename,tableheads,tabledata = self.GetDelorAddListandOthers(fg)
        for i in range(len(del_id_list) - 1, -1 , -1 ):
            if fg == 0:
                del tabledata[del_id_list[i]-2]
            elif fg == 1:
                del tableheads[del_id_list[i] - 1]
                for item in tabledata:
                    del item[del_id_list[i] - 1]
            else:
                raise

        self.ReplaceCurTableWidget( tablename,tableheads,tabledata)

    @pyqtSignature("")
    #leRowId
    def on_btnDelRow_clicked(self):
        try:
            self.DelRoworCol(0)
        except:
            QtGui.QMessageBox.warning( self, "WebExt", "Failed. :(", QtGui.QMessageBox.Ok )
        
    @pyqtSignature("")
    def on_btnAddRow_clicked(self):
        try:
            self.AddRoworCol(0)
        except:
            QtGui.QMessageBox.warning( self, "WebExt", "Failed. :(", QtGui.QMessageBox.Ok )
    
    #leColId
    @pyqtSignature("")
    def on_btnDelCol_clicked(self):
        try:
            self.DelRoworCol(1)
        except:
            QtGui.QMessageBox.warning( self, "WebExt", "Failed. :(", QtGui.QMessageBox.Ok )
        
    @pyqtSignature("")
    def on_btnAddCol_clicked(self):
        try:
            self.AddRoworCol(1)
        except:
            QtGui.QMessageBox.warning( self, "WebExt", "Failed. :(", QtGui.QMessageBox.Ok )
    
    @pyqtSignature("")
    def on_btnAppend_clicked(self):
        try:
            if unicode(self.lbState.text() ) == unicode('Unconnected'):
                r = QtGui.QMessageBox.warning( self, "WebExt", "Please connect first. :)", QtGui.QMessageBox.Ok )
                return
            curid = self.tabWidget.currentIndex() 
            if curid == -1:
                QtGui.QMessageBox.warning( self, "WebExt", "Please extract first. :)", QtGui.QMessageBox.Ok )
                return
            dba = self.tabWidget.currentIndex()
            print self.tabBuf
            dbb = self.tabBuf[self.tabWidget.currentIndex()]
            dbc = self.tabWidget.indexOf(self.tabBuf[self.tabWidget.currentIndex()])
            dbd = self.tabWidget.tabText(self.tabWidget.indexOf(self.tabBuf[self.tabWidget.currentIndex()]))
            tablename = unicode(self.tabWidget.tabText(self.tabWidget.indexOf(self.tabBuf[self.tabWidget.currentIndex()])))
            tableheads = []
            tabledata = []
            tmpQTableObj = self.tableBuf[self.tabWidget.currentIndex()]
            for i in range(tmpQTableObj.rowCount()):
                if i !=0:
                    tabledata.append([])
                for j in range(tmpQTableObj.columnCount()):
                    if i == 0:
                        tableheads.append(unicode(tmpQTableObj.item(i, j).text()))
                    else:
                        tabledata[i - 1].append(unicode(tmpQTableObj.item(i, j).text()))

            SQLmodel.UpdateTableinMySQL(tablename, tableheads, tabledata, self.conn)
        except:
            QtGui.QMessageBox.warning( self, "WebExt", "Failed. :(", QtGui.QMessageBox.Ok )
    
    
    @pyqtSignature("")
    def on_btnSave_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        #CreateTableinMySQL(tablename, tableheads, tabledata, conn):
        try:
            if unicode(self.lbState.text() ) == unicode('Unconnected'):
                r = QtGui.QMessageBox.warning( self, "WebExt", "Please connect first. :)", QtGui.QMessageBox.Ok )
                return
            curid = self.tabWidget.currentIndex() 
            if curid == -1:
                QtGui.QMessageBox.warning( self, "WebExt", "Please extract first. :)", QtGui.QMessageBox.Ok )
                return
            dba = self.tabWidget.currentIndex()
            print self.tabBuf
            dbb = self.tabBuf[self.tabWidget.currentIndex()]
            dbc = self.tabWidget.indexOf(self.tabBuf[self.tabWidget.currentIndex()])
            dbd = self.tabWidget.tabText(self.tabWidget.indexOf(self.tabBuf[self.tabWidget.currentIndex()]))
            tablename = unicode(self.tabWidget.tabText(self.tabWidget.indexOf(self.tabBuf[self.tabWidget.currentIndex()])))
            tableheads = []
            tabledata = []
            tmpQTableObj = self.tableBuf[self.tabWidget.currentIndex()]
            for i in range(tmpQTableObj.rowCount()):
                if i !=0:
                    tabledata.append([])
                for j in range(tmpQTableObj.columnCount()):
                    if i == 0:
                        tableheads.append(unicode(tmpQTableObj.item(i, j).text()))
                    else:
                        tabledata[i - 1].append(unicode(tmpQTableObj.item(i, j).text()))
            
            SQLmodel.CreateTableinMySQL(tablename, tableheads, tabledata, self.conn)
            #print unicode(self.tabBuf[self.tabWidget.currentIndex()].objectName())
            #raise NotImplementedError
        except:
            QtGui.QMessageBox.warning( self, "WebExt", "Failed. :(", QtGui.QMessageBox.Ok )
        
    @pyqtSignature("")
    def on_btnChangeTName_clicked(self):
        tmpstr = unicode(self.leCurTableName.text())
        #curid = self.tabWidget.currentIndex() 
        curid = self.tabWidget.currentIndex() 
        if curid != -1:
            self.tabWidget.setTabText(self.tabWidget.currentIndex() , _translate("Dialog", tmpstr, None))
        else:
            QtGui.QMessageBox.warning( self, "WebExt", "No any tab yet. :(", QtGui.QMessageBox.Ok )

    def fuc(self):
        curitem = self.listTables.currentItem()
        self.leTablename.setText(curitem.text())

    @pyqtSignature("")
    def on_btnShowTables_clicked(self):
        #howTablesfromMySQL(conn):
        try:
            self.listTables.clear()
            #self.teTables.setText(u'')
            restables = SQLmodel.ShowTablesfromMySQL(self.conn)
            for tmpcur in restables:
                #self.teTables.append(tmpcur)
                self.listTables.addItem(tmpcur)
            self.listTables.itemClicked.connect(self.fuc)
        except:
            QtGui.QMessageBox.warning( self, "WebExt", "Failed. :(", QtGui.QMessageBox.Ok )
    #btnChangeTName
        
    
    @pyqtSignature("")
    def on_btnCloseCurTab_clicked(self):
        #print self.tabWidget.currentIndex() 
        curid = self.tabWidget.currentIndex() 
        try:
            if curid != -1:                
                self.tabWidget.removeTab(curid)
                del self.tabBuf[curid]
                del self.tableBuf[curid]
            else:
                 QtGui.QMessageBox.warning( self, "WebExt", "No any tab yet. :(", QtGui.QMessageBox.Ok )
        except:
            QtGui.QMessageBox.warning( self, "WebExt", "Failed. :(", QtGui.QMessageBox.Ok )
        pass
    @pyqtSignature("")
    def on_btnLoad_clicked(self):
        """
        Slot documentation goes here.
        """
        #LoadTablefromMySQL(tablename, conn):
        #updateTabWidgetType2(self, superTable2, superTable2Name, extTableHeadsLists):
        tablename = unicode(self.leTablename.text())
        superTable2 =[]
        superTable2Name = []
        extTableHeadsLists = []
        superTable2Name.append(tablename)
        try :
            tmpheads, tmptabledata = SQLmodel.LoadTablefromMySQL(tablename, self.conn)
            superTable2.append(tmptabledata)
            extTableHeadsLists.append(tmpheads)
            self.updateTabWidgetType2(superTable2, superTable2Name, extTableHeadsLists)
        except:
            QtGui.QMessageBox.warning( self, "WebExt", "Failed. :(", QtGui.QMessageBox.Ok )
        # TODO: not implemented yet
        #raise NotImplementedError
if __name__ == "__main__":
    app = PyQt4.QtGui.QApplication(sys.argv)
    
    dlg = Dialog()
    
    dlg.show()    
    #app.setStyleSheet(qdarkstyle.load_stylesheet(pyside=False))
    sys.exit(app.exec_())
