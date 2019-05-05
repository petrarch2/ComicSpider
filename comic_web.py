#从app模块中导入app应用
from app import app

if __name__ == '__main__':
    app.run(debug=True)       #调用 app.run() 方法启动,调试模式
