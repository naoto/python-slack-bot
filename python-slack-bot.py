import os
import re
import sys
import random
import string
import requests
import subprocess
import json
import base64
import io

from os.path import join, dirname
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from PIL import Image, PngImagePlugin

args = sys.argv

if 2 >= len(args):
    env_file = args[1]
else:
    env_file = ".env"

dotenv_path = join(dirname(__file__), env_file)
load_dotenv(dotenv_path)

app = App(token=os.environ.get("SLACK_APP_TOKEN"))

@app.message(re.compile("^naobot\sbokete\s(.*)$"))
def message_bokete(say, context):
    word = context['matches'][0]
    print(word)

    odai = f"大喜利をしてください。お題「{word}」"
    answer = chatgpt(odai)
    print(answer)

    say(answer)

@app.message(re.compile("^naobot\stalk\s(.*)$"))
def message_talk(say, context):
    word = context['matches'][0]
    print(word)

    answer = chatgpt(word)
    print(answer)

    say(answer)

def chatgpt(text):
    my_env = os.environ.copy()
    answer = subprocess.run(["./chatgpt", text], encoding='utf-8', stdout=subprocess.PIPE, env=my_env)

    return answer.stdout

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
naobot art: AIイラスト
naobot raw: AIイラスト（翻訳なし）
naobot talk: ChatGPT会話
naobot bokete: ChatGPT大喜利
    """)


@app.message("naobot")
def message(message, say):
    say("naobot help")


if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_BOT_TOKEN")).start()
