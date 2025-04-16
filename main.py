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

retos_narrativos = {
    "autorregulación": [
        "Hoy vamos a enfocarnos en una técnica de respiración consciente. La respiración diafragmática es una herramienta poderosa para ayudar a tu cuerpo a salir del estado de alerta cuando sentís ansiedad. El reto es practicarla dos veces hoy, durante 3 a 5 minutos cada vez. Buscá un lugar tranquilo, sentate con la espalda recta y probá este ritmo: inhalá en 4 tiempos, sostené el aire 4 tiempos, y exhalá en 6 tiempos. Después, registrá cómo te sentís antes y después de la práctica."
    ],
    "autoconciencia": [
        "Hoy vas a escribir en un diario emocional sobre una situación reciente que te hizo sentir incómodo o confundido. Anotá qué pasó, cómo reaccionaste y qué emociones identificás en ese momento. Esta práctica de registro ayuda a mejorar la autoconciencia emocional."
    ],
    "toma de decisiones responsable": [
        "El reto de hoy es una simulación de decisiones. Escribí una situación imaginaria donde tengas que decidir entre lo correcto y lo fácil. Describí tus opciones, pensá en las consecuencias de cada una y luego elegí conscientemente."
    ],
    "conciencia social": [
        "Observá una conversación o interacción (presencial o virtual) y tratá de ponerte en el lugar de la otra persona: ¿Qué pudo haber estado sintiendo? ¿Qué necesidad emocional podría haber detrás de su comportamiento? Anotá tu reflexión."
    ],
    "confianza": [
        "Anotá tres momentos de tu vida donde lograste algo importante. Luego escribí qué habilidades o fortalezas usaste para lograrlo."
    ]
}

def procesar_mensaje(mensaje, user_id):
    texto = mensaje.strip().lower()
    estado = usuarios_estado.get(user_id, {})

    if any(s in texto for s in SALUDOS_INICIALES):
        estado = {}
        estado["fase"] = "esperando_descripcion"
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

    if estado.get("fase") == "esperando_descripcion":
        estado["mensaje_usuario"] = mensaje
        estado.setdefault("historial", []).append(mensaje)
        estado["fase"] = "indagacion_1"
        usuarios_estado[user_id] = estado
        return "Gracias por compartirlo. ¿Qué es lo más difícil de esta situación para vos?"

    if estado.get("fase") == "indagacion_1":
        estado["indagacion_1"] = mensaje
        estado.setdefault("historial", []).append(mensaje)
        estado["fase"] = "indagacion_2"
        usuarios_estado[user_id] = estado
        return "¿Y cómo reacciona tu cuerpo o tu mente cuando estás en esa situación?"

    if estado.get("fase") == "indagacion_2":
        estado["indagacion_2"] = mensaje
        estado.setdefault("historial", []).append(mensaje)
        texto_total = " ".join(estado.get("historial", []))
        emocion_detectada = "tristeza"
        for emocion in emociones_habilidades:
            if emocion in texto_total:
                emocion_detectada = emocion
                break
        habilidad = emociones_habilidades[emocion_detectada]
        descripcion = descripcion_habilidades.get(habilidad, "una habilidad clave para tu bienestar emocional")
        estado["fase"] = "emocion_confirmada"
        estado["emocion"] = emocion_detectada
        estado["habilidad"] = habilidad
        usuarios_estado[user_id] = estado
        return (
            f"Por lo que me contás, podrías estar sintiendo *{emocion_detectada}*. Esta emoción suele aparecer en momentos de desafío o cambio.\n"
            f"Podemos trabajarla desarrollando tu habilidad de *{habilidad}*, que es {descripcion}.\n"
            "¿Te hace sentido esto? ¿Querés trabajar en esa habilidad? (sí/no)"
        )

    if estado.get("fase") == "emocion_confirmada":
        if texto in RESPUESTAS_SI:
            habilidad = estado["habilidad"]
            reto = retos_narrativos.get(habilidad, ["Vamos a empezar con pequeños pasos."])[0]
            estado["fase"] = "reto_entregado"
            usuarios_estado[user_id] = estado
            return (
                f"Perfecto. Vamos a comenzar a trabajar en *{habilidad}*.\n\n"
                f"Tu primer reto es el siguiente:\n\n{reto}\n\n¿Querés que mañana te recuerde cómo te fue con este reto?"
            )
        elif texto in RESPUESTAS_NO:
            estado["fase"] = "esperando_descripcion"
            usuarios_estado[user_id] = estado
            return "Está bien. Podemos explorar otra emoción o situación si querés. Contame más."
        else:
            return "¿Querés que trabajemos esa habilidad? Respondé sí o no."

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
