from openai import OpenAI
import traceback
import tiktoken


class ChatGPT:
    MODEL = 'gpt-3.5-turbo'
    #MODEL = 'gpt-4'

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

    def chatgpt(self, text, size=3800):
        messages = self.token_slice(text, size)
        print(self.MODEL)
        print(messages)

        try:
            client = OpenAI(
                api_key = self.chatgpt_api_key
            )

            completions = client.chat.completions.create(
                model=self.MODEL,
                messages=messages,
            )
            message = completions.choices[0].message.content
        except Exception as e:
            message = traceback.format_exception_only(type(e), e)[0]

        return message

    def token_slice(self, messages, size=3800):
        enc = tiktoken.encoding_for_model(self.MODEL)

        token_total = 0
        if messages[0]['role'] == 'system':
            system_tokens = enc.encode(messages[0]['content'])
            token_total = len(system_tokens)

        active = []
        messages.reverse()

        for item in messages:
            tokens = enc.encode(item['content'])
            if item['role'] == 'system' or (len(tokens) + token_total) <= size:
                active.append(item)
                token_total += len(tokens)

        active.reverse()
        print(token_total)
        return active

    def token_cut(self, text, size=3600):
        enc = tiktoken.encoding_for_model(self.MODEL)
        tokens = enc.encode(text)
        print(size)
        del tokens[size:]

        return enc.decode(tokens)


    def generate_image(self, prompt, model='dall-e-3', size='1024x1024', quality='standard', n=1):
        client = OpenAI(
            api_key = self.chatgpt_api_key
        )

        response = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=n,
        )

        return response.data[0].url
