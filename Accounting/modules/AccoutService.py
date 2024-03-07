from modules import app, sysConfig
from modules.DBUtility import createConnection, update, query
from modules.AccountUtility import accountLave
from modules.OpenaiService import pushTranTogpt
from flask import request, make_response
from datetime import datetime
import json


# 帳戶相關各種功能

# 記帳功能
@app.route('/api/v1/transactions/add', methods=['POST'])
def TransactionsAdd():
    print(request)
    try:
        #透過封裝前端所有資訊的Request物件取出body中所傳遞json
        transactions = request.get_json() #dict物件
        #取得連接物件(具有開啟連接作用)
        message = {} #空的dict物件
        response = make_response()
    
    
        conn = createConnection()
        #新增作業
        sql='Insert Into Transactions(AccountID,CategoryID,Amount,Description,Type) values(%s,%s,%s,%s,%s)'
        #呼叫資料維護模組update()
        result=update(conn,sql,(transactions['AccountID'],transactions['CategoryID'],transactions['Amount'],transactions['Description'],transactions['Type']))
        accountLave(transactions['AccountID'],transactions['Amount'],transactions['Type'])
        # print(result)
        message = {'code':200,'msg':'記帳新增成功!!'}
        response.status_code = 200           
        conn.close()
        
    except Exception as ex:
        print(ex)
        #回json訊息  
        message={'code':400,'msg':'記帳新增失敗!!'}   
        response.status=400
    
    #設定response header Content-Type  
    response.content_type = "application/json"
    response.set_data(json.dumps(message)) #序列化物件為json String
    return response

# TODO QR code新增
@app.route('/api/v1/transactions/qrcodeadd', methods=['POST'])
def TransactionsQRCodeAdd():
    #透過封裝前端所有資訊的Request物件取出body中所傳遞json
    transactions = request.get_json() #dict物件
    print(transactions)
    #取得連接物件(具有開啟連接作用)
    message = {} #空的dict物件
    response = make_response()
    
    # try:
    #     conn = createConnection()
    #     #新增作業
    #     sql='Insert Into Transactions(AccountID,CategoryID,Amount,Description,Type) values(%s,%s,%s,%s,%s)'
    #     #呼叫資料維護模組update()
    #     result=update(conn,sql,(transactions['AccountID'],transactions['CategoryID'],transactions['Amount'],transactions['Description'],transactions['Type']))
    #     accountLave(transactions['AccountID'],transactions['Amount'],transactions['Type'])
    #     # print(result)
    #     message = {'code':200,'msg':'記帳新增成功!!'}
    #     response.status_code = 200           
    #     conn.close()
        
    # except Exception as ex:
    #     print(ex)
    #     #回json訊息  
    #     message={'code':400,'msg':'記帳新增失敗!!'}   
    #     response.status=400
    
    #設定response header Content-Type  
    response.content_type = "application/json"
    response.set_data(json.dumps(message)) #序列化物件為json String
    return response

# GPT文字記帳功能
@app.route('/api/v1/transactions/textadd', methods=['POST'])
def TransactionsGptAdd():
    #透過封裝前端所有資訊的Request物件取出body中所傳遞json
    transactions = request.get_json() #dict物件

    Account = AccoutQry(transactions['userID']).get_json()
    # print(Account)
    category = sysConfig['Category']
    message = f'請把傳送內容 轉為json 項目有AccountID,CategoryID,Amount,Description,Type 依照輸入的帳戶名稱挑選AccountID={Account} 如為空值挑選Description = 常用 的AccountID CategoryID={category}'

    result = pushTranTogpt(message,transactions['message']+'Type支出=0，收入=1')
    #取得連接物件(具有開啟連接作用)
    message = {} #空的dict物件
    response = make_response()
    # print(result)
    # print(eval(result))
    result = eval(result)
    
    try:
        conn = createConnection()
        #新增作業
        sql='Insert Into Transactions(AccountID,CategoryID,Amount,Description,Type) values(%s,%s,%s,%s,%s)'
        #呼叫資料維護模組update()
        update(conn,sql,(result['AccountID'],result['CategoryID'],result['Amount'],result['Description'],result['Type']))
        accountLave(result['AccountID'],result['Amount'],result['Type'])
        # print(result)
        message = {'code':200,'msg':'記帳新增成功!!'}
        response.status_code = 200           
        conn.close()
        
    except Exception as ex:
        print(ex)
        #回json訊息  
        message={'code':400,'msg':'記帳新增失敗!!'}   
        response.status=400
    
    #設定response header Content-Type  
    response.content_type = "application/json"
    response.set_data(json.dumps(message)) #序列化物件為json String
    return response

