import os
import re
import sys
import random
import string
import requests
import json
import base64
import io
import openai
import traceback
import datetime

from os.path import join, dirname
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from PIL import Image, PngImagePlugin
from extractcontent3 import ExtractContent
from youtube_transcript_api import YouTubeTranscriptApi

class TalkBot:
    def __init__(self, app_token, bot_token, chatgpt_api_key, deepl_api_key):
        self.app_token = app_token
        self.bot_token = bot_token
        self.chatgpt_api_key = chatgpt_api_key
        self.deepl_api_key = deepl_api_key
        self.message_history = []
        self.talk_system = "あなたは友人です。フランクに友人に話しかけるような言葉遣いをしてください"
        self.app = App(token=app_token)
        self.slack_client = WebClient(token=bot_token)

        self.register_message_handler()

    def register_message_handler(self):
        self.app.message(re.compile("^talk reset"))(self.message_talk_reset)
        self.app.message(re.compile("^ボケて\s(.*)$", re.S))(self.message_bokete)
        self.app.message(re.compile("^naobot\sbokete\s(.*)$", re.S))(self.message_bokete)
        self.app.message(re.compile("^job$"))(self.message_job_check)
        self.app.message(re.compile("^job reset$"))(self.message_job_reset)
        self.app.message(re.compile("^job\s(.*)", re.S))(self.message_job)
        self.app.message(re.compile("^おじさん\s(.*)$", re.S))(self.message_ojisan)
        self.app.message(re.compile("^マギ\s(.*)$", re.S))(self.message_magi)
        self.app.message(re.compile("^e2j\s(.*)$", re.S))(self.message_e2j)
        self.app.message(re.compile("^j2e\s(.*)$", re.S))(self.message_j2e)
        self.app.message(re.compile("^タロット", re.S))(self.message_talot)
        self.app.message(re.compile("^姓名判断\s(.*)$", re.S))(self.message_seimei)
        self.app.message(re.compile("^占い\s(.*)$", re.S))(self.message_uranai)
        self.app.message(re.compile("^運勢", re.S))(self.message_unsei)
        self.app.message(re.compile("^クソリプ\s(.*)", re.S))(self.message_kusorep)
        self.app.message(re.compile("^movie\s<?(.*?)>?$", re.S))(self.message_movie)
        self.app.message(re.compile("^summary\s<?(.*?)>?$", re.S))(self.message_summary)
        self.app.message(re.compile("^なおぼっと\s(.*)$", re.S))(self.message_talk)
        self.app.message(re.compile("^naobot\stalk\s(.*)", re.S))(self.message_talk)

        self.app.message(re.compile("^イラスト\s(.*)$", re.S))(self.message_art)
        self.app.message(re.compile("^naobot\sart\s(.*)$", re.S))(self.message_art)
        self.app.message(re.compile("^英語\s(.*)$", re.S))(self.message_raw_art)
        self.app.message(re.compile("^naobot\sraw\s(.*)$", re.S))(self.message_raw_art)
        self.app.message(re.compile("^naobot prompt:(.*)\n\s*negative:(.*)$", re.S))(self.message_prompt)

        self.app.message(re.compile("naobot help", re.S))(self.message_help)

    def start(self):
        SocketModeHandler(self.app, self.bot_token).start()

    def send_message(self, context, system_message):
        word = context['matches'][0]
        print(word)

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": word},
        ]

        answer = self.chatgpt(messages)
        print(answer)

        return answer

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

    def message_movie(self, say, context):
        url = context['matches'][0]
        print(url)

        regex = r"(?:youtu\.be/|youtube\.com/watch\?v=)(\w+)"
        match = re.search(regex, url)

        if match is not None:
            video_id = match.group(1)
        else:
            say("not movie url")
            return

        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        word = ''
        for transcript in transcript_list:
            for tr in transcript.fetch():
                word = word + tr['text']

        if len(word) > 3500:
            word = word[:3500]

        messages = [
            {"role": "system", "content": "文章を日本語で要約してください。"},
            {"role": "user", "content": word}
        ]

        answer = self.chatgpt(messages)
        print(answer)

        say(answer)

    def message_kusorep(self, say, context):
        system_message = "あなたはTwitterにいるクソリプが得意な人です。質問に対してクソリプをしてください。"
        answer = self.send_message(context, system_message)
        say(answer)

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

    def message_j2e(self, say, context):
        system_message = "日本語を英語に翻訳してください"
        answer = self.send_message(context, system_message)
        say(answer)

    def message_e2j(self, say, context):
        system_message = "英語を日本語に翻訳してください"
        answer = self.send_message(context, system_message)
        say(answer)

    def message_magi(self, say, context):
        system_message = "質問に対し「科学者」「母」「女」の代表3人でそれぞれの立場から討論し最後に結論を出してください。"
        answer = self.send_message(context, system_message)
        say(answer)

    def message_ojisan(self, message, say, context):
        user = message['user']
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

    def message_talk_reset(self, say, context):
        self.message_history = []
        say("Talk Reset Success")

    def message_bokete(self, say, context):
        system_message = "あなたは芸人です。大喜利をしてください"

        answer = self.send_message(context, system_message)
        say(answer)

    def message_job_check(self, say, context):
        print(f"job {self.talk_system}")

        say(f"job: {self.talk_system}")

    def message_job_reset(self, say, context):
        print("job reset")

        self.talk_system = "あなたは高性能AIです"
        say("job reset")

    def message_job(self, say, context):
        word = context['matches'][0]
        print(word)

        self.talk_system = word

        say(f"job: {self.talk_system}")
        self.message_talk_reset(say, context)

    def message_talk(self, say, context):
        word = context['matches'][0]
        print(word)

        self.message_history.append({"role": "user", "content": word})

        _message = self.message_history.copy()
        _message.insert(0, {"role": "system", "content": self.talk_system})

        answer = self.chatgpt(_message)
        print(answer)

        self.message_history.append({"role": "assistant", "content": answer})
        if len(self.message_history) > 8:
            self.message_history.pop(0)
            self.message_history.pop(0)

        say(answer)

    def chatgpt(self, text):
        print(text)
        try:
            openai.api_key = self.chatgpt_api_key
            completions = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=text,
            )
            message = completions.choices[0].message.content
        except Exception as e:
            message = traceback.format_exception_only(type(e), e)[0]

        return message

    def message_art(self, say, context):
        word = context['matches'][0]
        print(word)

        translated = self.translate(word)
        print(translated)

        url = self.automatic1111(translated)

        say(f"{translated} {url}")

    def message_raw_art(self, say, context):
        word = context['matches'][0]
        print(word)

        url = self.automatic1111(word)

        say(f"{word} {url}")

    def message_prompt(self, say, context):
        prompt = context['matches'][0]
        negative = context['matches'][1]
        print(prompt)
        print(negative)

        url = self.automatic1111(prompt, negative)

        say(f"{url}")

    def translate(self, word):
        params = {
            'auth_key': self.deepl_api_key,
            'text': word,
            'source_lang': 'JA',
            'target_lang': 'EN'
        }

        request = requests.post(
            "https://api-free.deepl.com/v2/translate", data=params
        )
        result = request.json()

        return result['translations'][0]['text']

    def filename(self, n):
        randlst = [
            random.choice(string.ascii_letters + string.digits) for i in range(n)
        ]
        return ''.join(randlst)

    def automatic1111(self, word, negative='text'):
        payload = {
            "enable_hr": False,
            "denoising_strength": 0,
            "firstphase_width": 0,
            "firstphase_height": 0,
            "prompt": word,
            "styles": [
                "string"
            ],
            "seed": -1,
            "subseed": -1,
            "subseed_strength": 0,
            "seed_resize_from_h": -1,
            "seed_resize_from_w": -1,
            "batch_size": 1,
            "n_iter": 1,
            "steps": 28,
            "cfg_scale": 6,
            "width": 512,
            "height": 512,
            "restore_faces": False,
            "tiling": False,
            "negative_prompt": negative,
            "eta": 0,
            "s_churn": 0,
            "s_tmax": 0,
            "s_tmin": 0,
            "s_noise": 1,
            "override_settings": {},
            "sampler_index": "Euler"
        }
        payload_json = json.dumps(payload)

        automatic1111_domain = os.environ.get("AUTOMATIC1111_DOMAIN")
        response = requests.post(
            url=f"http://{automatic1111_domain}/sdapi/v1/txt2img",
            data=payload_json
        ).json()

        name = self.filename(10)
        for i in response['images']:
            image = Image.open(io.BytesIO(base64.b64decode(i)))
            image.save(f"{name}.png")

        files = {
            'imagedata': open(f"./{name}.png", 'rb')
        }

        file_uploader_domain = os.environ.get("FILE_UPLOADER_DOMAIN")
        response = requests.post(f"https://{file_uploader_domain}/", files=files)

        os.remove(f"{name}.png")

        return response.text

    def message_help(self, message, say):
        say("""
```
naobot art {日本語prompt}: AIイラスト
naobot raw {英語prompt}: AIイラスト
naobot talk {word}: ChatGPT会話
naobot bokete {お題}: ChatGPT大喜利
e2j {word}: 英語を日本語に翻訳
j2e {word}: 日本語を英語に翻訳
summary {url}: urlの中身を要約
movie {youtube_url}: Youtubeの動画の内容を要約

Raw Prompt/Negative Promt
naobot prompt:{prompt}
negative:{negative prompt}

ChatGPT Talk History Clear
talk reset

job: ChatGPT Talk System Context Echo
job {役割}: ChatGPT Talk System Context Set
job reset: ChatGPT Talk System Context Reset

alias:
ボケて {お題}
イラスト {日本語prompt}
英語 {英語prompt}
なおぼっと {word}
マギ {word}
おじさん {word}
クソリプ {word}

spiritual:
タロット
姓名判断 {姓} {名}
占い {星座}
運勢
```
        """)

if __name__ == "__main__":
    args = sys.argv

    if 2 >= len(args):
        env_file = args[1]
    else:
        env_file = ".env"

    dotenv_path = join(dirname(__file__), env_file)
    load_dotenv(dotenv_path)

    talkbot = TalkBot(
            app_token=os.environ.get("SLACK_APP_TOKEN"),
            bot_token=os.environ.get("SLACK_BOT_TOKEN"),
            chatgpt_api_key=os.environ.get("CHATGPT_API_KEY"),
            deepl_api_key=os.environ.get("DEEPL_AUTH_KEY")
    )

    talkbot.start()
