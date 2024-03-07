from modules.DBUtility import createConnection, update, query
import json

def accountLave(AccountID, Amount, Type):
    Addsql = 'UPDATE Account SET Balance = Balance + %s WHERE AccountID = %s;'
    Redsql = 'UPDATE Account SET Balance = Balance - %s WHERE AccountID = %s;'
    try:
        conn = createConnection()
        # print(AccountID, Amount, Type)
        # print(type(Type))
        if Type == '1':
            update(conn,Addsql,(Amount, AccountID))
            # print('加')
        else:
            update(conn,Redsql,(Amount, AccountID))
            # print('減')
        message = True

    except Exception as ex:
        print(ex)
        message = False

    return message

