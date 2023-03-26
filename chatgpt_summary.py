import requests
import re

from chatgpt import ChatGPT
from extractcontent3 import ExtractContent

class ChatGPTSummary(ChatGPT):
    def message_summary(self, say, context):
        url = context['matches'][0]
        print(url)

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

        pattern = re.compile('[\u3040-\u309f\u30a0-\u30ff\u3005-\u3006\u30e0-\u9fcf]')
        if bool(pattern.search(text)) and (len(text) > 3500):
            text = text[:3500]
        elif len(text) == 0:
            say('No Text')
            return

        messages = [
            {"role": "system", "content": "文章を日本語で要約してください。"},
            {"role": "user", "content": text}
        ]

        answer = self.chatgpt(messages)
        print(answer)

        say(answer)

