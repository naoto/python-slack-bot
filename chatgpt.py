import openai
import traceback

class ChatGPT:
    def __init__(self, chatgpt_api_key):
        self.chatgpt_api_key = chatgpt_api_key

    def send_message(self, context, system_message):
        word = context['matches'][0]
        print(word)

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": word},
        ]

        answer = self.chatgpt(messages)
        print(answer)

        return answer

    def chatgpt(self, text):
        print(text)
        try:
            openai.api_key = self.chatgpt_api_key
            completions = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=text,
            )
            message = completions.choices[0].message.content
        except Exception as e:
            message = traceback.format_exception_only(type(e), e)[0]

        return message
