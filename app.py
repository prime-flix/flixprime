from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
import openai

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return "Olá, mundo!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if data is None:
            app.logger.error('No JSON received or malformed JSON.')
            return jsonify({"error": "No JSON received or malformed JSON."}), 400
        app.logger.info(f'Received data: {data}')
        
        user_message = data.get('senderMessage')
        if not user_message:
            app.logger.warning('No message found in the request.')
            return jsonify({"error": "No message found in the request."}), 400

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é uma assistente gentil e didática. Sua função é dar suporte a clientes de uma plataforma de streaming com instruções simples e práticas de como solucionar problemas no sinal. Responda sempre com uma frase simples, passe a instrução passo a passo e perguntando ao cliente se ele seguiu o passo orientado."},
                {"role": "user", "content": user_message},
            ]
        )
        message = response.choices[0].message['content']
        app.logger.info(f'Generated response: {message}')
        return jsonify({"response": message})
    except Exception as e:
        app.logger.error(f'Error processing request: {e}')
        return jsonify({"error": "Failed to process request"}), 500

if __name__ == '__main__':
    app.run(debug=True)
