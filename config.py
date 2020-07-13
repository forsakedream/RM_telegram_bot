#!/usr/bin/env python3

token = '1130492550:AAHZSf8KpiGQHPbgZ_D3F4Rs6naC8CNM-lA'

states = {'start': 0, 'enter_last': 1, 'enter_modem': 2, 'enter_modem_apn': 3, 'make_request': 4}

database_name = 'bot.db'

url = "https://supp-api.rm-tech.ru/mar"

szppk = [6, 7, 8, 10, 13, 14, 15, 18, 19, 20, 41, 99, 100, 237, 238, 239, 240]

mcc = [_ for _ in range(45, 87)]
mcc.extend([101, 106, 107, 108, 109, 110, 111, 112, 113])

last = {5: szppk,
        6: mcc}

commands = {
            1: 'reboot',
            2: 'reboot.sh',
            3: 'set-apn.sh',
            4: 'set-modem-mode.sh'}

modem_modes = ['0302', '03', '02']
modem_apn = ['rdl.msk', 'internet']










