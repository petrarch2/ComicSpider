# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 10:55:09 2017

@author: Quantum Liu
"""

from comic import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import sys

class Ui_Form(QtWidgets.QWidget):            #创建窗口类，继承QtWidgets.QWidget
    def __init__(self):
        super(Ui_Form,self).__init__()
        self.url=''
        self.dir=''
        self.show=True
        self.loaded=False
        self.comic=None
        
    def setupUi(self, Form):                #参数Form，建立UI界面
        Form.setObjectName("Form")
        Form.resize(480, 180)
        Form.setLayoutDirection(QtCore.Qt.LeftToRight)
        Form.setAutoFillBackground(False)
        Form.setWindowIcon(QtGui.QIcon('./batman.ico'))
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.label_url = QtWidgets.QLabel(Form)
        self.label_url.setAlignment(QtCore.Qt.AlignCenter)
        self.label_url.setObjectName("label_url")
        self.gridLayout.addWidget(self.label_url, 0, 0, 1, 1)
        #输入url的文本框
        self.edit_url = QtWidgets.QLineEdit(Form)
        self.edit_url.setObjectName("edit_url")
        self.gridLayout.addWidget(self.edit_url, 0, 1, 1, 1)
        #预览按键
        self.bt_preview = QtWidgets.QPushButton(Form)
        self.bt_preview.setAutoDefault(True)
        self.bt_preview.setDefault(False)
        self.bt_preview.setObjectName("bt_preview")
        self.bt_preview.clicked.connect(self.preview)#槽
        self.gridLayout.addWidget(self.bt_preview, 0, 2, 1, 1)
        #启动爬取按键
        self.bt_crawl = QtWidgets.QPushButton(Form)
        self.bt_crawl.setDefault(True)
        self.bt_crawl.setObjectName("bt_crawl")
        self.bt_crawl.clicked.connect(self.crawl)#槽
        self.gridLayout.addWidget(self.bt_crawl, 0, 3, 1, 2)
        self.label_dir = QtWidgets.QLabel(Form)
        self.label_dir.setAlignment(QtCore.Qt.AlignCenter)
        self.label_dir.setObjectName("label_dir")
        self.gridLayout.addWidget(self.label_dir, 1, 0, 1, 1)
        #选择目录的文本框
        self.edit_dir = QtWidgets.QLineEdit(Form)
        self.edit_dir.setObjectName("edit_dir")
        self.edit_url.textChanged.connect(self.edit_dir.clear)#URL变化就清空目录
        self.edit_url.textChanged.connect(self.loaded_statu)#预览加载状态
        self.edit_dir.textChanged.connect(self.loaded_statu)#预览加载状态
        self.gridLayout.addWidget(self.edit_dir, 1, 1, 1, 1)
        #选择目录按钮
        self.bt_select = QtWidgets.QPushButton(Form)
        self.bt_select.setObjectName("bt_select")
        self.bt_select.clicked.connect(self.select_dir)#槽
        self.gridLayout.addWidget(self.bt_select, 1, 2, 1, 1)
        #并行按钮
        self.bt_parallel = QtWidgets.QRadioButton(Form)
        self.bt_parallel.setChecked(False)
        self.bt_parallel.setObjectName("bt_parallel")
        self.gridLayout.addWidget(self.bt_parallel, 1, 4, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "漫画爬虫"))
        self.label_url.setText(_translate("Form", "漫画网址"))
        self.bt_preview.setText(_translate("Form", "预览"))
        self.bt_crawl.setText(_translate("Form", "爬取"))
        self.label_dir.setText(_translate("Form", "保存目录"))
        self.bt_select.setText(_translate("Form", "选择目录"))
        self.bt_parallel.setText(_translate("Form", "使用多线程"))

    def select_dir(self):
        '''
        弹出文件对话框选择保存目录
        '''
        self.dir=QFileDialog.getExistingDirectory(self,'选择保存路径',(self.dir if self.dir else './'))
    
    def loaded_statu(self):
        '''
        更改预览状态
        '''
        self.loaded=False
        
    def preview(self):
        '''
        预览
        '''
        self.url=self.edit_url.text()
        try:
            self.comic=Comic(self.url)
        except:
            traceback.print_exc()
            return False
        self.loaded=True
        title,des=self.comic.get_info()[:2]     #返回标题和描述
        if self.show:
            self.comic.print_chapters(self.show)
        else:
            print('使用自动设置')
        print('漫画：{t}\n简介：{d}'.format(t=title,d=des))
        if not (self.edit_dir.text()):
            dirname=os.path.join(os.path.abspath('./'),validatetitle(title))
            self.edit_dir.setText(dirname)
            self.dir=dirname
        return True
        
    def crawl(self):
        '''
        启动爬取
        '''
        if not self.url:
            print('请指定漫画地址！')
            return
        if not self.dir:
            self.show=False
            self.preview()
            self.show=True
        self.parallel=(self.bt_parallel.isChecked() and cpu_count()>1)
        print(('使用多线程下载' if self.parallel else '使用单线程下载'))
        if not self.loaded:
            comic=Comic(self.url,None,self.dir)
        self.dir,self.url='',''
        self.comic.download_all_chapters_s(self.parallel)
        
if __name__ == "__main__":
    if sys.platform.startswith('win'):      #判断操作系统类型
        freeze_support()#pyinstaller多线程,Win平台要加上这句，避免RuntimeError
    app = QtWidgets.QApplication(sys.argv)      #每一个PyQt5程序都需要有一个QApplication对象,sys.argv是从命令行传入的参数列表
    Form = QtWidgets.QWidget()                  #创建基础界面控件(GUI)
    ui = Ui_Form()                  #创建Ui_Form对象
    ui.setupUi(Form)                #执行setupUi方法
    Form.show()                     #显示控件
    sys.exit(app.exec_())           #消息循环结束之后返回0，接着调用sys.exit(0)退出程序

