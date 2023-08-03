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




import pygsheets

from difflib import get_close_matches
# from random import choice





import pygsheets

from difflib import get_close_matches
# from random import choice


class LearningBot:
    def __init__(self, secret_key:str, sheet_url:str):
        '''param: 
        secret_key: json string (remove the spaces in the json file and make it to only a line)
        
        sheet_url: the google sheet's URL
        '''
        
        
        gc = pygsheets.authorize(service_account_json=secret_key)

        sheet = gc.open_by_url(sheet_url)

        self.work_sheet:pygsheets.Worksheet = sheet.worksheet_by_title("sheet1")
    
    
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
    
    def get_known_questions_from_google_sheet(self):
        data_lists = self.work_sheet.get_all_values(returnas="matrix", include_tailing_empty=False, include_tailing_empty_rows=False)

        return data_lists
    
    
    def find_best_matched_question(self, data:list, user_question:str, percentage:int =0.87):
        questions = [data[row][0] for row in range(len(data))]

        match = get_close_matches(user_question, questions, n=1, cutoff=percentage)
        # print("match:", match)
        if match != []:
            match_question_index = questions.index(match[0])
        else:
            match_question_index = None
            
        return match_question_index


    def answer_the_question(self, data:list, question_index: int):
        answers = data[question_index][1:]
        
        return choice(answers)
    
    
    def teach_the_bot(self, data:list,  matched_question_index:int =None, new_question:str =None, new_answer:str =None, question_already_learned=False):
        # the dataframe row and col starts from 0, but the google work sheet starts from 1
        rows = len(data)
        
        if question_already_learned == True:
            self.work_sheet.update_value((matched_question_index+1, len(data[matched_question_index])+1), val=new_answer)
        else:
            self.work_sheet.update_value((rows+1, 1), val=new_question)
            self.work_sheet.update_value((rows+1, 2), val=new_answer)
    
    
    def main(self, user_question:str, new_answer:str|None =None ,to_teach=False):
        not_learn_reply = ["沒學過，也許你可以教我🙂?", "聽不懂😓，也許你能教我😘?", "沒聽過但這個好酷😍\n也許你可以教我😊?"]
        learn_reply = ["學習到新知識囉~", "新知識GET!", "謝謝seafood的教導~"]
        
        data:list = self.get_known_questions_from_google_sheet()
        # print(data, type(data))
        
        
        # if the user is going to have a conversation with the bot, 
        if to_teach == False:
            # then find the best matched question
            matched_question_index = self.find_best_matched_question(data, user_question)
            
            # if the best matched question is found, then answer it
            if matched_question_index != None:
                reply_msg = self.answer_the_question(data, matched_question_index)
            
            # if not found, reply with one of the not_learn_reply
            else:
                reply_msg = choice(not_learn_reply)
        
        # if the user is going to teach the bot, 
        else:
            # then find the exact question if it's in all the questions that the bot knows
            matched_question_index = self.find_best_matched_question(data, user_question, percentage=1)
            
            # if find a exact the same question, then add a new answer in the question's answers
            if matched_question_index != None:
                # if the new answer is already learned
                if new_answer in data[matched_question_index][1:]:
                    reply_msg = "我已經學過了悠~"
                else:
                    self.teach_the_bot(data, matched_question_index=matched_question_index, new_answer=new_answer, question_already_learned=True)
                    reply_msg = choice(learn_reply)
            
            # if not found the exact same one, then add a new question and an answer
            else:
                self.teach_the_bot(data, new_question=user_question, new_answer=new_answer, question_already_learned=False)
                reply_msg = choice(learn_reply)
        
        return reply_msg
    
    
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

