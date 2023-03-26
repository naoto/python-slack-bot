import os
import random
import string
import requests
import json
import base64
import io

from os.path import join, dirname
from PIL import Image, PngImagePlugin

class Illust:
    def __init__(self, deepl_api_key, automatic1111_domain):
        self.deepl_api_key = deepl_api_key
        self.automatic1111_domain = automatic1111_domain

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

        response = requests.post(
            url=f"http://{self.automatic1111_domain}/sdapi/v1/txt2img",
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
