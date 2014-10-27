# -*- coding: utf-8 -*-

"""
Module implementing btnExtfromHTMLCodeCls.
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
from MainWindow import Dialog
class btnExtfromHTMLCodeCls(Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
    
    @pyqtSignature("")
    def on_btnExtfromCode_clicked(self):
        """
        Slot documentation goes here.
        """
        doc = unicode(self.teHTMLCode.toPlainText())
        doc = doc.encode('utf-8')
        print doc
        self.DoExct(doc)
        # TODO: not implemented yet
if __name__ == "__main__":
    app = PyQt4.QtGui.QApplication(sys.argv)

    dlg = btnExtfromHTMLCodeCls()

    dlg.show()
    
    sys.exit(app.exec_())