# 查詢記帳
@app.route('/api/v1/transactions/qry/<country>/rawdata',methods=['GET'])
def TransactionsQry(country):
    response= make_response()
    response.content_type= 'application/json'
    try:
        #查詢user
        conn = createConnection() #具有開啟連接上資料庫
        sql = '''SELECT Transactions.TransactionID, Account.AccountID, Transactions.CategoryID, Transactions.Amount, Transactions.Description, Transactions.Date, Transactions.Type, Account.AccountName, Categories.CategoryName
                FROM Transactions
                INNER JOIN Account ON Transactions.AccountID = Account.AccountID
                INNER JOIN Categories ON Transactions.CategoryID = Categories.CategoryID
                WHERE Account.AccountID IN (''' + country + ') ORDER BY Transactions.Date DESC'
        # print(sql)
        result=query(conn,sql,'',True)
        # print(result)
        resultList=[]
        if len(result) == 0:
            message = {'code':400,'msg':'查無記帳'}
            response.status_code = 400   
            response.set_data(json.dumps(message)) #序列化物件為json String        
            
        else:
            for index in range(len(result)):
                #參考出tupe
                rec = result[index]
                time=rec[5].replace(microsecond=0)
                #建構dict
                recDict={'TransactionID':str(rec[0]),'AccountID':str(rec[1]),'CategoryID':rec[2],'Amount':rec[3],'Description':rec[4],'Date':str(time),'Type':rec[6],'AccountName':rec[7],'CategoryName':rec[8]}
                # print(recDict)
                resultList.append(recDict)
                response.set_data(json.dumps(resultList)) #序列化物件為json String

        conn.close()
        
    except Exception as ex:
        print(ex)
        #回json訊息  
        message={'code':500,'msg':'記帳查詢失敗'}   
        response.status=500
        response.set_data(json.dumps(message)) #序列化物件為json String

    #設定response header Content-Type  
    response.content_type = "application/json"
    return response

# 記帳刪除
@app.route('/api/v1/transactions/delete', methods=['DELETE'])
def TransactionsDelete():
    #使用底層request local proxy 進行參數取得
    TransactionID=request.args.get('TransactionID')
    AccountID=request.args.get('AccountID')
    # print(TransactionID)
    #sql
    sql='DELETE FROM Transactions Where TransactionID=%s'
    message={}
    #產生回應的Response物件
    response = make_response()
    response.content_type = 'application/json'
    try:
        #跟模組要一條連接物件 連接上northwnd
        conn = createConnection() #具有開啟連接上資料庫
        #先進行查詢(看看是否存在這一筆資料) 查詢語法統計紀錄數 有回1 沒有0
        rawdata = query(conn,"SELECT * FROM Transactions WHERE TransactionID=%s",(TransactionID))
        # print(rawdata)
        if rawdata:
            #呼叫update function
            update(conn, sql, (TransactionID))
            if rawdata[6]==True:
                accountLave(AccountID,rawdata[3],'0')
            else:
                accountLave(AccountID,rawdata[3],'1')
            message = {'code':200,'msg':'記帳資料刪除成功'}
            response.status_code = 200
            response.set_data(json.dumps(message))
        else:
            message = {'code':400,'msg':'記帳資料不存在'}
            response.status_code = 400
            response.set_data(json.dumps(message))

    except Exception as ex:
        print(ex)
        message = {'code':500,'msg':'記帳資料刪除失敗'}
        response.status_code = 500
        response.set_data(json.dumps(message))

    return response

