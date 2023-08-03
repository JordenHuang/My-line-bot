from random import choice


class ElementPicker:
    def __init__(self):
        self.reply_msg = ''

    
    def help(self):
        self.reply_msg = (\
"\
#指令:\n\
- 抽 (or pick)\n\
1️⃣目的: 幫助使用者從眾多選項中選擇出一個選項，適合有選擇困難的個人或討論不出結果的群體\n\
2️⃣用法參考:\n\
#抽\n\
蘋果\n\
香蕉\n\
芒果\n\
大便\n\
蓮霧\n\
釋迦\n\
100萬\n\n\
 如上，Bot會抽出以上的某個選項來回覆您\n\n\
❗使用換行來區隔指令、各個選項\n\
❗可先將常用選項記錄在記事本，方便呼叫Bot時使用\n\
")
        
        return self.reply_msg
    
    
    def pick(self, elements:list[str]):
        return choice(elements)
    
    
    def main(self, elements:list[str]):
        self.reply_msg = "已從選項中為您選擇: "
        self.reply_msg += self.pick(elements)
        
        return self.reply_msg
        

    def test(self, times=5):
        c = 0
        while c < times:
            c += 1
            
            elements = list(map(str, input("Enter elements, using space to seperate:\n").split()))
            
            result = self.main(elements)
            print(result)


# app = ElementPicker()
# print(app.help())
# # app.test()



