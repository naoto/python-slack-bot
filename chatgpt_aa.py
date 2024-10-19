import re
from chatgpt import ChatGPT


class ChatGPTAA(ChatGPT):
    SIGNATURE = "^aa\s(.*)$"

    def register_message_handler(self):
        self.app.message(re.compile(self.SIGNATURE, re.S))(self.message_aa)

    def message_aa(self, say, context):
        system_message = "あなたは匿名掲示板にるAA職人です。質問されたものをAAで作成してください。作成したAAはmarkdownのcodeブロックで囲んで回答してください"
        answer = self.send_message(context, system_message)
        say(answer)
