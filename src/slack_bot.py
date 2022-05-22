import requests


class SlackBot:
    def __init__(self, name) -> None:
        self.name = name
        token_dir = './token/' + name + '.txt'
        with open(token_dir) as f:
            self.token = f.readline().strip()
        self.channel = '#alert'

    def post_message(self, text) -> None:
        print(text)
        requests.post(
            'https://slack.com/api/chat.postMessage',
            headers={'Authorization': 'Bearer ' + self.token},
            data={'channel': self.channel, 'text': text}
        )
