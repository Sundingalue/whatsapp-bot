from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os

app = Flask(__name__)

# Configurar OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Historial de conversaciones por número
session_history = {}

@app.route("/", methods=["GET"])
def home():
    return "Bot de WhatsApp y llamadas activado."

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get('Body', '').lower()
    sender_number = request.values.get('From', '')

    response = MessagingResponse()

    # Inicializar historial si no existe
    if sender_number not in session_history:
        session_history[sender_number] = []

    # Respuestas básicas
    if any(word in incoming_msg.lower() for word in ["hola", "buenas", "hello", "hey"]):
        msg = response.message("Hola, bienvenido a In Houston Texas. Soy Sara. ¿Con quién tengo el gusto?")
        return str(response)

    if "quién eres" in incoming_msg or "sara" in incoming_msg:
        msg = response.message("Soy Sara, la asistente del Sr. Sundin Galue, CEO de In Houston Texas. Estoy aquí para ayudarte.")
        return str(response)

    # Agregar mensaje del usuario al historial
    session_history[sender_number].append({"role": "user", "content": incoming_msg})

    # Llamar a GPT-4o con historial completo
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=session_history[sender_number]
        )
        respuesta = completion.choices[0].message.content.strip()
        session_history[sender_number].append({"role": "assistant", "content": respuesta})
        msg = response.message(respuesta)
    except Exception as e:
        print(f"❌ Error GPT: {e}")
        msg = response.message("Lo siento, hubo un error procesando tu mensaje. Intenta de nuevo.")

    return str(response)

@app.route("/voice", methods=["POST"])
def voice():
    """Responde a llamadas entrantes con un mensaje de voz"""
    response = VoiceResponse()
    response.say("Hola. Esta llamada está siendo utilizada para verificar este número. Por favor, escucha con atención el siguiente código.", voice='woman', language='es-MX')
    response.pause(length=1)
    response.say("Ahora repito: escucha con atención el código que se dictará en breve.", voice='woman', language='es-MX')
    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
