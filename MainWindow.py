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
    #Exact Web Page Type 1        
    def ExctType1(self, doc, soup): 
        # find the most frequent class
        reptns = []
        reptns.append(r'([^"]*[Ii][Nn][Ff][Oo][^"]*)')
        reptns.append(r'([^"]*[Gg][oO][oO][Dd][Ss][^"]*)')
        reptns.append(r'([^"]*[Ii][Tt][Ee][Mm][^"]*)')
        reptns.append(r'([^"]*[Pp][Rr][Oo][Dd][^"]*)')
        extTstLists =[]
        for tmpreptn in reptns:
            extTstLists.append(soup.findAll('div', re.compile(tmpreptn)))
        #extTstList = soup.findAll('div', {'class' : re.compile(r'([^"]*[Ii][Nn][Ff][Oo][^"]*)|([^"]*[Gg][oO][oO][Dd][Ss][^"]*)|([^"]*[Ii][Tt][Ee][Mm][^"]*)|([^"]*[Pp][Rr][Oo][Dd][^"]*)')})
        hashval = {}
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
        #use the most frequent class to work
        extResList = soup.findAll('div', {'class' : mfreqcls})
        superTab = []
        resCols = []
        resCols2 = []
        resCols3 = []
        #find possible cols
        col = 0
        hashval = {}
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
                            if tmpColRePtnRes[idkey+1].strip()!="":
                                resCols2.append(tmpColRePtnRes[idkey])
        row = 0
        #assign the suiperTab[0...row-1][0...col-1]
        for tmpRes in extResList:
            tmpStr = unicode(tmpRes)
            superTab.append([])
            #assign with way 1
            for curCol in resCols:
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
        self.tableWidget.setRowCount(row)
        self.tableWidget.setColumnCount(col)
        self.tableWidget.setHorizontalHeaderLabels(resCols + resCols2)
        #update Tabel Widget
        for i in range(row):
            for j in range(col):
                self.newItem = QTableWidgetItem(unicode(superTab[i][j].strip().encode('utf-8'), 'utf-8', 'ignore'))    
                self.tableWidget.setItem(i, j, self.newItem)
                self.QTout(superTab[i][j].encode('utf-8') )
    @pyqtSignature("")
    def on_btnExct_clicked(self):
        """
        Exact Web Page
        """
        self.teExctData.setText("")
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
