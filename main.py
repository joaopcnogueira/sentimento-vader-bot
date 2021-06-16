import os
from telegram import Update
from telegram.ext.filters import Filters
from telegram.ext import Updater, CommandHandler, MessageHandler, dispatcher, CallbackContext
from telegram.files.file import File
from leia import SentimentIntensityAnalyzer
import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()

# iniciando o bot
updater = Updater(token=os.getenv("BOT_TOKEN"), use_context=True)
dispatcher = updater.dispatcher

# métodos do bot
def get_sentiment_scores(text: str):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)['compound']

    if sentiment_score < 0:
        reply = "O que é isso jovem, pra quê essa raiva?"
    else:
        reply = "E aí saltitante, tá feliz né xD"

    return reply


def convert_audio(from_file: str, to_file: str) -> bool: 
    return os.system(f"test -f {from_file}") == 0 and os.system(f"ffmpeg -i {from_file} {to_file} 2>/dev/null") == 0


def transcript(audiofile: File) -> str:
    voice_file = "audio.ogg"
    recog_file = "audio.wav"
    audiofile.download(voice_file)
    recognizer = sr.Recognizer()

    if not convert_audio(voice_file, recog_file):
        return "Erro na conversão seu bosta!"
    
    with sr.AudioFile(recog_file) as source:
        audio = recognizer.record(source)

    os.system("rm audio.ogg audio.wav")

    return recognizer.recognize_google(audio, language="pt-BR")


# métodos de callbacks
def start_callback(update: Update, context: CallbackContext):
    context.bot.sendChatAction(chat_id=update.message.chat_id, action="typing")
    update.message.reply_text(f"Olá, meu nome é {context.bot.first_name}!")


def text_callback(update: Update, context: CallbackContext):
    reply = get_sentiment_scores(update.message.text)
    # print(update.message.chat_id)
    context.bot.sendChatAction(chat_id=update.message.chat_id, action="typing")
    update.message.reply_text(reply)


def voice_callback(update: Update, context: CallbackContext):
    audiofile = context.bot.getFile(update.message.voice.file_id)

    text = transcript(audiofile)
    reply = get_sentiment_scores(text)

    context.bot.sendChatAction(chat_id=update.message.chat_id, action="typing")
    update.message.reply_text(text)
    update.message.reply_text(reply)
    

def error_callback(update: Update, context: CallbackContext):
    context.bot.send_message('272072293', f"Erro '{context.error}' na mensagem '{update.message}' enviada por {update.message.from_user.first_name} ({update.message.from_user.id})")


# callbacks
dispatcher.add_handler(CommandHandler("start", start_callback))
dispatcher.add_handler(MessageHandler(Filters.text, text_callback))
dispatcher.add_handler(MessageHandler(Filters.voice, voice_callback))
dispatcher.add_error_handler(error_callback)

updater.start_polling()
updater.idle()
