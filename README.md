# RM_telegram_bot

Бот для настройки МАРов и модемов на поездах Ласточка. Работает через подключение к внутреннему API компании.

Для работы в диалоге с ботом вводится запрос с командой и ласточками, на которых нужно сделать работы.

Команды: 
1. Ребут МАРа
2. Ребут модема
3. Узнать режим работы модема
4. Установить режим работы модема
5. Узнать параметры сигнала модема
6. Узнать iccid модема
7. Вывести информацию для мониторинга
8. Узнать APN
9. Установить APN
10. Узнать статус сим-карты

Запрос вводится в виде: 

<номер команды> <номера ласточек через пробел>

Например, запрос "1 45 65 72" ребутнет МАРы на ЭС-2Г-45, ЭС-2Г-65, ЭС-2Г-72

После ввода в запросе команд №2, 3, 5, 6, 7, 8, 10, бот предложит ввести номера модемов

Например, сперва нужно ввести запрос "2 65" для работы с ласточкой ЭС-2Г-65.
После чего, бот предложит ввести номера модемов
Например, "1 2 3", что ребутнет модемы 1, 2, 3 на ЭС-2Г-65

После ввода в запросе команд №4,9 бот предложит ввести номер модема и нужное значение (только одно)

Например, сперва нужно ввести запрос "4 45" для работы с ласточкой ЭС-2Г-45
После чего, бот предложит ввести номер модемов и значение APN или режим модема (только одно)
Например, "2 0302", что установит на ЭС-2Г-45 режим работы второго модема 3G-LTE

Если в исходном запросе было указано несколько ласточек и команда 2-10, то бот будет предлагать ввести значения для каждой ласточки
