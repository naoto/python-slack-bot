import requests
import re
from chatgpt import ChatGPT
from extractcontent3 import ExtractContent


class ChatGPTSummary(ChatGPT):
    MODEL = 'gpt-3.5-turbo'

    def __init__(self, chatgpt_api_key, slack_client):
      self.slack_client = slack_client
      self.chatgpt_api_key = chatgpt_api_key

    def message_summary(self, say, context):
        url = context['matches'][0]
        print(url)

        text = self.extract(url)

        if len(text) == 0:
            say('No Text')
            return

        answer = self.summary(text)
        say(answer)

    def reaction(self, event, say):
        emoji = event["reaction"]
        channel = event["item"]["channel"]
        ts = event["item"]["ts"]

        if emoji != "youyaku":
            return

        # タイムスタンプでメッセージを特定
        conversations_history = self.slack_client.conversations_history(
            channel=channel, oldest=ts, latest=ts, inclusive=1
        )

        messages = conversations_history.data["messages"]

        # メッセージが取得出来ない場合、スレッドからメッセージを特定
        if not messages:
            group_history = self.slack_client.conversations_replies(channel=channel, ts=ts)
            messages = group_history.data["messages"]

        message = messages[0]["text"]
        pattern = re.compile(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', re.S)
        url = re.findall(pattern, message)

        if not url:
            return

        text = self.extract(url[0])

        if len(text) == 0:
            say('No Text')
            return

        answer = self.summary(text)
        say(text=answer, thread_ts=ts)


    def summary(self, text):
        text = self.token_cut(text, 15000)

        messages = [
            {"role": "system", "content": "文章を日本語で要約してください。"},
            {"role": "user", "content": text}
        ]

        answer = self.chatgpt(messages, 16000)
        print(answer)

        return answer

    def extract(self, url):
        extractor = ExtractContent()

        opt = {
            "threshold": 80,
        }
        extractor.set_option(opt)

        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        header = {
            'User-Agent': user_agent
        }

        res = requests.get(url, headers=header)
        html = res.text

        extractor.analyse(html)
        text, title = extractor.as_text()

        return text
