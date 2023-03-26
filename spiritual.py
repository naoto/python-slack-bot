import datetime

from chatgpt import ChatGPT

class Spiritual(ChatGPT):
    def message_unsei(self, say, context):
        print("運勢")

        date = datetime.date.today()
        message = [
            {"role": "user", "content": f"{date}の運勢"}
        ]

        answer = self.chatgpt(message)
        print(answer)

        say(answer)

    def message_uranai(self, say, context):
        word = context['matches'][0]
        print(word)

        message = [
            {"role": "system", "content": "ムーンプリンセス妃弥子になりきって今日の12星座占いをしてください。各星座に1文程度の占い結果も付けてください。"},
            {"role": "user", "content": f"{word}の占い結果を教えてください"},
        ]

        answer = self.chatgpt(message)
        print(answer)

        say(answer)


    def message_seimei(self, say, context):
        word = context['matches'][0]
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
            {"role": "system", "content": """
あなたはタロットカードの占い師です。
タロットカードを大アルカナを 3 枚引いて、過去と現在と未来を占ってください。

例
```
【過去】 正位置の「死神」
過去には、大きな変化があったようです。あなたがこれまで手にしてきたもの、経験してきたこと、人生のターニングポイントなどを思い出しましょう。死神は変化、終わり、新しい始まりを表しています。何かが終わった後、あなたは空白期間を過ごし、そこから新しい人生をスタートさせたのかもしれません。
```
"""},
            {"role": "user", "content": "占い結果を教えてください"},
        ]

        answer = self.chatgpt(message)
        print(answer)

        say(answer)