# 修改記帳資料
@app.route('/api/v1/transactions/revise', methods=['POST'])
def TransactionsRevise():  
    transactions = request.get_json()
    print(transactions)
    message = {}
    response = make_response()
    response.content_type = 'application/json'

    sql = 'UPDATE Transactions SET AccountID=%s, CategoryID=%s, Amount=%s, Description=%s, Type=%s WHERE TransactionID=%s'

    try:
        conn = createConnection()
        #先進行查詢(看看是否存在這一筆資料) 查詢語法統計紀錄數 有回1 沒有0
        rawdata = query(conn,"SELECT * FROM Transactions WHERE TransactionID=%s",(transactions['TransactionID']))
        if rawdata:
            if rawdata[6]==False:
                if rawdata[6]==transactions['Type']:
                    accountLave(transactions['AccountID'],rawdata[3]-int(transactions['Amount']),'1')
                else:
                    accountLave(transactions['AccountID'],rawdata[3]+int(transactions['Amount']),'1')
            else:
                if rawdata[6]==transactions['Type']:
                    accountLave(transactions['AccountID'],rawdata[3]-int(transactions['Amount']),'0')
                else:
                    accountLave(transactions['AccountID'],rawdata[3]+int(transactions['Amount']),'0')
            # print(transactions['AccountID'],transactions['CategoryID'],transactions['Amount'],transactions['Description'],transactions['Type'],transactions['TransactionID'])
            update(conn,sql,(transactions['AccountID'],transactions['CategoryID'],transactions['Amount'],transactions['Description'],transactions['Type'],transactions['TransactionID']))
            message = {'code':200,'msg':f'記帳資料修改完成'}
            response.status_code = 200
            response.set_data(json.dumps(message))
    
    except Exception as ex:
        print(ex)
        message = {'code':500,'msg':f'記帳資料修改失敗'}
        response.status_code = 500
        response.set_data(json.dumps(message))

    return response

#新增帳戶
@app.route('/api/v1/account/add', methods=['POST'])
def AccountAdd():
    #透過封裝前端所有資訊的Request物件取出body中所傳遞json
    account = request.get_json() #dict物件
    #取得連接物件(具有開啟連接作用)
    message = {} #空的dict物件
    response = make_response()
    
    try:
        conn = createConnection()
        #新增作業
        sql='Insert Into Account(UserID,AccountName,Balance,Currency,Description) values(%s,%s,%s,%s,%s)'
        #呼叫資料維護模組update()
        result=update(conn,sql,(account['UserID'],account['AccountName'],account['Balance'],account['Currency'],account['Description']))
        print(result)
        message = {'code':200,'msg':'帳戶新增成功!!'}
        response.status_code = 200           
        conn.close()
        
    except Exception as ex:
        print(ex)
        #回json訊息  
        message={'code':400,'msg':'帳戶新增失敗!!'}   
        response.status=400
    
    #設定response header Content-Type  
    response.content_type = "application/json"
    response.set_data(json.dumps(message)) #序列化物件為json String
    return response

