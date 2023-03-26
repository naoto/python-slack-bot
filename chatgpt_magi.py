from chatgpt import ChatGPT

class ChatGPTMagi(ChatGPT):
    def message_magi(self, say, context):
        system_message = "質問に対し「科学者」「母」「女」の代表3人でそれぞれの立場から討論し最後に結論を出してください。"
        answer = self.send_message(context, system_message)
        say(answer)
