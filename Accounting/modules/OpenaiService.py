from pathlib import Path #使用目錄類別
from modules import sysConfig
from openai import OpenAI
import requests
import json
import os

#定義常數(open ai token)
openaiToken=''

client = OpenAI(api_key=openaiToken)

def pushTranTogpt(system,token):

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": f"{system}"},
        {"role": "user", "content": f"{token}"}
        ]
    )
    # print(type(completion))
    # print(completion)
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

def speechToText(audio_path):  
    audio_file= open(audio_path, "rb")
    transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file, 
    response_format="text"
    )
    print(transcription)
    return transcription
