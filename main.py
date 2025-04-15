import os
from flask import Flask, request
import telegram
from telegram.ext import Dispatcher, MessageHandler, Filters
import random

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
BOT_USERNAME = "@MME_SE_bot"

app = Flask(__name__)
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Diccionario base de emociones y habilidades asociadas
emociones_habilidades = {
    "ansiedad": "autorregulación",
    "tristeza": "autoconciencia",
    "enojo": "toma de decisiones responsable",
    "soledad": "conciencia social",
    "inseguridad": "confianza",
    "culpa": "toma de decisiones responsable"
}

# Descripciones CASEL básicas
descripcion_habilidades = {
    "autorregulación": "la capacidad de manejar emociones intensas de forma saludable",
    "autoconciencia": "la habilidad de entender lo que sentís y por qué",
    "toma de decisiones responsable": "la capacidad de elegir conductas seguras y éticas",
    "conciencia social": "la habilidad de entender a los demás y actuar con empatía",
    "confianza": "una valoración sólida de vos misma/o basada en tu valor, no en la aprobación externa"
}

# Herramientas prácticas por habilidad (TCC + retos)
herramientas = {
    "autorregulación": [
        "Hacé una pausa de 5 minutos en silencio antes de responder a algo que te altere",
        "Probá la técnica del semáforo: Parar, Pensar, Actuar",
        "Escribí lo que te está irritando y tachá lo que no podés controlar"
    ],
    "autoconciencia": [
        "Anotá lo que sentiste hoy y qué situación lo disparó",
        "Identificá qué pensás de vos misma/o cuando te sentís mal",
        "Dibujá o escribí cómo se siente tu emoción en el cuerpo"
    ],
    "toma de decisiones responsable": [
        "Antes de decidir, escribí dos consecuencias posibles de cada opción",
        "Preguntate: ¿esto es impulsivo o reflexionado?",
        "Elegí una situación y buscá el consejo que le darías a otra persona en tu lugar"
    ],
    "conciencia social": [
        "Observá una conversación y anotá cómo se sintieron los otros",
        "Hacé una pequeña acción empática hoy (aunque no te la pidan)",
        "Preguntale a alguien cómo está... y escuchá de verdad"
    ],
    "confianza": [
        "Anotá 3 cosas que valorás de vos misma/o que no dependen de nadie más",
        "Pensá en una vez en la que superaste algo difícil. ¿Qué hiciste bien?",
        "Elegí una crítica que te hicieron y desmentila con evidencia real"
    ]
}

usuarios_estado = {}

RESPUESTAS_SI = ["sí", "si", "sí.", "si.", "claro", "exacto", "eso"]
RESPUESTAS_NO = ["no", "no.", "nop", "negativo"]

SALUDOS_INICIALES = ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches"]


def procesar_mensaje(mensaje, user_id):
    texto_normalizado = mensaje.strip().lower()
    estado = usuarios_estado.get(user_id, {})

    if any(saludo in texto_normalizado for saludo in SALUDOS_INICIALES) and "fase" not in estado:
        estado["fase"] = "esperando_descripcion"
        usuarios_estado[user_id] = estado
        return "Hola. Estoy aquí para ayudarte a desarrollar las habilidades que necesitás para afrontar los desafíos de la vida. Contame, ¿qué te está pasando?"

    if "fase" not in estado:
        estado["fase"] = "inicio"
        usuarios_estado[user_id] = estado

    if estado["fase"] == "inicio" or estado["fase"] == "esperando_descripcion":
        estado["fase"] = "emocion_detectada"
        estado["mensaje_usuario"] = mensaje
        emocion_detectada = random.choice(list(emociones_habilidades.keys()))
        estado["emocion"] = emocion_detectada
        habilidad = emociones_habilidades[emocion_detectada]
        estado["habilidad"] = habilidad
        usuarios_estado[user_id] = estado
        return f"Gracias por contarme eso. Por lo que decís, podría ser que estés sintiendo *{emocion_detectada}*. ¿Te suena eso? (Responé 'sí' o 'no')"

    if estado["fase"] == "emocion_detectada":
        if texto_normalizado in RESPUESTAS_SI:
            habilidad = estado["habilidad"]
            estado["fase"] = "plan_sugerido"
            descripcion = descripcion_habilidades.get(habilidad, "una habilidad clave")
            herramienta = random.choice(herramientas[habilidad])
            usuarios_estado[user_id] = estado
            return f"Genial. Entonces vamos a trabajar en *{habilidad}*, que es {descripcion}.

Tu primer reto es: {herramienta}"
        elif texto_normalizado in RESPUESTAS_NO:
            estado["fase"] = "reinicio"
            usuarios_estado[user_id] = estado
            return "Ok, vamos a intentar identificar otra emoción. Contame de nuevo qué está pasando."
        else:
            return "Perdón, necesito que me confirmes si la emoción que mencioné te suena o no. Escribí 'sí' o 'no'."

    if estado["fase"] == "plan_sugerido":
        return "Ya comenzamos tu plan. Si querés seguir con otro desafío, contame una nueva situación."

    if estado["fase"] == "reinicio":
        estado["fase"] = "inicio"
        usuarios_estado[user_id] = estado
        return procesar_mensaje(mensaje, user_id)

    return "Estoy procesando tu emoción. Gracias por compartirla."

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
