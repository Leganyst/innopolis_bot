import sqlite3


# Создаем соединение с базой данных
conn = sqlite3.connect("users_telegram.db")

# Создаем курсор для выполнения SQL-запросов
cur = conn.cursor()

# Создаем таблицу users, если она еще не существует
cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, nickname TEXT, blacklist bool)")

# Функция проверки нахождения юзера в бд
def check_user_in_db(user_id):
    # Проверяем, есть ли уже такой пользователь в таблице
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    if user is None:
        return False
    return True


# Функция для записи данных пользователя в таблицу
def insert_user_db(user_id, nickname):
    # Проверяем, есть ли уже такой пользователь в таблице
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    if user is None:
        # Если нет, то добавляем его в таблицу
        cur.execute("INSERT INTO users (user_id, nickname) VALUES (?, ?)", (user_id, nickname))
        conn.commit()
        print(f"Пользователь {nickname} добавлен в базу данных.")
    else:
        # Если есть, то выводим сообщение об ошибке
        print(f"Пользователь {nickname} уже есть в базе данных.")

# Функция для удаления данных пользователя из таблицы
def delete_user_db(user_id):
    # Проверяем, есть ли такой пользователь в таблице
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    if user is not None:
        # Если есть, то удаляем его из таблицы
        cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        print(f"Пользователь {user[1]} удален из базы данных.")
    else:
        # Если нет, то выводим сообщение об ошибке
        print(f"Пользователя с таким id нет в базе данных.")

# Функция для обновления данных пользователя в таблице
def update_user_db(user_id, new_nickname):
    # Проверяем, есть ли такой пользователь в таблице
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    if user is not None:
        # Если есть, то обновляем его никнейм в таблице
        cur.execute("UPDATE users SET nickname = ? WHERE user_id = ?", (new_nickname, user_id))
        conn.commit()
        print(f"Пользователь {user[1]} обновлен на {new_nickname}.")
    else:
        # Если нет, то выводим сообщение об ошибке
        print(f"Пользователя с таким id нет в базе данных.")

# Создаем функцию для получения никнейма из базы данных по user_id
def get_nickname_db(user_id):
    # Создаем подключение к базе данных
    # Пытаемся найти запись в таблице users по user_id
    cur.execute("SELECT nickname FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    # Если запись найдена, возвращаем никнейм
    if row:
        nickname = row[0]
        return nickname
    # Если запись не найдена, возвращаем None
    else:
        return None
    
# Функция для проверки, находится ли пользователь в черном списке
async def is_banned(user_id):
    # Формируем SQL-запрос для получения значения столбца blacklist по user_id
    sql = f"SELECT blacklist FROM users WHERE user_id = {user_id};"
    # Выполняем запрос и получаем результат
    cur.execute(sql)
    result = cur.fetchone()
    # Если результат не пустой, возвращаем значение столбца blacklist (True или False)
    if result:
        return result[0]
    # Иначе возвращаем False, так как пользователь не находится в базе данных
    else:
        return False

# Функция для добавления пользователя в черный список
async def ban_user(user_id):
    # Проверяем, есть ли пользователь в базе данных
    if await is_banned(user_id) is False:
        # Если нет, то добавляем его в таблицу users с значением столбца blacklist в True
        sql = f"INSERT INTO users (user_id, blacklist) VALUES ({user_id}, True);"
        cur.execute(sql)
        conn.commit()
    else:
        # Если есть, то обновляем значение столбца blacklist в True
        sql = f"UPDATE users SET blacklist = True WHERE user_id = {user_id};"
        cur.execute(sql)
        conn.commit()


# Функция для удаления пользователя из черного списка
async def unban_user(user_id):
    # Проверяем, есть ли пользователь в базе данных
    if await is_banned(user_id) is True:
        # Если есть, то обновляем значение столбца blacklist в False
        sql = f"UPDATE users SET blacklist = False WHERE user_id = {user_id};"
        cur.execute(sql)
        conn.commit()
