import os
import random
import string
import requests
import json
import base64
import io
import re
import html

from os.path import join, dirname
from PIL import Image, PngImagePlugin

class Illust:
    def __init__(self, deepl_api_key, automatic1111_domain):
        self.deepl_api_key = deepl_api_key
        self.automatic1111_domain = automatic1111_domain

    def response(self, url, prompt, jp_prompt=None):
        if jp_prompt is None:
            jp_prompt = prompt

        return [
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": prompt
                    },
                    "block_id": "image4",
                    "image_url": url,
                    "alt_text": jp_prompt
                }
               ]

    def parent(self, context, event):
        if 'thread_ts' not in event:
            return -1, None

        channel = event['channel']
        ts = event['thread_ts']

        conversations_history = context.client.conversations_history(
            channel=channel, oldest=ts, latest=ts, inclusive=1
        )

        messages = conversations_history.data["messages"]

        if not messages:
            group_history = context.client.conversations_replies(channel=channel, ts=ts)
            messages = group_history.data["messages"]
        print(messages[0]['blocks'][0]['image_url'])
        seeds = re.findall('\?seed=(\d+)', messages[0]['blocks'][0]['image_url'])

        if not seeds:
            return -1, ts

        return seeds[0], ts

    def message_art(self, say, context, event):
        word = context['matches'][0]
        print(word)

        seed, ts = self.parent(context, event)

        translated = html.unescape(self.translate(word))
        print(translated)

        url = self.automatic1111(word=translated, seed=seed)

        say(blocks=self.response(url, translated, word), thread_ts=ts)

    def message_raw_art(self, say, context, event):
        word = html.unescape(context['matches'][0])
        print(word)

        seed, ts = self.parent(context, event)

        url = self.automatic1111(word=word, seed=seed)

        say(blocks=self.response(url, word), thread_ts=ts)

    def message_prompt(self, say, context, event):
        prompt = context['matches'][0]
        negative = context['matches'][1]
        print(prompt)
        print(negative)

        seed, ts = self.parent(context, event)
        prompt = html.unescape(prompt)

        url = self.automatic1111(prompt, negative, seed)

        say(blocks=self.response(url, prompt), thread_ts=ts)

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

    def automatic1111(self, word, negative='anime, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated,ugly, disfigured, ullustration, (((painting))), toon, manga, comic, Cartoonize', seed=-1):
        payload = {
            "enable_hr": False,
            "denoising_strength": 0,
            "firstphase_width": 0,
            "firstphase_height": 0,
            "hr_scale": 2,
            "hr_upscaler": "string",
            "hr_second_pass_steps": 0,
            "hr_resize_x": 0,
            "hr_resize_y": 0,
            #"prompt": f"cinematic still ({word}) . emotional, harmonious, vignette,highly detailed, highbudget, bokeh, cinemascope, moody, epic,gorgeous, film grain, grainy",
            "prompt": f"cinematic still ({word}), emotional, harmonious, highly detailed, highbudget, vignette, photograph, cinema photo",
            "styles": [
                ""
            ],
            "seed": seed,
            "subseed": -1,
            "subseed_strength": 0,
            "seed_resize_from_h": -1,
            "seed_resize_from_w": -1,
            "sampler_name": "Euler a",
            "sampler_index": "Euler a",
            "batch_size": 1,
            "n_iter": 1,
            "steps": 30,
            "cfg_scale": 7,
            "width": 512,
            "height": 512,
            "restore_faces": False,
            "tiling": False,
            "do_not_save_samples": False,
            "do_not_save_grid": False,
            "negative_prompt": negative,
            "eta": 0,
            "s_churn": 0,
            "s_tmax": 0,
            "s_tmin": 0,
            "s_noise": 1,
            "override_settings": {},
            "override_settings_restore_afterwards": True,
            "script_args": [],
            "send_images": True,
            "save_images": False,
            "alwayson_scripts": {}
        }
        payload_json = json.dumps(payload)
        print(payload_json)

        response = requests.post(
            url=f"http://{self.automatic1111_domain}/sdapi/v1/txt2img",
            data=payload_json
        ).json()

        seed = json.loads(response["info"])["seed"]
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
        img_url = response.text + "?seed=" + str(seed)
        requests.get(img_url)

        return img_url
