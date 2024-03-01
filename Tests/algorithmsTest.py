from functools import lru_cache
import sqlite3 as sql
import time

# db = sql.connect("Tests/main.db")
# c = db.cursor()
# c.execute("CREATE TABLE IF NOT EXISTS Books (id PRIMARY KEY, Title string, Author string)")
# db.commit()
# db.close()


def findBook(title):
    result = {}
    with sql.connect("Tests/main.db") as db:
        c = db.cursor()
        c.execute(f"SELECT * FROM Books WHERE Title = '{title}'")
        # result = c.fetchall()[0]
        result[title] = c.fetchall()[0]
    db.close()
    return result

@lru_cache(maxsize=256)
# @lru_cache()
def findBook_lru(title):
    result = {}
    with sql.connect("Tests/main.db") as db:
        c = db.cursor()
        c.execute(f"SELECT * FROM Books WHERE Title = '{title}'")
        result[title] = c.fetchall()[0]
    db.close()
    return result




# sTime = time.time()
# book = findBook("Book1")
# print(f"Book (normal): {book}, in: {time.time() - sTime}")
# sTime = time.time()
# book_lru = findBook_lru("Book1")
# print(f"Book (with lru): {book_lru}, in: {time.time() - sTime}")

############################## more inputs #########################

def run(titles):
    result = []
    for title in titles:
        result.append(findBook(title))
    return result

def run_lru(titles):
    result = []
    for title in titles:
        result.append(findBook_lru(title))
    return result


sTime = time.time()
book = run(["Book1", "Book1", "Book1", "Book1", "Book1"])
print(f"Book (normal): {book}, in: {time.time() - sTime}")
sTime = time.time()
book_lru = run_lru(["Book1", "Book1", "Book1", "Book1", "Book1"])
print(f"Book (with lru): {book_lru}, in: {time.time() - sTime}")