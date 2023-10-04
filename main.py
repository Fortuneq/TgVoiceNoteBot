import telebot
import traceback
import speech_recognition as sr
import subprocess
import os
import logging
from gtts import gTTS

from telebot import types

BOT_TOKEN = None

BOT_TOKEN = 'token'

r = sr.Recognizer()
bot = telebot.TeleBot(BOT_TOKEN)

LOG_FOLDER = '.logs'
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=f'{LOG_FOLDER}/app.log'
)

logger = logging.getLogger('telegram-bot')
logging.getLogger('urllib3.connectionpool').setLevel('INFO')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'вел кам')


@bot.message_handler(content_types=['voice'])
def voice_handler(message):
    file_id = message.voice.file_id  # file size check. If the file is too big, FFmpeg may not be able to handle it.
    file = bot.get_file(file_id)

    file_size = file.file_size
    if int(file_size) >= 715000:
        bot.send_message(message.chat.id, 'Upload file size is too large.')
    else:
        download_file = bot.download_file(file.file_path)  # download file for processing
        with open('audio.ogg', 'wb') as file:
            file.write(download_file)
        text = voice_recognizer('ru_RU')

        for i in ['ru', 'en', 'es', 'it']:
            language = i
            myobj = gTTS(text=text, lang=language, slow=False)
            concstr = "audio_" + i + ".mp3"
            myobj.save(concstr)
            bot.send_audio(message.from_user.id, audio=open(concstr, 'rb'))

            # language = 'ru'
        _clear()


@bot.message_handler(content_types=['video_note'])
def voice_handler(message):
    file_id = message.video_note.file_id  # file size check. If the file is too big, FFmpeg may not be able to handle it.
    file = bot.get_file(file_id)

    file_size = file.file_size
    if int(file_size) >= 715000:
        bot.send_message(message.chat.id, 'Upload file size is too large.')
    else:
        download_file = bot.download_file(file.file_path)  # download file for processing
        with open('audio.ogg', 'wb') as file:
            file.write(download_file)
        text = voice_recognizer('ru_RU')
        for i in ['ru', 'en', 'es', 'it']:
            language = i
            myobj = gTTS(text=text, lang=language, slow=False)
            concstr = "audio_" + i + ".mp3"
            myobj.save(concstr)
            bot.send_audio(message.from_user.id, audio=open(concstr, 'rb'))
            # language = 'ru'
        _clear()


def voice_recognizer(language):
    subprocess.run(['ffmpeg', '-i', 'audio.ogg', 'audio.wav', '-y'])  # formatting ogg file in to wav format
    text = 'Words not recognized.'
    file = sr.AudioFile('audio.wav')
    with file as source:
        try:
            audio = r.record(source)  # listen to file
            text = r.recognize_google(audio, language=language)  # and write the heard text to a text variable
        except:
            logger.error(f"Exception:\n {traceback.format_exc()}")

    return text


def _clear():
    """Remove unnecessary files"""
    _files = ['audio.wav', 'audio.ogg']
    for _file in _files:
        if os.path.exists(_file):
            os.remove


if __name__ == '__main__':
    logger.info('start bot')
    bot.polling(True)
    logger.info('stop bot')
