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


# functionalities
from api.all_functions import show_commands, using_functions


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
        
        # some variables
        event_type = event.source.type
        user_id = event.source.user_id
        user_message = event.message.text
        
        if event_type == "user":
            chatroom_id = user_id
        elif event_type == "group":
            chatroom_id = event.source.group_id
        
        # print(f"{event_type} {user_id} {user_message} {chatroom_id}\n\n{events}\n")


        if user_message[0] != "#" and user_message[0] != ' ':
            continue
        
        else:
            if len(user_message) == 1:
                reply_msg = "輸入 #help 來查看所有指令"
            
            elif user_message[0] == ' ':
                reply_msg = using_functions(chatroom_id, msg=user_message[1:])
            
            else:
                # 將msg改為去除#後的資訊 (也去除#旁的空格)
                if user_message[1] == ' ':  # 如果user_message像 "# help"
                    msg = user_message.split(maxsplit=1)[1]
                else:  # 如果user_message像 "#help"
                    msg = user_message[1:]

                # print(msg)
                reply_msg = ''
                
                try:                    
                    if msg[0:4] == "help" :
                        reply_msg = show_commands()
                    
                    else:
                        reply_msg = using_functions(chatroom_id=chatroom_id, msg=msg)
                
                    # echo 功能
                    # reply_msg += f"你說了{msg}"
                
                except:
                    reply_msg += "Some error happend!\nPlease contact the author"
        
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
    # TODO: when runing on vercel, remove the port
    app.run()