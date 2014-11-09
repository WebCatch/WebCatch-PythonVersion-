import MySQLdb

def ConnectMySQL(hostaddr, username, password, portstr, dbname):
    try:
        conn = MySQLdb.connect(host=hostaddr,user=username,passwd=password,port=int(portstr))
        conn.select_db(dbname)
        return conn
    except MySQLdb.Error,e:
        return None
def CrateTableinMySQL(tablename, tableheads, tabledata, cur):
    pass
def DisconnectMySQL(cur, conn):
    cur.close()
    conn.close()
