
# Python program to translate
# speech to text and text to speech

import speech_recognition as sr
import pyttsx3
import re
from collections import defaultdict
import ctypes
import time
    
# Initialize the recognizer
class SpeechToText:
    def __init__(self):
        self.rg = sr.Recognizer()
        self.lib = {'一':'1', '兩':'2', '二':'2', '三':'3', '四':'4', '五':'5', '六':'6', '七':'7', '八':'8', '九':'9', '十':'10', '零':'0'}
    def listen(self):
        with sr.Microphone() as source:
            self.rg.adjust_for_ambient_noise(source, duration=0.2)
            audioData = self.rg.listen(source, )
            try:
                text = self.rg.recognize_google(audioData, language='zh-tw')
            #         text = self.rg.recognize_whisper(audioData,model='base',language='chinese') # model tiny, base, small, medium, large, tiny.en, base.en, small.en, medium.en
            except:
                text = ''
            text = self.chinese_to_number(text)
        return text

    def __call__(self):
        return self.listen()

    # convert text to speech
    
    def chinese_to_number(self, text):
        for i in self.lib:
            text = text.replace(i, self.lib[i])
        return text

def text_to_speech(command):
    # Initialize the engine
    global engine
    engine.say(command)
    engine.runAndWait()
  
def format_output(input_str):
    # 不處理例外情況
    # 假設不會出現相同商品各自表述
    # 使用正则表达式解析输入字符串
    global item   
    global item_num
    global item_price
    global item_dc
       
    pattern00 = r'(重置清單)' #重製清單
    pattern0 = r'(刪除)(\d+)\D(\D+)' #刪除2包衛生紙
    pattern1 = r'(.+?)第(\d+)\D(\d+)折(\d+)\D(\d+)\D+(\d+)\D' #"橡皮擦第2個7折1個8塊總共4個"
    pattern2 = r'(.+?)(\d+)折(\d+)\D(\d+)\D+(\d+)\D' #"蘋果5折1顆8塊總共10顆"
    pattern3 = r'(.+?)(\d+)\D(\d+)\D+(\d+)\D' #"衛生紙1包10塊總共24包"
    pattern4 = r'(查看)' #查看目前清單
    match00 = re.match(pattern00, input_str)
    match0 = re.match(pattern0, input_str)
    match1 = re.match(pattern1, input_str)
    match2 = re.match(pattern2, input_str)
    match3 = re.match(pattern3, input_str)
    match4 = re.match(pattern4, input_str)
    if match00: #reset
        item = []
        item_num = defaultdict(int)
        item_price = defaultdict(lambda: (1, 1)) 
        item_dc = defaultdict(lambda: (1, 1))
    elif match0:
        if match0.group(3) in item:
            
            item_num[match0.group(3)] -= int(match0.group(2))
            if item_num[match0.group(3)] <= 0:
                item.remove(match0.group(3))
                del item_num[match0.group(3)]
                del item_dc[match0.group(3)]
                del item_price[match0.group(3)]
                
            #查看目前清單
            for key, value in item_num.items():
                print(f"item: {key}, numbers: {value}")
            
        else:
            print("查無此項")
    elif match1:
            
        if match1.group(1) not in item:
            #create new item
            item.append(match1.group(1))
            #print(item, len(item))
            #build relation between item and numbers
            item_num[match1.group(1)] = int(match1.group(6))
            #print(f"item: {match1.group(1)}, numbers: {item_num[match1.group(1)]}")
            #build relation between item and discounts
            dc = int(match1.group(3))
            while dc >1:
                dc*=0.1
            item_dc[match1.group(1)] = (int(match1.group(2)),dc)
            #build relation between item and price
            item_price[match1.group(1)] = (int(match1.group(4)), int(match1.group(5)))
        else:
            item_num[match1.group(1)] += int(match1.group(6))
            
    elif match2:
        if match2.group(1) not in item:
            item.append(match2.group(1))
            item_num[match2.group(1)] = int(match2.group(5))
            #build relation between item and discounts
            dc = int(match2.group(2))
            while dc >1:
                dc*=0.1
            item_dc[match2.group(1)] = (1,dc)
            #build relation between item and price
            item_price[match2.group(1)] = (int(match2.group(3)),int(match2.group(4)))
        else:
            item_num[match2.group(1)] += int(match2.group(5))
    elif match3:
        if match3.group(1) not in item:
            item.append( match3.group(1))
            item_num[match3.group(1)] = int(match3.group(4))
            item_price[match3.group(1)] = (int(match3.group(2)), int(match3.group(3)))
            item_dc[match3.group(1)] = (1,1)
        else:
            item_num[match3.group(1)] += int(match3.group(4))
        #for i in range (len(item)):
            #print(f"item: {item[i]}, numbers: {item_num[item[i]]}, price: {item_price[item[i]][1]}, discount: {item_dc[item[i]][1]}")
    elif match4:
        if len(item) <= 0:
            print("沒有購買東西")
        else:
            for key, value in item_num.items():
                    subtotal = 0
                    if item_dc[key][1] == 1: #沒打折
                        subtotal += int(item_num[key] * item_price[key][1] / item_price[key][0])
                    elif item_dc[key][0] == 1: #有打折，每件價格一樣
                        subtotal += int(item_num[key] * item_price[key][1] / item_price[key][0] * item_dc[key][1])
                    else:
                        tmpsubTotal = 0
                        for j in range (1,item_num[key]+1):
                            if j % int(item_dc[key][0]) == 0:
                                tmpsubTotal += item_dc[key][1] * item_price[key][1]
                            else:
                                tmpsubTotal += item_price[key][1]
                        subtotal += int(tmpsubTotal / item_price[key][0])
                    print(f"item: {key}, numbers: {value}, subtotal: {subtotal}")
    else:
        print("输入格式不正确")
