import pymssql #引用資料庫的API for MS SQL
from modules import sysConfig
#定義常數 連接上資料屬性
serverName = sysConfig['dbConfig']['serverName']
databaseName = sysConfig['dbConfig']['databaseName']
userName = sysConfig['dbConfig']['userName']
password = sysConfig['dbConfig']['password']

#產生一個連接上資料庫 連接物件
def createConnection():
    try:
        connection = pymssql.connect(serverName, userName, password, databaseName)
        return connection
    except Exception as ex:
        #職出例外到應用系統去
        raise ex

#查詢功能 sqlString 查詢字串,args 參數條件(s) tuple-元組   
def query(connection,sqlString,args,isMulti = False):
    #判斷連接物件傳進來
    if connection!=None:
        #連接物件產生執行命令的Cursor物件
        cursor=connection.cursor()
        #使用cursor物件執行命令(執行查詢 產生Fetching 逐筆讀取下來 )
        cursor.execute(sqlString,args)
        #判斷回單筆或者是多筆查詢 
        if isMulti:
            return cursor.fetchall() #回應多筆
        else:
            return cursor.fetchone() #回應tuple
    
#新增(修改)資料
def update(connection,sqlString,args):
    try:
        #透過連接物件取得Cursor物件
        cursor = connection.cursor()
        #執行SQL敘述(insert or update)
        cursor.execute(sqlString, args)
        #正式Commit
        connection.commit()
        #執行完成
        return True
    except Exception as ex:
        connection.rollback()
        raise ex #將例外擲出到應用系統