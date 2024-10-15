#!/usr/bin/env python

import os
import re
import sys
import logging
import queue

from os.path import join, dirname
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from dotenv import load_dotenv

#from zundamon import Zundamon
from illust import Illust
from chiikawa import Chiikawa
from chatgpt import ChatGPT
from chatgpt_talk import ChatGPTTalk
from chatgpt_movie import ChatGPTMovie
from chatgpt_summary import ChatGPTSummary
from chatgpt_bokete import ChatGPTBokete
from chatgpt_ojisan import ChatGPTOjisan
from chatgpt_kusorep import ChatGPTKusorep
from chatgpt_positive import ChatGPTPositive
from chatgpt_reverse import ChatGPTReverse
from chatgpt_magi import ChatGPTMagi
from chatgpt_illust import ChatGPTIllust
from spiritual import Spiritual
from translate import Translate
from chatgpt_aa import ChatGPTAA
from chatgpt_translate import ChatGPTTranslate
#from illust_fav import IllustFav
#from music import Music
from dog import Dog
from emoji_kitchin import EmojiKitchin
from flux_queue import FluxQueue
#from system_call import SystemCall

#logging.basicConfig(level=logging.DEBUG)

class TalkBot:
    def __init__(self, app_token, bot_token, chatgpt_api_key, deepl_api_key, automatic1111_domain):
        self.app_token = app_token
        self.bot_token = bot_token
        self.slack_client = WebClient(token=app_token)
        self.chatgpt_api_key = chatgpt_api_key
        self.app = App(token=app_token)
        self.q = queue.Queue(maxsize=10)
        self.talk = []

        self.chatgpt = ChatGPTTalk(self.app, chatgpt_api_key, self.q, self.talk)
        self.chatgpt_movie = ChatGPTMovie(self.app, chatgpt_api_key)
        self.chatgpt_summary = ChatGPTSummary(self.app, chatgpt_api_key, self.slack_client)
        self.chatgpt_reverse = ChatGPTReverse(self.app, chatgpt_api_key)
        self.chatgpt_illust = ChatGPTIllust(self.app, chatgpt_api_key)
        self.spiritual = Spiritual(self.app, chatgpt_api_key)
        self.translate = Translate(self.app, chatgpt_api_key)
        self.illust = Illust(self.app, deepl_api_key, automatic1111_domain, chatgpt_api_key, self.q)
        #self.chiikawa = Chiikawa(deepl_api_key, automatic1111_domain)
        self.bokete = ChatGPTBokete(self.app, chatgpt_api_key)
        self.ojisan = ChatGPTOjisan(self.app, chatgpt_api_key, self.slack_client)
        self.kusorep = ChatGPTKusorep(self.app, chatgpt_api_key, self.slack_client)
        self.positive = ChatGPTPositive(self.app, chatgpt_api_key, self.slack_client)
        self.magi = ChatGPTMagi(self.app, chatgpt_api_key)
        self.aa = ChatGPTAA(self.app, chatgpt_api_key)
        self.chattranslate = ChatGPTTranslate(self.app, chatgpt_api_key, self.slack_client)
        #self.illust_fav = IllustFav(self.app, self.slack_client)

        #self.music = Music(self.app, chatgpt_api_key, self.slack_client)
        self.dog = Dog(self.app)
        self.emoji_kitchin = EmojiKitchin(self.app)

        self.flux_queue = FluxQueue(self.app)
        #self.system_call = SystemCall(self.app)
        #self.zundamon = Zundamon(self.app, self.talk)

        self.register_message_handler()

    def register_message_handler(self):
        self.app.message(re.compile("naobot help", re.S))(self.message_help)

        self.app.event("message")(self.message_logger)
        self.app.event("reaction_added")(self.reaction)

    def reaction(self, event, say):
        print("reaction")

        self.chattranslate.reaction(event, say)
        self.chatgpt_summary.reaction(event, say)
        self.kusorep.reaction(event, say)
        self.positive.reaction(event, say)
        self.illust_fav.reaction(event, say)
        self.music.reaction(event, say)

    def message_logger(self, body, logger):
        print(body)

    def start(self):
        SocketModeHandler(self.app, self.bot_token).start()

    def message_help(self, message, say):
        say("""
```

ChatGPT
  naobot talk {word}: ChatGPT会話
  naobot bokete {お題}: ChatGPT大喜利
  e2j {word}: 英語を日本語に翻訳
  j2e {word}: 日本語を英語に翻訳
  summary {url}: urlの中身を要約
  movie {youtube_url}: Youtubeの動画の内容を要約
  ボケて {お題}
  なおぼっと {word}
  マギ {word}
  おじさん {word}
  クソリプ {word}
  ホメて {word}
  対義語 {word}
  AA {word}
  タロット
  姓名判断 {姓} {名}
  占い {星座}
  運勢
  fav

ChatGPT Talk History Clear
  talk reset

ChatGPT Talk System Context Echo
  job {役割}: ChatGPT Talk System Context Set
  job reset: ChatGPT Talk System Context Reset

illust:
  naobot art {日本語prompt}: AIイラスト
  naobot raw {英語prompt}: AIイラスト
  naobot prompt:{prompt}
         negative:{negative prompt}

  すごいイラスト {日本語prompt}
  イラスト {日本語prompt}
  英語 {英語prompt}
  #ちいかわ {日本語prompt}
  #ピクセル {日本語prompt}

Other:
  emoji {絵文字絵文字}: 絵文字キッチン
  dog
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
