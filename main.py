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
    "autorregulación": "la capacidad de manejar emociones intensas de forma saludable",
    "autoconciencia": "la habilidad de entender lo que sentís y por qué",
    "toma de decisiones responsable": "la capacidad de elegir conductas seguras y éticas",
    "conciencia social": "la habilidad de entender a los demás y actuar con empatía",
    "confianza": "una valoración sólida de vos misma/o basada en tu valor, no en la aprobación externa"
}

planes_personalizados = {
    "autorregulación": "Vamos a trabajar con pequeños pasos para ayudarte a manejar mejor la ansiedad. El objetivo de estos retos será que logres responder con más calma y claridad en los momentos difíciles, bajando la intensidad emocional y fortaleciendo tu capacidad de recuperar el control. La constancia es clave, así que aunque no sean ejercicios largos, sí requieren práctica. ¿Te parece bien si empezamos con el primer paso?",
    "autoconciencia": "Vamos a desarrollar tu capacidad de entender lo que sentís, cuándo lo sentís y por qué. El objetivo es ayudarte a identificar patrones emocionales y pensamientos que puedan estar afectando tu bienestar. Esto va a ayudarte a tomar mejores decisiones desde un lugar más consciente. La clave: observar sin juzgar. ¿Empezamos con el primer reto?",
    "toma de decisiones responsable": "Vamos a construir una forma de decidir que no esté basada en impulsos, sino en reflexión. El objetivo será ayudarte a tomar decisiones más seguras, éticas y alineadas con lo que realmente querés. Te voy a proponer ejercicios que activen tu parte más analítica. ¿Te gustaría probar?",
    "conciencia social": "Trabajar la conciencia social implica ampliar tu perspectiva para entender mejor a quienes te rodean. El objetivo de estos retos será fortalecer tu empatía, mejorar la comunicación y cultivar relaciones más sanas. Vamos a hacerlo paso a paso, ¿te parece bien?",
    "confianza": "Vamos a fortalecer tu confianza desde un lugar interno y estable. No desde el elogio externo, sino desde el valor que sabés que tenés. Estos ejercicios van a ayudarte a reconocer tu capacidad y tu historia. La práctica sostenida hace toda la diferencia. ¿Vamos con el primero?"
}

retos_narrativos = {
    "autorregulación": [
        "Hoy vamos a enfocarnos en una técnica de respiración consciente. La respiración diafragmática es una herramienta poderosa para ayudar a tu cuerpo a salir del estado de alerta cuando sentís ansiedad. El reto es practicarla dos veces hoy, durante 3 a 5 minutos cada vez. Buscá un lugar tranquilo, sentate con la espalda recta y probá este ritmo: inhalá en 4 tiempos, sostené el aire 4 tiempos, y exhalá en 6 tiempos. Hacelo lentamente. Después, registrá cómo te sentís antes y después de la práctica."
    ],
    "autoconciencia": [
        "Vamos a trabajar en tu capacidad de identificar y comprender tus emociones. Hoy vas a escribir en un diario emocional sobre una situación reciente que te hizo sentir incómodo o confundido. Anotá qué pasó, cómo reaccionaste y qué emociones identificás en ese momento. Esta práctica de registro ayuda a mejorar la autoconciencia emocional y se basa en enfoques de diario reflexivo validados por la CASEL y la terapia cognitivo-conductual."
    ],
    "toma de decisiones responsable": [
        "El reto de hoy es una simulación de decisiones. Escribí una situación imaginaria donde tengas que decidir entre lo correcto y lo fácil. Describí tus opciones, pensá en las consecuencias de cada una y luego elegí conscientemente. Esto entrena tu capacidad de análisis y reflexión moral."
    ],
    "conciencia social": [
        "Hoy vas a fortalecer tu empatía. El reto consiste en observar una conversación o interacción (presencial o virtual) y tratar de ponerte en el lugar de la otra persona: ¿Qué pudo haber estado sintiendo? ¿Qué necesidad emocional podría haber detrás de su comportamiento? Anotá tu reflexión. Este ejercicio desarrolla la conciencia social, una de las competencias clave de CASEL."
    ],
    "confianza": [
        "Hoy vamos a reforzar la confianza trabajando sobre logros pasados. Hacelo así: anotá tres momentos de tu vida donde lograste algo importante, por pequeño que parezca. Luego escribí qué habilidades o fortalezas usaste para lograrlo. Esta técnica de autoafirmación está respaldada por investigaciones en psicología positiva y TCC."
    ]
}

usuarios_estado = {}
seguimiento_usuarios = {}

RESPUESTAS_SI = ["sí", "si", "sí.", "si.", "claro", "exacto", "eso"]
RESPUESTAS_NO = ["no", "no.", "nop", "negativo"]
SALUDOS_INICIALES = ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches"]

