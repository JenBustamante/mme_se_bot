import os
from flask import Flask, request
import telegram
from telegram.ext import Dispatcher, MessageHandler, Filters
import random

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
BOT_USERNAME = "@MME_SE_bot"

app = Flask(__name__)
bot = telegram.Bot(token=TELEGRAM_TOKEN)

emociones_habilidades = {
    "ansiedad": "autorregulación",
    "tristeza": "autoconciencia",
    "enojo": "toma de decisiones responsable",
    "soledad": "conciencia social",
    "inseguridad": "confianza",
    "culpa": "toma de decisiones responsable"
}

descripcion_habilidades = {
    "autorregulación": "la capacidad de manejar emociones intensas de forma saludable",
    "autoconciencia": "la habilidad de entender lo que sentís y por qué",
    "toma de decisiones responsable": "la capacidad de elegir conductas seguras y éticas",
    "conciencia social": "la habilidad de entender a los demás y actuar con empatía",
    "confianza": "una valoración sólida de vos misma/o basada en tu valor, no en la aprobación externa"
}

herramientas = {
    "autorregulación": [
        "Practicá la respiración diafragmática: inhalá 4 segundos, sostené 4, exhalá 6.",
        "Antes de una situación difícil, hacé una pausa de 1 minuto en silencio.",
        "Usá la técnica del semáforo: Parar, Pensar, Actuar."
    ],
    "autoconciencia": [
        "Anotá qué sentiste hoy y qué lo disparó.",
        "Hacé una lluvia de pensamientos que te repetís cuando te sentís mal.",
        "Dibujá o describí en qué parte del cuerpo sentís tu emoción."
    ],
    "toma de decisiones responsable": [
        "Antes de actuar, escribí dos consecuencias posibles de cada decisión.",
        "Hacé una lista de decisiones pasadas: ¿fueron impulsivas o reflexivas?",
        "Pensá qué consejo le darías a un amigo en tu misma situación."
    ],
    "conciencia social": [
        "Observá cómo reaccionan los demás y qué podrían estar sintiendo.",
        "Hacé una acción amable sin que te la pidan.",
        "Preguntale a alguien cómo está y escuchá con atención."
    ],
    "confianza": [
        "Listá 3 logros tuyos que no dependen de la aprobación de otros.",
        "Recordá una situación difícil que superaste. ¿Qué recursos usaste?",
        "Escribí una crítica que recibiste y refutala con hechos."
    ]
}

usuarios_estado = {}

RESPUESTAS_SI = ["sí", "si", "sí.", "si.", "claro", "exacto", "eso"]
RESPUESTAS_NO = ["no", "no.", "nop", "negativo"]
SALUDOS_INICIALES = ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches"]


def procesar_mensaje(mensaje, user_id):
    texto = mensaje.strip().lower()
    estado = usuarios_estado.get(user_id, {})

    if any(s in texto for s in SALUDOS_INICIALES) and "fase" not in estado:
        estado["fase"] = "esperando_descripcion"
        usuarios_estado[user_id] = estado
        return "¡Hola! Estoy aquí para ayudarte a desarrollar habilidades que te ayuden a afrontar lo que estás viviendo. Contame, ¿qué te está preocupando en este momento?"

    if "fase" not in estado:
        estado["fase"] = "esperando_descripcion"
        usuarios_estado[user_id] = estado

    if estado["fase"] == "esperando_descripcion":
        estado["mensaje_usuario"] = mensaje
        estado["fase"] = "indagacion_1"
        usuarios_estado[user_id] = estado
        return "Gracias por compartirlo. ¿Qué es lo más difícil de esa situación para vos?"

    if estado["fase"] == "indagacion_1":
        estado["indagacion_1"] = mensaje
        estado["fase"] = "indagacion_2"
        usuarios_estado[user_id] = estado
        return "¿Y en esos momentos, notás alguna sensación física o pensamientos que se repitan?"

    if estado["fase"] == "indagacion_2":
        estado["indagacion_2"] = mensaje
        estado["fase"] = "emocion_confirmada"
        emocion_detectada = "ansiedad" if "trabajo" in estado["mensaje_usuario"] else "tristeza"
        habilidad = emociones_habilidades[emocion_detectada]
        estado["emocion"] = emocion_detectada
        estado["habilidad"] = habilidad
        usuarios_estado[user_id] = estado
        return f"Parece que lo que estás sintiendo se relaciona con *{emocion_detectada}*. Para trabajar en eso, podríamos enfocarnos en fortalecer tu *{habilidad}*. ¿Te gustaría comenzar por ahí? (sí/no)"

    if estado["fase"] == "emocion_confirmada":
        if texto in RESPUESTAS_SI:
            habilidad = estado["habilidad"]
            descripcion = descripcion_habilidades.get(habilidad, "una habilidad clave")
            herramienta = random.choice(herramientas[habilidad])
            estado["fase"] = "plan_sugerido"
            usuarios_estado[user_id] = estado
            return f"Perfecto. Vamos a trabajar en *{habilidad}*, que es {descripcion}.\n\nTu primer reto práctico es: {herramienta}"
        elif texto in RESPUESTAS_NO:
            estado["fase"] = "reinicio"
            usuarios_estado[user_id] = estado
            return "Ok, podemos replantearlo. Contame un poco más sobre lo que estás sintiendo."
        else:
            return "¿Querés que trabajemos esa habilidad? Respondé sí o no."

    if estado["fase"] == "plan_sugerido":
        return "Ya comenzamos tu plan. Si querés trabajar otra situación, contame qué te está pasando."

    if estado["fase"] == "reinicio":
        estado["fase"] = "esperando_descripcion"
        usuarios_estado[user_id] = estado
        return "Volvamos al inicio. Contame qué te está preocupando."

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
