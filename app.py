import time
import random

from flask import Flask, request, jsonify

from bot.ai_bot import AIBot
from services.waha import Waha

app = Flask(__name__)

@app.route('/chatbot/webhook/',methods=['Post'])
def webhook():
    data = request.json

    waha = Waha()
    ai_bot = AIBot()

    chat_id = data['payload']['from']
    received_message = data['payload']['body']

    is_group = '@g.us' in chat_id
    is_status ='@status@broacast' in chat_id

    if is_group or is_status:
        return jsonify({'status':'sucess','message':'Mensagem de grupo/status ignorada.'}),
    
    waha.start_typing(chat_id=chat_id)
    
    response = ai_bot.invoke(question=received_message)

    time.sleep(random.randint(3,10))
    
    waha.send_message(
        chat_id=chat_id,
        message= response,
    )
    waha.stop_typing(chat_id=chat_id)
    
    return jsonify({'status': 'sucess'}), 200

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000, debug=True)