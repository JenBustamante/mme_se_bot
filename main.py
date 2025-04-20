import os
from flask import Flask, request
import telegram
from telegram.ext import Dispatcher, MessageHandler, Filters
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
BOT_USERNAME = "@MME_SE_bot"

app = Flask(__name__)
bot = telegram.Bot(token=TELEGRAM_TOKEN)

usuarios_estado = {}
SALUDOS_INICIALES = ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches"]

RESPUESTAS_SI = ["sí", "si", "sí.", "si.", "claro", "dale", "quiero", "sí, dale"]
RESPUESTAS_NO = ["no", "no.", "nop", "prefiero seguir sin test"]


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
            "• *Teoría Cognitivo-Conductual (TCC)*\n"
            "• *Aprendizaje Social y Emocional (SEL)*\n"
            "• *Buenas prácticas y evidencia científica*\n\n"
            "¿Cómo querés comenzar?\n1. Escribir una situación que estás viviendo\n2. Quiero aprender una habilidad"
        )

    if estado.get("fase") == "menu_inicio":
        if "2" in texto:
            estado["fase"] = "seleccion_habilidad"
            usuarios_estado[user_id] = estado
            return (
                "Genial. ¿Qué habilidad te gustaría desarrollar?\n\n"
                "1. Autoconciencia\n"
                "2. Autorregulación\n"
                "3. Empatía\n"
                "4. Habilidades de relación\n"
                "5. Toma de decisiones responsable"
            )

    if estado.get("fase") == "seleccion_habilidad":
        if "1" in texto:
            estado["fase"] = "modulo_autoconciencia_inicio"
            usuarios_estado[user_id] = estado
            return (
                "Vamos a trabajar juntos en desarrollar tu *autoconciencia*. Eso significa aprender a identificar lo que estás sintiendo, pensando y por qué.\n"
                "Esto te va a ayudar a tomar mejores decisiones, entenderte mejor y sentirte más en control de tu vida.\n\n"
                "¿Te gustaría comenzar con una pregunta para reflexionar?\n\n"
                "1. Sí, dale.\n2. Prefiero seguir sin test."
            )

    if estado.get("fase") == "modulo_autoconciencia_inicio":
        if "1" in texto:
            estado["fase"] = "microtest_emocional"
            usuarios_estado[user_id] = estado
            return (
                "En este momento, ¿podés identificar cómo te sentís?\n\n"
                "1. Triste\n2. Ansioso/a\n3. Cansado/a\n4. Enojado/a\n5. Bien\n6. No sé / No puedo ponerlo en palabras"
            )
        elif "2" in texto:
            estado["fase"] = "explicacion_autoconciencia"
            usuarios_estado[user_id] = estado
            return "Perfecto. Entonces vamos a seguir directo a conocer más sobre la habilidad."

    if estado.get("fase") == "microtest_emocional":
        estado["fase"] = "explicacion_autoconciencia"
        usuarios_estado[user_id] = estado
        if "6" in texto:
            return "No te preocupes, eso también es una forma válida de sentir. Vamos paso a paso."
        else:
            return "Gracias por compartir cómo te sentís. Sigamos."

    if estado.get("fase") == "explicacion_autoconciencia":
        estado["fase"] = "modelo_abc"
        usuarios_estado[user_id] = estado
        return (
            "La *autoconciencia* es como tener un espejo interior. Nos ayuda a observar nuestras emociones y pensamientos sin juzgarlos.\n"
            "Cuando no sabemos qué sentimos o por qué reaccionamos de cierta forma, nos cuesta cambiar. Pero si aprendemos a identificar eso, podemos actuar con más claridad y calma.\n\n"
            "Te voy a mostrar una herramienta que usan mucho los psicólogos: el *modelo ABC*. Sirve para entender qué pasó, qué pensaste y cómo eso te hizo sentir o actuar.\n\n"
            "A: Acontecimiento – ¿Qué pasó?\n"
            "B: Pensamiento o creencia – ¿Qué pensaste en ese momento?\n"
            "C: Consecuencia – ¿Cómo te sentiste o qué hiciste?\n\n"
            "¿Querés probarlo ahora con algo que te haya pasado?\n1. Sí, quiero probar\n2. No, prefiero seguir sin ejercicio"
        )

    if estado.get("fase") == "modelo_abc":
        if "1" in texto:
            estado["fase"] = "abc_evento"
            usuarios_estado[user_id] = estado
            return "Contame algo que te haya pasado hoy o esta semana que te haya hecho sentir algo intenso."
        else:
            estado["fase"] = "mision_diaria"
            usuarios_estado[user_id] = estado
            return "No hay problema. Podés pasar directo al desafío diario."

    if estado.get("fase") == "abc_evento":
        estado["evento"] = texto
        estado["fase"] = "abc_pensamiento"
        usuarios_estado[user_id] = estado
        return "¿Qué pensaste justo después de eso?"

    if estado.get("fase") == "abc_pensamiento":
        estado["pensamiento"] = texto
        estado["fase"] = "abc_consecuencia"
        usuarios_estado[user_id] = estado
        return "¿Y cómo te sentiste o qué hiciste después de ese pensamiento?"

    if estado.get("fase") == "abc_consecuencia":
        estado["fase"] = "reencuadre"
        usuarios_estado[user_id] = estado
        return (
            "Muchas veces lo que pensamos no es un hecho, sino una interpretación. Vamos a ver si podemos encontrar otra forma de mirar lo que pasó.\n\n"
            "¿Qué otra explicación podría haber?\n¿Hay algo que contradiga ese pensamiento?\n¿Qué le dirías a un amigo que pensara eso?"
        )

    if estado.get("fase") == "reencuadre":
        estado["fase"] = "mision_diaria"
        usuarios_estado[user_id] = estado
        return (
            "Gracias por compartir eso. Vamos con el desafío de hoy.\n\n"
            "Durante el día de hoy pensá en 2 momentos donde sentiste una emoción fuerte. Cuando eso pase, preguntate:\n"
            "¿Qué pensé justo antes de sentirme así?\n\n"
            "Esa práctica diaria es como un músculo que se entrena. ¡Funciona!"
        )

    if estado.get("fase") == "mision_diaria":
        estado["fase"] = "fin_modulo"
        usuarios_estado[user_id] = estado
        return (
            "¡Muy bien! Trabajar en tu autoconciencia es un paso enorme para conocerte y sentirte mejor.\n"
            "Podés volver a esta herramienta cuando lo necesites, o seguir con otro módulo. Estoy acá para acompañarte.\n\n"
            "¿Qué te gustaría hacer ahora?\n1. Volver al inicio\n2. Ir al módulo de autorregulación\n3. Escribir cómo me siento ahora"
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