def procesar_mensaje(mensaje, user_id):
    texto = mensaje.strip().lower()
    estado = usuarios_estado.get(user_id, {})

    if user_id in seguimiento_usuarios:
        seguimiento = seguimiento_usuarios[user_id]
        fecha_guardada = datetime.strptime(seguimiento["fecha"], "%Y-%m-%d")
        if seguimiento["pendiente"] and datetime.now() - fecha_guardada >= timedelta(days=1):
            return f"¡Hola! Solo quería saber cómo te fue con el reto sobre *{seguimiento['habilidad']}*. ¿Querés contarme si lo pudiste hacer o si preferís cambiarlo?"

    if any(s in texto for s in SALUDOS_INICIALES) and "fase" not in estado:
        estado["fase"] = "introduccion"
        usuarios_estado[user_id] = estado
        return (
            "¡Hola! Gracias por estar acá. Me alegra que hayas llegado. Este es un espacio pensado para ayudarte a desarrollar habilidades sociales y emocionales que te permitan afrontar los desafíos de la vida con más claridad y bienestar.\n\n"
            "Antes de comenzar, quiero aclararte algo importante: esto no es terapia, ni busca reemplazarla. Lo que vas a encontrar acá son herramientas prácticas y basadas en evidencia científica — desde la psicología cognitivo-conductual y el enfoque de CASEL — para ayudarte a vivir mejor.\n\n"
            "1. Vamos a *identificar* lo que estás sintiendo\n"
            "2. Vamos a *nombrarlo* con claridad\n"
            "3. Vamos a *entender* de dónde viene\n"
            "4. Y después, te propongo un *plan práctico* para enfrentarlo\n\n"
            "¿Te gustaría comenzar contándome qué te está preocupando o afectando últimamente?"
        )

    if estado.get("fase") == "introduccion":
        estado["fase"] = "esperando_descripcion"
        usuarios_estado[user_id] = estado
        return "Perfecto, contame entonces qué situación o pensamiento te está afectando hoy."

    if estado.get("fase") == "esperando_descripcion":
        estado["mensaje_usuario"] = mensaje
        estado.setdefault("historial", []).append(mensaje)
        estado["fase"] = "indagacion_1"
        usuarios_estado[user_id] = estado
        return (
            "Gracias por compartirlo. Lo que estás viviendo suena realmente agotador y entiendo que puede hacerte sentir sobrepasada/o."
            " Vamos a seguir explorando juntas/os. ¿Qué es lo más difícil de esa situación para vos?"
        )

    if estado.get("fase") == "indagacion_1":
        estado["indagacion_1"] = mensaje
        estado.setdefault("historial", []).append(mensaje)
        estado["fase"] = "indagacion_2"
        usuarios_estado[user_id] = estado
        return (
            "Gracias por contarme eso. Me da la impresión de que estás enfrentando una presión constante y eso puede ser muy difícil de sostener."
            " ¿Y en esos momentos, notás alguna sensación física o pensamientos que se repitan?"
        )

    if estado.get("fase") == "indagacion_2":
        estado["indagacion_2"] = mensaje
        estado.setdefault("historial", []).append(mensaje)
        estado["fase"] = "emocion_confirmada"

        texto_total = " ".join(estado.get("historial", []))
        emocion_detectada = "ansiedad"
        for emocion in emociones_habilidades:
            if emocion in texto_total:
                emocion_detectada = emocion
                break

        habilidad = emociones_habilidades[emocion_detectada]
        estado["emocion"] = emocion_detectada
        estado["habilidad"] = habilidad
        usuarios_estado[user_id] = estado

        return (
            f"Gracias por compartir todo eso conmigo. Por lo que me contás, podría ser que estés sintiendo *{emocion_detectada}*.\n"
            f"¿Te hace sentido eso? Si querés, podemos trabajarla desarrollando tu habilidad de *{habilidad}*.\n"
            "¿Querés empezar por ahí? (sí/no)"
        )

    if estado.get("fase") == "emocion_confirmada":
        if texto in RESPUESTAS_SI:
            habilidad = estado["habilidad"]
            estado["fase"] = "plan_sugerido"
            usuarios_estado[user_id] = estado
            return planes_personalizados.get(habilidad, "Vamos a empezar con pequeños pasos para trabajar esa habilidad. ¿Vamos?")
        elif texto in RESPUESTAS_NO:
            estado["fase"] = "reinicio"
            usuarios_estado[user_id] = estado
            return "Está bien, contame un poco más para buscar otra forma de abordarlo."
        else:
            return "¿Querés que trabajemos esa habilidad? Respondé sí o no."

    if estado.get("fase") == "plan_sugerido":
        habilidad = estado["habilidad"]
        descripcion = descripcion_habilidades.get(habilidad, "una habilidad clave")
        herramienta = retos_narrativos.get(habilidad, ["Este es tu primer reto: observá tus reacciones con atención. Luego vamos a profundizar."])[0]
        estado["fase"] = "primer_reto"
        usuarios_estado[user_id] = estado
        seguimiento_usuarios[user_id] = {
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "reto": herramienta,
            "habilidad": habilidad,
            "pendiente": True
        }
        return (
            f"Entonces el primer objetivo será ayudarte a fortalecer tu *{habilidad}*, que es {descripcion}.\n\n"
            "Para lograrlo, vamos a armar un plan de pequeños retos diarios. Yo puedo enviarte recordatorios todos los días para ver cómo te fue y ayudarte a ajustar lo que sigue.\n\n"
            f"{herramienta}"
        )

    if estado.get("fase") == "primer_reto":
        return "Si querés avanzar o revisar algo más, contame una nueva situación."

    if estado.get("fase") == "reinicio":
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
