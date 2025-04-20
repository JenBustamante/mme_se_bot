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
        if "2" in texto:
            estado["fase"] = "modulo_autorregulacion_intro"
            usuarios_estado[user_id] = estado
            return (
                "Ahora vamos a trabajar en tu *autorregulación emocional*, que es la capacidad de manejar lo que sentís sin que eso te desborde.\n"
                "No se trata de evitar las emociones, sino de reconocerlas y elegir cómo responder en lugar de reaccionar automáticamente.\n\n"
                "¿Te ha pasado últimamente que una emoción te hizo decir o hacer algo de lo que después te arrepentiste?\n\n"
                "1. Sí\n2. No\n3. No estoy seguro/a"
            )

    if estado.get("fase") == "modulo_autorregulacion_intro":
        if texto in ["1", "3"]:
            estado["fase"] = "autorregulacion_exp"
            usuarios_estado[user_id] = estado
            return (
                "Gracias por compartirlo. Eso nos pasa a todos, y lo importante es que se puede trabajar. Vamos a ver cómo.\n\n"
                "Las emociones fuertes como la ira, la ansiedad o la tristeza nos quieren decir algo, pero si no las regulamos, pueden tomar el control.\n"
                "La autorregulación es como un *semáforo interno*: nos permite poner una pausa entre lo que sentimos y lo que hacemos.\n\n"
                "Te presento una herramienta sencilla y poderosa: el *Semáforo emocional*.\n\n"
                "🔴 Rojo: Alto. Pausá. ¿Qué estás sintiendo?\n"
                "🟡 Amarillo: Pensá. ¿Qué pasó? ¿Qué opciones tenés?\n"
                "🟢 Verde: Actuá. Elegí cómo responder de forma más saludable.\n\n"
                "¿Querés probar esta herramienta con algo que te haya pasado recientemente?\n1. Sí\n2. No por ahora"
            )
        elif texto == "2":
            estado["fase"] = "autorregulacion_exp"
            usuarios_estado[user_id] = estado
            return (
                "Gracias. Vamos a explorar juntos cómo manejar emociones intensas.\n\n"
                "Las emociones fuertes como la ira, la ansiedad o la tristeza nos quieren decir algo, pero si no las regulamos, pueden tomar el control.\n"
                "La autorregulación es como un *semáforo interno*: nos permite poner una pausa entre lo que sentimos y lo que hacemos.\n\n"
                "Te presento una herramienta sencilla y poderosa: el *Semáforo emocional*.\n\n"
                "🔴 Rojo: Alto. Pausá. ¿Qué estás sintiendo?\n"
                "🟡 Amarillo: Pensá. ¿Qué pasó? ¿Qué opciones tenés?\n"
                "🟢 Verde: Actuá. Elegí cómo responder de forma más saludable.\n\n"
                "¿Querés probar esta herramienta con algo que te haya pasado recientemente?\n1. Sí\n2. No por ahora"
            )

    if estado.get("fase") == "autorregulacion_exp":
        if "1" in texto:
            estado["fase"] = "autorregulacion_ejercicio"
            usuarios_estado[user_id] = estado
            return "Contame una situación reciente donde sentiste una emoción intensa."
        else:
            estado["fase"] = "autorregulacion_tecnica"
            usuarios_estado[user_id] = estado
            return (
                "Durante el día de hoy, te invito a que observes si podés identificar alguna emoción fuerte justo cuando aparece.\n"
                "Intentá ponerle un nombre y elegir una forma diferente de responder. Aunque no lo logres, el solo intento ya es parte del aprendizaje.\n\n"
                "¿Querés aprender una técnica rápida para calmarte cuando estés muy activado emocionalmente?\n1. Respiración 4-7-8\n2. Aterrizaje con 5 sentidos\n3. No por ahora"
            )

    if estado.get("fase") == "autorregulacion_ejercicio":
        estado["evento"] = texto
        estado["fase"] = "autorregulacion_abc"
        usuarios_estado[user_id] = estado
        return (
            "Rojo 🔴: ¿Qué emoción sentiste? ¿Dónde la sentiste en el cuerpo?"
        )

    if estado.get("fase") == "autorregulacion_abc":
        estado["fase"] = "autorregulacion_amarillo"
        usuarios_estado[user_id] = estado
        return (
            "Amarillo 🟡: ¿Qué pasó? ¿Qué pensaste? ¿Qué opciones tenías?"
        )

    if estado.get("fase") == "autorregulacion_amarillo":
        estado["fase"] = "autorregulacion_verde"
        usuarios_estado[user_id] = estado
        return (
            "Verde 🟢: ¿Qué hiciste finalmente? ¿Te sirvió esa reacción?\n\nMuy bien. Solo el hecho de detenerte a pensar ya es un gran paso para regular lo que sentís.\n\n"
            "¿Querés aprender una técnica rápida para calmarte cuando estés muy activado emocionalmente?\n1. Respiración 4-7-8\n2. Aterrizaje con 5 sentidos\n3. No por ahora"
        )

    if estado.get("fase") == "autorregulacion_tecnica" or estado.get("fase") == "autorregulacion_verde":
        if "1" in texto:
            estado["fase"] = "autorregulacion_cierre"
            usuarios_estado[user_id] = estado
            return (
                "Inhalá por 4 segundos... Mantené por 7... Exhalá por 8... Repetí 3 veces. Esta técnica ayuda a calmar el sistema nervioso rápidamente."
            )
        elif "2" in texto:
            estado["fase"] = "autorregulacion_cierre"
            usuarios_estado[user_id] = estado
            return (
                "Decí en voz alta o pensá:\n5 cosas que ves,\n4 que podés tocar,\n3 que podés oír,\n2 que podés oler,\n1 que podés saborear.\nEs un ejercicio de conexión con el presente."
            )
        else:
            estado["fase"] = "autorregulacion_cierre"
            usuarios_estado[user_id] = estado
            return "Perfecto, seguimos."

    if estado.get("fase") == "autorregulacion_cierre":
        estado["fase"] = "fin_modulo"
        usuarios_estado[user_id] = estado
        return (
            "¡Bien hecho! Regular tus emociones no significa controlarlas al 100%, sino aprender a navegar por ellas sin que te arrastren.\n"
            "Podés practicar esto cada día, y vas a ver cómo mejora tu bienestar y tus relaciones.\n\n"
            "¿Qué te gustaría hacer ahora?\n1. Volver al inicio\n2. Ir al módulo de conciencia social\n3. Compartir cómo me sentí hoy"
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
