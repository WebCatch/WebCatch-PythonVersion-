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
    typelist = [u'a', u'b', u'c']
    typestr = u'simple'
    if type(supertable) == type(typelist):
        for i in range(len(supertable)):
            supertable[i] = supertable[i].replace(' ', '')
    elif type(supertable) == type(typestr):
        supertable = supertable.replace(' ', '')
        
def ReplaceSpace(supertable):
    typelist = [u'a', u'b', u'c']
    typestr = u'simple'
    if type(supertable) == type(typelist):
        for i in range(len(supertable)):
            supertable[i] = supertable[i].replace(' ', '_')
    elif type(supertable) == type(typestr):
        supertable = supertable.replace(' ', '_')
        return supertable


