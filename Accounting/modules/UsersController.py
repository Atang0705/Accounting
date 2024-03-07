#引用Flask物件 定義端點
#針對會員Member CRUD(Create/Read/Update/Delete)
from modules import app, sysConfig
from flask import render_template, request

#定義一個端點 進行會員註冊作業(採用調用頁面)
#限制請求 具有方法 request Method=GET(使用超連結)
@app.route('/users/register/form')
def register():
    return render_template('usersRegister.html')


#定義一個端點 進行會員登入作業(採用調用頁面)
@app.route('/users/login/form')
def login():
    return render_template('usersLogin.html')


#定義一個端點 進行會員記帳作業(採用調用頁面)
@app.route('/users/index/form')
def indes():
    currency = sysConfig['Currency']
    descr = sysConfig['CurrencyDescr']
    category = sysConfig['Category']
    return render_template('index.html', currency=currency, descr=descr, category=category)

