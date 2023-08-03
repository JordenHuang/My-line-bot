from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler,
    WebhookParser
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)


import os
import sys


import pygsheets

from difflib import get_close_matches
from random import choice

''' learning bot'''
class LearningBot:
    def help(self):
        reply_msg = (
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
    
    
    def __init__(self, secret_key:str, sheet_url:str):
        '''param: 
        secret_key: json string (remove the spaces in the json file and make it to only a line)
        
        sheet_url: the google sheet's URL
        '''
        
        
        gc = pygsheets.authorize(service_account_json=secret_key)

        sheet = gc.open_by_url(sheet_url)

        self.work_sheet:pygsheets.Worksheet = sheet.worksheet_by_title("sheet1")
    
    
    def get_known_questions_from_google_sheet(self):
        data_lists = self.work_sheet.get_all_values(returnas="matrix", include_tailing_empty=False, include_tailing_empty_rows=False)

        return data_lists
    
    
    def find_best_matched_question(self, data:list, user_question:str, percentage:int =0.87):
        questions = [data[row][0] for row in range(len(data))]

        matched = get_close_matches(user_question, questions, n=1, cutoff=percentage)
        
        # print("matched:", matched)
        if matched != []:
            match_question_index = questions.index(matched[0])
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
    



# functionalities
# from api.all_functions import show_commands, determine_functions


channel_secret = os.environ.get('LINE_CHANNEL_SECRET')
channel_access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')


if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

parser = WebhookParser(channel_secret=channel_secret)
configuration = Configuration(access_token=channel_access_token)





app = Flask(__name__)


# domain root
@app.route('/')
def home():
    return 'Hello, World!'


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessageContent):
            continue
        
        # some variables to store informations about the message
        event_type = event.source.type
        user_id = event.source.user_id
        user_message = event.message.text
        
        if event_type == "user":
            chatroom_id = user_id
        elif event_type == "group":
            chatroom_id = event.source.group_id
        
        # print(f"{event_type} {user_id} {user_message} {chatroom_id}\n\n{events}\n")

        
        # 排除所有不是#或' '(空格)開頭的訊息
        if user_message[0] != "#" and user_message[0] != ' ':
            continue
        
        else:
            reply_msg = ''
            
            if len(user_message) == 1:
                reply_msg = "- 輸入 #help 來查看指令目錄"
                reply_msg += "\n- 可使用 #echo 來echo"
            
            elif user_message == "#help":
                # reply_msg = show_commands()
                pass
            
            elif user_message[0:5] == "#echo":
                # echo 功能
                reply_msg = f"你說了: {user_message[5:]}"
            
            else:
                try:
                    # reply_msg = determine_functions(msg=user_message)
                    try:
                        key = os.environ.get("GOOGLE_SECRET_KEY")
                        url = os.environ.get("GOOGLE_SHEET_URL_LEARNINGBOT")
                    except:
                        reply_msg += "secret key or url not found"
                    
                    lb = LearningBot(key, url)
                    reply_msg += lb.main(user_message[1:])
                
                except:
                    reply_msg = "Some error happend!\nPlease check your command or contact the author"
            
            
            # send the message
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=reply_msg)]
                    )
                )

    return 'OK'





if __name__ == "__main__":
    app.run()
