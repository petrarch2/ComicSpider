from app import app
#导入模板模块
from flask import render_template
from flask import request


#路由
@app.route('/')
@app.route('/index') 
def index():        #视图函数
    user_agent = request.headers.get('User-Agent')
    return render_template('index.html',user_agent=user_agent)


#动态路由
@app.route('/user/<name>')      #尖括号里的内容是动态部分,任何能匹配静态部分的 URL 都会映射到这个路由上
def user(name):
    html = '''
    <html>
    <head>
        <title>Home Page - Microblog</title>
    </head>
    <body>
        <h1>Hello, ''' + name + '''!</h1>
        <p>This is a test!</p>
    </body>
    </html>
    '''
    return html

@app.route('/user')
def error():
    return '<h1>Bad Request</h1>', 400

    
