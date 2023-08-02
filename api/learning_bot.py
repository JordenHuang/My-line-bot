import os
import pygsheets
import pygsheets.spreadsheet
import pygsheets.worksheet

from difflib import get_close_matches
from random import choice
# import pandas


class LearningBot:
    def help(self):
        reply_msg = (\
"\
#指令:\n\
- 學習 (or learn)\n\
1️⃣目的: 使機器人學會更多用語，提升回答的靈活度及趣味性\n\
2️⃣用法參考:\n\
#學習\n\
放馬過來吧! (->要學的語句)\n\
沒問題! 你要幾匹馬?🫡 (->回覆)\n\n\
  如上，當使用對話模式輸入\"放馬過來吧!\"，Bot會回覆\"沒問題...\"的語句\n\n\
❗多多訓練同樣的語句搭配不同的回覆，可使回復更加多樣\n\n\
\n\
- 對話模式\n\
1️⃣用法參考:\n\
 放馬過來吧 (❗注意開頭空一格)\n\
回覆: 沒問題! 你要幾匹馬?🫡\n\n\
❗使用換行來區隔指令、語句、回覆等敘述\n\
❗您的語句不須完全符合訓練時的語句，只要語句的相似度夠高，Bot還是能猜到您大概想表達的\n\
❕相似度夠高為: 87%以上\n\
\n\
")
        return reply_msg
    
    
    def __init__(self):
        # the dataframe row and col starts from 0, but the google work sheet starts from 1
        
        self.reply_msg = ''
        self.list_dataframe = list()

    
    
    def get_known_questions_from_google_sheet(self):
        try:
            # gc = pygsheets.authorize(service_account_env_var="GOOGLE_SECRET_KEY")
            gc = pygsheets.authorize(service_account_json=r'{"type":"service_account","project_id":"majestic-lodge-394107","private_key_id":"cdddd4872e4d8c48a0fd2a0986bb529ca1f42519","private_key":"-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCq8RuVoLFOSzKU\neuj6iM7IPmaVjYqySyhEKr9zusHxNZE7UpGhBr/mMr3JwYViRlTSLOvI3n74KT1m\nJjzpNjZQWFPjWsUaSCdpIQ99w+H/spqViDkanNlPm68DH1Oy1ArJFT3DCfKDlrza\nYyUCUw59j44W06elnWZlEawIGELMiU795FlMSYxEFFS0K5cQ2a4I4Q/OpvK9/niS\nF8xNIgKPiBkMIc5nDNR6h+78lbkC1h7EbvSOwSG99mrPq2b3f5VWV93ZAuhSA1vn\nB8D8tchtNINJfaM8NOzhqkdQYoSRrEWK20gUmTQyrvP9flsJJDt89w4KRTbnM1Be\nR0qs3q17AgMBAAECggEATPcU/+gjnMhPxDmY12Cslc0+u/xII+GiBhsnK1C9jMCd\nHNQe3J0g3uEewY3f4/EdtKnkGYNQMKTEz87MowY1KzSxxI50a1JsaDGp+2qsQUfl\nwQjeCSTw1R6YDHRY544AMyxcrAm5BtViP4PfQG4r+o2doJp4g6FcXoo35kciIFu+\nix35S9eFn+urmBcWDOJAVjBtrfZpC1BivCkAdPdiKQPwJsxoUu9TtVMf9iDvNhhf\ncbbk/cGiY1c2ZMgmGhgPMWBQQasx+gxpnc52hhOjzNPDrYRh4RJXCx/rISY9geVU\n3W21ZzO28u490WIOfTuuzmFEAmW/6nhqU6Oz4bCW0QKBgQDsaFsQ/pshMbUjjRYq\n9seJmlqmpyxlHSGsruZ4zUMQuS4keXWb7DL4ypXWhvgpndSoRskSwqRcBsOxVAbq\nw+VypyclrwHM3DzQ1OvYEBbaTiQkz31ZtY46PR4J7k//c2T4sYuY8CxbOJsKdrfY\n83cEMELUC+HZBse2gD4YzDt38QKBgQC5G9Lo95SPeK66Fq9XkQsVKbTkbLk49+X4\newDgGEVKoViR9BnWByvj+/17/WnpDut02a+pgxMMxTMvySNs8XGVHkDEtZohCnHA\n7HJlSWFxGGIPWeeVeVc0hgbdd7cUmMk2jeNNvYRB/uVAdxYeNynfkvofrtwLN2er\nGM9CB0IIKwKBgFOMGcrqv/Y+M+7peJEcf64wn6LP58+gOPtnIEpG+FGbsCPxzM+a\n7PSh28xiDKfggHwr7/myUhW3ykcMFBm5u4gGbL5TmAZHOzLuXJ8SKJFkFj/wGDOx\nBx+r48bMsvbrWB7P2C7nijV+zsQm6phAiqovSB7aSCnDzKbBsbBf1RBxAoGAafpN\nEQYV7uIoHvA36Qlob/BV2WWJ0dzTtCQwBxy+JxEi1UUMuaWXckpmAOPADCd3lInA\n8WrSsEACozwj5Q6Ced49NKHIIVyKbeqxP934RLiyA5n0ZXZ3/+Ev8wHENq2WnX40\ngeCb5PDbLcJAToJEnfTW8Oa6ok1RM/rbRjFDk8sCgYEA1CjmQ9xT+u3+CRyKMJzs\nnoJMSGkIfgGyejWTZAhK7gbDmFNLl1OUwtfFaonk6aqIU9+hOiI2c0/N1Zy6Zsdg\nn0ynGC1DH0iOBpX1Er4+h1U73x2oYos1bN6PUT4s3kSaTo6Bn/WDKjI64jVi4nk7\n80rMCNAugu2sorZCw1TG66w=\n-----END PRIVATE KEY-----\n","client_email":"my-line-bot-service@majestic-lodge-394107.iam.gserviceaccount.com","client_id":"116040915155022016894","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/my-line-bot-service%40majestic-lodge-394107.iam.gserviceaccount.com","universe_domain":"googleapis.com"}')

            # sheet_url = os.environ.get("GOOGLE_SHEET_URL_LEARNINGBOT")
            sheet_url = "https://docs.google.com/spreadsheets/d/1CCZnka0AEZz2WyiniWXyGUAqMfKW17vNSpZ5g4qCp6w/edit?hl=zh-TW#gid=0"
            sheet = gc.open_by_url(sheet_url)
        except:
            self.reply_msg += "Error! Check authorization key or sheet url"
            self.not_ok = True
            return
            # raise Exception("Error! Check authorization key or sheet url")

        try:
            self.work_sheet:pygsheets.Worksheet = sheet.worksheet_by_title("sheet1")
        except pygsheets.SpreadsheetNotFound:
            self.reply_msg += "Work sheet NOT found"
            self.not_ok = True
            return
            # raise Exception("Work sheet NOT found")

        self.dataframe = self.work_sheet.get_as_df(has_header=False, include_tailing_empty=False)
        
        # df.shape returns a tuple that indicates (rows, cols) (the number of rows and columns) in the dataframe
        self.rows = self.dataframe.shape[0]
    
    
    def turn_dataframe_to_list(self):
        # print("to_numpy and list test:\n", self.dataframe.to_numpy(dtype=str).tolist(), type(self.dataframe.to_numpy(dtype=str).tolist()))
        self.list_dataframe = list()
        
        temp_list = self.dataframe.to_numpy(dtype='str').tolist()
        for i in range(len(temp_list)):
            self.list_dataframe += [list(filter(None, temp_list[i]))]
    
    
    def find_best_matched_question(self, user_question:str, percentage:int =0.87):
        questions = [self.list_dataframe[row][0] for row in range(self.rows)]

        match = get_close_matches(user_question, questions, n=1, cutoff=percentage)
        # print("match:", match)
        if match != []:
            match_question_index = questions.index(match[0])
        else:
            match_question_index = None
            
        return match_question_index


    def answer_the_question(self, question_index: int):
        answers = self.list_dataframe[question_index][1:]
        
        return choice(answers)
    
    
    def teach_the_bot(self, matched_question_index:int =None, new_question:str =None, new_answer:str =None, question_already_learned=False):
        # the dataframe row and col starts from 0, but the google work sheet starts from 1
        
        if question_already_learned == True:
            self.work_sheet.update_value((matched_question_index+1, len(self.list_dataframe[matched_question_index])+1), val=new_answer)
        else:
            self.work_sheet.update_value((self.rows+1, 1), val=new_question)
            self.work_sheet.update_value((self.rows+1, 2), val=new_answer)
    
    
    def main(self, user_question:str, new_answer:str|None =None ,to_teach=False):
        not_learn_reply = ["沒學過，也許你可以教我🙂?", "聽不懂😓，也許你能教我😘?", "沒聽過但這個好酷😍\n也許你可以教我😊?"]
        learn_reply = ["學習到新知識囉~", "新知識GET!", "謝謝seafood的教導~"]
        
        self.not_ok = False
        self.get_known_questions_from_google_sheet()
        if self.not_ok == True:
            return self.reply_msg
        self.turn_dataframe_to_list()
        if self.not_ok == True:
            return self.reply_msg
        
        # print(self.list_dataframe)
        
        '''
        # if the user is going to have a conversation with the bot, 
        if to_teach == False:
            # then find the best matched question
            matched_question_index = self.find_best_matched_question(user_question)
            
            # if the best matched question is found, then answer it
            if matched_question_index != None:
                self.reply_msg += self.answer_the_question(matched_question_index)
            
            # if not found, reply with one of the not_learn_reply
            else:
                self.reply_msg += choice(not_learn_reply)
        
        # if the user is going to teach the bot, 
        else:
            # then find the exact question if it's in all the questions that the bot knows
            matched_question_index = self.find_best_matched_question(user_question, percentage=1)
            
            # if find a exact the same question, then add a new answer in the question's answers
            if matched_question_index != None:
                # if the new answer is already learned
                if new_answer in self.list_dataframe[matched_question_index][1:]:
                    self.reply_msg += "我已經學過了悠~"
                else:
                    self.teach_the_bot(matched_question_index=matched_question_index, new_answer=new_answer, question_already_learned=True)
                    self.reply_msg += choice(learn_reply)
            
            # if not found the exact same one, then add a new question and an answer
            else:
                self.teach_the_bot(new_question=user_question, new_answer=new_answer, question_already_learned=False)
                self.reply_msg += choice(learn_reply)
        '''
        return self.reply_msg
    
    
    def test(self, times=10):
        c = 0
        while c < times:
            c += 1
            user_input = input("You: ")
            new_answer = input("new answer: ")
            to_teach = bool(input("to teach: "))
            
            if user_input.lower() == 'quit':
                break
            
            msg = self.main(user_input, new_answer, to_teach)
            print("Bot:",msg)



# app = LearningBot()
# print(app.help())
# app.test()


'''
talk to the bot: leave a space at beginning of the sentance to talk to the bot
teach the bot: a '#' at the beginning of the sentance
'''
