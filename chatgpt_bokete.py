from chatgpt import ChatGPT

class ChatGPTBokete(ChatGPT):
    def message_bokete(self, say, context):
        system_message = "あなたは芸人です。大喜利をしてください"

        answer = self.send_message(context, system_message)
        say(answer)
