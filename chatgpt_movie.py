import re
from chatgpt import ChatGPT
from youtube_transcript_api import YouTubeTranscriptApi


class ChatGPTMovie(ChatGPT):
    MODEL = 'gpt-3.5-turbo'

    def message_movie(self, say, context):
        url = context['matches'][0]
        print(url)

        regex = r"(?:youtu\.be/|youtube\.com/watch\?v=)([\-\w]+)"
        match = re.search(regex, url)

        if match is not None:
            video_id = match.group(1)
        else:
            say("not movie url")
            return

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            word = ''
            for transcript in transcript_list:
                for tr in transcript.fetch():
                    word = word + tr['text']

            word = self.token_cut(word, 15000)

            messages = [
                {"role": "system", "content": "文章を日本語で要約してください。"},
                {"role": "user", "content": word}
            ]

            answer = self.chatgpt(messages, 16000)
        except Exception as e:
            answer = "字幕が取得できなかったよ"
        print(answer)

        say(answer)
