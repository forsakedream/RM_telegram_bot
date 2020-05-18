#!/usr/bin/env python3
import config
import telebot
from telebot import apihelper
# import logging
# Настройка прокси
# apihelper.proxy = {'https' : 'socks5://95.216.33.245:10614'}
# Токен для бота
bot = telebot.TeleBot(config.token)
# logger = telebot.logger
# telebot.logger.setLevel(logging.DEBUG)

def log(message, state):
    bot.send_message(-1001352225714, f'{message.from_user.first_name} {message.from_user.last_name} '
                                     f'({message.from_user.id}) \nСостояние: {state}\nВвел: {message.text}\n')


@bot.message_handler(commands=['help'])
def help_message(message):
    if message.chat.id == 261169183:
        bot.send_message(-1001352225714, f'Пользователи: \n\n{list(config.users_states.keys())}')
    else:
        bot.send_message(message.chat.id,
                         f'Команды: \n'
                         f'1. Ребут МАРа\n'
                         f'2. Ребут модема\n'
                         f'3. Узнать режим работы модема\n'
                         f'4. Установить режим работы модема\n'
                         f'5. Узнать параметры сигнала модема\n'
                         f'6. Узнать iccid модема\n'
                         f'7. Вывести информацию для мониторинга\n'
                         f'8. Узнать APN\n'
                         f'9. Установить APN\n'
                         f'10. Узнать статус сим-карты\n\n'
                         f'Запрос вводится в виде: \n\n<номер команды> <номера ласточек через пробел>\n\n'
                         f'Например, запрос "1 45 65 72" ребутнет МАРы на ЭС-2Г-45, ЭС-2Г-65, ЭС-2Г-72\n\n'
                         f'После ввода в запросе команд №2, 3, 5, 6, 7, 8, 10, бот предложит ввести номера модемов\n\n'
                         f'Например, сперва нужно ввести запрос "2 65" для работы с ласточкой ЭС-2Г-65.\n'
                         f'После чего, бот предложит ввести номера модемов\n'
                         f'Например, "1 2 3", что ребутнет модемы 1, 2, 3 на ЭС-2Г-65\n\n'
                         f'После ввода в запросе команд №4,9 бот предложит ввести номер модема и нужное значение'
                         f' (только одно)\n\n'
                         f'Например, сперва нужно ввести запрос "4 45" для работы с ласточкой ЭС-2Г-45\n'
                         f'После чего, бот предложит ввести номер модемов и значение APN или режим модема (только одно)\n'
                         f'Например, "2 0302", что установит на ЭС-2Г-45 режим работы второго модема 3G-LTE\n\n'
                         f'Если в исходном запросе было указано несколько ласточек и команда 2-10, '
                         f'то бот будет предлагать ввести значения для каждой ласточки\n\n'
                         f'Нажми /start, чтобы продолжить')


@bot.message_handler(commands=['start'])
def start_message(message):
    state = config.get_current_state(message.chat.id)
    if state == config.states['enter_last']:
        bot.send_message(message.chat.id, 'Кажется, ты не ввел запрос. '
                                          'Введи номер команды и номера ласточек через пробел')
    elif state == config.states['enter_modem']:
        bot.send_message(message.chat.id, 'Кажется, ты не ввел номера модемов. Введи их через пробел')
    elif state == config.states['enter_modem_apn']:
        bot.send_message(message.chat.id, 'Кажется, ты не ввел номер модема и режим модема или APN. '
                                          'Введи их через пробел')
    else:
        bot.send_message(message.chat.id, f'Введи запрос: \n\nНажми /help для справки')
        config.set_state(message.chat.id, 'enter_last')


