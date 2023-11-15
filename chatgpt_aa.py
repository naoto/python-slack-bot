from chatgpt import ChatGPT


class ChatGPTAA(ChatGPT):
    def message_aa(self, say, context):
        system_message = "あなたは匿名掲示板にるAA職人です。質問されたものをAAで作成してください。作成したAAはmarkdownのcodeブロックで囲んで回答してください"
        answer = self.send_message(context, system_message)
        say(answer)
