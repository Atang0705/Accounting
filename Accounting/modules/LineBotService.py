#Line Bot 聊天機器人 網際網路掛勾WebHook callback服務
#處理加入好友 或者文字聊天或者圖片聊天
from modules import app, sysConfig  #引用Flask物件 公用變數
#引用flask模組代表一個前端的請求資訊request local proxy
from flask import request, make_response  #具有與前端一個獨立的交談層session
from modules.DBUtility import createConnection, query, update
from modules.LineUtility import replyMessage, readAudio, readImage, sendPushTextMessage
from modules.AccoutService import AccoutQry
from modules.OpenaiService import speechToText
from modules.QRcodeUtility import QRcodeRead
from pydub import AudioSegment
import io
#Openai 模組
from modules.OpenaiService import pushTranTogpt 
import json
import requests
import os

#send repy message api服務位址
replyUrl = 'https://api.line.me/v2/bot/message/reply'  #回覆訊息api 
ProfileUrl = 'https://api.line.me/v2/bot/profile/'  #用戶訊息api
# audioGetUrl = 'https://api-data.line.me/v2/bot/message/{audioId}/content/transcoding'

token = 'Bearer hPwnQTfdo7tFucJTWyK6b/uWRCRPF9s8DB4O01xBvm6dd/p6ifisbHsv4h06cQ5jknfSNH7F47ZeX7zhAFr3TEivwGgcmfRKqyzxSMnMKTPao3kAboBn/WLpUFHkHYiHIdfFvGebcJ/FlXxYZ5ftAwdB04t89/1O/w1cDnyilFU='

IssueUrl = 'https://b180-182-233-241-127.ngrok-free.app'

# CatVisionURL = 'https://atang0705-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/c6223989-3122-431c-b049-c403028f39a6/detect/iterations/AtangVision/image'
PredictionKey = 'b808dfd312d64ee99141af63cf374805'

# liff服務網址
liffURL = 'https://liff.line.me/2003756205-0AAX4krZ'

# ChatGPT_key = "Bearer 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"
# ChatGPT_URL = "https://api.openai.com/v1/chat/completions"



