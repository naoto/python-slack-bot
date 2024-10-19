import os
import random
import string
import requests
import json
import base64
import io
import re
import html
import queue
import threading
import time
import subprocess
import signal

from os.path import join, dirname
from PIL import Image, PngImagePlugin
from plugin import Plugin
from chatgpt import ChatGPT
from modules import buckup

class Illust(ChatGPT):
    SIGNATURE_JP = '^イラスト\s(.*)$'
    SIGNATURE_EN = '^naobot\sart\s(.*)$'
    SIGNATURE_RAW = '^naobot\sraw\s(.*)$'
    SIGNATURE_PROMPT = '^naobot prompt:(.*)\n\s*negative:(.*)$'
    SIGNATURE_I2I_PROMPT = '^i2i\s(.*)$'
    SIGNATURE_I2I2_PROMPT = '^イメイメ\s(.*)$'

    SIGNATURE_HOKUSAI = '^葛飾北斎\s(.*)$'
    SIGNATURE_UKIYOE = '^浮世絵\s(.*)$'

    SIGNATURE_POEMU = '^ポエム\s(.*)$'

    SIGNATURE_QUEUE_CHECK = "^イラストキュー$"

    def __init__(self, app, deepl_api_key, automatic1111_domain, chatgpt_api_key, queue):
        super().__init__(app, chatgpt_api_key)
        self.deepl_api_key = deepl_api_key
        self.automatic1111_domain = automatic1111_domain
        self.q = queue
        self.worker_count = 0
        self.worker_queue = ""
        self.sd_path = os.environ.get("SD_PATH")
        self.sd_start()
        thread = threading.Thread(target=self.worker, args=(self.q,))
        thread.start()
        response = app.client.auth_test()
        self.user_id = response["user_id"]
        self.buckup_queue_file_path = "queue.pkl"
        self.load_queue()

    def register_message_handler(self):
        self.app.message(re.compile(self.SIGNATURE_JP, re.S))(self.message_art)
        self.app.message(re.compile(self.SIGNATURE_EN, re.S))(self.message_art)
        self.app.message(re.compile(self.SIGNATURE_RAW, re.S))(self.message_raw_art)
        self.app.message(re.compile(self.SIGNATURE_PROMPT, re.S))(self.message_prompt)
        self.app.message(re.compile(self.SIGNATURE_I2I_PROMPT, re.S))(self.message_i2i_prompt)
        self.app.message(re.compile(self.SIGNATURE_I2I2_PROMPT, re.S))(self.message_i2i_prompt)

        self.app.message(re.compile(self.SIGNATURE_HOKUSAI, re.S))(self.message_hokusai)
        self.app.message(re.compile(self.SIGNATURE_UKIYOE, re.S))(self.message_ukiyoe)
        self.app.message(re.compile(self.SIGNATURE_QUEUE_CHECK, re.S))(self.message_queue_check)

        self.app.message(re.compile(self.SIGNATURE_POEMU, re.S))(self.message_poemu)

    def load_queue(self):
        queue = buckup.load_buckup_queue(self.buckup_queue_file_path)
        if queue is not None:
            for item in queue:
                self.queue_put(**item)


    def sd_start(self):
        self.process = subprocess.Popen(['./webui.sh', '--skip-python-version-check', '--skip-torch-cuda-test', '--nowebui', '--no-hashing', '--skip-version-check', '--allow-code', '--medvram', '--xformers', '--enable-insecure-extension-access', '--api', '--opt-channelslast'], cwd=self.sd_path, preexec_fn=os.setsid)
        time.sleep(25)

    def sd_restart(self):
        #self.process.terminate()
        #self.process.wait()
        os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
        self.sd_start()

    def queue_put(self, word, negative, seed, url, prompt, ts, say):
        if self.q.full():
            raise Exception("Queueがいっぱいです")

        qp = {"word": word, "negative": negative, "seed": seed, "url": url, "prompt": prompt, "ts": ts, "say": say}
        self.q.put(qp)
        buckup.buckup_queue(self.q.queue, self.buckup_queue_file_path)

    def worker(self, q):
        while True:
            try:
                item = q.get()
                if item is None:
                    time.sleep(10)
                    continue;
                elif item['url'] is None:
                    self.worker_count = 1
                    self.worker_queue = item['prompt']
                    url = self.automatic1111(item['word'], item['negative'], item['seed'])
                else:
                    self.worker_count = 1
                    self.worker_queue = item['prompt']
                    print(f"i2i:{item['word']}, {item['url']}")
                    url = self.automatic1111_i2i(item['word'], item['url'])

                self.worker_count = 0
                self.worker_queue = ""
                item["say"](blocks=self.response(url, item["word"], item["prompt"]), thread_ts=item["ts"], reply_broadcast=True)
                q.task_done()
                buckup.buckup_queue(q.queue, self.buckup_queue_file_path)
                self.sd_restart()

            except Exception as e:
                self.worker_count = 0
                self.worker_queue = ""
                item["say"](str(e))

    def response(self, url, prompt, jp_prompt=None):
        if jp_prompt is None:
            jp_prompt = prompt

        return [
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": jp_prompt
                    },
                    "block_id": "image4",
                    "image_url": url,
                    "alt_text": prompt
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

    def get_parent_url(self, context, event):
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

        return messages[0]['blocks'][0]['image_url'], ts


    def message_poemu(self, say, context):
        system_message = """
        あなたは画像生成ＡＩのプロンプト職人です。
        ワードの場面を情景的に英語で説明してください。
        """

        answer = self.send_message(context, system_message)
        print(answer)

        prompt = [
            {"role": "system", "content": "あなたは通訳です。質問の内容を日本語に翻訳して返答してください。返答は翻訳した内容だけにしてください"},
            {"role": "user", "content": answer}
        ]

        trans = self.chatgpt(prompt)
        print(trans)

        self.queue_put(answer, None, -1, None, trans, None, say)

    def message_hokusai(self, say, context, event):
        word = context['matches'][0]
        print(word)

        try:
            prompt_word = f"葛飾北斎が描いた浮世絵版「{word}」"
            seed, ts = self.parent(context, event)

            translated = html.unescape(self.translate(prompt_word))
            print(translated)

            self.queue_put(translated, None, seed, None, prompt_word, ts, say)
            #url = self.automatic1111(word=translated, seed=seed)

            #say(blocks=self.response(url, translated, prompt_word), thread_ts=ts, reply_broadcast=True)
        except Exception as e:
            say(str(e))

    def message_queue_check(self, say, context, event):
        size = self.q.qsize() + self.worker_count
        say(f"キュー残り:{size}")

        q = self.q.queue
        qlist = [f"- {item['prompt']}" for item in q]

        if self.worker_count == 1:
          qlist.insert(0, f"- {self.worker_queue}")

        say("\n".join(qlist))

    def message_ukiyoe(self, say, context, event):
        word = context['matches'][0]
        print(word)

        try:
            prompt_word = f"<lora:Ukiyo-e Art:1>, Ukiyo-e Art - {word}"
            seed, ts = self.parent(context, event)

            translated = html.unescape(self.translate(prompt_word))
            print(translated)

            self.queue_put(translated, None, seed, None, prompt_word, ts, say)
            #url = self.automatic1111(word=translated, seed=seed)

            #say(blocks=self.response(url, translated, prompt_word), thread_ts=ts, reply_broadcast=True)
        except Exception as e:
            say(str(e))


    def message_art(self, say, context, event):
        word = context['matches'][0]
        print(word)

        try:
            seed, ts = self.parent(context, event)

            translated = html.unescape(self.translate(word))
            print(translated)

            self.queue_put(translated, None, seed, None, word, ts, say)
            #url = self.automatic1111(word=translated, seed=seed)

            #say(blocks=self.response(url, translated, word), thread_ts=ts, reply_broadcast=True)
        except Exception as e:
            say(str(e))

    def message_raw_art(self, say, context, event):
        word = html.unescape(context['matches'][0])
        print(word)

        try:
            seed, ts = self.parent(context, event)

            self.queue_put(word, None, seed, None, word, ts, say)
            #url = self.automatic1111(word=word, seed=seed)

            #say(blocks=self.response(url, word), thread_ts=ts, reply_broadcast=True)
        except Exception as e:
            say(str(e))

    def message_prompt(self, say, context, event):
        prompt = context['matches'][0]
        negative = context['matches'][1]
        print(prompt)
        print(negative)

        try:
            seed, ts = self.parent(context, event)
            prompt = html.unescape(prompt)

            self.queue_put(prompt, negative, seed, None, prompt, ts, say)
            #url = self.automatic1111(prompt, negative, seed)

            #say(blocks=self.response(url, prompt), thread_ts=ts, reply_broadcast=True)
        except Exception as e:
            say(str(e))

    def message_i2i_prompt(self, say, context, event):
        word = context['matches'][0]
        print(word)

        try:
            url, ts = self.get_parent_url(context, event)
            translated = html.unescape(self.translate(word))
            print(translated)

            self.queue_put(translated, None, None, url, word, ts, say)
            #url = self.automatic1111_i2i(translated, url)

            #say(blocks=self.response(url, translated, word), thread_ts=ts, reply_broadcast=True)
        except Exception as e:
            say(str(e))


    def translate(self, word):
        params = {
            'auth_key': self.deepl_api_key,
            'text': word,
            'source_lang': 'JA',
            'target_lang': 'EN'
        }

        try:
            request = requests.post(
                "https://api-free.deepl.com/v2/translate", data=params
            )
            result = request.json()
        except Exception as e:
            print(e)
            raise Exception('DeepLエラー')

        return result['translations'][0]['text']

    def filename(self, n):
        randlst = [
            random.choice(string.ascii_letters + string.digits) for i in range(n)
        ]
        return ''.join(randlst)

    def automatic1111(self, word, negative, seed=-1):
        #negative = "anime, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated,ugly, disfigured, ullustration, (((painting))), toon, manga, comic, Cartoonize"
        negative = ""
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
            "prompt": word,
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
            "scheduler": "Simple",
            "batch_size": 1,
            "n_iter": 1,
            "steps": 25,
            "cfg_scale": 1,
            "distilled_cfg_scale": 3.5,
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

    def automatic1111_i2i(self, word, url, negative='', seed=-1):

        response = requests.get(url)
        image_data = response.content
        b64image = base64.b64encode(image_data).decode('utf-8')

        payload = {
            "prompt": word,
            "negative_prompt": "",
            "seed": seed,
            "batch_size": 1,
            "n_iter": 1,
            "steps": 25,
            "cfg_scale": 1,
            "scheduler": "Simple",
            "distilled_cfg_scale": 3.5,
            "width": 512,
            "height": 512,
            "denoising_strength": 0.75,
            "comments": {},
            "init_images": [
                b64image
            ],
            "sampler_index": "Euler a"
        }
        payload_json = json.dumps(payload)

        response = requests.post(
            url=f"http://{self.automatic1111_domain}/sdapi/v1/img2img",
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
