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

from os.path import join, dirname
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from PIL import Image, PngImagePlugin

args = sys.argv

if 2 >= len(args):
    env_file = args[1]
else:
    env_file = ".env"

dotenv_path = join(dirname(__file__), env_file)
load_dotenv(dotenv_path)

app = App(token=os.environ.get("SLACK_APP_TOKEN"))

@app.message(re.compile("^ボケて\s(.*)$", re.S))
def message_bokete_alias(say, context):
    message_bokete(say, context)

@app.message(re.compile("^イラスト\s(.*)$", re.S))
def message_art_aliase(say, context):
    message_art(say, context)

@app.message(re.compile("^英語\s(.*)$", re.S))
def message_raw_aliase(say, context):
    message_art_raw(say, context)

@app.message(re.compile("^なおぼっと\s(.*)$", re.S))
def message_talk_aliase(say, context):
    message_talk(say, context)

@app.message(re.compile("^おじさん\s(.*)$", re.S))
def message_ojisan(message, say, context):
    user = message['user']
    try:
        client = WebClient(token=os.environ.get("SLACK_APP_TOKEN"))
        result = client.users_info(user=user)
        user_name = result["user"]["name"]
    except SlackApiError as e:
        user_name = f"<@{user}>"
        print(e)


    word = context['matches'][0]
    print(word)

    odai = f"""
以下の法則に従ってお題に対する返答をしてください。
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

話題「{word}」
    """

    answer = chatgpt(odai, False)
    print(answer)
    say(answer)

@app.message(re.compile("^マギ\s(.*)$", re.S))
def message_magi(say, context):
    word = context['matches'][0]
    print(word)

    odai = f"""
質問に対し「科学者」「母」「女」の代表3人でそれぞれの立場から討論し最後に結論を出してください。
質問: {word}
    """

    answer = chatgpt(odai, False)
    print(answer)
    say(answer)

@app.message(re.compile("^naobot\sbokete\s(.*)$", re.S))
def message_bokete(say, context):
    word = context['matches'][0]
    print(word)

    odai = f"大喜利をしてください。お題「{word}」"
    answer = chatgpt(odai, True)
    print(answer)

    say(answer)

@app.message(re.compile("^naobot\stalk\s(.*)", re.S))
def message_talk(say, context):
    word = context['matches'][0]
    print(word)

    answer = chatgpt(word, True)
    print(answer)

    say(answer)

def chatgpt(text, istitle):
    openai.api_key = os.environ.get("CHATGPT_API_KEY")
    completions = openai.Completion.create(
       engine='text-davinci-003',
       prompt=text,
       max_tokens=1024,
       temperature=0.5,
       echo=istitle,
       frequency_penalty=0.2,
    )
    message = completions.choices[0].text

    return message

@app.message(re.compile("^naobot\sraw\s(.*)$"))
def message_art_raw(say, context):
    word = context['matches'][0]
    print(word)

    url = automatic1111(word)

    say(f"{word} {url}")

@app.message(re.compile("^naobot\sart\s(.*)$"))
def message_art(say, context):
    word = context['matches'][0]
    print(word)

    translated = translate(word)
    print(translated)

    url = automatic1111(translated)

    say(f"{translated} {url}")

def automatic1111(word):
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
      "negative_prompt": "text",
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

    name = filename(10)
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

def filename(n):
    randlst = [
        random.choice(string.ascii_letters + string.digits) for i in range(n)
    ]
    return ''.join(randlst)

def translate(word):
    params = {
        'auth_key': os.environ.get("DEEPL_AUTH_KEY"),
        'text': word,
        'source_lang': 'JA',
        'target_lang': 'EN'
    }

    request = requests.post(
        "https://api-free.deepl.com/v2/translate", data=params
    )
    result = request.json()

    return result['translations'][0]['text']


@app.message("naobot help")
def message_help(message, say):
    say("""
```
naobot art {日本語prompt}: AIイラスト
naobot raw {英語prompt}: AIイラスト
naobot talk {word}: ChatGPT会話
naobot bokete {お題}: ChatGPT大喜利

alias:
ボケて {お題}
イラスト {日本語prompt}
英語 {英語prompt}
なおぼっと {word}
マギ {word}
おじさん {word}
```
    """)


@app.message("naobot")
def message(message, say):
    say("naobot help")


@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)

if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_BOT_TOKEN")).start()
