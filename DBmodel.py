# -*- coding:utf-8 -*-

"""
Module implementing DBmodel.
"""
import   sys
import urllib2
import re
import bs4
import sip
import MySQLdb

def RemoveSpace(supertable):
    for i in range(len(supertable)):
        supertable[i] = supertable[i].replace(' ', '')
        


