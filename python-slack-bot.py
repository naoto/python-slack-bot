import os
import re
import sys

from os.path import join, dirname
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from illust import Illust
from chatgpt import ChatGPT
from chatgpt_talk import ChatGPTTalk
from chatgpt_movie import ChatGPTMovie
from chatgpt_summary import ChatGPTSummary
from chatgpt_bokete import ChatGPTBokete
from chatgpt_ojisan import ChatGPTOjisan
from chatgpt_kusorep import ChatGPTKusorep
from chatgpt_magi import ChatGPTMagi
from spiritual import Spiritual
from translate import Translate

class TalkBot:
    def __init__(self, app_token, bot_token, chatgpt_api_key, deepl_api_key, automatic1111_domain):
        self.app_token = app_token
        self.bot_token = bot_token
        self.chatgpt_api_key = chatgpt_api_key
        self.app = App(token=app_token)
        self.chatgpt = ChatGPTTalk(chatgpt_api_key)
        self.chatgpt_movie = ChatGPTMovie(chatgpt_api_key)
        self.chatgpt_summary = ChatGPTSummary(chatgpt_api_key)
        self.spiritual = Spiritual(chatgpt_api_key)
        self.translate = Translate(chatgpt_api_key)
        self.illust = Illust(deepl_api_key, automatic1111_domain)
        self.bokete = ChatGPTBokete(chatgpt_api_key)
        self.ojisan = ChatGPTOjisan(chatgpt_api_key, bot_token)
        self.kusorep = ChatGPTKusorep(chatgpt_api_key)
        self.magi = ChatGPTMagi(chatgpt_api_key)

        self.register_message_handler()

    def register_message_handler(self):
        self.app.message(re.compile("^talk reset"))(self.chatgpt.message_talk_reset)
        self.app.message(re.compile("^job$"))(self.chatgpt.message_job_check)
        self.app.message(re.compile("^job reset$"))(self.chatgpt.message_job_reset)
        self.app.message(re.compile("^job\s(.*)", re.S))(self.chatgpt.message_job)
        self.app.message(re.compile("^なおぼっと\s(.*)$", re.S))(self.chatgpt.message_talk)
        self.app.message(re.compile("^naobot\stalk\s(.*)", re.S))(self.chatgpt.message_talk)

        self.app.message(re.compile("^ボケて\s(.*)$", re.S))(self.bokete.message_bokete)
        self.app.message(re.compile("^naobot\sbokete\s(.*)$", re.S))(self.bokete.message_bokete)
        self.app.message(re.compile("^タロット", re.S))(self.spiritual.message_talot)
        self.app.message(re.compile("^姓名判断\s(.*)$", re.S))(self.spiritual.message_seimei)
        self.app.message(re.compile("^占い\s(.*)$", re.S))(self.spiritual.message_uranai)
        self.app.message(re.compile("^運勢", re.S))(self.spiritual.message_unsei)
        self.app.message(re.compile("^e2j\s(.*)$", re.S))(self.translate.message_e2j)
        self.app.message(re.compile("^j2e\s(.*)$", re.S))(self.translate.message_j2e)
        self.app.message(re.compile("^movie\s<?(.*?)>?$", re.S))(self.chatgpt_movie.message_movie)
        self.app.message(re.compile("^summary\s<?(.*?)>?$", re.S))(self.chatgpt_summary.message_summary)

        self.app.message(re.compile("^おじさん\s(.*)$", re.S))(self.ojisan.message_ojisan)
        self.app.message(re.compile("^マギ\s(.*)$", re.S))(self.magi.message_magi)
        self.app.message(re.compile("^クソリプ\s(.*)", re.S))(self.kusorep.message_kusorep)

        self.app.message(re.compile("^イラスト\s(.*)$", re.S))(self.illust.message_art)
        self.app.message(re.compile("^naobot\sart\s(.*)$", re.S))(self.illust.message_art)
        self.app.message(re.compile("^英語\s(.*)$", re.S))(self.illust.message_raw_art)
        self.app.message(re.compile("^naobot\sraw\s(.*)$", re.S))(self.illust.message_raw_art)
        self.app.message(re.compile("^naobot prompt:(.*)\n\s*negative:(.*)$", re.S))(self.illust.message_prompt)

        self.app.message(re.compile("naobot help", re.S))(self.message_help)

    def start(self):
        SocketModeHandler(self.app, self.bot_token).start()

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
            deepl_api_key=os.environ.get("DEEPL_AUTH_KEY"),
            automatic1111_domain=os.environ.get("AUTOMATIC1111_DOMAIN"),
    )

    talkbot.start()
