from chatgpt import ChatGPT
import re

class ChatGPTKusorep(ChatGPT):
    SIGNATURE = '^クソリプ\s(.*)$'

    def register_message_handler(self):
        self.app.message(re.compile(self.SIGNATURE, re.S))(self.message_kusorep)

    def __init__(self, app, chatgpt_api_key, slack_client):
        super().__init__(app, chatgpt_api_key)
        self.slack_client = slack_client

    def reaction(self, event, say):
        emoji = event["reaction"]
        channel = event["item"]["channel"]
        ts = event["item"]["ts"]

        if emoji != 'kusorep':
            return

        conversations_history = self.slack_client.conversations_history(
            channel=channel, oldest=ts, latest=ts, inclusive=1
        )

        messages = conversations_history.data["messages"]

        if not messages:
            group_history = self.slack_client.conversations_replies(
                channel=channel, ts=ts)
            messages = group_history.data["messages"]

        print(messages[0]["text"])

        message = [
            {"role": "system", "content": "あなたはTwitterにいるクソリプが得意な人です。質問に対して日本語で140文字以内でクソリプをしてください。"},
            {"role": "user", "content": messages[0]["text"]},
        ]

        answer = self.chatgpt(message)
        print(answer)

        say(text=answer, thread_ts=ts)

    def message_kusorep(self, say, context):
        system_message = "あなたはTwitterにいるクソリプが得意な人です。質問に対して日本語で140文字以内でクソリプをしてください。"
        answer = self.send_message(context, system_message)
        say(answer)
