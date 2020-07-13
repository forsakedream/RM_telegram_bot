import sqlite3


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database, check_same_thread=False)

    def close(self):
        self.connection.close()

    def executor(self, query):
        cursor = self.connection.cursor()
        with self.connection:
            return cursor.execute(query).fetchall()

    def get_all(self, table):
        return self.executor(f'SELECT * FROM {table}')

    def get_users(self):
        users = []
        for item in self.executor('SELECT user_tid FROM users'):
            users.append(item[0])
        return users

    def get_state(self, user):
        return self.executor(f'SELECT state FROM users WHERE user_tid = {user}')[0][0]

    def get_command(self, user):
        return self.executor(f'SELECT command FROM users WHERE user_tid = {user}')[0][0]

    def get_last(self, user):
        return self.executor(f'SELECT last, m1, m2, m3, m4, m5, m6, m7, m8, m9 FROM user_data WHERE user_id = {user}')

    def get_cycle(self, user):
        return self.executor(f'SELECT cycle FROM users WHERE user_tid = {user}')[0][0]

    def update_cycle(self, user):
        return self.executor(f'update users set cycle = cycle+1 where user_tid = {user}')

    def insert_user(self, user):
        if user not in self.get_users():
            self.executor(f'insert into users (user_tid) values ({user})')

    def insert_last(self, user, last):
        self.executor(f'insert into user_data (user_id, last) values ({user}, {last})')

    def set_state(self, user, state):
        self.executor(f'update users set state = {state} where user_tid = {user}')

    def set_command(self, user, command):
        self.executor(f'update users set command = {command} where user_tid = {user}')

    def set_modems(self, user, last, modem, value):
        self.executor(f'update user_data set m{modem} = {value} where user_id = {user} and last = {last}')

    def truncate(self):
        self.executor(f'DELETE FROM users')
        self.executor(f'DELETE FROM user_data')

    def set_default(self, user):
        self.executor(f'delete from user_data where user_id = {user}')
        self.executor(f'update users set command = {0}, state = {1}, cycle = {0} where user_tid = {user}')



