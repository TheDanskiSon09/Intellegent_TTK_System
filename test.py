import os
import uuid
import speech_recognition as sr
from pydub import AudioSegment
import telebot

API_TOKEN = 'API_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

os.makedirs('voice', exist_ok=True)


def save_file(file_info, filename):
    file = bot.download_file(file_info.file_path)
    with open(filename, 'wb') as f:
        f.write(file)


def convert_ogg_to_wav(ogg_filename, wav_filename):
    audio = AudioSegment.from_ogg(ogg_filename)
    silence = AudioSegment.silent(duration=500)
    audio = silence + audio + silence
    audio.export(wav_filename, format='wav')


def recognize_speech(wav_filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_filename) as source:
        audio = recognizer.record(source)
        return recognizer.recognize_google(audio, language='ru-RU')


@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    unique_id = str(uuid.uuid4())
    ogg_filename = f'voice/{unique_id}.ogg'
    wav_filename = f'voice/{unique_id}.wav'
    save_file(bot.get_file(message.voice.file_id), ogg_filename)
    convert_ogg_to_wav(ogg_filename, wav_filename)

    try:
        text = recognize_speech(wav_filename)
        bot.send_message(message.chat.id, f"🗣 Вы сказали: {text}")
    except sr.UnknownValueError:
        bot.send_message(message.chat.id, "❌ Не удалось распознать голос.")
    except sr.RequestError as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка сервиса: {e}")
    finally:
        cleanup_files(wav_filename, ogg_filename)


def cleanup_files(*filenames):
    for filename in filenames:
        try:
            os.remove(filename)
        except Exception as e:
            print(f"Ошибка при удалении файла {filename}: {e}")


if __name__ == "__main__":
    bot.polling(none_stop=True)
