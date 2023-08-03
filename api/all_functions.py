import os

from my_functions.element_picker import ElementPicker, LearningBot
# from my_functions.learning_bot_v3 import LearningBot


def show_commands():
    reply_msg = (
"\
#指令:\n\
- 抽(或 pick)\n\
- 學習(或 learn)\n\
- 開頭空一格 = 對話模式\n\
  會回答學習過的東西\n\n\
使用 '#指令 help' 來查詢完整指令用法\n\
"
)
    return reply_msg



def determine_functions(msg:str):
    # recognize the command name
    command = msg.split(sep='\n')
    command_name = command[0]
    # print("command name:", command_name)
    # print("msg:", msg)

    reply_msg = ''
    key = ''
    url = ''
    
    try:
        key = os.environ.get("GOOGLE_SECRET_KEY")
        url = os.environ.get("GOOGLE_SHEET_URL_LEARNINGBOT")
    except:
        reply_msg = "secret key or url not found"
        return reply_msg
    
    
    try:
        if command_name in ["#抽 help", "#pick help"]:
            ep = ElementPicker()
            reply_msg += ep.help()
        elif command_name in ["#抽", "# 抽", "#pick", "# pick"]:
            ep = ElementPicker()
            reply_msg += ep.main(command[1:])

        
        
        elif command_name in ["#學習 help", "#learn help"]:
            lb = LearningBot(key, url)
            reply_msg += lb.help()
                
        elif command_name in ["#學習", "# 學習", "#learn", "# learn"]:
            lb = LearningBot(key, url)
            reply_msg += lb.main(user_question=command[1], new_answer=command[2], to_teach=True)
        
        elif msg[0] == ' ':
            lb = LearningBot(key, url)
            reply_msg += lb.main(msg[1:])

        
        else:
            reply_msg += "Unknow command"
    
    except:
        reply_msg += "Command format not CORRECT!\n指令格式不正確"
    
    return reply_msg


def test(times=10):
    '''
    For testing command name, not the ep.main() or lb.main() functions
    '''
    c = 0
    while c < times:
        c += 1
        
        msg = input("Enter the msg:\n")
        reply = determine_functions(msg)
        print(reply)



# print(show_commands())
# test(5)
