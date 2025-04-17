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
    "autorregulación": ["Hoy vamos a enfocarnos en una técnica de respiración consciente..."],
    "autoconciencia": ["Hoy vas a escribir en un diario emocional..."],
    "toma de decisiones responsable": ["El reto de hoy es una simulación de decisiones..."],
    "conciencia social": ["Observá una conversación o interacción..."],
    "confianza": ["Anotá tres momentos de tu vida donde lograste algo importante..."]
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
        estado = {"fase": "menu_inicio"}
        usuarios_estado[user_id] = estado
        return (
            "¡Hola! Qué alegría que estés aquí.\n\n"
            "Este espacio fue creado especialmente para acompañarte a afrontar los desafíos de la vida y ayudarte a desarrollar habilidades sociales y emocionales que te permitan sentirte mejor, tomar decisiones con más claridad y construir relaciones más sanas.\n\n"
            "Quiero contarte algo importante: esto NO es terapia, ni pretende serlo, pero sí vas a encontrar herramientas prácticas y confiables, basadas en:\n\n"
            "• *Teoría Cognitivo-Conductual (TCC)*: una metodología respaldada por la ciencia que conecta tus pensamientos, emociones y acciones.\n"
            "• *Aprendizaje Social y Emocional (SEL)*: un enfoque educativo desarrollado por CASEL que fortalece tu bienestar emocional.\n"
            "• *Buenas prácticas y evidencia científica*: nada de frases vacías ni promesas mágicas; solo ejercicios y reflexiones que funcionan de verdad.\n\n"
            "¿Cómo funciona MME?\n\n"
            "Puedes contarme qué estás sintiendo o qué te preocupa, y te devolveré ejercicios prácticos, y con posibilidad de seguimiento diario, para ayudarte a desarrollar la habilidad socioemocional que necesitas para afrontar esa situación.\n\n"
            "También puedes explorar habilidades clave como autoconciencia, regulación emocional, empatía, relaciones y toma de decisiones.\n\n"
            "Si no sabes por dónde empezar, solo escribí *ayuda* o *no sé*, y te guiaré paso a paso.\n\n"
            "¿Cómo querés comenzar?\n1. Escribir una situación que estás viviendo\n2. Acceder a un módulo de aprendizaje sobre habilidades socioemocionales"
        )

    if estado.get("fase") == "menu_inicio":
        if "1" in texto:
            estado["fase"] = "esperando_descripcion"
            usuarios_estado[user_id] = estado
            return "Perfecto, contame qué te está preocupando o afectando últimamente."
        elif "2" in texto:
            estado["fase"] = "menu_modulos"
            usuarios_estado[user_id] = estado
            return (
                "¡Genial! Estas son algunas de las habilidades que podés explorar:

1. Autoconciencia
2. Autorregulación
3. Conciencia social
4. Confianza
5. Toma de decisiones responsable
6. Habilidades de relacionamiento

Escribí el número o el nombre de la habilidad que te interesa."
            )
        elif texto in ["ayuda", "no sé", "nose"]:
            return "Podés comenzar contándome qué estás sintiendo o elegir una habilidad sobre la que quieras aprender. Decime lo que quieras y yo te guío."
        else:
            return "¿Querés empezar por una situación personal (1) o por un módulo de aprendizaje (2)? Escribí 1 o 2."
        elif "2" in texto:
            estado["fase"] = "menu_modulos"
            usuarios_estado[user_id] = estado
            return "¡Genial! ¿Sobre qué habilidad te gustaría aprender más? (Por ejemplo: autorregulación, empatía, confianza, etc.)"
        elif texto in ["ayuda", "no sé", "nose"]:
            return "Podés comenzar contándome qué estás sintiendo o elegir una habilidad sobre la que quieras aprender. Decime lo que quieras y yo te guío."
        else:
            return "¿Querés empezar por una situación personal (1) o por un módulo de aprendizaje (2)? Escribí 1 o 2."

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
