from plugin import Plugin
import queue
import re

class FluxQueue(Plugin):
    SIGNATURE_PUT = '^put\s(.*)$'
    SIGNATURE_GET = '^get$'

    def __init__(self, app):
        super().__init__(app)
        self.q = queue.Queue(maxsize=10)

    def register_message_handler(self):
        self.app.message(re.compile(self.SIGNATURE_PUT, re.S))(self.message_put)
        self.app.message(re.compile(self.SIGNATURE_GET, re.S))(self.message_get)

    def message_put(self, say, context):
        self.q.put(context['matches'][0])
        say("put")

    def message_get(self, say, context):
        say(self.q.get())

