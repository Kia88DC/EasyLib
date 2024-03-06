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
import SimpleSql
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


# def Caching_Key_Generator(args, prefix:str="", sep:str="|"):
def Caching_Key_Generator(mainArgs, args, kwargs, prefix:str="", sep:str="|"):
    key = prefix
    if mainArgs:
        for mainArg in mainArgs:
            key += str(mainArg) + sep
        key = key.strip(sep)
    if args:
        key += sep + "*:"
        for arg in args:
            key += str(arg) + sep
        key = key.strip(sep)
    if kwargs:
        key += sep + "**:"
        for kwarg in kwargs.keys():
            key += str(kwargs[kwarg]) + sep
        key = key.strip(sep)

    return key

def cache_on_kwargs(func, namespace="", sep="|", key_generator=Caching_Key_Generator):
    nargs = func.__code__.co_argcount
    def wrapper(*args, **kwargs):
        # key = key_generator(args, namespace, sep)
        _ = 0
        if func.__code__.co_varnames[0] in ("self", "cls"): _ = 1
        key = key_generator(args[_:nargs], args[nargs:], kwargs, namespace, sep)
        _cache_value = CacheRegion.get(key)

        if _cache_value == dogpile.cache.api.NO_VALUE:
            result = func(*args, **kwargs)
            CacheRegion.set(key, result)
            return result
        
        else:
            return _cache_value

    return wrapper

class Datebase(SimpleSql.Sql):
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


    def Search(self, text:str, category:str, tableName:str, opr:str="LIKE", all=True):
        # return self.cached_sql_show(tableName, all=True, column=category) 
        return self.cached_sql_show(tableName, all=all, 
            condition_columns=[category], 
            condition_values=[text], 
            condition_oprs=[opr], 
        )


