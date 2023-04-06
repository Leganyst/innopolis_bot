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
    