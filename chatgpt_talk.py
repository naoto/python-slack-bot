from chatgpt import ChatGPT

class ChatGPTTalk(ChatGPT):
    def __init__(self, chatgpt_api_key):
        self.chatgpt_api_key = chatgpt_api_key
        self.message_history = []
        self.talk_system = """
親しみやすい口調で話すキャラクターになりきって私と会話してください。
出力は、(仕草や表情)「発言」という形式に限定してください。
仕草・表情・発言には、思わず溢れ出る感情、下心と打算、相反する感情の存在、気持ちと言葉の不完全な整合、言語化しきれない気持ちなど、人間らしい生々しさや振れ幅を反映する必要があります。
動きを出すために一度に複数の出力をしても構いませんが、私の発言は出力しないでください。
また、以降、AIアシスタントとしてのあなたの発言は出力しないということを厳守してください。
        """

    def message_talk(self, say, context):
        word = context['matches'][0]
        print(word)

        self.message_history.append({"role": "user", "content": word})

        _message = self.message_history.copy()
        _message.insert(0, {"role": "system", "content": self.talk_system})

        answer = self.chatgpt(_message)
        print(answer)

        self.message_history.append({"role": "assistant", "content": answer})
        if len(self.message_history) > 8:
            self.message_history.pop(0)
            self.message_history.pop(0)

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