# 查詢帳戶
@app.route('/api/v1/accout/qry/<country>/rawdata',methods=['GET'])
def AccoutQry(country):

    response = make_response()
    response.content_type = 'application/json'

    try:
        #查詢user
        conn = createConnection() #具有開啟連接上資料庫
        sql = 'SELECT * FROM Account WHERE UserID=%s ORDER BY Account.CreatedAt DESC'
        result=query(conn,sql,country,True)
        resultList=[]
        if len(result) == 0:
            message = {'code':400,'msg':'查無帳戶'}
            response.status_code = 400   
            response.set_data(json.dumps(message)) #序列化物件為json String        
            
        else:
            for index in range(len(result)):
                #參考出tupe
                rec = result[index]
                time=rec[5].date()
                # print(time)
                #建構dict
                recDict={'AccountID':str(rec[0]),'UserID':rec[1],'AccountName':rec[2],'Balance':rec[3],'Currency':rec[4],'CreatedAt':str(time),'Description':str(rec[6])}
                # print(rec[6], type(rec[6]), str(rec[6]))
                resultList.append(recDict)
                response.set_data(json.dumps(resultList)) #序列化物件為json String

        conn.close()
        
    except Exception as ex:
        print(ex)
        #回json訊息  
        message={'code':500,'msg':'帳戶查詢失敗'}   
        response.status=500
        response.set_data(json.dumps(message)) #序列化物件為json String

    #設定response header Content-Type  
    response.content_type = "application/json"
    return response

# 帳戶刪除
@app.route('/api/v1/account/delete', methods=['DELETE'])
def AccountDelete():
    #使用底層request local proxy 進行參數取得
    AccountID=request.args.get('AccountID')
    AccountName=request.args.get('AccountName')
    #sql
    sql='DELETE FROM Account Where AccountID=%s'
    message={}
    #產生回應的Response物件
    response = make_response()
    response.content_type = 'application/json'
    try:
        #跟模組要一條連接物件 連接上northwnd
        conn = createConnection() #具有開啟連接上資料庫
        #先進行查詢(看看是否存在這一筆資料) 查詢語法統計紀錄數 有回1 沒有0
        rawdata = query(conn,'SELECT * FROM Account WHERE AccountID=%s',(AccountID))
        print(rawdata)
        if rawdata:
            #呼叫update function
            update(conn, sql, (AccountID))
            message = {'code':200,'msg':f'帳戶資料:{AccountName} 刪除成功'}
            response.status_code = 200
            response.set_data(json.dumps(message))
        else:
            message = {'code':400,'msg':f'帳戶資料:{AccountName} 不存在'}
            response.status_code = 400
            response.set_data(json.dumps(message))

    except Exception as ex:
        message = {'code':500,'msg':f'帳戶資料:{AccountName} 刪除失敗'}
        response.status_code = 500
        response.set_data(json.dumps(message))

    return response

# 修改帳戶資料
@app.route('/api/v1/account/revise', methods=['POST'])
def AccountRevise():
    account = request.get_json()
    print(account)
    message = {}
    response = make_response()
    response.content_type = 'application/json'

    sql = 'UPDATE Account SET AccountName=%s, Balance=%s, Currency=%s, Description=%s WHERE AccountID=%s'

    try:
        conn = createConnection()
        print(account['AccountName'],account['Balance'],account['Currency'],account['Description'],account['AccountID'])
        update(conn,sql,(account['AccountName'],account['Balance'],account['Currency'],account['Description'],account['AccountID']))
        message = {'code':200,'msg':f'帳戶資料:{account['AccountName']} 修改完成'}
        response.status_code = 200
        response.set_data(json.dumps(message))
    
    except Exception as ex:
        print(ex)
        message = {'code':500,'msg':f'帳戶資料:{account['AccountName']} 修改失敗'}
        response.status_code = 500
        response.set_data(json.dumps(message))

    return response

