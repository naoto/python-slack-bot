import re
import requests
import time
import json
from plugin import Plugin


class Dog(Plugin):

    SIGNATURE = "^dog$"

    def __init__(self, app):
        super().__init__(app)

    def register_message_handler(self):
        self.app.message(re.compile(self.SIGNATURE, re.S))(self.generate)

    def generate(self, say, context, event):
        response = requests.get("https://dog.ceo/api/breeds/image/random")
        result = response.json()

        message = [
            {
                "type": "image",
                "title": {"type": "plain_text", "text": "dog!"},
                "alt_text": "dog!",
                "block_id": "image4",
                "image_url": result["message"],
            }
        ]
        say(blocks=message)