# Main Window Class -> Home UI
class MainWindow(QMainWindow, QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        # loadUi(f"{current_path}../UI/home-fa.ui", self)
        loadUi(f"{current_path}/UI/home-fa.ui", self)
        
        # Start Local DataBase Connection
        self._all_DB_Tables = {
            "All": ["Library", "Category", "Book", "User", "Transaction"],
            "AllInstances": {},
            "Category": {
                "table" : "'id' INTEGER PRIMARY KEY AUTOINCREMENT, 'Name' TEXT NOT NULL UNIQUE",
                "columns" : ["id", "Name"]
            },
            "Library": {
                "table" : "'id' INTEGER PRIMARY KEY, 'Name' TEXT DEFAULT '-', 'Librarian' TEXT DEFAULT '-', 'bookCount' INTEGER DEFAULT 0, 'userCount' INTEGER DEFAULT 0, 'created_at' TEXT DEFAULT CURRENT_TIMESTAMP",
                "columns": ["id", "Name", "Librarian", "bookCount", "userCount"]
            },
            "Book": {
                # "table" : "id INTEGER PRIMARY KEY,title TEXT,author TEXT,category TEXT,book_code TEXT,state_borrowed INTEGER,borrowedCount INTEGER,created_at TEXT",
                "table" : "'id' INTEGER PRIMARY KEY, 'Title' TEXT NOT NULL, 'Author' TEXT, 'Category' TEXT NOT NULL, 'book_code' TEXT, 'state_borrowed' INTEGER DEFAULT 0, 'borrowedCount' INTEGER DEFAULT 0, 'created_at' TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY('Category') REFERENCES 'Category'('Name')",
                "columns": ["id", "Title", "Author", "Category", "book_code", "state_borrowed", "borrowedCount", "created_at"]
            },
            "User": {
                # "table" : "id INTEGER PRIMARY KEY,name TEXT,user_code TEXT,number TEXT,state_subscribed INTEGER,subExpDate TEXT,state_hasBorrowed INTEGER,currBorrowedCount INTEGER,created_at TEXT",
                "table" : "'id' INTEGER PRIMARY KEY, 'Name' TEXT NOT NULL, 'user_code' TEXT, 'Number' TEXT, 'state_subscribed' INTEGER DEFAULT 1, 'subExpDate' TEXT NOT NULL, 'state_hasBorrowed' INTEGER DEFAULT 0, 'currBorrowedCount' INTEGER DEFAULT 0, 'created_at' TEXT DEFAULT CURRENT_TIMESTAMP",
                "columns": ["id", "Name", "user_code", "Number", "state_subscribed", "subExpDate", "state_hasBorrowed", "currBorrowedCount", "created_at"]
            },
            "Transaction": {
                # "table" : "id INTEGER PRIMARY KEY,user_id TEXT,book_id TEXT,title TEXT,state_done INTEGER,borrowDate TEXT,retrieveDate TEXT,renewCount INTEGER,created_at TEXT",
                "table" : "'id' INTEGER PRIMARY KEY, 'user_id' TEXT NOT NULL, 'book_id' TEXT NOT NULL, 'state_done' INTEGER DEFAULT 0, 'borrowDate' TEXT NOT NULL, 'retrieveDate' TEXT, 'renewCount' INTEGER DEFAULT 0, 'created_at' TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY('user_id') REFERENCES 'User'('id'), FOREIGN KEY('book_id') REFERENCES 'Book'('id')",
                "columns": ["id", "user_id", "book_id", "state_done", "borrowDate", "retrieveDate", "renewCount", "created_at"]
            }
        }
        self.database = Datebase(f"{current_path}/DB/main.db", self._all_DB_Tables)

        # define var

        # define Widgets
        self.btn_menu_book = self.findChild(QtWidgets.QPushButton, "btn_menu_books")
        self.btn_menu_user = self.findChild(QtWidgets.QPushButton, "btn_menu_users")
        self.btn_menu_transaction = self.findChild(QtWidgets.QPushButton, "btn_menu_transactions")
        #
        self.lbl_info_LibName = self.findChild(QtWidgets.QLabel, "lbl_info_LibName")
        self.lbl_info_Librarian = self.findChild(QtWidgets.QLabel, "lbl_info_Librarian")
        self.lbl_info_BookCount = self.findChild(QtWidgets.QLabel, "lbl_info_BookCount")
        self.lbl_info_UserCount = self.findChild(QtWidgets.QLabel, "lbl_info_UserCount")
        #
        self.btn_quick_accsess_1 = self.findChild(QtWidgets.QPushButton, "btn_acc_1")
        self.btn_quick_accsess_2 = self.findChild(QtWidgets.QPushButton, "btn_acc_2")
        self.btn_quick_accsess_3 = self.findChild(QtWidgets.QPushButton, "btn_acc_3")
        self.btn_quick_accsess_4 = self.findChild(QtWidgets.QPushButton, "btn_acc_4")
        self.btn_quick_accsess_5 = self.findChild(QtWidgets.QPushButton, "btn_acc_5")
        self.btn_quick_accsess_6 = self.findChild(QtWidgets.QPushButton, "btn_acc_6")
        self.btn_quick_accsess_7 = self.findChild(QtWidgets.QPushButton, "btn_acc_7")
        self.btn_quick_accsess_8 = self.findChild(QtWidgets.QPushButton, "btn_acc_8")
        #

        # Pre Start
        self.library = self.database.cached_sql_show("Library", all=True)[1]
        self.lbl_info_LibName.setText(str(self.library[self._all_DB_Tables["Library"]["columns"].index("Name")]))
        self.lbl_info_Librarian.setText(str(self.library[self._all_DB_Tables["Library"]["columns"].index("Librarian")]))
        self.lbl_info_BookCount.setText(str(self.library[self._all_DB_Tables["Library"]["columns"].index("bookCount")]))
        self.lbl_info_UserCount.setText(str(self.library[self._all_DB_Tables["Library"]["columns"].index("userCount")]))

        # set Signals/Slots
        self.btn_menu_book.clicked.connect(lambda : Switch_Screen(main_widgets, "book"))
        self.btn_menu_user.clicked.connect(lambda : Switch_Screen(main_widgets, "user"))
        self.btn_menu_transaction.clicked.connect(lambda : Switch_Screen(main_widgets, "transaction"))
        #
        self.btn_quick_accsess_1.clicked.connect(lambda : Switch_Screen(main_widgets, "transaction"))
        self.btn_quick_accsess_2.clicked.connect(lambda : Switch_Screen(main_widgets, "transaction"))
        self.btn_quick_accsess_5.clicked.connect(lambda : Switch_Screen(main_widgets, "transaction"))

        self.btn_quick_accsess_3.clicked.connect(lambda : Switch_Screen(main_widgets, "book"))
        self.btn_quick_accsess_7.clicked.connect(lambda : Switch_Screen(main_widgets, "book"))
        
        self.btn_quick_accsess_4.clicked.connect(lambda : Switch_Screen(main_widgets, "user"))
        self.btn_quick_accsess_6.clicked.connect(lambda : Switch_Screen(main_widgets, "user"))
        self.btn_quick_accsess_8.clicked.connect(lambda : Switch_Screen(main_widgets, "user"))
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
        self.SearchCategories = {
            "عنوان": "Title", 
            "نویسنده": "Author", 
            "موضوع": "Category", 
            "کد کتاب": "book_code"
        }
        self.info_widgets = {}

        # define Widgets
        self.btn_menu_home = self.findChild(QtWidgets.QPushButton, "btn_menu_home")
        self.btn_menu_user = self.findChild(QtWidgets.QPushButton, "btn_menu_users")
        self.btn_menu_transaction = self.findChild(QtWidgets.QPushButton, "btn_menu_transactions")
        #                     Search widgets
        self.btn_search = self.findChild(QtWidgets.QPushButton, "btn_Search")
        self.inp_search_box = self.findChild(QtWidgets.QLineEdit, "inp_search_box")
        self.inp_search_category = self.findChild(QtWidgets.QComboBox, "inp_search_category")
        self.tableWidget_search_results = self.findChild(QtWidgets.QTableWidget, "tableWidget_search_results")
        #                     info widgets
        self.inp_book_title = self.findChild(QtWidgets.QLineEdit, "input_book_title")
        self.info_widgets["Title"] = self.inp_book_title
        self.inp_book_author = self.findChild(QtWidgets.QLineEdit, "input_book_author")
        self.info_widgets["Author"] = self.inp_book_author
        self.inp_book_category = self.findChild(QtWidgets.QLineEdit, "input_book_category")
        self.info_widgets["Category"] = self.inp_book_category
        self.inp_book_code = self.findChild(QtWidgets.QLineEdit, "input_book_code")
        self.info_widgets["book_code"] = self.inp_book_code
        self.lbl_book_state = self.findChild(QtWidgets.QLabel, "lbl_book_state")
        self.info_widgets["state_borrowed"] = self.lbl_book_state
        self.lbl_book_LendCount = self.findChild(QtWidgets.QLabel, "lbl_book_LendCount")
        self.info_widgets["borrowedCount"] = self.lbl_book_LendCount
        self.btn_book_save = self.findChild(QtWidgets.QPushButton, "btn_book_save")
        #

        # Pre Start
        self._clearRows(self.tableWidget_search_results)
        #                     info
        self.btn_book_save.hide()
        self._clearInfo()

        # set Signals/Slots
        self.btn_menu_home.clicked.connect(lambda : Switch_Screen(main_widgets, "home"))
        self.btn_menu_user.clicked.connect(lambda : Switch_Screen(main_widgets, "user"))
        self.btn_menu_transaction.clicked.connect(lambda : Switch_Screen(main_widgets, "transaction"))
        # Search action
        self.btn_search.clicked.connect(lambda : self.BookSearch())
        # Book Select
        self.tableWidget_search_results.itemSelectionChanged.connect(lambda : self.ShowBook())
        #
    

    def BookSearch(self):
        if self.inp_search_category.currentIndex() == 0:
            showMessageBox("خطا!", "لطفا ابتدا دسته بندی جستجو را انتخاب کنید.", icon="Warning", buttons=True)
            return None
        
        _serach_category = self.SearchCategories[self.inp_search_category.currentText()]
        _search_text = self.inp_search_box.text()
        
        try:
            _results = self.mainwindow.database.Search(text=f"%{_search_text}%", category=_serach_category, tableName="Book", opr="LIKE")
        except SimpleSql.SqlSelectError.NoDataFoundError:
            showMessageBox("", "هیچ کتابی با این مشخصات پیدا نشد!", icon="", buttons=True)
            self._clearRows(self.tableWidget_search_results)
            return None
        self.ShowSearchResults(_results[1:])

    def _clearInfo(self):
        self.inp_book_title.clear()
        self.inp_book_author.clear()
        self.inp_book_category.clear()
        self.inp_book_code.clear()

        self.inp_book_title.setReadOnly(True)
        self.inp_book_author.setReadOnly(True)
        self.inp_book_category.setReadOnly(True)
        self.inp_book_code.setReadOnly(True)

        self.lbl_book_state.setText("")
        self.lbl_book_LendCount.setText("")

    def _clearRows(self, table:QtWidgets.QTableWidget):
        rc = table.rowCount()
        for row in range(rc):
            table.removeRow(rc-row-1)

    def ShowSearchResults(self, results:list[tuple]):
        self._clearRows(self.tableWidget_search_results)

        for row in results:
            _pose = self.tableWidget_search_results.rowCount()
            self.tableWidget_search_results.insertRow(_pose)

            for column in [self.SearchCategories[key] for key in self.SearchCategories.keys()]:
                _col_index = self.mainwindow._all_DB_Tables["Book"]["columns"].index(column)
                _value = row[_col_index]
                if _value == None: _value = ""

                self.tableWidget_search_results.setItem(_pose , _col_index-1, QtWidgets.QTableWidgetItem(str(_value)))

    def _selectBook(self):
        _book_code = self.tableWidget_search_results.selectedItems()[3].text()
        return self.mainwindow.database.Search(text=_book_code, category="book_code", tableName="Book", opr="=")[1]

    def ShowBook(self):
        self._clearInfo()
        _book = self._selectBook()
        
        self.inp_book_title.setReadOnly(False)
        self.inp_book_author.setReadOnly(False)
        self.inp_book_category.setReadOnly(False)
        self.inp_book_code.setReadOnly(False)

        for column in self.info_widgets.keys():
            _col_index = self.mainwindow._all_DB_Tables["Book"]["columns"].index(column)
            self.info_widgets[column].setText(str(_book[_col_index]))


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
            qmb.button(QtWidgets.QMessageBox.Ok).setText(buttonsText[0]).setFocusPolicy(QtCore.Qt.NoFocus)
            qmb.button(QtWidgets.QMessageBox.Cancel).setText(buttonsText[1]).setFocusPolicy(QtCore.Qt.NoFocus)
    else:
        if len(buttonsText) == 1:
            qmb.setStandardButtons(QtWidgets.QMessageBox.Ok).setFocusPolicy(QtCore.Qt.NoFocus)
            qmb.button(QtWidgets.QMessageBox.Ok).setText(buttonsText[0]).setFocusPolicy(QtCore.Qt.NoFocus)
    
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
