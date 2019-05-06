#从app模块中导入app应用
from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)       #调用 app.run() 方法启动,调试模式
