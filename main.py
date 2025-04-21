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
RESPUESTAS_SI = [
    "sí", "si", "sí.", "si.", "claro", "dale", "quiero", "sí, dale",
    "sí quiero", "me gustaría", "por supuesto", "de una", "sí quiero hacerlo",
    "sí quiero probar", "obvio", "vale", "está bien"
]
RESPUESTAS_NO = [
    "no", "no.", "nop", "prefiero seguir sin test",
    "no gracias", "mejor no", "no por ahora", "prefiero que no",
    "no quiero", "quizá después", "no estoy seguro", "no estoy segura"
]

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

        # Detección básica de emociones (ampliada con género, sinónimos y raíz de la palabra emoción)
        if re.search(r"ansios[oa]|ansiedad|nervios[oa]|preocupad[oa]|inquiet[oa]|ansiosidad", texto):
            estado["emocion_detectada"] = "ansiedad"
        elif re.search(r"trist[ea]|tristeza|deprimid[oa]|vac[ií]([o|a])|melanc[oó]lic[oa]|apagad[oa]", texto):
            estado["emocion_detectada"] = "tristeza"
        elif re.search(r"frustrad[oa]|frustración|impotente|bloquead[oa]|incapaz|rendid[oa]", texto):
            estado["emocion_detectada"] = "frustración"
        elif re.search(r"enoj[oa]|enojo|molest[oa]|rabia|furios[oa]|coleric[oa]|bronca|impotencia", texto):
            estado["emocion_detectada"] = "enojo"
        elif re.search(r"sol[oa]|soledad|aislad[oa]|invisible|abandonad[oa]|desconectad[oa]", texto):
            estado["emocion_detectada"] = "soledad"
        elif re.search(r"insegur[oa]|inseguridad|no soy capaz|valgo poco|dud[oa] de m[ií]|me siento menos", texto):
            estado["emocion_detectada"] = "inseguridad"
        elif re.search(r"estrés|estresad[oa]|sobrecargad[oa]|agotad[oa]|saturad[oa]|acelerad[oa]", texto):
            estado["emocion_detectada"] = "estrés"
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
            "estrés": "Muchas veces el estrés aparece cuando sentimos que tenemos que encargarnos de todo al mismo tiempo. ¿Últimamente has notado que tu cuerpo o tu mente te están pidiendo una pausa?"
        }

        return respuestas.get(emocion, "¿Podés contarme un poco más sobre eso?")

    # Segunda pregunta de profundización emocional
    if estado.get("fase") == "preguntas_emocion_2":
        estado["respuesta2"] = texto
        emocion = estado.get("emocion_detectada")

        # Validación para detectar múltiples emociones
        posibles_emociones = []
        if "estrés" in texto or "estresado" in texto or "saturado" in texto:
            posibles_emociones.append("estrés")
        if "ansiedad" in texto or "preocupado" in texto or "nervioso" in texto:
            posibles_emociones.append("ansiedad")

        if len(posibles_emociones) > 1:
            if set(posibles_emociones) == {"ansiedad", "estrés"}:
                emocion = "una mezcla de ansiedad y estrés"
                descripcion = "una combinación de preocupación constante y una sensación de sobrecarga que puede hacer que todo parezca demasiado."
            elif set(posibles_emociones) == {"frustración", "tristeza"}:
                emocion = "una mezcla de frustración y tristeza"
                descripcion = "una mezcla entre el desánimo por lo que no salió como esperabas y el cansancio emocional que eso genera."
            elif set(posibles_emociones) == {"enojo", "inseguridad"}:
                emocion = "una mezcla de enojo e inseguridad"
                descripcion = "puede ser que estés sintiendo una tensión entre la frustración interna y la duda sobre vos mismo, algo muy común cuando sentimos que no nos valoran."
            elif set(posibles_emociones) == {"soledad", "ansiedad"}:
                emocion = "una mezcla de soledad y ansiedad"
                descripcion = "cuando sentimos que estamos solos con nuestras preocupaciones, es natural que la ansiedad crezca."
            else:
                emocion = "emociones combinadas"
                descripcion = "una combinación de emociones que pueden estar interactuando entre sí y dificultando encontrar claridad."
"una combinación de preocupación constante y una sensación de sobrecarga que puede hacer que todo parezca demasiado."
        else:
            estado["fase"] = "emocion_confirmada"
            usuarios_estado[user_id] = estado
            descripcion_emocion = {
                "ansiedad": "una emoción que suele sentirse como un nudo en el pecho, acompañada de pensamientos acelerados o preocupación constante.",
                "tristeza": "una sensación de vacío o desánimo que puede venir acompañada de ganas de aislarse o llorar sin razón aparente.",
                "frustración": "una emoción que aparece cuando sentimos que nuestros esfuerzos no tienen resultados, lo que genera tensión o ganas de rendirse.",
                "enojo": "una respuesta emocional intensa ante algo que percibimos como injusto o irritante, y que a veces puede salir en forma de gritos o enojo acumulado.",
                "soledad": "una sensación de desconexión o falta de compañía significativa, que puede doler incluso estando rodeado de gente.",
                "inseguridad": "una percepción interna de no ser suficiente, de dudar de uno mismo o de sentirse constantemente comparado con los demás.",
                "estrés": "una sobrecarga física o mental, como si todo fuera demasiado al mismo tiempo y no pudiéramos parar."
            }
            descripcion = descripcion_emocion.get(emocion, "una emoción difícil de identificar")

        estado["fase"] = "emocion_confirmada"
        usuarios_estado[user_id] = estado

        return (
            f"Por lo que me contás, puede que estés sintiendo *{emocion}*, que es {descripcion}
"
            f"¿Te hace sentido eso? Si querés, podemos trabajarla desarrollando una habilidad que te ayude. ¿Querés empezar por ahí? (sí/no)"
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
