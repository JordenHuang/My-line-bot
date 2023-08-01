from restaurant_picker import RestaurantPicker
from learning_bot import LearningBot


def show_commands():
    reply_msg = (
"\
#指令:\n\
- 商家\n\
- 學習(或 learn)\n\n\
使用 '指令 + help' 來查詢完整指令用法\n\
(使用'學習-help' 或 'learn-help' 來查詢學習的完整指令用法)"
)
    return reply_msg

# print(show_commands())



def using_functions(chatroom_id:str, msg:str):
    # recognize the command name
    name = msg.split(maxsplit=1)[0]

    reply_msg = ''
    
    if name == "商家":
        # turn msg into list
        msg = msg.split()
        rp = RestaurantPicker(chatroom_id)
        reply_msg = rp.main(msg)
        pass
    
    else:
        lb = LearningBot()
        reply_msg = lb.main(msg)
    
    return reply_msg


# msg = "商家 抽 不允許 1 2 3 4 5"
# msg = "t"
# test = using_functions("工作表1", msg)
# print(test, msg)