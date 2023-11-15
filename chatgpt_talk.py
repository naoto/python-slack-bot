from chatgpt import ChatGPT

class ChatGPTTalk(ChatGPT):
    def __init__(self, chatgpt_api_key):
        self.chatgpt_api_key = chatgpt_api_key
        self.message_history = []
        self.talk_system = "あなたは高性能AIです"

    def message_talk(self, say, context):
        word = context['matches'][0]
        print(word)

        self.message_history.append({"role": "user", "content": word})

        _message = self.message_history.copy()
        _message.insert(0, {"role": "system", "content": self.talk_system})

        answer = self.chatgpt(_message)
        print(answer)

        self.message_history.append({"role": "assistant", "content": answer})
        say(answer)

    def message_job_check(self, say, context):
        print(f"job {self.talk_system}")

        say(f"job: {self.talk_system}")

    def message_job_reset(self, say, context):
        print("job reset")

        self.talk_system = "あなたは高性能AIです"
        say("job reset")

    def message_job(self, say, context):
        word = context['matches'][0]
        print(word)

        self.talk_system = word

        say(f"job: {self.talk_system}")
        self.message_talk_reset(say, context)

    def message_talk_reset(self, say, context):
        self.message_history = []
        say("Talk Reset Success")
