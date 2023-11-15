from chatgpt import ChatGPT

class ChatGPTReverse(ChatGPT):
    #MODEL = 'gpt-4'

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
