import datetime
import re
from chatgpt import ChatGPT


class Spiritual(ChatGPT):
    SIGNATURE_TALOT = "^タロット$"
    SIGNATURE_SEIMEI = "^姓名判断\s(.*)$"
    SIGNATURE_URANAI = "^占い\s(.*)$"
    SIGNATURE_UNSEI = "^運勢"

    def register_message_handler(self):
        self.app.message(re.compile(self.SIGNATURE_TALOT, re.S))(self.message_talot)
        self.app.message(re.compile(self.SIGNATURE_SEIMEI, re.S))(self.message_seimei)
        self.app.message(re.compile(self.SIGNATURE_URANAI, re.S))(self.message_uranai)
        self.app.message(re.compile(self.SIGNATURE_UNSEI, re.S))(self.message_unsei)

    def message_unsei(self, say, context):
        print("運勢")

        date = datetime.date.today()
        message = [{"role": "user", "content": f"{date}の運勢"}]

        answer = self.chatgpt(message)
        print(answer)

        say(answer)

    def message_uranai(self, say, context):
        word = context["matches"][0]
        print(word)

        message = [
            {
                "role": "system",
                "content": "ムーンプリンセス妃弥子になりきって今日の12星座占いをしてください。各星座に1文程度の占い結果も付けてください。",
            },
            {"role": "user", "content": f"{word}の占い結果を教えてください"},
        ]

        answer = self.chatgpt(message)
        print(answer)

        say(answer)

    def message_seimei(self, say, context):
        word = context["matches"][0]
        print(word)

        message = [
            {"role": "user", "content": f"「{word}」の姓名判断をしてください"},
        ]

        answer = self.chatgpt(message)
        print(answer)

        say(answer)

    def message_talot(self, say, context):
        print("タロット")

        message = [
            {
                "role": "system",
                "content": """
あなたはタロットカードの占い師です。
タロットカードを大アルカナを 3 枚引いて、過去と現在と未来を占ってください。

例
```
【過去】 正位置の「死神」
過去には、大きな変化があったようです。あなたがこれまで手にしてきたもの、経験してきたこと、人生のターニングポイントなどを思い出しましょう。死神は変化、終わり、新しい始まりを表しています。何かが終わった後、あなたは空白期間を過ごし、そこから新しい人生をスタートさせたのかもしれません。
```
""",
            },
            {"role": "user", "content": "占い結果を教えてください"},
        ]

        answer = self.chatgpt(message)
        print(answer)

        say(answer)
