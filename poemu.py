import re
from chatgpt import ChatGPT
from illust import Illust


class Poemu(ChatGPT, Illust):
    SIGNATURE = "^ポエム\s(.*)$"

    def __init__(self, app, automatic1111_domain, chatgpt_api_key):
        self.app = app
        self.automatic1111_domain = automatic1111_domain
        self.chatgpt_api_key = chatgpt_api_key
        self.register_message_handler()

    def register_message_handler(self):
        self.app.message(re.compile(self.SIGNATURE, re.S))(self.message)

    def message(self, say, context):
        system_message = """
        あなたは画像生成ＡＩのプロンプト職人です。
        ワードの場面を情景的に英語で説明してください。
        追加のコメントは含めず、完了したシステム プロンプトのみを出力してください。特に、プロンプトの先頭または末尾に追加のメッセージを含めないでください。(例: "---" なし)
        """

        answer = self.send_message(context, system_message)
        print(answer)

        url = self.automatic1111(word=answer)

        prompt = [
            {
                "role": "system",
                "content": "あなたは通訳です。質問の内容を日本語に翻訳して返答してください。返答は翻訳した内容だけにしてください",
            },
            {"role": "user", "content": answer},
        ]

        trans = self.chatgpt(prompt)
        print(trans)

        say(blocks=self.response(url, trans, context["matches"][0]))
