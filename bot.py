#!/usr/bin/env python3
import config
import telebot
import utils
from db import SQLighter
# Токен для бота
bot = telebot.TeleBot(config.token)
db = SQLighter(config.database_name)
db.truncate()


# Функция для отправки логов в чат
def log(message, state):
    bot.send_message(-1001352225714, f'{message.from_user.first_name} {message.from_user.last_name} '
                                     f'({message.from_user.id}) \nСостояние: {state}\nВвел: {message.text}\n')


# Хэндлер для вывода справки об использовании бота
@bot.message_handler(commands=['help'])
def help_message(message):
    db.set_default(message.from_user.id)
    db.insert_user(message.from_user.id)
    if message.from_user.id == 261169183:
        bot.send_message(-1001352225714, f'Пользователи: \n\n{db.get_all("users")}')

    bot.send_message(message.chat.id,
                         f'Команды: \n'
                         f'1. Ребут МАРа\n'
                         f'2. Ребут модема\n'
                         f'3. Установить APN\n'
                         f'4. Установить режим работы модема\n\n'
                         f'Запрос вводится в виде: \n\n<номер команды> <номера ласточек через пробел>\n\n'
                         f'Например, запрос "1 45 65 72" ребутнет МАРы на ЭС-2Г-45, ЭС-2Г-65, ЭС-2Г-72\n\n'
                         f'После ввода в запросе команды №2 бот предложит ввести номера модемов\n\n'
                         f'Например, сперва нужно ввести запрос "2 65" для работы с ласточкой ЭС-2Г-65.\n'
                         f'После чего, бот предложит ввести номера модемов\n'
                         f'Например, "1 2 3", что ребутнет модемы 1, 2, 3 на ЭС-2Г-65\n\n'
                         f'После ввода в запросе команд 3 и 4 бот предложит ввести номер модема и нужное значение'
                         f' (только одно)\n\n'
                         f'Например, сперва нужно ввести запрос "4 45" для работы с ласточкой ЭС-2Г-45\n'
                         f'После чего бот предложит ввести номер модемов и значение APN или режим модема (только одно)\n'
                         f'Например, "2 0302", что установит на ЭС-2Г-45 режим работы второго модема 3G-LTE\n\n'
                         f'Если в исходном запросе было указано несколько ласточек и команда 2-4, '
                         f'то бот будет предлагать ввести значения для каждой ласточки\n\n'
                         f'Нажми /start, чтобы вернуться')


# Хэндлер для запуска бота
@bot.message_handler(commands=['start'])
def start_message(message):
    db.set_default(message.from_user.id)
    db.insert_user(message.from_user.id)
    state = db.get_state(message.from_user.id)
    if state == config.states['enter_last']: # если не был введен запрос, просим ввести снова
        bot.send_message(message.chat.id, 'Кажется, ты не ввел запрос. '
                                          'Введи номер команды и номера ласточек через пробел')
    elif state == config.states['enter_modem']: # если не были введена номера модемов, просим ввести снова
        bot.send_message(message.chat.id, 'Кажется, ты не ввел номера модемов. Введи их через пробел')
    elif state == config.states['enter_modem_apn']: # если не были введены параметры модемов, просим ввести снова
        bot.send_message(message.chat.id, 'Кажется, ты не ввел номер модема и режим модема или APN. '
                                          'Введи их через пробел')
    else: # во всем остальных случаях, запускаем бота
        bot.send_message(message.chat.id, f'Введи запрос: \n\nНажми /help для справки')
        db.set_state(message.from_user.id, 1)


# После ввода запроса и изменения состояния на enter_last, обрабатываем запрос пользователя
@bot.message_handler(func=lambda message: db.get_state(message.from_user.id) == config.states['enter_last'])
def enter_last(message):
    log(message, db.get_state(message.from_user.id))
    utils.last_handler(message)
    command = db.get_command(message.from_user.id)
    last = db.get_last(message.from_user.id)
    # Смотрим, какую команду ввел пользователь и продолжаем работу
    if command == 1:
        making_request(message)
    elif command == 2:
        db.set_state(message.from_user.id, 2)
        bot.send_message(message.chat.id, f'Введи номера veth через пробел для '
                                          f'ЭС-2Г-{last[db.get_cycle(message.from_user.id)][0]}: ')
    elif command in [3, 4]:
        db.set_state(message.from_user.id, 3)
        bot_mes = f'Введи номер veth и ' + (command == 3)*'APN'+(command == 4)*f'режим работы модема' + \
                  f' для ЭС-2Г-{last[db.get_cycle(message.from_user.id)][0]}:'
        bot.send_message(message.chat.id, bot_mes)

    elif db.get_command(message.from_user.id) == -1:
        bot.send_message(message.chat.id, f'Такого я не умею.')
        bot.send_message(message.chat.id, f'Введи запрос: \n\nНажми /help для справки')
        db.set_state(message.from_user.id, 1)


# Этот хэндлер будет работать с модемами
@bot.message_handler(func=lambda message: db.get_state(message.from_user.id) == config.states['enter_modem'])
def enter_modem(message):
    log(message, db.get_state(message.from_user.id))
    row = utils.modem_handler(message)
    last = db.get_last(message.from_user.id)
    if row[0] == -1:
        bot.send_message(message.chat.id, f'Ты ввел неправильные данные.\n '
                                          f'Введи номера veth через пробел для '
                                          f'ЭС-2Г-{last[db.get_cycle(message.from_user.id)][0]}: ')
        return
    db.update_cycle(message.from_user.id)
    if db.get_cycle(message.from_user.id) != len(last):
        bot.send_message(message.chat.id, f'Введи номера veth через пробел для '
                                          f'ЭС-2Г-{last[db.get_cycle(message.from_user.id)][0]}: ')
        return
    else:
        making_request(message)


# Этот хэндлер будет работать с параметрами модемов
@bot.message_handler(func=lambda message: db.get_state(message.from_user.id) == config.states['enter_modem_apn'])
def enter_modem(message):
    log(message, db.get_state(message.from_user.id))
    row = utils.modem_params_handler(message)
    last = db.get_last(message.from_user.id)
    command = db.get_command(message.from_user.id)
    bot_mes = f'Введи номер veth и ' + (command == 3) * 'APN' + (command == 4) * f'режим работы модема' + \
              f' для ЭС-2Г-{last[db.get_cycle(message.from_user.id)][0]}:'

    if row[0] == -1:
        bot.send_message(message.chat.id, f'Ты ввел неправильные данные.\n {bot_mes}')
        return

    db.update_cycle(message.from_user.id)
    if db.get_cycle(message.from_user.id) != len(last):
        bot_mes = f'Введи номер veth и ' + (command == 3) * 'APN' + (command == 4) * f'режим работы модема' + \
                  f' для ЭС-2Г-{last[db.get_cycle(message.from_user.id)][0]}:'
        bot.send_message(message.chat.id, bot_mes)
        return
    else:
        making_request(message)


def making_request(message):
    mess = utils.make_requests(message.from_user.id)
    for i in range(len(mess)):
        for j in range(len(mess[i])):
            bot.send_message(message.chat.id, mess[i][j])
    db.set_default(message.from_user.id)
    bot.send_message(message.chat.id, 'Я все сделал.')
    bot.send_message(message.chat.id, f'Введи запрос: \n\nНажми /help для справки')


if __name__ == '__main__':
    bot.infinity_polling()
