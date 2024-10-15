from plugin import Plugin
import re
import requests
import time
import json
import emoji

class EmojiKitchin(Plugin):

  SIGNATURE = '^emoji\s(.*)$'

  def __init__ (self, app):
    super().__init__(app)

  def register_message_handler(self):
    self.app.message(re.compile(self.SIGNATURE, re.S))(self.generate)

  def generate(self, say, context, event):
    print(context['matches'][0])
    matches = re.findall(r'(:[a-zA-Z0-9_\+]+:)', context['matches'][0])
    print(matches)

    first = format(self.codepoint(emoji.emojize(matches[0], language='alias')), 'x')
    second = format(self.codepoint(emoji.emojize(matches[1], language='alias')), 'x')

    url = f"https://emojik.vercel.app/s/{first}_{second}?size=128"
    print(url)
    response = requests.get(url)

    if (response.status_code == 200):
      message = [{"type": "section", "text": { "type": "plain_text", "text": " " }, "accessory": {"type": "image", "image_url": url, "alt_text": "emoji"}}]
      say(blocks=message)

  def codepoint(self, uni):
    code = [ord(char) for char in uni]
    return code[0]
