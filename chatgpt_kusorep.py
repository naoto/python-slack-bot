from chatgpt import ChatGPT

class ChatGPTKusorep(ChatGPT):
    def message_kusorep(self, say, context):
        system_message = "あなたはTwitterにいるクソリプが得意な人です。質問に対してクソリプをしてください。"
        answer = self.send_message(context, system_message)
        say(answer)
