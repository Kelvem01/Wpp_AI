import logging

import requests

logger = logging.getLogger(__name__)


class Waha:
    def __init__(self, base_url='http://waha:3000', timeout=10):
        self.__api_url = base_url
        self.__timeout = timeout

    def _post(self, endpoint, payload):
        url = f'{self.__api_url}{endpoint}'
        headers = {'Content-Type': 'application/json'}
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.__timeout)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            logger.error('Falha ao chamar WAHA %s: %s', endpoint, e)
            raise

    def send_message(self, chat_id, message):
        self._post('/api/sendText', {
            'session': 'default',
            'chatId': chat_id,
            'text': message,
        })

    def start_typing(self, chat_id):
        self._post('/api/startTyping', {
            'session': 'default',
            'chatId': chat_id,
        })

    def stop_typing(self, chat_id):
        self._post('/api/stopTyping', {
            'session': 'default',
            'chatId': chat_id,
        })

if __name__ == '__main__':
    waha = Waha()