# 總開銷圖表
@app.route('/api/v1/categorychart/qry/<country>/rawdata',methods=['GET'])
def CategoryChartQry(country):
    response= make_response()
    response.content_type= 'application/json'
    try:
        #查詢user
        conn = createConnection() #具有開啟連接上資料庫
        sql ='''SELECT
                    Transactions.CategoryID,
                    SUM(CASE WHEN Transactions.Type = 0 THEN Transactions.Amount ELSE 0 END) AS TotalAmountFalse,
                    SUM(CASE WHEN Transactions.Type = 1 THEN Transactions.Amount ELSE 0 END) AS TotalAmountTrue
                FROM
                    Transactions
                INNER JOIN
                    Account ON Transactions.AccountID = Account.AccountID
                INNER JOIN
                    Categories ON Transactions.CategoryID = Categories.CategoryID
                WHERE
                    Account.AccountID IN ( ''' + country + ''' )
                GROUP BY
                    Transactions.CategoryID
                ORDER BY
                    Transactions.CategoryID ASC;'''   # 搜尋各類別加總 以Type區隔
        # print(sql)
        result=query(conn,sql,'',True)
        # print(result)
        category = sysConfig['Category']
        # print(result)
        if len(result) == 0:
            message =  [0] * len(category)
            response.status_code = 400   
            response.set_data(json.dumps(message)) #序列化物件為json String        
            
        else:
            
            Datafalse = [0] * len(category)
            Datatrue = [0] * len(category)
            for index in range(len(result)):
                #參考出tupe
                Datafalse[int(result[index][0])-1] = result[index][1]
                Datatrue[int(result[index][0])-1] = result[index][2]

            Data = [Datafalse,Datatrue,sum(Datafalse),sum(Datatrue)]
            # print(Data)
            response.set_data(json.dumps(Data)) #序列化物件為json String

        conn.close()
        
    except Exception as ex:
        print(ex)
        #回json訊息  
        message={'code':500,'msg':'後端錯誤'}   
        response.status=500
        response.set_data(json.dumps(message)) #序列化物件為json String

    #設定response header Content-Type  
    response.content_type = "application/json"
    return response

# 每月總開銷圖表
@app.route('/api/v1/monthchart/qry/<country>/rawdata',methods=['GET'])
def MonthChartQry(country): 
    response= make_response()
    response.content_type= 'application/json'
    try:
        #查詢user
        conn = createConnection() #具有開啟連接上資料庫
        sql ='''SELECT
                    YEAR(Transactions.Date) AS Year,
                    MONTH(Transactions.Date) AS Month,
                    SUM(CASE WHEN Transactions.Type = 0 THEN Transactions.Amount ELSE 0 END) AS TotalAmountFalse,
                    SUM(CASE WHEN Transactions.Type = 1 THEN Transactions.Amount ELSE 0 END) AS TotalAmountTrue
                FROM
                    Transactions
                INNER JOIN
                    Account ON Transactions.AccountID = Account.AccountID
                INNER JOIN
                    Categories ON Transactions.CategoryID = Categories.CategoryID
                WHERE
                    Account.AccountID IN ( ''' + country + ''' )
                GROUP BY
                    YEAR(Transactions.Date), MONTH(Transactions.Date)
                ORDER BY
                    Year DESC, Month DESC;'''   # 搜尋各月加總 以Type區隔
        # print(sql)
        result=query(conn,sql,'',True)
        # print(result)
        category = sysConfig['Category']
        # print(result)
        if len(result) == 0:
            message =  [0] * len(category)
            response.status_code = 400   
            response.set_data(json.dumps(message)) #序列化物件為json String        
            
        else:
            month = [0] * len(result)
            sum = [0] * len(result)
            for index in range(len(result)):
                #參考出tupe
                month[index]=str(result[index][0])+"-"+str(result[index][1])
                sum[index]=result[index][2]

            Data = [month,sum]
            # print(Data)
            response.set_data(json.dumps(Data)) #序列化物件為json String

        conn.close()
        
    except Exception as ex:
        print(ex)
        #回json訊息  
        message={'code':500,'msg':'後端錯誤'}   
        response.status=500
        response.set_data(json.dumps(message)) #序列化物件為json String

    #設定response header Content-Type  
    response.content_type = "application/json"
    return response

# 各帳戶額度