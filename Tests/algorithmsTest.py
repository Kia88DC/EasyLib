# from functools import lru_cache
# import sqlite3 as sql
# import time

# # db = sql.connect("Tests/main.db")
# # c = db.cursor()
# # c.execute("CREATE TABLE IF NOT EXISTS Books (id PRIMARY KEY, Title string, Author string)")
# # db.commit()
# # db.close()


# def findBook(title):
#     result = {}
#     with sql.connect("Tests/main.db") as db:
#         c = db.cursor()
#         # c.execute(f"SELECT * FROM Books WHERE Title = '{title}'")
#         c.execute("SELECT * FROM Books WHERE Title = ?", (title,))
#         # result = c.fetchone()
#         result[title] = c.fetchone()
#     db.close()
#     return result

# @lru_cache(maxsize=256)
# # @lru_cache()
# def findBook_lru(title):
#     result = {}
#     with sql.connect("Tests/main.db") as db:
#         c = db.cursor()
#         # c.execute(f"SELECT * FROM Books WHERE Title = '{title}'")
#         c.execute("SELECT * FROM Books WHERE Title = ?", (title,))
#         result[title] = c.fetchone()
#     db.close()
#     return result




# # sTime = time.time()
# # book = findBook("Book1")
# # print(f"Book (normal): {book}, in: {time.time() - sTime}")
# # sTime = time.time()
# # book_lru = findBook_lru("Book1")
# # print(f"Book (with lru): {book_lru}, in: {time.time() - sTime}")

# ############################## more inputs #########################

# def run(titles):
#     result = []
#     for title in titles:
#         result.append(findBook(title))
#     return result

# def run_lru(titles):
#     result = []
#     for title in titles:
#         result.append(findBook_lru(title))
#     return result


# sTime = time.time()
# book = run(["Book1", "Book1", "Book1", "Book1", "Book1"])
# print(f"Book (normal): {book}, in: {time.time() - sTime}")
# sTime = time.time()
# book_lru = run_lru(["Book1", "Book1", "Book1", "Book1", "Book1"])
# print(f"Book (with lru): {book_lru}, in: {time.time() - sTime}")



###################################




# from functools import lru_cache
# import sqlite3 as sql
# import time


# def findBook(title):
#     result = {}
#     with sql.connect("Tests/main.db") as db:
#         c = db.cursor()
#         c.execute("SELECT * FROM Books WHERE Title = ?", (title,))
#         result[title] = c.fetchone()
#     return result

# @lru_cache(maxsize=256)
# def findBook_lru(title):
#     result = {}
#     with sql.connect("Tests/main.db") as db:
#         c = db.cursor()
#         c.execute("SELECT * FROM Books WHERE Title = ?", (title,))
#         result[title] = c.fetchone()
#     return result



# # def run(titles):
# #     result = []
# #     for title in titles:
# #         result.append(findBook(title))
# #     return result

# # def run_lru(titles):
# #     result = []
# #     for title in titles:
# #         result.append(findBook_lru(title))
# #     return result


# sTime = time.time()
# # book = run(["Book1", "Book1", "Book1", "Book1", "Book1"])
# book = findBook("Book1")
# print(f"Book  (normal) : {book}, in: {time.time() - sTime}")


# sTime_lru = time.time()
# # book_lru = run_lru(["Book1", "Book1", "Book1", "Book1", "Book1"])
# book_lru = findBook_lru("Book1")
# print(f"Book (with lru): {book_lru}, in: {time.time() - sTime_lru}")

# sTime_lru2 = time.time()
# book_lru2 = findBook_lru("Book1")
# print(f"Book (with lru): {book_lru2}, in: {time.time() - sTime_lru2}")

# sTime_lru3 = time.time()
# book_lru3 = findBook_lru("Book1")
# print(f"Book (with lru): {book_lru3}, in: {time.time() - sTime_lru3}")

# sTime_lru4 = time.time()
# book_lru4 = findBook_lru("Book1")
# print(f"Book (with lru): {book_lru4}, in: {time.time() - sTime_lru4}")



################################


import time
import sqlite3
import dogpile.cache

# Configure your dogpile.cache region (adjust settings as needed)
my_region = dogpile.cache.make_region().configure(
    'dogpile.cache.dbm',  # Using a file-based backend for persistence
    expiration_time = 300,  # Cache items expire after 5 minutes (adjust this as needed)
    arguments = {
        'filename': 'Tests/my_app_cache.dbm' 
    }
)

# Connect to your database
database_file = "Tests/main.db"
conn = sqlite3.connect(database_file)

def get_data(item_id, table_name="Books"):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM {} WHERE id = ?".format(table_name), (item_id,))
    result = cursor.fetchone()
    return result

@my_region.cache_on_arguments()
def get_data_lru(item_id, table_name="Books"):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM {} WHERE id = ?".format(table_name), (item_id,))
    result = cursor.fetchone()
    return result

conn.close()