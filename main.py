import os
from flask import Flask, request
import telegram
from telegram.ext import Dispatcher, MessageHandler, Filters
import random
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
BOT_USERNAME = "@MME_SE_bot"

app = Flask(__name__)
bot = telegram.Bot(token=TELEGRAM_TOKEN)

emociones_habilidades = {
    "abandono": "confianza",
    "rechazo": "autoconciencia",
    "vergüenza": "confianza",
    "culpa": "toma de decisiones responsable",
    "impotencia": "autorregulación",
    "miedo": "autorregulación",
    "celos": "autoconciencia",
    "desesperanza": "confianza",
    "aburrimiento": "autoconciencia",
    "confusión": "toma de decisiones responsable",
    "preocupación": "autorregulación",
    "soledad": "conciencia social",
    "enojo": "toma de decisiones responsable",
    "frustración": "autorregulación",
    "ansiedad": "autorregulación",
    "tristeza": "autoconciencia",
    "inseguridad": "confianza"
}

descripcion_habilidades = {
    "autorregulación": "la capacidad de manejar emociones intensas como el enojo, la frustración o el miedo, sin dejar que tomen el control",
    "autoconciencia": "la habilidad de identificar lo que sentís, ponerle nombre y entender de dónde viene",
    "toma de decisiones responsable": "la capacidad de evaluar opciones y actuar de forma ética, segura y coherente con tus valores",
    "conciencia social": "la habilidad de comprender y respetar las emociones y necesidades de los demás",
    "confianza": "la seguridad interna de que tenés valor, incluso cuando las cosas no salen como esperabas"
}

usuarios_estado = {}

RESPUESTAS_SI = ["sí", "si", "sí.", "si.", "claro", "exacto", "eso"]
RESPUESTAS_NO = ["no", "no.", "nop", "negativo"]
SALUDOS_INICIALES = ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches"]

def procesar_mensaje(mensaje, user_id):
    texto = mensaje.strip().lower()
    estado = usuarios_estado.get(user_id, {})

    if any(s in texto for s in SALUDOS_INICIALES):
        estado = {}
        estado["fase"] = "introduccion"
        usuarios_estado[user_id] = estado
        return (
            """¡Hola! Gracias por estar acá. Me alegra que hayas llegado. Este es un espacio pensado para ayudarte a desarrollar habilidades sociales y emocionales que te permitan afrontar los desafíos de la vida con más claridad y bienestar.

Antes de comenzar, quiero aclararte algo importante: esto no es terapia, ni busca reemplazarla. Lo que vas a encontrar acá son herramientas prácticas y basadas en evidencia científica — desde la psicología cognitivo-conductual y el enfoque de CASEL — para ayudarte a vivir mejor.

1. Vamos a *identificar* lo que estás sintiendo
2. Vamos a *nombrarlo* con claridad
3. Vamos a *entender* de dónde viene
4. Y después, te propongo un *plan práctico* para enfrentarlo

¿Te gustaría comenzar contándome qué te está preocupando o afectando últimamente?"""
        )

    return "Estoy procesando lo que me compartiste. Gracias por tu paciencia."

def handle_message(update, context):
    texto = update.message.text
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    respuesta = procesar_mensaje(texto, user_id)
    context.bot.send_message(chat_id=chat_id, text=respuesta, parse_mode=telegram.ParseMode.MARKDOWN)

@app.route(f"/{TELEGRAM_TOKEN}", methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

@app.route('/')
def index():
    return 'MME está corriendo. 🎉'

if __name__ == '__main__':
    from telegram.ext import Updater
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT)
