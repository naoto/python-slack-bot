from chatgpt import ChatGPT
from modules import buckup
import re

class ChatGPTTalk(ChatGPT):
    SIGNATURE_TALK_JP = '^なおぼっと\s(.*)$'
    SIGNATURE_TALK_EN = '^naobot\stalk\s(.*)$'
    SIGNATURE_TALK_RESET = '^talk reset$'
    SIGNATURE_JOB = '^job$'
    SIGNATURE_JOB_RESET = '^job reset$'
    SIGNATURE_JOB_SET = '^job\s(.*)$'
    SIGNATURE_PICTURE = '^挿絵$'

    def __init__(self, app, chatgpt_api_key, queue, talk):
        super().__init__(app, chatgpt_api_key)
        self.message_history = talk
        self.talk_history_file = "talk_history.json"
        self.talk_job_file = "talk_job.json"
        self.load_buckup(self.talk_history_file)
        self.talk_system = buckup.load_buckup_job(self.talk_job_file)
        self.q = queue

    def register_message_handler(self):
        self.app.message(re.compile(self.SIGNATURE_TALK_JP, re.S))(self.message_talk)
        self.app.message(re.compile(self.SIGNATURE_TALK_EN, re.S))(self.message_talk)
        self.app.message(re.compile(self.SIGNATURE_TALK_RESET, re.S))(self.message_talk_reset)
        self.app.message(re.compile(self.SIGNATURE_JOB, re.S))(self.message_job_check)
        self.app.message(re.compile(self.SIGNATURE_JOB_RESET, re.S))(self.message_job_reset)
        self.app.message(re.compile(self.SIGNATURE_JOB_SET, re.S))(self.message_job)
        self.app.message(re.compile(self.SIGNATURE_PICTURE, re.S))(self.message_picture)

    def load_buckup(self, filepath):
        talk = buckup.load_buckup(filepath)
        for t in talk:
            self.message_history.append(t)

    def queue_put(self, word, negative, seed, url, prompt, ts, say):
        if self.q.full():
            raise Exception("Queueがいっぱいです")

        qp = {"word": word, "negative": negative, "seed": seed, "url": url, "prompt": prompt, "ts": ts, "say": say}
        self.q.put(qp)

    def message_picture(self, say, context):
        _message = self.message_history.copy()
        _message.append({"role": "user", "content": "この話を象徴する場面の情景を英語で簡潔に教えて。"})

        answer = self.chatgpt(_message)

        prompt = [
            {"role": "system", "content": "あなたは通訳です。質問の内容を日本語に翻訳して返答してください。返答は翻訳した内容だけにしてください"},
            {"role": "user", "content": answer}
        ]

        jp_answer = self.chatgpt(prompt)
        print(jp_answer)

        self.queue_put(answer, None, -1, None, jp_answer, None, say) 


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
        buckup.buckup(self.message_history, self.talk_history_file)

    def message_job_check(self, say, context):
        print(f"job {self.talk_system}")

        say(f"job: {self.talk_system}")

    def message_job_reset(self, say, context):
        print("job reset")
        self.talk_system = "あなたは高性能AIです"
        buckup.buckup_job(self.talk_system, self.talk_job_file)
        say("job reset")

    def message_job(self, say, context):
        word = context['matches'][0]
        print(word)

        self.talk_system = word
        buckup.buckup_job(self.talk_system, self.talk_job_file)

        say(f"job: {self.talk_system}")
        self.message_talk_reset(say, context)

    def message_talk_reset(self, say, context):
        self.message_history.clear()
        buckup.buckup(self.message_history, self.talk_history_file)
        say("Talk Reset Success")
