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


# import time
# import sqlite3
# import dogpile.cache

# # Configure your dogpile.cache region (adjust settings as needed)
# my_region = dogpile.cache.make_region().configure(
#     'dogpile.cache.dbm',  # Using a file-based backend for persistence
#     expiration_time = 300,  # Cache items expire after 5 minutes (adjust this as needed)
#     arguments = {
#         'filename': 'Tests/my_app_cache.dbm' 
#     }
# )
# """
# __main__:get_data_lru|Book1 Books
# """

# # Connect to your database
# database_file = "Tests/main.db"
# conn = sqlite3.connect(database_file)

# def get_data(item_id, table_name="Books"):
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM {} WHERE title = ?".format(table_name), (item_id,))
#     result = cursor.fetchone()
#     return result

# # @my_region.cache_on_arguments(namespace="db")
# @my_region.cache_on_arguments()
# def get_data_lru(item_id, table_name="Books"):
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM {} WHERE title = ?".format(table_name), (item_id,))
#     result = cursor.fetchone()
#     return result


# # sTime = time.time()
# # book = get_data("Book1")
# # print(f"Book  (normal) : {book}, in: {time.time() - sTime}")

# # print(my_region.get("__main__:get_data_lru|Book1 Books"))

# # sTime_lru = time.time()
# # book_lru = get_data_lru("Book1")
# # print(f"Book (with lru): {book_lru}, in: {time.time() - sTime_lru}")

# # print(my_region.get("__main__:get_data_lru|Book1 Books"))


# @my_region.cache_on_arguments()
# def func1(name: str, all=True):
#     result = ""
#     result += name
#     result += str(all)
    
#     return result


# @my_region.cache_multi_on_arguments()
# def func2(name: str, all=True, *args):
#     result = ""
#     result += name
#     result += str(all)
#     for arg in args:
#         result += str(arg)
    
#     return [result, name, all, args]


# @my_region.cache_multi_on_arguments()
# def func3(name: str, all=True, **kwargs):
#     result = ""
#     result += name
#     result += str(all)
#     if "a" in kwargs.keys():
#         result += kwargs["a"]
#     if "b" in kwargs.keys():
#         result += kwargs["b"]
    
#     return result


# func1("ali", False)
# print(my_region.get("__main__:func1|ali False"))

# func2("ali", False, "A", "B", "C")
# for key in ['__main__:func2|ali', '__main__:func2|False', '__main__:func2|A', '__main__:func2|B', '__main__:func2|C']:
#     print(my_region.get(key))

# func3("ali", False, a="A", b="B", c="C")
# print(my_region.get("__main__:func1|ali False"))


# conn.close()




#################################################################################################

# import dogpile.cache
# import sqlite3

# current_path = "App/0.0.1"

# CacheRegion = dogpile.cache.make_region().configure(
#     'dogpile.cache.dbm',  # Using a file-based backend for persistence
#     expiration_time = 86400,  # Cache items expire after 1 day
#     arguments = {
#         'filename': f'{current_path}/temp/EasyLib_Cache.dbm'
#     }
# )

# database_file = "Tests/main.db"
# conn = sqlite3.connect(database_file)

# def Caching_Key_Generator(args, prefix:str="", sep:str="|"):
#     key = prefix
#     for arg in args:
#         key += str(arg) + sep
#     key.strip(sep)
#     return key

# def cache_on_kwargs(func, namespace="", sep="|", key_generator=Caching_Key_Generator):
#     def wrapper(*args, **kwargs):
#         key = key_generator(args, namespace, sep)
#         _cache_value = CacheRegion.get(key)

#         if _cache_value == dogpile.cache.api.NO_VALUE:
#             result = func(*args, **kwargs)
#             CacheRegion.set(key, result)
#             return result
        
#         else:
#             return _cache_value

#     return wrapper


# @cache_on_kwargs
# def cached_sql_show(table_name: str, all=True, **_kwargs):
#     cursor = conn.cursor()
#     if all == True:
#         cursor.execute(f"SELECT * FROM {table_name}")
#     else:
#         cursor.execute(f"SELECT {_kwargs['column']} FROM {table_name}")
#     result = cursor.fetchone()
#     return result


# print(cached_sql_show("Books", True))
# print(cached_sql_show("Books", False, column="ID"))