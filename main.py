# -*- coding: utf-8 -*-
import os
from flask import Flask, request
import telegram
from telegram.ext import Dispatcher, MessageHandler, Filters
from datetime import datetime

# Configuración del bot
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
BOT_USERNAME = "@MME_SE_bot"

# Inicialización de la app Flask y del bot de Telegram
app = Flask(__name__)
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Almacenamiento temporal del estado de cada usuario
usuarios_estado = {}

# Frases que identifican saludos y respuestas comunes
SALUDOS_INICIALES = ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches"]
RESPUESTAS_SI = ["sí", "si", "sí.", "si.", "claro", "dale", "quiero", "sí, dale"]
RESPUESTAS_NO = ["no", "no.", "nop", "prefiero seguir sin test"]

import re
import random

def procesar_mensaje(mensaje, user_id):
    texto = mensaje.strip().lower()
    estado = usuarios_estado.get(user_id, {})

    # Inicio del flujo si detecta un saludo
    if any(s in texto for s in SALUDOS_INICIALES):
        estado = {"fase": "menu_inicio"}
        usuarios_estado[user_id] = estado
        return (
            "¡Hola! Qué alegría que estés aquí.\n\n"
            "Este espacio fue creado especialmente para acompañarte a afrontar situaciones difíciles de la vida y ayudarte a desarrollar habilidades sociales y emocionales que te permitan sentirte mejor, tomar decisiones con más claridad y construir relaciones más sanas.\n\n"
            "Quiero contarte algo importante: esto NO es terapia, ni pretende serlo, pero sí vas a encontrar herramientas prácticas y confiables, basadas en:\n\n"
            "• *Teoría Cognitivo-Conductual (TCC)*\n"
            "• *Aprendizaje Social y Emocional (SEL)*\n"
            "• *Buenas prácticas y evidencia científica*\n\n"
            "¿Cómo querés comenzar?\n1. Escribir una situación que estás viviendo\n2. Quiero aprender una habilidad"
        )

    # Menú principal
    if estado.get("fase") == "menu_inicio":
        if "2" in texto:
            estado["fase"] = "habilidades_guardado_para_despues"
            usuarios_estado[user_id] = estado
            return "Perfecto, esa opción está disponible pero la vamos a retomar más adelante. Por ahora, concentrémonos en otra parte."
        elif "1" in texto:
            estado["fase"] = "situacion_usuario"
            usuarios_estado[user_id] = estado
            return "Gracias por confiar en este espacio. Podés contarme qué situación estás viviendo o qué te preocupa últimamente, y vamos a ir entendiéndolo paso a paso."

    # Usuario cuenta una situación personal
    if estado.get("fase") == "situacion_usuario":
        estado["situacion"] = texto
        estado["fase"] = "preguntas_emocion_1"
        usuarios_estado[user_id] = estado

        # Detección básica de emociones
        if re.search(r"ansioso|ansiedad|nervioso", texto):
            estado["emocion_detectada"] = "ansiedad"
        elif re.search(r"triste|deprimido|vacío", texto):
            estado["emocion_detectada"] = "tristeza"
        elif re.search(r"frustrado|impotente|bloqueado", texto):
            estado["emocion_detectada"] = "frustración"
        elif re.search(r"enojo|molesto|rabia|impotencia", texto):
            estado["emocion_detectada"] = "enojo"
        elif re.search(r"solo|aislado|invisible", texto):
            estado["emocion_detectada"] = "soledad"
        elif re.search(r"inseguro|no soy capaz|valgo poco", texto):
            estado["emocion_detectada"] = "inseguridad"
        elif re.search(r"estresado|sobrecargado", texto):
            estado["emocion_detectada"] = "estrés"
        else:
            estado["emocion_detectada"] = "indefinida"
            return "Gracias por compartir eso. Me gustaría entender un poco más lo que estás sintiendo. ¿Podés contarme con más detalle qué fue lo que te hizo sentir así?"

        # Si se detectó alguna emoción, pasa a la siguiente fase
        return "Gracias por compartirlo. Me gustaría entender un poco mejor lo que sentís. ¿Qué situaciones suelen disparar esa emoción en vos?"

    # Primera pregunta de profundización emocional
    if estado.get("fase") == "preguntas_emocion_1":
        estado["respuesta1"] = texto
        emocion = estado.get("emocion_detectada")
        estado["fase"] = "preguntas_emocion_2"
        usuarios_estado[user_id] = estado

        respuestas = {
            "ansiedad": "La ansiedad puede sentirse como un nudo en el pecho que aparece justo cuando más necesitamos claridad. ¿Has intentado alguna estrategia para calmarte en esos momentos?",
            "tristeza": "A veces, cuando estamos tristes, cuesta encontrar algo que nos alivie. ¿Qué hacés normalmente cuando te sentís así?",
            "frustración": "La frustración puede agotar nuestra energía emocional. ¿Qué hacés cuando sentís que nada sale como querés?",
            "enojo": "Después de una explosión de enojo, muchas veces nos queda culpa o duda. ¿Cómo reaccionás normalmente cuando te sentís así?",
            "soledad": "La soledad prolongada puede hacer que incluso nuestras relaciones más cercanas se sientan lejanas. ¿Hay personas con las que te gustaría conectar más pero no sabés cómo?",
            "inseguridad": "La inseguridad a veces se mete silenciosamente. ¿Qué pensamientos aparecen cuando te sentís inseguro o insegura?",
            "estrés": "El estrés nos empuja a seguir incluso cuando nuestro cuerpo nos pide una pausa. ¿Qué haces para aliviarlo últimamente?"
        }

        return respuestas.get(emocion, "¿Podés contarme un poco más sobre eso?")

    # Segunda pregunta de profundización emocional
    if estado.get("fase") == "preguntas_emocion_2":
        estado["respuesta2"] = texto
        emocion = estado.get("emocion_detectada")
        estado["fase"] = "emocion_confirmada"
        usuarios_estado[user_id] = estado

        return f"Por lo que me contás, puede que estés sintiendo *{emocion}*. ¿Te hace sentido eso? Si querés, podemos trabajarla desarrollando una habilidad que te ayude. ¿Querés empezar por ahí? (sí/no)"

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
