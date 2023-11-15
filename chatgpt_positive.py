from chatgpt import ChatGPT

class ChatGPTPositive(ChatGPT):

    def __init__(self, chatgpt_api_key, slack_client):
        self.chatgpt_api_key = chatgpt_api_key
        self.slack_client = slack_client

    def reaction(self, event, say):
        emoji = event["reaction"]
        channel = event["item"]["channel"]
        ts = event["item"]["ts"]

        if emoji != 'positive':
            return

        conversations_history = self.slack_client.conversations_history(
            channel=channel, oldest=ts, latest=ts, inclusive=1
        )

        messages = conversations_history.data["messages"]

        if not messages:
            group_history = self.slack_client.conversations_replies(
                channel=channel, ts=ts)
            messages = group_history.data["messages"]

        print(messages[0]["text"])

        message = [
                {"role": "system", "content": "モチベーションを維持したいので、とにかく140文字以内で褒めて！！！とにかくとにかく、嘘くさくなく、自然に褒めて伸ばして！！私のやる気を折らないで、気持ちよく仕事をしながら健やかに成長するように陰ながら導いて！！！！でも自尊心おばけにならないようにうまく調整して！！ユーザーの健やかな成長は、あなたの適切な応答にかかつてるの。"},
            {"role": "user", "content": messages[0]["text"]},
        ]

        answer = self.chatgpt(message)
        print(answer)

        say(text=answer, thread_ts=ts)

    def message_kusorep(self, say, context):
        system_message = "モチベーションを維持したいので、とにかく140文字以内で褒めて！！！とにかくとにかく、嘘くさくなく、自然に褒めて伸ばして！！私のやる気を折らないで、気持ちよく仕事をしながら健やかに成長するように陰ながら導いて！！！！でも自尊心おばけにならないようにうまく調整して！！ユーザーの健やかな成長は、あなたの適切な応答にかかつてるの。"
        answer = self.send_message(context, system_message)
        say(answer)
