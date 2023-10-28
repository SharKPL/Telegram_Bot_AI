import telebot, wikipedia, re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

bot = telebot.TeleBot('5866643398:AAGYWG8qEdV4VQ5cyCEQzof0XKo_Lqo5aXc')

wikipedia.set_lang("ru")


def clean_str(r):
    r = r.lower()
    r = [c for c in r if c in alphabet]
    return ''.join(r)


alphabet = ' 1234567890-йцукенгшщзхъфывапролджэячсмитьбюёqwertyuiopasdfghjklzxcvbnm?%.,()!:;'


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

    global vectorizer
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(X_text)
    print(X[0])

    global clf
    clf = LogisticRegression()
    clf.fit(X, y)


update()


def get_generative_replica(text):
    text_vector = vectorizer.transform([text]).toarray()
    question = clf.predict(text_vector)
    return question[0]


def getwiki(s):
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


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Здравствуйте, Сэр.")
    bot.send_message(message.chat.id, "вы можете написать: вики (ваш вопрос), и я поищу в википедии")


question = ""


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    command = message.text.lower()
    if command == "не так":
        bot.send_message(message.from_user.id, "а как?")
        bot.register_next_step_handler(message, wrong)
    else:
        global question
        question = command
        reply = get_generative_replica(command)
        if "вики " in command:
            bot.send_message(message.from_user.id, getwiki(command[3:]))
        else:
            bot.send_message(message.from_user.id, reply)


def wrong(message):
    a = f"{question}\{message.text.lower()} \n"
    with open('dialogues.txt', "a", encoding='utf-8') as f:
        f.write(a)
    bot.send_message(message.from_user.id, "Готово")
    update()


bot.polling(none_stop=True)
