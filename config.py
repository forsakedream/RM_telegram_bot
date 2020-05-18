#!/usr/bin/env python3
import requests
token = '1114935726:AAHySxNvyQg5Sn3SWQgxS38wiIXI4mvgDoo'

states = {'start': 0, 'enter_last': 1, 'enter_modem': 2, 'enter_modem_apn': 3}


url = "https://supp-api.rm-tech.ru/mar"
szpk_last = [6, 7, 8, 10, 13, 14, 15, 18, 19, 20, 41, 99, 100, 237, 238, 239, 240]
mcc_last = [i for i in range(45, 87)]
mcc_last.extend([101, 106, 107, 108, 109, 110, 111, 112, 113])
commands = {
            1: 'reboot',
            2: 'reboot.sh',
            3: 'get-modem-mode.sh',
            4: 'set-modem-mode.sh',
            5: 'signal.sh',
            6: 'iccid.sh',
            7: 'monitoring.sh',
            8: 'get-apn.sh',
            9: 'set-apn.sh',
            10: 'simstatus.sh'
                               }

modem_modes = ['0302', '03', '02']

users_states = {}
users_lst_list = {}
users_lst_modem_list = {}
users_commands = {}

i = 0


def get_current_state(user_id):
    try:
        return users_states[user_id]
    except KeyError:
        users_states[user_id] = 0
        return users_states[user_id]


def set_state(user_id, value):
    try:
        users_states[user_id] = states[value]
        return True
    except:
         return False


def check_value(a, state, user):
    b = a.split()
    checked = []
    j = 0
    try:
        if state in [1, 4, 9]:
            b[0] = int(b[0])
            if state == 1:
                users_commands[user] = int(b[0])
            j = 1
    except ValueError:
        users_commands[user] = -1
        checked.append(-1)
        return checked
    try:
        if (len(b) < 2 and state not in [2, 3]) or int(b[0]) not in list(commands.keys()):
            users_commands[user] = -1
            checked.append(-1)
            return checked
    except ValueError:
        users_commands[user] = -1
        checked.append(-1)
        return checked
    if len(b) < 1 and state in [2, 3]:
        users_commands[user] = -1
        checked.append(-1)
        return checked

    try:
        for item in b[j:]:
            if item.isnumeric():
                item = int(item)
                if item not in checked:
                    if state == 1 and (item in szpk_last or item in mcc_last):
                        checked.append(item)
                    elif state != 1 and (item in list(commands.keys())):
                        checked.append(item)
            else:
                checked = [-1]
                return checked
    except ValueError:
        users_commands[user] = -1
        checked.append(-1)
        return checked
    checked.sort()
    if state == 1:
        users_lst_list[user] = checked
        users_lst_modem_list[user] = [[0] * 10 for _ in range(len(users_lst_list[user]))]
        for i in range(len(checked)):
            users_lst_modem_list[user][i][0] = users_lst_list[user][i]
    return checked


def work(lst, command):
    server_responce = []
    for i in range(len(lst)):
        row = []
        if lst[i][0] in szpk_last:
            train = 5
        else:
            train = 6
        if command == 1:
            params = {"cmd": commands[command], "sip": f'10.11{train}.{lst[i][0]}.253'}
            r = requests.get(url, params=params, verify=False)
            row.append(f'Ответ от ЭС-2Г-{lst[i][0]}:\n\n{r.text[80:]}')
        for j in range(1,10):
            if lst[i][j] != 0:
                res = []
                if command in (4, 9):
                    p = [f' {lst[i][j]}']
                elif command == 5:
                    p = [' ecio', ' rssi', ' sinr']
                else:
                    p = ['']
                for item in p:
                    params = {
                              "cmd": f'ip netns exec ETH{j} /hilink/{commands[command]}{item}',
                              "sip": f'10.11{train}.{lst[i][0]}.253'}
                    r = requests.get(url, params=params, verify=False)
                    l = len(r.text)-1
                    res.append(r.text[80:l])
                if command == 5:
                    row.append(f'Ответ от ЭС-2Г-{lst[i][0]}, veth{j} :\n\nECIO: {res[0]}\nRSSI: {res[1]}\nSINR: {res[2]}')
                else:
                    row.append(f'Ответ от ЭС-2Г-{lst[i][0]}, veth{j} :\n\n{res[0]}')
        server_responce.append(row)
    return server_responce







