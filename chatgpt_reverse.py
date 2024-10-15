from chatgpt import ChatGPT
import re

class ChatGPTReverse(ChatGPT):
    SIGNATURE = '^対義語\s(.*)$'

    def register_message_handler(self):
        self.app.message(re.compile(self.SIGNATURE, re.S))(self.message_reverse)

    def message_reverse(self, say, context):
        system_message = "質問を単語毎に分解して対義語を返してください。一例として「とびだせどうぶつの森」は「ひっこめ人間の砂漠」になります"

        messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": "とびだせどうぶつの森"},
                {"role": "assistant", "content": "ひっこめ人間の砂漠"},
                {"role": "user", "content": context['matches'][0]},
        ]

        answer = self.chatgpt(messages)
        say(answer)
