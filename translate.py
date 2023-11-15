from chatgpt import ChatGPT

class Translate(ChatGPT):
    def message_j2e(self, say, context):
        system_message = "日本語を英語に翻訳して意訳してください"
        answer = self.send_message(context, system_message)
        say(answer)

    def message_e2j(self, say, context):
        system_message = "英語を日本語に翻訳して意訳してください"
        answer = self.send_message(context, system_message)
        say(answer)
