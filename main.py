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

# Nueva lista de emociones para mejorar la detección
lista_emociones = list(emociones_habilidades.keys())

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
        "Hoy vamos a enfocarnos en una técnica de respiración consciente..."
    ],
    "autoconciencia": [
        "Hoy vas a escribir en un diario emocional..."
    ],
    "toma de decisiones responsable": [
        "El reto de hoy es una simulación de decisiones..."
    ],
    "conciencia social": [
        "Observá una conversación o interacción..."
    ],
    "confianza": [
        "Anotá tres momentos de tu vida donde lograste algo importante..."
    ]
}

def detectar_emocion(texto):
    conteo = {emocion: texto.count(emocion) for emocion in lista_emociones}
    emociones_probables = sorted(conteo.items(), key=lambda x: x[1], reverse=True)
    top_emociones = [emocion for emocion, count in emociones_probables if count > 0][:3]
    return top_emociones if top_emociones else ["tristeza"]

def procesar_mensaje(mensaje, user_id):
    texto = mensaje.strip().lower()
    estado = usuarios_estado.get(user_id, {})

    if any(s in texto for s in SALUDOS_INICIALES):
        estado = {}
        estado["fase"] = "esperando_descripcion"
        usuarios_estado[user_id] = estado
        return (
          "¡Hola! Gracias por estar acá. Me alegra que hayas llegado. Este es un espacio pensado para ayudarte a desarrollar habilidades sociales y emocionales que te permitan afrontar los desafíos de la vida con más claridad y bienestar.\n\n"
            "Quiero aclararte que esto no es ni pretende ser terapia.\n\n"
            "Lo que vas a encontrar acá es ciencia: herramientas prácticas basadas en teoría cognitivo-conductual, el enfoque CASEL y buenas prácticas de enseñanza socioemocional. Todas ellas están basadas en evidencia y que han demostrado ser efectivas para ayudar a las personas a sentirse mejor y superar retos.\n\n"
            "¿Te gustaría comenzar contándome qué te está preocupando o afectando últimamente?"
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
        emociones_detectadas = detectar_emocion(texto_total)
        opciones = "\n".join([f"- {e}" for e in emociones_detectadas])
        estado["fase"] = "emocion_confirmada"
        estado["emociones_opciones"] = emociones_detectadas
        usuarios_estado[user_id] = estado
        return (
            f"Gracias por contarme más. Por lo que me compartiste, parece que hay varias emociones en juego.\n\n"
            f"Estas podrían ser algunas de ellas:\n{opciones}\n\n"
            "¿Te sentís identificado con alguna de estas? Si es así, escribila tal como aparece en la lista."
        )

    if estado.get("fase") == "emocion_confirmada":
        if texto in estado.get("emociones_opciones", []):
            emocion_detectada = texto
            habilidad = emociones_habilidades[emocion_detectada]
            descripcion = descripcion_habilidades.get(habilidad, "una habilidad clave para tu bienestar emocional")
            estado["habilidad"] = habilidad
            estado["fase"] = "aceptar_trabajo"
            usuarios_estado[user_id] = estado
            return (
                f"Gracias por compartir eso. Entonces podría ser que estés sintiendo *{emocion_detectada}*.\n"
                f"Para trabajar esa emoción, podemos enfocarnos en desarrollar tu habilidad de *{habilidad}*, que significa {descripcion}.\n\n"
                "¿Te gustaría que exploremos esa habilidad juntos? (sí/no)"
            )
        else:
            return "No encontré esa emoción en la lista anterior. ¿Podrías escribirla exactamente como aparecía?"

    if estado.get("fase") == "aceptar_trabajo":
        if texto in RESPUESTAS_SI:
            habilidad = estado["habilidad"]
            reto = retos_narrativos.get(habilidad, ["Vamos a empezar con pequeños pasos."])[0]
            estado["fase"] = "reto_entregado"
            usuarios_estado[user_id] = estado
            return (
                f"Perfecto. Vamos a comenzar a trabajar en *{habilidad}*.\n\n"
                f"Tu primer reto es el siguiente:\n\n"
                f"{reto}\n\n"
                "¿Querés que mañana te recuerde cómo te fue con este reto?"
            )
        elif texto in RESPUESTAS_NO:
            estado["fase"] = "esperando_descripcion"
            usuarios_estado[user_id] = estado
            return "Entiendo. Si querés contarme más sobre lo que te pasa, acá estoy."
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
