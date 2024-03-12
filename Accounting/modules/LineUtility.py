#引用Http client
import requests
import json 
#Replye Message API端點
replyURL='https://api.line.me/v2/bot/message/reply'
lineToken='Bearer hPwnQTfdo7tFucJTWyK6b/uWRCRPF9s8DB4O01xBvm6dd/p6ifisbHsv4h06cQ5jknfSNH7F47ZeX7zhAFr3TEivwGgcmfRKqyzxSMnMKTPao3kAboBn/WLpUFHkHYiHIdfFvGebcJ/FlXxYZ5ftAwdB04t89/1O/w1cDnyilFU='
getContent='https://api-data.line.me/v2/bot/message/%s/content'
pushMessageURL = 'https://api.line.me/v2/bot/message/push'
CatVisionURL = 'https://atang0705-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/c6223989-3122-431c-b049-c403028f39a6/detect/iterations/AtangVision/image'
PredictionKey = 'b808dfd312d64ee99141af63cf374805'
audioPath= 'https://97f6-2403-c300-d413-6c6c-7c58-82b7-4e86-4f4a.ngrok-free.app/static/audio/'

#定義回復文字訊息的功能
def replyMessage(replyToken,message, audioFile, duration):
    #回應訊息的dict物件 
    msg={
    "replyToken":replyToken,
    "messages":[
        {
            "type":"text",
            "text":message
        },
        {
            "type":'audio',
            "originalContentUrl":audioPath+audioFile+'.mp3',
            "duration":duration*1000 #毫秒 1000=1秒

        }
    ]
   
    }
    #定義Header dict
    myHeader={"Content-Type":"application/json","Authorization":lineToken}
    #呼叫reply message api
    requests.post(url=replyURL,data=json.dumps(msg),headers=myHeader)


def readAudio(audioId, userId):
    urlString=getContent %(audioId)
    headers = {'Authorization':lineToken}
    # print(audioGetUrl.format(audioId=audioId))

    response = requests.get(urlString,headers=headers)
    print(response.content)

    # 检查请求是否成功
    if response.status_code == 200:
        # 获取文件内容
        audio_content = response.content
         # 设置保存文件的路径
        save_path = "modules/static/audio/"+userId+".m4a"    

        # 使用文件操作将字节数据写入到文件中
        with open(save_path, "wb") as audio_file:
            audio_file.write(audio_content)

#讀取特定image id 圖檔
def readImage(imageId, userId):
    urlString=getContent %(imageId)
    print(urlString)
    #正式提出請求
    myHeader={"Authorization":lineToken}
    response=requests.get(url=urlString,headers=myHeader)
    #進行串流讀取
    if response.status_code==200:
        #try with resource with 開啟 在區段(縮排結束) 會自動執行close
        with open("modules/static/img/"+userId+".jpg", 'wb') as f:
            f.write(response.content)   #response透過content 取回bytes class(bytes array)
        #auto close file 
        # VisionHeader = {"Content-Type":"application/octet-stream","Prediction-Key":PredictionKey}
        # print(requests.post(url=CatVisionURL,data=response.content,headers=VisionHeader).content)\
        return response.content  #回應bytes 類別
            
#send push Message(後端啟動 送出訊息到特定Line user id端)
def sendPushTextMessage(userid, message):
    #設定Request Header
    myHeaders={"Content-Type":"application/json","Authorization":lineToken}
    #訊息
    msg = {
    "to": userid,
    "messages":[
        {
            "type":"text",
            "text":message
        },
        
    ]
    }
    #使用requests client
    requests.post(pushMessageURL, data=json.dumps(msg), headers=myHeaders)
