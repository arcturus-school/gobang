from tkinter import Text
from tkinter.scrolledtext import ScrolledText
from tkinter.constants import WORD, FLAT, BOTTOM, N, S, END
from time import strftime, localtime
import tkinter.ttk as ttk


# 聊天类
class Chat:
    def interfaces(self, w):
        '''
        聊天界面
        '''
        # 聊天框
        self.t1 = ScrolledText(w, width=40, height=24, wrap=WORD, relief=FLAT)
        self.t1.grid(row=0, columnspan=2)
        self.t1['state'] = 'disabled'  # 聊天框不允许输入
        # 输入框
        self.t2 = Text(w, width=35, height=3, relief=FLAT)
        self.t2.grid(row=1, pady=10)
        # 发送按钮
        self.button = ttk.Button(w, text='发送', width=5, compound=BOTTOM)
        self.button.grid(row=1, column=1, sticky=(N, S), padx=(10, 0), pady=10)

    def writeToText(self, content, IP, PORT):
        '''
        向 ScrolledText 写入数据
        '''
        # 当前时间
        t = strftime("%Y-%m-%d %H:%M:%S", localtime())

        # 向 ScrolledText 写入数据
        self.t1['state'] = 'normal'
        chat_record = f"[{t}] # {IP}:{PORT}>\n{content}\n"
        print(chat_record)
        self.t1.insert(END, chat_record)
        self.t1['state'] = 'disabled'
        self.t2.delete('1.0', 'end')
