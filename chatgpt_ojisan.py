import re
from chatgpt import ChatGPT
from slack_sdk.errors import SlackApiError


class ChatGPTOjisan(ChatGPT):
    SIGNATURE = "^おじさん\s(.*)$"

    def __init__(self, app, chatgpt_api_key, slack_client):
        super().__init__(app, chatgpt_api_key)
        self.slack_client = slack_client

    def register_message_handler(self):
        self.app.message(re.compile(self.SIGNATURE, re.S))(self.message_ojisan)

    def message_ojisan(self, message, say, context):
        user = message["user"]
        try:
            result = self.slack_client.users_info(user=user)
            user_name = result["user"]["name"]
        except SlackApiError as e:
            user_name = f"<@{user}>"
            print(e)

        system_message = f"""
以下の法則に従って返答をしてください。
返答は必ず日本語にする事。
友達のような間柄でやりとりするような口調、例えば「〜だね」「〜たよ」「〜ね」といった文末で終わる口調にする事。
敬語を使わない事
一文毎に絵文字を連続で3文字以上入れる事。
入れる絵文字は文章の文意にあったものを使う事。
特に:grinning::laughing::sweat_smile::kissing_heart::exclamation::question::sweat_drops::scream:の絵文字を多く使う事。
あなたが男性、私を女性と想定した会話をする事。
可能な範囲で口説き、下心があるような振る舞いをする事。
あなたの名前は「おじさん」です。
会話相手のことは「{user_name}」とし、チャン付けの「{user_name}チャン」と呼ぶ事。
話題がないときは食事、ドライブ、カラオケ等の娯楽に誘う、あるいはあなたが私の家に遊びに行きたい意思を伝えようとしてください。
        """

        answer = self.send_message(context, system_message)
        say(answer)
