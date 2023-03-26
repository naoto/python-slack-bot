import re
from chatgpt import ChatGPT
from youtube_transcript_api import YouTubeTranscriptApi

class ChatGPTMovie(ChatGPT):
    def message_movie(self, say, context):
        url = context['matches'][0]
        print(url)

        regex = r"(?:youtu\.be/|youtube\.com/watch\?v=)(\w+)"
        match = re.search(regex, url)

        if match is not None:
            video_id = match.group(1)
        else:
            say("not movie url")
            return

        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        word = ''
        for transcript in transcript_list:
            for tr in transcript.fetch():
                word = word + tr['text']

        if len(word) > 3500:
            word = word[:3500]

        messages = [
            {"role": "system", "content": "文章を日本語で要約してください。"},
            {"role": "user", "content": word}
        ]

        answer = self.chatgpt(messages)
        print(answer)

        say(answer)
