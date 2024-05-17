import time

from fuzzywuzzy import fuzz
import logging
from config import HOST, USER, PASSWORD, DB_NAME
import psycopg2

logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")


# Establishes a connection to the PostgreSQL database
def connect():
    try:
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            database=DB_NAME
        )
        connection.autocommit = True
        return connection
    except (Exception, psycopg2.Error) as error:
        logging.error('[ERROR] Could not connect to database:', exc_info=error)
        return None


# Closes the connection to the PostgreSQL database
def disconnect(connection):
    if connection:
        connection.close()


# Функция вывода всех номеров
def parsing_all_plate(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT number FROM employees;""")
            rows = cursor.fetchall()

            return rows
    except (Exception, psycopg2.Error) as error:
        logging.error('parsing_all_plate not implemented: ', exc_info=error)


# Функция перевода текста в нормальный вид
def standard_view(text):
    # Перевод в верхний регистр
    text = text.upper()

    # Проверка на лишнии знаки
    standart_symbol = "0123456789ABEKMHOPCTYX"
    for i in text:
        if i not in standart_symbol:
            text = text.replace(i, "")

    # Срез номера без региона
    text = text[:6]

    # Разделение на цифры и буквы
    num = text[1:4]
    lit = text[:1]+text[4:]

    # Замена символов
    num = num.replace("O", "0")
    lit = lit.replace("0", "O")

    # Возврат к обычному виду
    text = lit[:1]+num+lit[1:]

    return text

a = ["E005AM", "B606OE"]
# Функция сравнивания номеров по % схожести
def comparison(string, con):
    # parsing_all_plate(con)
    status = False
    for i in a: # Вместо a parsing_all_plate(con)
        similarity = fuzz.ratio(string, i)
        if similarity >= 50:
            status = True
    return status


# Функция открытия шлагбаума
def open_barrier():
    print("OPEN")
    time.sleep(5)
    print("CLOSED")


