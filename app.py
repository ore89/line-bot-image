import os
from flask import Flask, request, abort
from db import DB

from linebot import (
    LineBotApi, WebhookHandler
)

from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage
)

app = Flask(__name__)

'''以下のパラメーターは都度変更する'''
ACCESS_TOKEN = "xojKlKKAdwV+S4ojP9cq8m3pKeOnHszRTjWlet/ts53gFbukIdBARQ4kB10cUJLQxpuVVYnBHRN5H1eOVw0QKcNHJFi7a4K2kWueq7ZNsHdeTjKB7VrCeu5k4ISuWFns4LcBbVOIxTq3Q5LUF311qAdB04t89/1O/w1cDnyilFU="
SECRET = "ae249ed60cbdd468fc59533f5b8e4e8c"

line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@app.route("/")
def hello_world():
    return "hello world!"


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    message_content = line_bot_api.get_message_content(event.message.id)
    user_id = profile.user_id
    image_content = message_content.content
    db = DB(user_id=user_id,img=image_content,root_path=app.root_path)
    db.treat_picture()
    reply_text = "画像の登録が完了したよ｡\n次に名前を入力してね｡\n｢キャンセル｣と入力で終了"
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_text))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    user_id = profile.user_id
    text = event.message.text
    db = DB(user_id=user_id, text=text, root_path=app.root_path)
    reply_text = db.input_plant_data()
    if reply_text[0] == 1:
        if not reply_text[1]:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_text[1]))
        else:
            line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=reply_text,preview_image_url=reply_text))
    elif reply_text[0] == 0:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_text[1]))
    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="画像を投稿してね｡"))


if __name__ == "__main__":
    app.run()
