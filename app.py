from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
import openai

load_dotenv()

app = Flask(__name__)

# Armazenar histórico das conversas
conversations = {}

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

        user_id = data.get('senderName')
        user_message = data.get('senderMessage')
        if not user_message:
            app.logger.warning('No message found in the request.')
            return jsonify({"error": "No message found in the request."}), 400

        # Inicializa ou atualiza o histórico da conversa
        if user_id not in conversations:
            conversations[user_id] = []
        conversations[user_id].append({"role": "user", "content": user_message})

        # Adiciona instrução inicial se for a primeira mensagem
        if len(conversations[user_id]) == 1:
            conversations[user_id].insert(0, {"role": "system", "content": "Você é uma assistente gentil e didática. Sua função é dar suporte a clientes de uma plataforma de streaming com instruções simples e práticas de como solucionar problemas no sinal. Responda sempre com uma frase simples, passe a instrução passo a passo e perguntando ao cliente se ele seguiu o passo orientado. Após o cliente informar que esta tudo ok, encerre a conversa."})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversations[user_id]
        )
        message = response.choices[0].message['content']
        app.logger.info(f'Generated response: {message}')
        
        # Adiciona a resposta da IA ao histórico da conversa
        conversations[user_id].append({"role": "assistant", "content": message})

        # Verifica se o problema foi resolvido
        if "problema resolvido" in message.lower():
            conversations[user_id].append({"role": "assistant", "content": "Fico feliz que o problema foi resolvido. Se precisar de mais ajuda, por favor, entre em contato novamente. Tenha um ótimo dia!"})
            app.logger.info(f'Finalizing conversation with user {user_id}')
            return jsonify({"response": "Fico feliz que o problema foi resolvido. Se precisar de mais ajuda, por favor, entre em contato novamente. Tenha um ótimo dia!"})

        return jsonify({"response": message})
    except Exception as e:
        app.logger.error(f'Error processing request: {e}')
        return jsonify({"error": "Failed to process request"}), 500

if __name__ == '__main__':
    app.run(debug=True)