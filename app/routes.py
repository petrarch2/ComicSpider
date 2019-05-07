from app import app
#导入模板模块
from flask import render_template,request


#路由
@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/', methods=['POST'])
def signin_form():
    if request.form['username'] == 'admin' and request.form['password'] == 'password':
        return render_template('index.html')
    return render_template('home.html')
    
    
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
        <title>Home Page - ComicViewer</title>
    </head>
    <body>
        <h1>Hello, ''' + name + '''!</h1>
        <p>This is a test!</p>
    </body>
    </html>
    '''
    return html

@app.errorhandler(404)
def page_not_found(e):
    return '<h1>Bad Request</h1>', 404

@app.errorhandler(500)
def internal_server_error(e):
    return '<h1>Server Error</h1>', 500