def totalPrice ():
    global total
    total = 0
    for i in range (len(item)):
        if item_dc[item[i]][1] == 1: #沒打折
            total += int(item_num[item[i]] * item_price[item[i]][1] / item_price[item[i]][0])
        elif item_dc[item[i]][0] == 1: #有打折，每件價格一樣
            total += int(item_num[item[i]] * item_price[item[i]][1] / item_price[item[i]][0] * item_dc[item[i]][1])
        else:
            tmpTotal = 0
            for j in range (1,item_num[item[i]]+1):
                if j % int(item_dc[item[i]][0]) == 0:
                    tmpTotal += item_dc[item[i]][1] * item_price[item[i]][1]
                else:
                    tmpTotal += item_price[item[i]][1]
            total += int(tmpTotal / item_price[item[i]][0])
    
            
if __name__ == '__main__':
    speech_to_text = SpeechToText()
    text = ''
    engine = pyttsx3.init()
    item_num = defaultdict(int)
    item = []
    item_price = defaultdict(lambda: (1, 1)) #1個1塊
    item_dc = defaultdict(lambda: (1, 1))#第幾個，幾折 
    while 1:
        text = speech_to_text()

        if text == '':
            text_to_speech('聽不清楚')
        elif text == "結帳":
            print('確認要去結帳?')
            text_to_speech('確認要去結帳?')
            text = speech_to_text()
            pattern = r'([不否])|(取消)'
            match = re.match(pattern , text)
            if match:
                print('收到取消指令')
                text_to_speech('收到取消指令')
            else: 
                print(text)
                break
        else:
            
            text_to_speech(text)
            print(text)
            try:
                format_output(text)
            except Exception as e:
                print(e)
        text = ''
    totalPrice()
    print('總共金額為'+str(int(total)))
    text_to_speech('總共金額為'+str(int(total)))
    
    #exit(0)
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)
    time.sleep(100000)
    ctypes.windll.kernel32.SetThreadExecutionState(0x00000002)
    