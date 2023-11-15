from chatgpt import ChatGPT
import urllib.request
import os
import random
import string
import requests


class ChatGPTIllust(ChatGPT):
    def message(self, say, context):
        prompt = context['matches'][0]

        try:
            url = self.generate_image(prompt)
            print(url)
            cache_url = self.cache(url)
            say(blocks=self.response(cache_url, prompt))
        except Exception as e:
            file_uploader_domain = os.environ.get("FILE_UPLOADER_DOMAIN")
            say(blocks=self.response("https://{file_uploader_domain}/data/a313829b554653a04c8f.jpg", "エラー"))


    def response(self, url, prompt):
        return [
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": prompt
                    },
                    "block_id": "image4",
                    "image_url": url,
                    "alt_text": prompt,
                }
               ]

    def cache(self, url):
        filename = self.filename(10)
        path = f"./{filename}.png"
        urllib.request.urlretrieve(url, path)

        files = {
            'imagedata': open(path, 'rb')
        }

        fileyy_uploader_domain = os.environ.get("FILE_UPLOADER_DOMAIN")
        response = requests.post(f"https://{file_uploader_domain}/", files=files)

        os.remove(path)
        img_url = response.text
        requests.get(img_url)

        return img_url


    def filename(self, n):
        randlst = [
            random.choice(string.ascii_letters + string.digits) for i in range(n)
        ]
        return ''.join(randlst)
