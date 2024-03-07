from modules import app
from flask import render_template

@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host='localhost', port=1111)
    