@bot.message_handler(func=lambda message: config.get_current_state(message.chat.id) == config.states['enter_last'])
def enter_last(message):
    log(message, config.get_current_state(message.chat.id))
    config.check_value(message.text, config.get_current_state(message.chat.id), message.chat.id)

    if config.users_commands[message.chat.id] == 1:
        mess = config.work(config.users_lst_modem_list[message.chat.id], config.users_commands[message.chat.id])
        for i in range(len(mess)):
            bot.send_message(message.chat.id, mess[i][0])
        bot.send_message(message.chat.id, 'Я все сделал. Нажми /start, чтобы попробовать снова ')
        config.set_state(message.chat.id, 'start')
    elif config.users_commands[message.chat.id] in [2, 3, 5, 6, 7, 8, 10]:
        config.set_state(message.chat.id, 'enter_modem')
        config.i = 0
        bot.send_message(message.chat.id, f'Введи номера veth через пробел для '
                                          f'ЭС-2Г-{config.users_lst_list[message.chat.id][config.i]}: ')
    elif config.users_commands[message.chat.id] in [4, 9]:
        config.set_state(message.chat.id, 'enter_modem_apn')
        config.i = 0
        if config.users_commands[message.chat.id] == 4:
            com = 'режим работы модема'
            com2 = f'\nДля установки режима LTE-3G, введи 0302\n' \
                   f'Для установки режима LTE, введи 03\n' \
                   f'Для установки режима 3G, введи 02\n'
        else:
            com = 'APN'
            com2 = ''

        bot.send_message(message.chat.id, f'Введи номер veth и {com} для '
                                          f'ЭС-2Г-{config.users_lst_list[message.chat.id][config.i]}: {com2}')
    elif config.users_commands[message.chat.id] == -1:
        bot.send_message(message.chat.id, f'Такого я не умею. Нажми /start, чтобы попробовать снова')
        config.set_state(message.chat.id, 'start')


@bot.message_handler(func=lambda message: config.get_current_state(message.chat.id) == config.states['enter_modem'])
def enter_modem(message):
    log(message, config.get_current_state(message.chat.id))
    row = config.check_value(message.text, config.get_current_state(message.chat.id), message.chat.id)
    if row[0] == -1:
        bot.send_message(message.chat.id, f'Ты ввел неправильные данные.\n '
                                          f'Введи номера veth через пробел для '
                                          f'ЭС-2Г-{config.users_lst_list[message.chat.id][config.i]}: ')
        return
    for j in row:
        config.users_lst_modem_list[message.chat.id][config.i][j] = 1
    if config.i != len(config.users_lst_list[message.chat.id]) - 1:
        config.i += 1
        bot.send_message(message.chat.id, f'Введи номера veth через пробел для '
                                          f'ЭС-2Г-{config.users_lst_list[message.chat.id][config.i]}: ')
        return
    else:
        mess = config.work(config.users_lst_modem_list[message.chat.id], config.users_commands[message.chat.id])
        for i in range(len(mess)):
            for j in range(len(mess[i])):
                bot.send_message(message.chat.id, mess[i][j])
        bot.send_message(message.chat.id, 'Я все сделал. Нажми /start, чтобы попробовать снова ')
        config.set_state(message.chat.id, 'start')


@bot.message_handler(func=lambda message: config.get_current_state(message.chat.id) == config.states['enter_modem_apn'])
def enter_modem(message):
    log(message, config.get_current_state(message.chat.id))
    row = message.text.split()
    try:
        row[0] = int(row[0])
    except ValueError:
        row[0] = -1

    if len(row) < 2:
        row[0] = -1
    if row[1] not in config.modem_modes:
        row[0] = -1
    if row[0] == -1:
        bot.send_message(message.chat.id, f'Ты ввел неправильные данные.\n '
                                          f'Введи номера veth через пробел для '
                                          f'ЭС-2Г-{config.users_lst_list[message.chat.id][config.i]}: ')
        return
    if config.users_commands[message.chat.id] == 4:
        com = 'режим работы модема'
        com2 = f'\nДля установки режима LTE-3G, введи 0302\n' \
               f'Для установки режима LTE, введи 03\n' \
               f'Для установки режима 3G, введи 02\n'
    else:
        com = 'APN'
        com2 = ''

    config.users_lst_modem_list[message.chat.id][config.i][row[0]] = row[1]
    if config.i != len(config.users_lst_list[message.chat.id]) - 1:
        config.i += 1
        bot.send_message(message.chat.id, f'Введи номер veth и '
                                          f'{com} для ЭС-2Г-{config.users_lst_list[message.chat.id][config.i]}: {com2}')
        return
    else:
        mess = config.work(config.users_lst_modem_list[message.chat.id], config.users_commands[message.chat.id])
        for i in range(len(mess)):
            for j in range(len(mess[i])):
                bot.send_message(message.chat.id, mess[i][j])

        bot.send_message(message.chat.id, 'Я все сделал. Нажми /start, чтобы попробовать снова ')
        config.set_state(message.chat.id, 'start')

bot.polling()
