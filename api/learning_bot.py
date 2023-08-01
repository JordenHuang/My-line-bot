import os
import pygsheets
from random import choice


class LearningBot:
    def __init__(self):
        self.reply_msg = ''
        
        # google worksheet
        gc = pygsheets.authorize(service_account_env_var="GOOGLE_SECRET_KEY")

        sheet_url = os.environ.get("GOOGLE_SHEET_URL_LEARNINGBOT")
        sheet = gc.open_by_url(sheet_url)
        
        # 開啟worksheet by名稱
        try:
            self.work_sheet = sheet.worksheet_by_title("sheet1")

        # 若沒有則create一個新的worksheet
        except pygsheets.SpreadsheetNotFound:
            self.work_sheet = sheet.add_worksheet("sheet1")


    def help(self):
        self.reply_msg = (
"\
說明: 可學習的聊天機器人\n\
指令: -learn 要學習的詞或句子 + 遇到時要回答的東西 (使用換行來分開)\n\
      -無 則使用學習過的來回答\
")

    
    def learn(self, new_learn:str, reply:str):
        all_learned = self.work_sheet.get_col(1, include_tailing_empty=False)[1:]
        # print(all_learned)
        
        # check if the word did not learn before
        if new_learn not in all_learned:
            # insert behind row 1, the 'A2' position
            self.work_sheet.insert_rows(row=1, number=1, values=[new_learn, reply])
            
            sentences = ["學到新知識!", "新知識GET!", "謝謝seafood的教導~"]
            self.reply_msg = choice(sentences)
        
        # if the word is learned
        else:
            row_num = all_learned.index(new_learn) + 2
            # print(row_num)
            row_value = self.work_sheet.get_row(row_num, include_tailing_empty=False)
            # print(row_value)
            row_length = len(self.work_sheet.get_row(row_num, returnas="cell", include_tailing_empty=False))

            if reply not in row_value:
                self.work_sheet.update_row(row_num, [reply], row_length)
                
                sentences = ["學習到新知識囉~", "新知識GET!", "謝謝seafood的教導~"]
                self.reply_msg = choice(sentences)
            
            else:
                self.reply_msg = "我已經學會了~"
        
    def reply_with_learned(self, msg:str):
        all_learned = self.work_sheet.get_col(1, include_tailing_empty=False)[1:]
        
        try:
            row_num = all_learned.index(msg) + 2
            row_value = self.work_sheet.get_row(row_num, include_tailing_empty=False)[1:]
            
            self.reply_msg = choice(row_value)
        
        # if the msg not learned
        except ValueError:
            sentences = ["沒學過", "聽不懂😓", "這個好酷😍\n教我這個"]
            self.reply_msg = choice(sentences)
    
    
    def main(self, msg:str):
        # 把 指令 跟 參數 拆開
        # 如果msg像是 "learn-help" or "learn word" or "learn word word" or "learn word word\nword word"
        # or "word word"
        command_msg = msg.split(maxsplit=1)
        
        if command_msg[0] == "learn-help" or command_msg[0] == "學習-help":
            self.help()
        
        else:           
            if command_msg[0] == "learn" or command_msg[0] == "學習":
                # 把參數拆開
                p = command_msg[1].split('\n')
                
                # tip: if don't want the prefix or postfix white space, use .strip()
                self.learn(p[0], p[1])
            
            else:
                # 到這裡代表不是要學習的，所以要傳入整個msg
                self.reply_with_learned(msg)
        
        return self.reply_msg
            
            



# test = LearningBot()
# msg = test.main("what the")
# print(msg)