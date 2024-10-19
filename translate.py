import re
from chatgpt import ChatGPT


class Translate(ChatGPT):
    SIGNATURE_E2J = "^e2j\s(.*)$"
    SIGNATURE_J2E = "^j2e\s(.*)$"

    def register_message_handler(self):
        self.app.message(re.compile(self.SIGNATURE_E2J, re.S))(self.message_e2j)
        self.app.message(re.compile(self.SIGNATURE_J2E, re.S))(self.message_j2e)

    def message_j2e(self, say, context):
        system_message = "日本語を英語に翻訳して意訳してください"
        answer = self.send_message(context, system_message)
        say(answer)

    def message_e2j(self, say, context):
        system_message = "英語を日本語に翻訳して意訳してください"
        answer = self.send_message(context, system_message)
        say(answer)
