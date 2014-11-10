# -*- coding: utf-8 -*-
import  MySQLdb
conn = MySQLdb.connect("localhost", "root", "003124")
cursor =conn.cursor()
cursor.execute("create database if not exists python")
cursor.execute("select version()")
data=cursor.fetchone()
print "DataBase Version is %s" % data
cursor.close()
conn.close()
#conn.selsct_db("python")

conn = MySQLdb.connect("localhost", "root", "003124", "python", charset="utf8")
cursor=conn.cursor()
cursor.execute("create table if not exists pythontable(name char(20) not null,sex char(1),age int)")
cursor.close()
conn.close()



conn = MySQLdb.connect("localhost", "root", "003124", "python",  charset="utf8")
#cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
cursor=conn.cursor()
try :
    sql="select * from pythontable"
    count=cursor.execute(sql)
    print count
    rows=cursor.fetchall()
    #for r in rows:
    for r in rows:
     fname=r[0]
     sex=r[1]
     age=r[2]
     print "fname=%s,sex=%c,age=%d" %(fname, sex, age)
except :
    print "Unable to fetch the data!"
cursor.close()
conn.close()

conn = MySQLdb.connect("localhost", "root", "003124", "python", charset="utf8")
cursor=conn.cursor()
sql="insert into pythontable(name,sex,age) values('%s','%c',%d)" % ('xyc', 'm', 20)
try :
    n=cursor.execute(sql)
    conn.commit()
    print n
except :
    conn.rollback()
cursor.close()
conn.close()

conn = MySQLdb.connect("localhost", "root", "003124", "python", charset="utf8")
cursor=conn.cursor()
sql="update pythontable set age=age+1 where sex='%c'" %('m')
try :
    n=cursor.execute(sql)
    conn.commit()
    print n
except :
    conn.rollback()
cursor.close()
conn.close()

conn = MySQLdb.connect("localhost", "root", "003124", "python", charset="utf8")
cursor=conn.cursor()
sql="delete from pythontable where age=%d"%(30)
try :
    n=cursor.execute(sql)
    conn.commit()
    print n
except :
    conn.rollback()
cursor.close()
conn.close()

