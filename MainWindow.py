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
        docuni = unicode(doc,'UTF-8')
        soup = bs4.BeautifulSoup(doc)
        extResList = soup.findAll('div', {'class' : 'skul_title'})
        finalRes= []
        saleprice = []
        skuname = []
        skucode = []
        row = 0
        col = 0
        sz = 0
        for tmpRes in extResList:
            #saleprice="(\d*\.\d*)"
            #print tmpRes
            tmpStr = unicode(tmpRes)
            #print tmpStr
            saleprice.append(re.search(r'salesprice="([^"]*)"', tmpStr).group(1))
            skuname.append(re.search(r'skuname="([^"]*)"', tmpStr).group(1))
            skucode.append(re.search(r'skucode="([^"]*)"', tmpStr).group(1))
            sz += 1;
            #skuname="([^"]*)"
            #skucode="([^"]*)"
        #resdata = '\n'.join(tsstr.encode('utf-8') in skuname)
        #resdata = skuname[0].encode('utf-8')
        self.QTout(skuname[0].encode('utf-8') )
        #fuc  = "中国\n中国"
        for i in range(sz):
            #print saleprice[i].encode('UTF-8')
            #print skuname[i].encode('UTF-8')
            if i != 0:
                self.QTout(skuname[i].encode('utf-8'))
                #resdata = resdata + fuc # + skuname[i].encode('utf-8')
            #print skucode[i].encode('UTF-8')
        #print resdata
        #self.teExctData.setText(resdata.encode('gbk', 'ignore'))
        #tmp1 = resdata.encode('utf-8', 'ignore')
        #tmp2 = unicode(resdata.encode('utf-8', 'ignore'), 'utf-8', 'ignore')
        #tmp3 = '中文'
        #self.teExctData.setText(unicode(resdata.encode('utf-8', 'ignore'), 'utf-8', 'ignore'))
        #self.teExctData.setText(unicode(resdata, 'utf-8', 'ignore'))
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
