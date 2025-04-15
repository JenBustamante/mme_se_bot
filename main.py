import os
from flask import Flask, request
import telegram
from telegram.ext import Dispatcher, MessageHandler, Filters

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
BOT_USERNAME = "@MME_SE_bot"  # actualizado con tu nuevo bot

app = Flask(__name__)
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def procesar_mensaje(mensaje):
    return "Estoy procesando tu emoción. Gracias por compartirla. Pronto te devolveré una habilidad que te puede ayudar."


def handle_message(update, context):
    texto = update.message.text
    chat_id = update.message.chat_id
    respuesta = procesar_mensaje(texto)
    context.bot.send_message(chat_id=chat_id, text=respuesta)


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

    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, handle_message))

    PORT = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT)
