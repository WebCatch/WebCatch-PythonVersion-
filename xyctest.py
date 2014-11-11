# -*- coding: utf-8 -*-
import  MySQLdb
def CreateDBinMySQL(hostaddr,usrname,password,DBname):
        conn = MySQLdb.connect("hostaddr", "usrname", "password",charset="utf8")
        cursor =conn.cursor()
        cursor.execute("create database if not exists " + DBname)
        cursor.close()
        conn.close()
def CreateTableinMySQL(hostaddr,usrname,password,DBname,tablename, tableheads, tabledata):
    conn = MySQLdb.connect("hostaddr", "usrname", "password","DBname",charset="utf8")
    cursor =conn.cursor()
    cursor.execute("drop table if exists " + tablename)
    try :
        tmpStr = 'create table if not exists ' + tablename + '(primid int unsigned not null auto_increment primary key'
        for tablehead in tableheads:
            tmpStr += ', ' + tablehead + ' varchar(250)'
        tmpStr += ');'
        cur.execute(tmpStr)
        for curcol in tabledata:
            tmpStr = 'insert into '+tablename + ' values(0'
            for item in curcol:
                tmpStr += ', "' + item +'"'
            tmpStr += ');'
            cur.execute(tmpStr)
            conn.commit()
    except :
           rollback()
    cur.close()
    conn.close()
def LoadDatafromtable():
    cur.execute('show columns from ' + tablename + ';')
    res = cur.fetchall()
    fst = 1
    for r in res:
        if fst == 1:
            fst = 0
            continue
        tableheads.append(r[0])
    cur.execute('select * from ' + tablename + ';')
    res = cur.fetchall()
    i = 0
    for row in res:
        tabledata.append([])
        fst = 1
        for item in row:
            if fst == 1:
                fst = 0
                continue
            tabledata[i].append(item)

        i += 1
    cur.commit()
    cur.close()
    return (tableheads, tabledata)



