import config, time
import telebot
from urllib.request import urlopen
from time import sleep
import wall_getting
import sqlite3

bot = telebot.TeleBot(config.token)
link = 'https://oauth.vk.com/authorize?client_id=6443431&display=page&redirect_uri=https://oauth.vk.com/callback&scope=wall+friends+offline&response_type=token&v=5.74&state=123456'

@bot.message_handler(commands=['start'])
def send_welcome(message):

    tg_id = message.chat.id
    print(tg_id, 'id tg')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    is_registering = c.execute('SELECT token FROM users WHERE tg_id=?', (tg_id,))
    if is_registering.fetchone() != None:
        bot.send_message(message.chat.id,
                         'Вы уже зарегестрированы')
    else:
        bot.send_message(message.chat.id,
                         'Пожалуйста, перейдите по ссылке для авторизации через ВКонтакте.\n После того, как вы авторизируетесь,'
                         'скопируйте ссылку из открывшегося окна и отправьте её боту')
        bot.send_message(message.chat.id, link)

@bot.message_handler(regexp="https://oauth.vk.com/blank.html#access_token=")
def auth(message):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    vk_code = message.text
    tg_id = message.chat.id
    vk_code = vk_code.split('=')
    vk_code = vk_code[1]
    vk_code = vk_code.split('&')
    token = vk_code[0]
    wall_getting.registration(token, tg_id)
    c.execute('UPDATE users SET token=? WHERE tg_id=?', (token, tg_id,), )
    conn.commit()
    bot.send_message(message.chat.id, 'Поздравляю, Вы зарегестрировались! Теперь Вы будуте получать новости')
    conn.close()


def send_wall(tg_id):
    all_posts = wall_getting.wall_get(tg_id)
    for post in all_posts:
        bot.send_message(tg_id, post['group_name'][0])
        if post['info'][0] != 0:
            print(post['content']['text'])
            bot.send_message(tg_id, post['content']['text'])
            if post['info'][1] != 0:
                for img in post['content']['photo']:
                    img = urlopen(img)
                    bot.send_photo(tg_id, img)
                    sleep(0.1)
        else:
            for img in post['content']['photo']:
                img = urlopen(img)
                bot.send_photo(tg_id, img)
                sleep(0.1)


if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(1)


