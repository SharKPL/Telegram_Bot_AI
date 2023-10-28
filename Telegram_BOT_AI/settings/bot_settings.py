import logging
import os


from aiogram import executor, types
from aiogram.types import ContentType, Message

import wikipedia, re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression


from pathlib import Path

from settings.bot_create import dp, bot
from settings.keyboard import com_kb

from settings.stt import STT

stt = STT()
vectorizer = CountVectorizer()
clf = LogisticRegression()


def clean_str(r):
    r = r.lower()
    r = [c for c in r if c in alphabet]
    return ''.join(r)


alphabet = ' 1234567890-йцукенгшщзхъфывапролджэячсмитьбюёqwertyuiopasdfghjklzxcvbnm?%.,()!:;'
question = ""


def update():
    with open('dialogues.txt', encoding='utf-8') as f:
        content = f.read()

    blocks = content.split('\n')
    dataset = []

    for block in blocks:

        replicas = block.split('\\')[:2]

        if len(replicas) == 2:
            pair = [clean_str(replicas[0]), clean_str(replicas[1])]
            if pair[0] and pair[1]:
                dataset.append(pair)

    X_text = []
    y = []

    for question, answer in dataset[:10000]:
        X_text.append(question)
        y += [answer]
    print(y[0])

    X = vectorizer.fit_transform(X_text)
    print(X[0])

    clf.fit(X, y)


update()


# вывод комманд
@dp.message_handler(commands=['start', 'help'])
async def start_message(message: types.message):

    await bot.send_message(chat_id=message.chat.id, reply_markup=com_kb, text='Вот комманды')
    await message.delete()


@dp.message_handler(content_types=[ContentType.VOICE])
async def voice_message_handler(message: Message):
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("voice/tempfile.tmp")
    await bot.download_file(file_path, destination=file_on_disk)

    text = stt.audio_to_text(file_on_disk)
    await bot.send_message(chat_id=message.chat.id, text=text)
    if not text:
        text = "Формат документа не поддерживается"
    reply = get_generative_replica(text)
    await message.answer(reply)

    os.remove(file_on_disk)  # Удаление временного файла


def get_generative_replica(text):
    print([text])
    text_vector = vectorizer.transform([text]).toarray()
    question = clf.predict(text_vector)
    return question[0]


async def getwiki(s):
    try:
        ny = wikipedia.page(s)
        wikitext = ny.content[:1000]
        wikimas = wikitext.split('.')

        wikimas = wikimas[:-1]

        wikitext2 = ''
        for x in wikimas:
            if not ('==' in x):
                if (len((x.strip())) > 3):
                    wikitext2 = wikitext2 + x + '.'

            else:
                break
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\{[^\{\}]*\}', '', wikitext2)
        return wikitext2
    except Exception as e:
        return 'В энциклопедии нет информации об этом'


@dp.message_handler(content_types=['text'])
async def get_text_messages(message):
    command = message.text.lower()
    if command == "не так":
        bot.send_message(message.from_user.id, "а как?")
        bot.register_next_step_handler(message, wrong)
    else:
        print(command)
        reply = get_generative_replica(command)
        if "вики " in command:
            await bot.send_message(chat_id=message.chat.id, text=getwiki(command[3:]))
        else:
            await bot.send_message(chat_id=message.chat.id, text=reply)


@dp.message_handler(content_types=['text'])
async def wrong(message):
    a = f"{question}\{message.text.lower()} \n"
    with open('dialogues.txt', "a", encoding='utf-8') as f:
        f.write(a)
    await bot.send_message(chat_id=message.chat.id, text="Готово")
    update()


if __name__ == '__main__':
    executor.start_polling(dp)
