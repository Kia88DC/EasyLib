#  ------------------------ 
# |                        |
# |  By @Kiarash Shahbazi  |
# |                        |
#  ------------------------ 
__version__ = "0.0.1"
"""
-EasyLib™- is a -Library Management Application-
This App will help you manage your library.
Its usage is for librarians ONLY and should not be accessable for members of a library
All of you data will be saved on your device LOCALY, therefor be careful with your data.
"""


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
import Resources
import os
import sys
from SimpleSql import Sql
import dogpile.cache

# current_path = str(os.path.abspath(__file__)).strip("main.py")
current_path = "App/0.0.1"

CacheRegion = dogpile.cache.make_region().configure(
    'dogpile.cache.dbm',  # Using a file-based backend for persistence
    expiration_time = 86400,  # Cache items expire after 1 day
    arguments = {
        'filename': f'{current_path}/temp/EasyLib_Cache.dbm'
    }
)


def Caching_Key_Generator(args, prefix:str="", sep:str="|"):
    key = prefix
    for arg in args:
        key += str(arg) + sep
    key.strip(sep)
    return key

def cache_on_kwargs(func, namespace="", sep="|", key_generator=Caching_Key_Generator):
    def wrapper(*args, **kwargs):
        key = key_generator(args, namespace, sep)
        _cache_value = CacheRegion.get(key)

        if _cache_value == dogpile.cache.api.NO_VALUE:
            result = func(*args, **kwargs)
            CacheRegion.set(key, result)
            return result
        
        else:
            return _cache_value

    return wrapper

class Datebase(Sql):
    def __init__(self, db_name: str, all_db) -> None:
        super().__init__(db_name)
        self.All_DBs = all_db
        self.CreateDB()


    def CreateDB(self):
        for _db in self.All_DBs["All"]:
            self.sql_table(_db, self.All_DBs[_db]["table"])


    @cache_on_kwargs
    def cached_sql_show(self, table_name: str, all=True, **_kwargs):
        return super().sql_show(table_name, all, **_kwargs)



