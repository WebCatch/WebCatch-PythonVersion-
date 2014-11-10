# -*- coding:utf-8 -*-
import MySQLdb

def ConnectMySQL(hostaddr, username, password, portstr, dbname):
    try:
        conn = MySQLdb.connect(host=hostaddr,user=username,passwd=password,port=int(portstr), charset='utf8')
        conn.select_db(dbname)
        return conn
    except MySQLdb.Error,e:
        return None
    
def LoadTablefromMySQL(tablename, conn):
    tableheads = []
    tabledata = []
    cur = conn.cursor()
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
def CreateTableinMySQL(tablename, tableheads, tabledata, conn):
    cur = conn.cursor()
    cur.execute('drop table if exists ' + tablename)

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
    cur.close()

def DisconnectMySQL(cur, conn):
    conn.close()
    
if __name__ == "__main__":
    conn = ConnectMySQL('localhost', 'root', '6191162', 3306, 'test')
    CreateTableinMySQL('hehe', ['a', 'b', 'c'], [['a', 'aa', 'aaa'], ['b', 'bb', 'bbb'], ['c', 'cc', 'ccc']], conn)
    LoadTablefromMySQL('hehe', conn)
    conn.close()
    