original_working_directory = os.getcwd() # 儲存當前工作目錄
#定義Line Bot回呼callback 端點
@app.route('/api/v1/linebot/hook', methods=['POST'])
def lintBotProcess():
    hookData=request.get_json()  #將json字串反序列化成dict or list物件
    #取出訊息的第一筆(可以多則訊息)
    data = hookData["events"][0]
    # print(data)

    curUser = data["source"]  #dict物件

    Account = AccoutQry(curUser["userId"]).get_json()
    category = sysConfig['Category']
    systemmessage = f'請把內容 轉為json 項目有AccountID,CategoryID,Amount,Description,Type 依照輸入的帳戶名稱挑選AccountID={Account} 無符合選 Description = 常用 的AccountID, CategoryID={category}'


    #取出Line系統id(user id)
    #判斷是否為個人使用者
    userId = ''
    if curUser['type'] == 'user':
        userId = curUser["userId"]

    #判斷其中的type屬性
    print(f'Line使用者 user id:{userId}')
    if data['type'] == 'follow':
        replyToken = data['replyToken']
        #新增好友
        print(f'User Id:{userId} 已經加入好友了')
        #獲取使用profile
        userProfileUrl = ProfileUrl + userId
        userProfileheaders = {'Authorization': token}
        resp = requests.get(userProfileUrl, headers=userProfileheaders)
        #讀回資料
        Profile = resp.json()
        #取使用者名稱與圖片
        name = Profile['displayName']
        image = Profile['pictureUrl']
        lang = Profile['language']
        print(f'{name}/{image}/{lang}')
        #寫到資料庫
        #呼叫資料庫模組 要一個連接物件(具有開啟連接)
        try:
            connection = createConnection()
            print(type(connection))
            #呼叫查詢(第一次加入-新增記錄 或者解鎖-修改記錄)
            result=query(connection,'select UserID from Users Where UserID=%s',(userId))
            print(result)
            #None 新增/修改 解鎖欄位isActive
            if result==None:
                #加入好友
                print('新增')
                sql='Insert Into Users(UserID,UserName) values(%s,%s)'
                #呼叫更新資料模組
                try:
                    update(connection, sql, (userId, name))
                except Exception as ex:
                    print(ex)      

            #關閉連接
            connection.close()

        except Exception as ex:
            print('資料連接有問題')

        #回應一個Response狀態碼 帶200 給Line Message api
        response=make_response('', 204) #http status code-204 OK 沒有回內容
        # send reply message 已讀已回
        #準備資料 送給Line使用者資料
        msg = f'{name}您好 歡迎使用記帳應用'
        data = {
        "replyToken":replyToken,
        "messages":[
            {
                "type":"text",
                "text":msg
            },
            {
                "type":"text",
                "text":liffURL
            }
            ]
        }


        #序列dict物件成json String
        jsonData = json.dumps(data)

        #標頭
        myheaders = {'Content-Type': 'application/json', 'Authorization': token}
        
        #採用Http Request post送出去
        requests.post(replyUrl, data=jsonData, headers=myheaders)
    #封鎖作業    
    # elif data['type']=='unfollow':
    #     connection=createConnection()
    #     print(type(connection))
    #     #進行封鎖 進行修改資料isActive false
    #     sql='update LinerUsers set isActive=%s where UserID=%s'
    #     #呼叫更新資料模組
    #     try:
    #             update(connection,sql,(False,userId))
    #     except Exception as ex:
    #             print(ex)  
        
    #聊天訊息處理
    elif data['type'] == 'message':
        replyToken=data['replyToken']
        #取出聊天訊息額外的屬性message
        message = data['message']
        #判斷聊天內容類型
        if message['type'] == 'text':
            #取出聊天文字
            content = message['text']
            print('聊天訊息: ' + content)
            # print(Account)
            
            result = pushTranTogpt(systemmessage,message['text']+'Type支出=0，收入=1')
            result = eval(result)
            # print(result)
            # print(type(result))

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(url=IssueUrl+'/api/v1/transactions/add',data=json.dumps(result),headers=headers)
            if response.status_code == 200:
                sendPushTextMessage(curUser["userId"],"新增記帳成功")
            else:
                sendPushTextMessage(curUser["userId"],"新增記帳失敗")

        elif message['type'] == 'audio':
            audioId = message['id']
            save_path = "modules/static/audio/"+userId+".m4a" 

            readAudio(audioId, userId)

            # 語音轉文字
            messageText = speechToText(save_path)

            # 辨識句意成記帳格式
            result = pushTranTogpt(systemmessage,messageText+'Type支出=0，收入=1')
            result = eval(result)
            # print(result)
            # print(type(result))

            headers = {
                'Content-Type': 'application/json'
            }
            # 呼叫記帳服務
            response = requests.post(url=IssueUrl+'/api/v1/transactions/add',data=json.dumps(result),headers=headers)
            if response.status_code == 200:
                sendPushTextMessage(curUser["userId"],"新增記帳成功")
            else:
                sendPushTextMessage(curUser["userId"],"新增記帳失敗")

        elif message['type'] == 'image':
            #處理圖片
            #取出圖片id
            imageId=message['id']
            save_path = "modules/static/img/"+userId+".jpg" 
            #借助getFile api結合這一個id圖取圖片檔
            byte = readImage(imageId, userId)

            # 呼叫open CV模組辨識QRcode
            qrcodeText = QRcodeRead(save_path)
            print(qrcodeText)
            

    elif data['type']=='beacon':
        print("beacon 打入...") 

    response=make_response("",204)
    return response  

#send Push Message端點
@app.route('/api/v1/send/message/<msg>/rawdata')
def sendPusMessageService(msg):
    #取出管理者的Line user id 應該進資料庫找出管理者
    #呼叫自訂函數取出一個連接上資料庫連接物件
    connection = createConnection()
    sql = 'select UserID from LinerUsers where Role=%s'
    result = query(connection, sql, ('admin'))
    if result != None:
        #取出admin Line User ID
        userid = result[0]
        #呼叫自訂模組功能
        sendPushTextMessage(userid, msg)
    else:
        #沒事
        pass 

    #產生Response
    resp = make_response()
    resp.status_code = 200

    return resp