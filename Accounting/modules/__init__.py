from flask import Flask
from flask_cors import CORS
import json

app=Flask(__name__, static_folder='static', template_folder="template")
CORS(app, resources={r"/api/*": {"origins": " https://7d9a-182-233-241-127.ngrok-free.app"}})

with open('config.json', encoding='utf-8')as config:

    sysConfig = json.load(config)

import modules.UsersController
import modules.UsersService
import modules.AccoutService
import modules.LineBotService