import config
import requests
from db import SQLighter

db = SQLighter(config.database_name)


def get_apn(apn):
    if apn not in config.modem_apn:
        config.modem_apn.append(apn)
    return config.modem_apn.index(apn)


def check_value(answer):
    checked = []
    for item in answer.split():
        if item.isdigit():
            checked.append(int(item))
    if len(checked) < 1:
        checked = [-1]
    return checked


def check_for_doubles(array):
    unique = []
    for item in array:
        if item not in unique:
            unique.append(item)
    return unique


def check_last(x):
    if (x in config.szppk) or (x in config.mcc):
        return True
    else:
        return False


def check_modems(x):
    if (x >= 1) and (x < 10):
        return True
    else:
        return False


def check_command(x):
    if (x < 0) and (x > 10):
        return -1
    else:
        return x


def last_handler(message):
    data = check_for_doubles(check_value(message.text))
    if len(list(filter(check_last, data[1:]))) > 0:
        for i in list(filter(check_last, data[1:])):
            db.insert_last(message.from_user.id, i)
    else:
        data = [-1]
    db.set_command(message.from_user.id, check_command(data[0]))


def modem_handler(message):
    data = check_for_doubles(check_value(message.text))
    last = db.get_last(message.from_user.id)
    if len(list(filter(check_modems, data))) > 0:
        for j in list(filter(check_modems, data)):
            db.set_modems(message.from_user.id, last[db.get_cycle(message.from_user.id)][0], j, 1)
    else:
        data = [-1]
    return data


def modem_params_handler(message):
    command = db.get_command(message.from_user.id)
    last = db.get_last(message.from_user.id)
    data = message.text.split()
    param = ''
    if len(data) == 2:
        if check_modems(check_value(data[0])[0]):
            if (command == 4) and (data[1] in config.modem_modes):
                param = config.modem_modes.index(data[1])
            elif command == 3:
                param = get_apn(data[1])
            else:
                data = [-1]
            db.set_modems(message.from_user.id, last[db.get_cycle(message.from_user.id)][0], check_value(data[0])[0], param)
        else:
            data = [-1]
    else:
        data = [-1]
    return data


def which(lst):
    if lst in config.last[5]:
        return 5
    elif lst in config.last[6]:
        return 6
    else:
        return -1


def make_requests(user):
    lst = db.get_last(user)
    command = db.get_command(user)
    server_response = []
    # s = requests.Session()
    for i in range(len(lst)):
        row = []
        mp = ''
        sip = f'10.11{which(lst[i][0])}.{lst[i][0]}.253'
        for j in range((command-1), 10):
            if lst[i][j] != 0:
                if command > 2:
                    mp = (command == 3)*config.modem_apn[lst[i][j]]+(command == 4)*config.modem_modes[lst[i][j]]
                cmd = (command > 1) * f'ip netns exec ETH{j} /hilink/' + config.commands[command] + (
                        command > 2) * f' {mp}'
                params = {"cmd": cmd, "sip": sip}
                # r = s.get(config.url, params=params, verify=False)
                row.append(f'Ответ от ЭС-2Г-{lst[i][0]}'+(command>1)*f', veth{j}'+f':\n\n{cmd}')
        server_response.append(row)
    return server_response
