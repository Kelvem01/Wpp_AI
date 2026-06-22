import logging

from flask import Flask, request, jsonify

from bot.ai_bot import AIBot
from services.waha import Waha

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

waha = Waha()
ai_bot = AIBot()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/chatbot/webhook/', methods=['POST'])
def webhook():
    try:
        data = request.json

        chat_id = data['payload']['from']
        received_message = data['payload']['body']

        is_group = '@g.us' in chat_id
        is_status = '@status@broadcast' in chat_id

        if is_group or is_status:
            return jsonify({'status': 'success', 'message': 'Mensagem de grupo/status ignorada.'}), 200

        waha.start_typing(chat_id=chat_id)
        response = ai_bot.invoke(question=received_message, chat_id=chat_id)
        waha.send_message(chat_id=chat_id, message=response)
        waha.stop_typing(chat_id=chat_id)

        logger.info('Mensagem processada para %s', chat_id)
        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.exception('Erro ao processar webhook: %s', e)
        return jsonify({'status': 'error', 'message': 'Erro interno'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)