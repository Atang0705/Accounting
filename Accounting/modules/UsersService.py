#RESTful Service-針對會員資料進行CRUD
from modules import app  #引用Flask物件
from flask import request, make_response  #Local Proxy(對應前端個別封裝資訊)
from modules.DBUtility import createConnection, update, query
import json
from datetime import datetime, timedelta

#配合前端瀏覽器維護註冊畫面 採用ajax呼喚進來的服務(註冊使用者資訊)
#前端傳遞一份會員json文件
@app.route('/api/v1/users/add', methods=['POST'])
def usersRegister():
    #透過封裝前端所有資訊的Request物件取出body中所傳遞json
    users = request.get_json() #dict物件
    #會員註冊(呼叫自訂的資料服務模組XxxUtility)
    #取得連接物件(具有開啟連接作用)
    message = {} #空的dict物件
    response = make_response()
    
    try:
        conn = createConnection()
        #新增作業
        sql='Insert Into Users(UserID,UserName,PassWord,Email) values(%s,%s,%s,%s)'
        #呼叫資料維護模組update()
        result=update(conn,sql,(users['userID'],users['userName'],users['passWord'],users['email']))
        print(result)
        message = {'code':200,'msg':'會員註冊成功!!'}
        response.status_code = 200           
        conn.close()
        
    except Exception as ex:
        print(ex)
        #回json訊息  
        message={'code':400,'msg':'會員註冊失敗!!'}   
        response.status=400
    
    #設定response header Content-Type  
    response.content_type = "application/json"
    response.set_data(json.dumps(message)) #序列化物件為json String
    return response


@app.route('/api/v1/users/qry', methods=['POST'])
def usersLogin():
    #登入判斷

    #透過封裝前端所有資訊的Request物件取出body中所傳遞json
    users = request.get_json() #dict物件
    # print(users)
    response = make_response()
    response.content_type = 'application/json'

    try:
        #查詢userID並比對passWord
        #取得連接物件
        conn = createConnection() #具有開啟連接上資料庫
        sql="select UserID,UserName from Users Where UserID=%s"
        result=query(conn,sql,(users['userID']),True)
        # print(result)
        if len(result) == 0:
            sql='Insert Into Users(UserID,UserName) values(%s,%s)'
            #呼叫資料維護模組update()
            result=update(conn,sql,(users['userID'],users['userName']))
            msg = {'code':200, 'message':'新增成功'}
            response.status_code = 200
            response.set_data(json.dumps(msg))

        else:
            msg = {'code':200, 'message':'登入成功'}
            response.status_code = 200
            response.set_data(json.dumps(msg))
        
    except Exception as ex:
        print(ex)
        msg = {'code':500, 'message':'後端錯誤，請聯繫管理員'}
        response.status_code = 500
        response.set_data(json.dumps(msg))

    return response

@app.route('/api/v1/users/dlt', methods=['POST'])
def usersDelete():
    # 帳號刪除
    #透過封裝前端所有資訊的Request物件取出body中所傳遞json
    users = request.get_json() #dict物件
    response = make_response()
    response.content_type = 'application/json'

    try:
        #查詢並刪除user
        conn = createConnection() #具有開啟連接上資料庫
        # DLT_Transactions_sql = 'DELETE FROM Transactions Where Account=%s'
        # DLT_Account_sql = 'DELETE FROM Account Where UserID=%s'
        sql = 'DELETE FROM Users Where UserID=%s'
        result=update(conn,sql,(users['userID']))
        print(result)
        message = {'code':200,'msg':'帳號已刪除'}
        response.status_code = 200           
        conn.close()
        
    except Exception as ex:
        print(ex)
        #回json訊息  
        message={'code':400,'msg':'帳號刪除失敗'}   
        response.status=400
    
    #設定response header Content-Type  
    response.content_type = "application/json"
    response.set_data(json.dumps(message)) #序列化物件為json String
    return response