# Main Window Class -> Home UI
class MainWindow(QMainWindow, QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        # loadUi(f"{current_path}../UI/home-fa.ui", self)
        loadUi(f"{current_path}/UI/home-fa.ui", self)
        
        # Start Local DataBase Connection
        self._all_DB_Tables = {
            "All": ["Library", "Book", "User", "Transaction"],
            "AllInstances": {},
            "Library": {
                "table" : "'id' INTEGER PRIMARY KEY, 'name' TEXT DEFAULT '-', 'librarian' TEXT DEFAULT '-', 'bookCount' INTEGER DEFAULT 0, 'userCount' INTEGER DEFAULT 0, 'created_at' TEXT",
                "columns": ["id", "name", "librarian", "bookCount", "userCount", "created_at"]
            },
            "Book": {
                # "table" : "id INTEGER PRIMARY KEY,title TEXT,author TEXT,category TEXT,book_code TEXT,state_borrowed INTEGER,borrowedCount INTEGER,created_at TEXT",
                "table" : "'id' INTEGER PRIMARY KEY, 'title' TEXT NOT NULL, 'author' TEXT, 'category' TEXT NOT NULL, 'book_code' TEXT, 'state_borrowed' INTEGER DEFAULT 0, 'borrowedCount' INTEGER DEFAULT 0, 'created_at' TEXT",
                "columns": ["id", "title", "author", "category", "book_code", "state_borrowed", "borrowedCount", "created_at"]
            },
            "User": {
                # "table" : "id INTEGER PRIMARY KEY,name TEXT,user_code TEXT,number TEXT,state_subscribed INTEGER,subExpDate TEXT,state_hasBorrowed INTEGER,currBorrowedCount INTEGER,created_at TEXT",
                "table" : "'id' INTEGER PRIMARY KEY, 'name' TEXT NOT NULL, 'user_code' TEXT, 'number' TEXT, 'state_subscribed' INTEGER DEFAULT 1, 'subExpDate' TEXT NOT NULL, 'state_hasBorrowed' INTEGER DEFAULT 0, 'currBorrowedCount' INTEGER DEFAULT 0, 'created_at' TEXT",
                "columns": ["id", "name", "user_code", "number", "state_subscribed", "subExpDate", "state_hasBorrowed", "currBorrowedCount", "created_at"]
            },
            "Transaction": {
                # "table" : "id INTEGER PRIMARY KEY,user_id TEXT,book_id TEXT,title TEXT,state_done INTEGER,borrowDate TEXT,retrieveDate TEXT,renewCount INTEGER,created_at TEXT",
                "table" : "'id' INTEGER PRIMARY KEY, 'user_id' TEXT NOT NULL, 'book_id' TEXT NOT NULL, 'state_done' INTEGER DEFAULT 0, 'borrowDate' TEXT NOT NULL, 'retrieveDate' TEXT, 'renewCount' INTEGER DEFAULT 0, 'created_at' TEXT, FOREIGN KEY('user_id') REFERENCES 'User'('id'), FOREIGN KEY('book_id') REFERENCES 'User'('id')",
                "columns": ["id", "user_id", "book_id", "state_done", "borrowDate", "retrieveDate", "renewCount", "created_at"]
            }
        }
        self.database = Datebase(f"{current_path}/DB/main.db", self._all_DB_Tables)

        # define var
        self.library = ()
        self.book = {
            "columns": ["title", "author", "category", "book_code", "state_borrowed", "borrowedCount", "created_at"]
            # id : {"title": "", "author": "", "category": "", "book_code": "", "state_borrowed": 0, "borrowedCount": 0, "created_at": ""}
        }
        self.user = {
            "columns": ["name", "user_code", "number", "state_subscribed", "subExpDate", "state_hasBorrowed", "currBorrowedCount", "created_at"]
            # id : {"name": "", "user_code": "", "number": "", "state_subscribed": 1, "subExpDate": "", "state_hasBorrowed": 0, "currBorrowedCount": 0, "created_at": ""}
        }
        self.transaction = {
            "columns": ["user_id", "book_id", "state_done", "borrowDate", "retrieveDate", "renewCount", "created_at"]
            # id : {"user_id": "", "book_id": "", "state_done": 0, "borrowDate": "", "retrieveDate": "", "renewCount": 0, "created_at": ""}
        }
        self._all_DB_Tables["AllInstances"]["Library"] = self.library
        self._all_DB_Tables["AllInstances"]["Book"] = self.book
        self._all_DB_Tables["AllInstances"]["User"] = self.user
        self._all_DB_Tables["AllInstances"]["Transaction"] = self.transaction

        # define Widgets
        self.btn_menu_book = self.findChild(QtWidgets.QPushButton, "btn_menu_books")
        self.btn_menu_user = self.findChild(QtWidgets.QPushButton, "btn_menu_users")
        self.btn_menu_transaction = self.findChild(QtWidgets.QPushButton, "btn_menu_transactions")
        #

        # Pre Start
        self.library = self.database.cached_sql_show("Library", all=True)[1]

        # set Signals/Slots
        self.btn_menu_book.clicked.connect(lambda : Switch_Screen(main_widgets, "book"))
        self.btn_menu_user.clicked.connect(lambda : Switch_Screen(main_widgets, "user"))
        self.btn_menu_transaction.clicked.connect(lambda : Switch_Screen(main_widgets, "transaction"))
        #


# Books Screen Class -> Book UI
class Books_Screen(QDialog):
    def __init__(self, mainwindow):
        super().__init__()
        # set main
        self.mainwindow = mainwindow
        # load ui
        # loadUi(f"{current_path}../UI/book-fa.ui", self)
        loadUi(f"{current_path}/UI/book-fa.ui", self)

        # define var

        # define Widgets
        self.btn_menu_home = self.findChild(QtWidgets.QPushButton, "btn_menu_home")
        self.btn_menu_user = self.findChild(QtWidgets.QPushButton, "btn_menu_users")
        self.btn_menu_transaction = self.findChild(QtWidgets.QPushButton, "btn_menu_transactions")
        #

        # Pre Start

        # set Signals/Slots
        self.btn_menu_home.clicked.connect(lambda : Switch_Screen(main_widgets, "home"))
        self.btn_menu_user.clicked.connect(lambda : Switch_Screen(main_widgets, "user"))
        self.btn_menu_transaction.clicked.connect(lambda : Switch_Screen(main_widgets, "transaction"))
        #


# Users Screen Class -> User UI
class Users_Screen(QDialog):
    def __init__(self, mainwindow):
        super().__init__()
        # set main
        self.mainwindow = mainwindow
        # load ui
        # loadUi(f"{current_path}../UI/user-fa.ui", self)
        loadUi(f"{current_path}/UI/user-fa.ui", self)

        # define var

        # define Widgets
        self.btn_menu_home = self.findChild(QtWidgets.QPushButton, "btn_menu_home")
        self.btn_menu_book = self.findChild(QtWidgets.QPushButton, "btn_menu_books")
        self.btn_menu_transaction = self.findChild(QtWidgets.QPushButton, "btn_menu_transactions")
        #

        # Pre Start

        # set Signals/Slots
        self.btn_menu_home.clicked.connect(lambda : Switch_Screen(main_widgets, "home"))
        self.btn_menu_book.clicked.connect(lambda : Switch_Screen(main_widgets, "book"))
        self.btn_menu_transaction.clicked.connect(lambda : Switch_Screen(main_widgets, "transaction"))
        #


# Transactions Screen Class -> Transaction UI
class Transactions_Screen(QDialog):
    def __init__(self, mainwindow):
        super().__init__()
        # set main
        self.mainwindow = mainwindow
        # load ui
        # loadUi(f"{current_path}../UI/transaction-fa.ui", self)
        loadUi(f"{current_path}/UI/transaction-fa.ui", self)

        # define var

        # define Widgets
        self.btn_menu_home = self.findChild(QtWidgets.QPushButton, "btn_menu_home")
        self.btn_menu_book = self.findChild(QtWidgets.QPushButton, "btn_menu_books")
        self.btn_menu_user = self.findChild(QtWidgets.QPushButton, "btn_menu_users")
        #

        # Pre Start

        # set Signals/Slots
        self.btn_menu_home.clicked.connect(lambda : Switch_Screen(main_widgets, "home"))
        self.btn_menu_book.clicked.connect(lambda : Switch_Screen(main_widgets, "book"))
        self.btn_menu_user.clicked.connect(lambda : Switch_Screen(main_widgets, "user"))
        #




def showMessageBox(title, text, icon="NoIcon", buttons=False, buttonsText=[], callback=None):
    """icon=[NoIcon, Information, Warning, Critical, Question]"""
    # make message box
    qmb = QtWidgets.QMessageBox()
    qmb.setText(text)
    qmb.setWindowTitle(title)
    # set icon
    if icon == "NoIcon":
        qmb.setIcon(QtWidgets.QMessageBox.NoIcon)
    if icon == "Information":
        qmb.setIcon(QtWidgets.QMessageBox.Information)
    if icon == "Warning":
        qmb.setIcon(QtWidgets.QMessageBox.Warning)
    if icon == "Critical":
        qmb.setIcon(QtWidgets.QMessageBox.Critical)
    if icon == "Question":
        qmb.setIcon(QtWidgets.QMessageBox.Question)
    
    # set buttons on message box
    if buttons == True:
        qmb.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        if len(buttonsText) == 2:
            qmb.button(QtWidgets.QMessageBox.Ok).setText(buttonsText[0])
            qmb.button(QtWidgets.QMessageBox.Cancel).setText(buttonsText[1])
    else:
        if len(buttonsText) == 1:
            qmb.setStandardButtons(QtWidgets.QMessageBox.Ok)
            qmb.button(QtWidgets.QMessageBox.Ok).setText(buttonsText[0])
    
    # set callback(if needed)
    exe = qmb.exec()
    if exe == QtWidgets.QMessageBox.Ok:
        if callback:
            return callback()
        else:
            return None
    else:
        return None

def Switch_Screen(widget:QtWidgets.QStackedWidget, target:str):
    screens = {
        "home"        : 0,
        "book"        : 1,
        "user"        : 2,
        "transaction" : 3,
    }
    widget.setCurrentIndex(screens[target])

def app_exit():
    print("Exiting")

if __name__ == "__main__":
    global mainwindow, todo, note
    app = QApplication(sys.argv)
    main_widgets = QtWidgets.QStackedWidget()
    
    mainwindow = MainWindow()
    book = Books_Screen(mainwindow)
    user = Users_Screen(mainwindow)
    transaction = Transactions_Screen(mainwindow)

    print(f"mainwindow= {main_widgets.addWidget(mainwindow)}")
    print(f"book= {main_widgets.addWidget(book)}")
    print(f"user= {main_widgets.addWidget(user)}")
    print(f"transaction= {main_widgets.addWidget(transaction)}")
    
    main_widgets.setFixedWidth(960)
    main_widgets.setFixedHeight(720)

    main_widgets.setWindowTitle("EasyLib - Library Management Application")
    main_widgets.show()

    Switch_Screen(main_widgets, "home")

    try:
        sys.exit(app.exec_())
    except:
        app_exit()
