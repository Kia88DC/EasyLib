#  ------------------------ 
# |                        |
# |  By @Kiarash Shahbazi  |
# |                        |
#  ------------------------ 
__version__ = "0.1.0"
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


current_path = "/" + str(os.path.abspath(__file__)).strip("/Code/main.py")
print(current_path)
# current_path = "App/0.1.0"

# Configure Caching System Based on OS
# on Unix Based
if os.name == "posix":
    import dogpile.cache
    CacheRegion = dogpile.cache.make_region().configure(
        'dogpile.cache.dbm',  # Using a file-based backend for persistence
        expiration_time = 86400,  # Cache items expire after 1 day
        arguments = {
            'filename': f'{current_path}/temp/EasyLib_Cache.dbm'
        }
    )
# on Windows
if os.name == "nt":
    import diskcache
    CacheRegion = diskcache.Cache(f'{current_path}/temp')


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

# Configure Caching Process Based on OS
# on Unix Based
if os.name == "posix":
    def cache_on_kwargs(func, namespace="", sep="|", key_generator=Caching_Key_Generator):
        nargs = func.__code__.co_argcount
        def wrapper(*args, **kwargs):
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
# on Windows
if os.name == "nt":
    def cache_on_kwargs(func, namespace="", sep="|", key_generator=Caching_Key_Generator):
        nargs = func.__code__.co_argcount
        def wrapper(*args, **kwargs):
            _ = 0
            if func.__code__.co_varnames[0] in ("self", "cls"): _ = 1
            key = key_generator(args[_:nargs], args[nargs:], kwargs, namespace, sep)
            # _cache_value = CacheRegion.get(key)

            # if _cache_value == dogpile.cache.api.NO_VALUE:
            if key in CacheRegion:
                result = CacheRegion[key]
                return result
            
            else:
                # _result = CacheRegion.set(key, result)
                _result = func(*args, **kwargs)
                CacheRegion[key] = _result
                return _result

        return wrapper



class Datebase(SimpleSql.Sql):
    def __init__(self, db_name: str, all_db) -> None:
        super().__init__(db_name)
        self.All_DBs = all_db
        self.CreateDB()

    def CreateDB(self):
        for _db in self.All_DBs["All"]:
            self.sql_table(_db, self.All_DBs[_db]["table"])

    # on Unix
    if os.name == "posix":
        def _ExpireCache(self, hard=True):
            CacheRegion.invalidate(hard=hard)
    # on Windows
    if os.name == "nt":
        def _ExpireCache(self, hard=True):
            CacheRegion.clear()
    
    @cache_on_kwargs
    def cached_sql_show(self, table_name: str, all=True, **_kwargs):
        return super().sql_show(table_name, all, **_kwargs)

    def Search(self, text:str, category:str, tableName:str, opr:str="LIKE", all=True):
        return self.cached_sql_show(tableName, all=all, 
            condition_columns=[category], 
            condition_values=[text], 
            condition_oprs=[opr], 
        )
    
    def Add(self, tableName, columns:list[str], values=tuple[str]):
        _columns = str(columns).strip("[]").strip("]")
        _nValue = ("?,"*len(_columns.split(","))).strip(",")
        self.sql_insert(tableName, _columns, _nValue, values)
        self._ExpireCache(hard=True)

    def Delete(self, tableName:str, searchCol:str, searchValue:str, searchOpr:str, deleteAll=False):
        self.sql_delete_row(tableName, condition=not deleteAll, condition_columns=[searchCol], condition_values=[searchValue], condition_oprs=[searchOpr])
        self._ExpireCache(hard=True)

    def Update(self, tableName, targetColumn, newValue, condition_column, condition_opr, condition_value):
        self.sql_update(tableName, targetColumn, newValue, condition_column, condition_opr, condition_value)
        self._ExpireCache(hard=True)


# Main Window Class -> Home UI
class MainWindow(QMainWindow, QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi(f"{current_path}/UI/home-fa.ui", self)
        # loadUi(f"{current_path}/home-fa.ui", self)
        
        # Start Local DataBase Connection
        self._all_DB_Tables = {
            "All": ["Library", "Category", "Book", "User", "Transaction"],
            "AllInstances": {},
            "Category": {
                "table" : "'id' INTEGER PRIMARY KEY AUTOINCREMENT, 'Name' TEXT NOT NULL UNIQUE, 'CodeName' TEXT NOT NULL UNIQUE",
                "columns" : ["id", "Name", "CodeName"]
            },
            "Library": {
                "table" : "'id' INTEGER PRIMARY KEY, 'Name' TEXT DEFAULT '-', 'Librarian' TEXT DEFAULT '-', 'bookCount' INTEGER DEFAULT 0, 'userCount' INTEGER DEFAULT 0, 'created_at' TEXT DEFAULT CURRENT_TIMESTAMP",
                "columns": ["id", "Name", "Librarian", "bookCount", "userCount"]
            },
            "Book": {
                # "table" : "id INTEGER PRIMARY KEY,title TEXT,author TEXT,category TEXT,book_code TEXT,state_borrowed INTEGER,borrowedCount INTEGER,created_at TEXT",
                "table" : "'id' INTEGER PRIMARY KEY, 'Title' TEXT NOT NULL, 'Author' TEXT, 'Category' TEXT NOT NULL, 'book_code' TEXT NOT NULL UNIQUE, 'state_borrowed' INTEGER DEFAULT 0, 'borrowedCount' INTEGER DEFAULT 0, 'created_at' TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY('Category') REFERENCES 'Category'('Name')",
                "columns": ["id", "Title", "Author", "Category", "book_code", "state_borrowed", "borrowedCount", "created_at"]
            },
            "User": {
                # "table" : "id INTEGER PRIMARY KEY,name TEXT,user_code TEXT,number TEXT,state_subscribed INTEGER,subExpDate TEXT,state_hasBorrowed INTEGER,currBorrowedCount INTEGER,created_at TEXT",
                "table" : "'id' INTEGER PRIMARY KEY, 'Name' TEXT NOT NULL, 'user_code' TEXT NOT NULL UNIQUE, 'Number' TEXT, 'state_subscribed' INTEGER DEFAULT 1, 'subExpDate' TEXT NOT NULL, 'state_hasBorrowed' INTEGER DEFAULT 0, 'currBorrowedCount' INTEGER DEFAULT 0, 'created_at' TEXT DEFAULT CURRENT_TIMESTAMP",
                "columns": ["id", "Name", "user_code", "Number", "state_subscribed", "subExpDate", "state_hasBorrowed", "currBorrowedCount", "created_at"]
            },
            "Transaction": {
                # "table" : "id INTEGER PRIMARY KEY,user_id TEXT,book_id TEXT,title TEXT,state_done INTEGER,borrowDate TEXT,retrieveDate TEXT,renewCount INTEGER,created_at TEXT",
                "table" : "'id' INTEGER, 'transaction_code' TEXT, 'user_id' TEXT NOT NULL, 'book_id' TEXT NOT NULL, 'state_done' INTEGER DEFAULT 0, 'borrowDate' TEXT NOT NULL DEFAULT CURRENT_DATE, 'retrieveDate' TEXT, 'renewCount' INTEGER DEFAULT 0, 'created_at' TEXT DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY('id'), FOREIGN KEY('book_id') REFERENCES 'Book'('id'), FOREIGN KEY('user_id') REFERENCES 'User'('id')",
                "columns": ["id", "transaction_code", "user_id", "book_id", "state_done", "borrowDate", "retrieveDate", "renewCount", "created_at"]
            }
        }
        # self.database = Datebase(f"{current_path}/main.db", self._all_DB_Tables)
        self.database = Datebase(f"{current_path}/DB/main.db", self._all_DB_Tables)

        # define var
        self._user_select_in_progress = False
        self._selected_user = {}
        self._book_select_in_progress = False
        self._selected_book = {}

        # define Widgets
        self.btn_menu_book = self.findChild(QtWidgets.QPushButton, "btn_menu_books")
        self.btn_menu_user = self.findChild(QtWidgets.QPushButton, "btn_menu_users")
        self.btn_menu_transaction = self.findChild(QtWidgets.QPushButton, "btn_menu_transactions")
        # Lib Info widgets
        self.lbl_lib_name = self.findChild(QtWidgets.QLabel, "lbl_lib_name")
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
        _libBookCount, _libUserCount = self.database.cur.execute("SELECT  (SELECT COUNT(*) FROM Book) As bookCount, (SELECT COUNT(*) FROM User) as userCount;").fetchone()
        _r = self.database.cur.execute("SELECT  Name, Librarian, created_at FROM Library;").fetchone()
        print(_r)
        _libName, _libLibrarian, _libCreated_at = self.database.cur.execute("SELECT  Name, Librarian, created_at FROM Library;").fetchone()
        self.database.Delete("Library", "id", "1", "=")
        self.database.Add("Library", ["Name", "Librarian", "bookCount", "userCount", "created_at"], (_libName, _libLibrarian, _libBookCount, _libUserCount, _libCreated_at))
        # Lib Info
        self.library = self.database.cached_sql_show("Library", all=True)[1]

        self.lbl_lib_name.setText(str(self.library[self._all_DB_Tables["Library"]["columns"].index("Name")]))
        
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
        loadUi(f"{current_path}/UI/book-fa.ui", self)
        # loadUi(f"{current_path}/book-fa.ui", self)

        # define var
        self.SearchCategories = {
            "عنوان": "Title", 
            "نویسنده": "Author", 
            "موضوع": "Category", 
            "کد کتاب": "book_code"
        }
        self.info_widgets = {}
        self.__clear_in_progress = False
        self.__item_is_selected = False

        # define Widgets
        self.btn_menu_home = self.findChild(QtWidgets.QPushButton, "btn_menu_home")
        self.btn_menu_user = self.findChild(QtWidgets.QPushButton, "btn_menu_users")
        self.btn_menu_transaction = self.findChild(QtWidgets.QPushButton, "btn_menu_transactions")
        #                     Search widgets
        self.btn_search = self.findChild(QtWidgets.QPushButton, "btn_Search")
        self.inp_search_box = self.findChild(QtWidgets.QLineEdit, "inp_search_box")
        self.inp_search_category = self.findChild(QtWidgets.QComboBox, "inp_search_category")
        self.tableWidget_search_results = self.findChild(QtWidgets.QTableWidget, "tableWidget_search_results")
        #                     Lib Info widgets
        self.lbl_lib_name = self.findChild(QtWidgets.QLabel, "lbl_lib_name")
        #                     info widgets
        self.info_widgets["info"] = {}
        self.inp_book_title = self.findChild(QtWidgets.QLineEdit, "input_book_title")
        self.info_widgets["info"]["Title"] = self.inp_book_title
        self.inp_book_author = self.findChild(QtWidgets.QLineEdit, "input_book_author")
        self.info_widgets["info"]["Author"] = self.inp_book_author
        self.inp_book_category = self.findChild(QtWidgets.QLineEdit, "input_book_category")
        self.info_widgets["info"]["Category"] = self.inp_book_category
        self.inp_book_code = self.findChild(QtWidgets.QLineEdit, "input_book_code")
        self.info_widgets["info"]["book_code"] = self.inp_book_code
        self.lbl_book_state = self.findChild(QtWidgets.QLabel, "lbl_book_state")
        self.info_widgets["info"]["state_borrowed"] = self.lbl_book_state
        self.lbl_book_LendCount = self.findChild(QtWidgets.QLabel, "lbl_book_LendCount")
        self.info_widgets["info"]["borrowedCount"] = self.lbl_book_LendCount
        self.btn_book_save = self.findChild(QtWidgets.QPushButton, "btn_book_save")
        #                     addBook widgets
        self.input_bookAdd_title = self.findChild(QtWidgets.QLineEdit, "input_bookAdd_title")
        self.input_bookAdd_author = self.findChild(QtWidgets.QLineEdit, "input_bookAdd_author")
        self.input_bookAdd_category = self.findChild(QtWidgets.QComboBox, "ComboBox_bookAdd_category")
        self.input_bookAdd_book_code = self.findChild(QtWidgets.QLineEdit, "input_bookAdd_book_code")
        self.ChBox_automatic_code = self.findChild(QtWidgets.QCheckBox, "ChBox_automatic_code")
        self.btn_bookAdd_submit = self.findChild(QtWidgets.QPushButton, "btn_bookAdd_submit")
        #                     addBook widgets
        self.info_widgets["delBook"] = {}
        self.lbl_delBook_title = self.findChild(QtWidgets.QLabel, "lbl_delBook_title")
        self.info_widgets["delBook"]["Title"] = self.lbl_delBook_title
        self.lbl_delBook_author = self.findChild(QtWidgets.QLabel, "lbl_delBook_author")
        self.info_widgets["delBook"]["Author"] = self.lbl_delBook_author
        self.lbl_delBook_category = self.findChild(QtWidgets.QLabel, "lbl_delBook_category")
        self.info_widgets["delBook"]["Category"] = self.lbl_delBook_category
        self.lbl_delBook_book_code = self.findChild(QtWidgets.QLabel, "lbl_delBook_book_code")
        self.info_widgets["delBook"]["book_code"] = self.lbl_delBook_book_code
        self.btn_delBook_submit = self.findChild(QtWidgets.QPushButton, "btn_delBook_submit")
        #

        # Pre Start
        self._clearRows(self.tableWidget_search_results)
        #                     info
        self.btn_book_save.hide()
        self._clear()
        # Lib Info
        self.lbl_lib_name.setText(str(self.mainwindow.library[self.mainwindow._all_DB_Tables["Library"]["columns"].index("Name")]))

        # set Signals/Slots
        self.btn_menu_home.clicked.connect(lambda : Switch_Screen(main_widgets, "home"))
        self.btn_menu_user.clicked.connect(lambda : Switch_Screen(main_widgets, "user"))
        self.btn_menu_transaction.clicked.connect(lambda : Switch_Screen(main_widgets, "transaction"))
        # Search action
        self.btn_search.clicked.connect(lambda : self.BookSearch())
        # Book Select
        self.tableWidget_search_results.itemSelectionChanged.connect(lambda : self.ShowBook())
        # Book Add
        self.btn_bookAdd_submit.clicked.connect(lambda : self.AddBook())
        # Book Del
        self.btn_delBook_submit.clicked.connect(lambda : self.DeleteBook())
        #
    

    def BookSearch(self, _search_category=None):
        self._clear()
        if self.inp_search_category.currentIndex() == 0 and _search_category == None:
            showMessageBox("خطا!", "لطفا ابتدا دسته بندی جستجو را انتخاب کنید.", icon="Critical")
            return None
        if not _search_category:
            _search_category = self.SearchCategories[self.inp_search_category.currentText()]
        _search_text = self.inp_search_box.text()
        
        _results = self.mainwindow.database.Search(text=f"%{_search_text}%", category=_search_category, tableName="Book", opr="LIKE")
        if _results == None or _results == []:
            showMessageBox("", "هیچ کتابی با این مشخصات پیدا نشد!", icon="")
            self._clearRows(self.tableWidget_search_results)
            return None
        self.ShowSearchResults(_results[1:])

    def _clear(self, infoBox=True, delBox=True, addBox=False):
        if infoBox:
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
        
        if delBox:
            self.__item_is_selected = False
            self.lbl_delBook_title.clear()
            self.lbl_delBook_author.clear()
            self.lbl_delBook_category.clear()
            self.lbl_delBook_book_code.clear()

        if addBox:
            self.input_bookAdd_title.clear()
            self.input_bookAdd_author.clear()
            self.input_bookAdd_book_code.clear()
            self.input_bookAdd_category.setCurrentIndex(0)

    def _clearRows(self, table:QtWidgets.QTableWidget):
        self.__clear_in_progress = True
        rc = table.rowCount()
        for row in range(rc):
            table.removeRow(rc-row-1)
        self.__clear_in_progress = False

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
        self.__item_is_selected = True
        return self.mainwindow.database.Search(text=_book_code, category="book_code", tableName="Book", opr="=")[1]

    def ShowBook(self):
        if self.mainwindow._book_select_in_progress == True:
            _user = self._selectBook()
            self.mainwindow._selected_book["Title"] = _user[self.mainwindow._all_DB_Tables["Book"]["columns"].index("Title")]
            self.mainwindow._selected_book["book_code"] = _user[self.mainwindow._all_DB_Tables["Book"]["columns"].index("book_code")]
            Switch_Screen(main_widgets, "transaction")
            screen_transaction._selectBook()
            return None
        
        if self.__clear_in_progress:
            return None
        self._clear()
        _book = self._selectBook()
        
        self.inp_book_title.setReadOnly(False)
        self.inp_book_author.setReadOnly(False)
        self.inp_book_category.setReadOnly(False)
        self.inp_book_code.setReadOnly(False)

        for column in self.info_widgets["info"].keys():
            _col_index = self.mainwindow._all_DB_Tables["Book"]["columns"].index(column)
            _text = str(_book[_col_index])
            if column == "state_borrowed":
                if _text == "0":
                    _text = "موجود"
                elif _text == "1":
                    _text = "نا موجود"
            self.info_widgets["info"][column].setText(_text)
        
        for column in self.info_widgets["delBook"].keys():
            _col_index = self.mainwindow._all_DB_Tables["Book"]["columns"].index(column)
            _text = str(_book[_col_index])
            self.info_widgets["delBook"][column].setText(_text)

    def _codeCreate(self, _category):
        _id = f'{self.mainwindow.database.cur.execute("SELECT MAX(id) from Book;").fetchone()[0]:03}'
        query = f"SELECT CodeName from Category WHERE Name = '{_category}';"
        _cat = f"{self.mainwindow.database.cur.execute(query).fetchone()[0]}"
        _num = ""
        import random
        for i in range(4):
            _num += str(random.randint(0, 9))
        return str(f"{_cat}{_id}{_num}")

    def AddBook(self):
        _title = self.input_bookAdd_title.text()
        _author = self.input_bookAdd_author.text()
        _category = self.input_bookAdd_category.currentText()
        _book_code = self.input_bookAdd_book_code.text()
        # if i[0] == False or i[1] == False and i[2] == False:
        if _title == "" or _book_code == "" and not self.ChBox_automatic_code.isChecked():
            showMessageBox("خطا!", "لطفا ابتدا اطلاعات کتاب را وارد کنید.", icon="Critical")
            return None
        if self.input_bookAdd_category.currentIndex() == 0:
            showMessageBox("خطا!", "لطفا ابتدا موضوع کتاب را انتخاب کنید.", icon="Critical")
            return None
        
        if self.ChBox_automatic_code.isChecked():
           _book_code = self._codeCreate(_category)

        import sqlite3
        try:
            self.mainwindow.database.Add("Book", "Title,Author,Category,book_code", (str(_title), str(_author), str(_category), str(_book_code)))
        except sqlite3.IntegrityError:
            if self.ChBox_automatic_code.isChecked():
                self.AddBook()
            else:
                showMessageBox("خطا!", "کد کتاب نباید تکراری باشد!", icon="Warning")
                return None
        showMessageBox("موفقیت", "کتاب مورد نظر با موفقیت اضافه شد.")
        self._clear(infoBox=True, delBox=True, addBox=True)
        self._clearRows(self.tableWidget_search_results)

    def DeleteBook(self):
        if not self.__item_is_selected:
            showMessageBox("خطا!", "لطفا ابتدا یک کتاب را انتخاب کنید.", icon="Critical")
            return None
        _book_code = self.lbl_delBook_book_code.text()
        self.mainwindow.database.Delete("Book", "book_code", _book_code, "=")
        showMessageBox("موفقیت", "کتاب مورد نظر با موفقیت حذف شد.")
        self._clear(infoBox=True, delBox=True)
        self._clearRows(self.tableWidget_search_results)


# Users Screen Class -> User UI
class Users_Screen(QDialog):
    def __init__(self, mainwindow):
        super().__init__()
        # set main
        self.mainwindow = mainwindow
        # load ui
        loadUi(f"{current_path}/UI/user-fa.ui", self)
        # loadUi(f"{current_path}/user-fa.ui", self)

        # define var
        self.SearchCategories = {
            "نام": "Name", 
            "شناسه": "user_code", 
            "شماره تلفن": "Number", 
        }
        self.subAmount_Directives = {
            "یک ماه":   {"Directive": "%m", "Addition": 1},
            "دو ماه":   {"Directive": "%m", "Addition": 2},
            "سه ماه":   {"Directive": "%m", "Addition": 3},
            "چهار ماه": {"Directive": "%m", "Addition": 4},
            "شش ماه":   {"Directive": "%m", "Addition": 6},
            "یک سال":   {"Directive": "%Y", "Addition": 1},
            "دو سال":   {"Directive": "%Y", "Addition": 2},
        }
        self.info_widgets = {}
        self.__clear_in_progress = False
        self.__item_is_selected = False

        # define Widgets
        self.btn_menu_home = self.findChild(QtWidgets.QPushButton, "btn_menu_home")
        self.btn_menu_book = self.findChild(QtWidgets.QPushButton, "btn_menu_books")
        self.btn_menu_transaction = self.findChild(QtWidgets.QPushButton, "btn_menu_transactions")
        #                     Search widgets
        self.btn_search = self.findChild(QtWidgets.QPushButton, "btn_Search")
        self.inp_search_box = self.findChild(QtWidgets.QLineEdit, "inp_search_box")
        self.inp_search_category = self.findChild(QtWidgets.QComboBox, "inp_search_category")
        self.tableWidget_search_results = self.findChild(QtWidgets.QTableWidget, "tableWidget_search_results")
        #                     Lib Info widgets
        self.lbl_lib_name = self.findChild(QtWidgets.QLabel, "lbl_lib_name")
        #                     info widgets
        self.info_widgets["info"] = {}
        self.inp_user_name = self.findChild(QtWidgets.QLineEdit, "input_user_name")
        self.info_widgets["info"]["Name"] = self.inp_user_name
        self.inp_user_code = self.findChild(QtWidgets.QLineEdit, "input_user_code")
        self.info_widgets["info"]["user_code"] = self.inp_user_code
        self.inp_user_number = self.findChild(QtWidgets.QLineEdit, "input_user_number")
        self.info_widgets["info"]["Number"] = self.inp_user_number
        self.lbl_user_borrow_state = self.findChild(QtWidgets.QLabel, "lbl_user_borrow_state")
        self.info_widgets["info"]["state_hasBorrowed"] = self.lbl_user_borrow_state
        self.lbl_user_subscribtion_state = self.findChild(QtWidgets.QLabel, "lbl_user_subscribtion_state")
        self.info_widgets["info"]["state_subscribed"] = self.lbl_user_subscribtion_state
        self.lbl_user_borrow_count = self.findChild(QtWidgets.QLabel, "lbl_user_borrow_count")
        self.info_widgets["info"]["currBorrowedCount"] = self.lbl_user_borrow_count
        self.btn_user_save = self.findChild(QtWidgets.QPushButton, "btn_user_save")
        #                     addBook widgets
        self.input_userAdd_name = self.findChild(QtWidgets.QLineEdit, "input_userAdd_name")
        self.input_userAdd_user_code = self.findChild(QtWidgets.QLineEdit, "input_userAdd_user_code")
        self.input_userAdd_number = self.findChild(QtWidgets.QLineEdit, "input_userAdd_number")
        self.input_userAdd_subAmount = self.findChild(QtWidgets.QComboBox, "ComboBox_userAdd_subAmount")
        self.ChBox_automatic_code = self.findChild(QtWidgets.QCheckBox, "ChBox_userAdd_automatic_code")
        self.btn_userAdd_submit = self.findChild(QtWidgets.QPushButton, "btn_userAdd_submit")
        #                     delUser widgets
        self.info_widgets["delUser"] = {}
        self.lbl_delUser_name = self.findChild(QtWidgets.QLabel, "lbl_delUser_name")
        self.info_widgets["delUser"]["Name"] = self.lbl_delUser_name
        self.lbl_delUser_user_code = self.findChild(QtWidgets.QLabel, "lbl_delUser_user_code")
        self.info_widgets["delUser"]["user_code"] = self.lbl_delUser_user_code
        self.lbl_delUser_number = self.findChild(QtWidgets.QLabel, "lbl_delUser_number")
        self.info_widgets["delUser"]["Number"] = self.lbl_delUser_number
        self.btn_delUser_submit = self.findChild(QtWidgets.QPushButton, "btn_delUser_submit")
        #                     subRenew widgets
        self.info_widgets["renewSub"] = {}
        self.lbl_renewSub_name = self.findChild(QtWidgets.QLabel, "lbl_renewSub_name")
        self.info_widgets["renewSub"]["Name"] = self.lbl_renewSub_name
        self.lbl_renewSub_user_code = self.findChild(QtWidgets.QLabel, "lbl_renewSub_user_code")
        self.info_widgets["renewSub"]["user_code"] = self.lbl_renewSub_user_code
        self.input_renewSub_amount = self.findChild(QtWidgets.QComboBox, "ComboBox_renewSub_amount")
        self.btn_renewSub_submit = self.findChild(QtWidgets.QPushButton, "btn_renewSub_submit")
        #

        # Pre Start
        self._clearRows(self.tableWidget_search_results)
        #                     info
        self.btn_user_save.hide()
        self._clear()
        # Lib Info
        self.lbl_lib_name.setText(str(self.mainwindow.library[self.mainwindow._all_DB_Tables["Library"]["columns"].index("Name")]))

        # set Signals/Slots
        self.btn_menu_home.clicked.connect(lambda : Switch_Screen(main_widgets, "home"))
        self.btn_menu_book.clicked.connect(lambda : Switch_Screen(main_widgets, "book"))
        self.btn_menu_transaction.clicked.connect(lambda : Switch_Screen(main_widgets, "transaction"))
        # Search action
        self.btn_search.clicked.connect(lambda : self.UserSearch())
        # User Select
        self.tableWidget_search_results.itemSelectionChanged.connect(lambda : self.ShowUser())
        # User Add
        self.btn_userAdd_submit.clicked.connect(lambda : self.AddUser())
        # User Del
        self.btn_delUser_submit.clicked.connect(lambda : self.DeleteUser())
        # Renew Sub
        self.btn_renewSub_submit.clicked.connect(lambda : self.RenewSub())
        #
    

    def UserSearch(self, _search_category=None):
        self._clear()
        if self.inp_search_category.currentIndex() == 0 and _search_category == None:
            showMessageBox("خطا!", "لطفا ابتدا دسته بندی جستجو را انتخاب کنید.", icon="Critical")
            return None
        if not _search_category:
            _search_category = self.SearchCategories[self.inp_search_category.currentText()]
        _search_text = self.inp_search_box.text()
        
        _results = self.mainwindow.database.Search(text=f"%{_search_text}%", category=_search_category, tableName="User", opr="LIKE")
        if _results == None or _results == []:
            showMessageBox("", "هیچ عضوی با این مشخصات پیدا نشد!", icon="")
            self._clearRows(self.tableWidget_search_results)
            return None
        self.ShowSearchResults(_results[1:])

    def _clear(self, infoBox=True, delBox=True, renewBox=True, addBox=False):
        if infoBox:
            self.inp_user_name.clear()
            self.inp_user_code.clear()
            self.inp_user_number.clear()
            self.inp_user_name.setReadOnly(True)
            self.inp_user_code.setReadOnly(True)
            self.inp_user_number.setReadOnly(True)
            self.lbl_user_borrow_state.setText("")
            self.lbl_user_borrow_count.setText("")
            self.lbl_user_subscribtion_state.setText("")
        
        if delBox:
            self.__item_is_selected = False
            self.lbl_delUser_name.clear()
            self.lbl_delUser_user_code.clear()
            self.lbl_delUser_number.clear()
        
        if renewBox:
            self.lbl_renewSub_name.clear()
            self.lbl_renewSub_user_code.clear()

        if addBox:
            self.input_userAdd_name.clear()
            self.input_userAdd_user_code.clear()
            self.input_userAdd_number.clear()

    def _clearRows(self, table:QtWidgets.QTableWidget):
        self.__clear_in_progress = True
        rc = table.rowCount()
        for row in range(rc):
            table.removeRow(rc-row-1)
        self.__clear_in_progress = False

    def ShowSearchResults(self, results:list[tuple]):
        self._clearRows(self.tableWidget_search_results)

        for row in results:
            _pose = self.tableWidget_search_results.rowCount()
            self.tableWidget_search_results.insertRow(_pose)

            for column in [self.SearchCategories[key] for key in self.SearchCategories.keys()]:
                _col_index = self.mainwindow._all_DB_Tables["User"]["columns"].index(column)
                _value = row[_col_index]
                if _value == None: _value = ""

                self.tableWidget_search_results.setItem(_pose , _col_index-1, QtWidgets.QTableWidgetItem(str(_value)))

    def _selectUser(self):
        _user_code = self.tableWidget_search_results.selectedItems()[1].text()
        self.__item_is_selected = True
        return self.mainwindow.database.Search(text=_user_code, category="user_code", tableName="User", opr="=")[1]

    def ShowUser(self):
        if self.mainwindow._user_select_in_progress == True:
            _user = self._selectUser()
            self.mainwindow._selected_user["Name"] = _user[self.mainwindow._all_DB_Tables["User"]["columns"].index("Name")]
            self.mainwindow._selected_user["user_code"] = _user[self.mainwindow._all_DB_Tables["User"]["columns"].index("user_code")]
            Switch_Screen(main_widgets, "transaction")
            screen_transaction._selectUser()
            return None
        
        if self.__clear_in_progress:
            return None
        self._clear()
        _user = self._selectUser()
        
        self.inp_user_name.setReadOnly(False)
        self.inp_user_code.setReadOnly(False)
        self.inp_user_number.setReadOnly(False)

        for column in self.info_widgets["info"].keys():
            _col_index = self.mainwindow._all_DB_Tables["User"]["columns"].index(column)
            _text = str(_user[_col_index])
            if column == "state_hasBorrowed":
                if _text == "0":
                    _text = "گرفته نشده"
                elif _text == "1":
                    _text = "گرفته شده"
            elif column == "state_subscribed":
                if _text == "0":
                    _text = "عضو نیست"
                elif _text == "1":
                    _text = "عضو است"
            self.info_widgets["info"][column].setText(_text)
        
        for column in self.info_widgets["delUser"].keys():
            _col_index = self.mainwindow._all_DB_Tables["User"]["columns"].index(column)
            _text = str(_user[_col_index])
            self.info_widgets["delUser"][column].setText(_text)

        for column in self.info_widgets["renewSub"].keys():
            _col_index = self.mainwindow._all_DB_Tables["User"]["columns"].index(column)
            _text = str(_user[_col_index])
            self.info_widgets["renewSub"][column].setText(_text)

    def _codeCreate(self):
        _id = f'{self.mainwindow.database.cur.execute("SELECT MAX(id) from User;").fetchone()[0]:03}'
        _cat = "UID"
        _num = ""
        import random
        for i in range(3):
            _num += str(random.randint(0, 9))
        return str(f"{_cat}{_id}{_num}")

    def AddUser(self):
        _name = self.input_userAdd_name.text()
        _user_code = self.input_userAdd_user_code.text()
        _number = self.input_userAdd_number.text()
        _subAmount = self.input_userAdd_subAmount.currentText()
        if _name == "" or _number == "" or _user_code == "" and not self.ChBox_automatic_code.isChecked():
            showMessageBox("خطا!", "لطفا ابتدا اطلاعات عضو را وارد کنید.", icon="Critical")
            return None
        if self.input_userAdd_subAmount.currentIndex() == 0:
            showMessageBox("خطا!", "لطفا ابتدا مدت عضویت را انتخاب کنید.", icon="Critical")
            return None
        
        if self.ChBox_automatic_code.isChecked():
           _user_code = self._codeCreate()

        import time
        _targetVal = int(time.strftime(self.subAmount_Directives[_subAmount]["Directive"]))
        _targetVal += int(self.subAmount_Directives[_subAmount]["Addition"])
        _targetVal = f'{_targetVal:02}'
        if self.subAmount_Directives[_subAmount]["Directive"] == "%Y":
            _subExpDate = time.strftime(f"{_targetVal}-%m-%d %H:%M:%S")
        elif self.subAmount_Directives[_subAmount]["Directive"] == "%m":
            _subExpDate = time.strftime(f"%Y-{_targetVal}-%d %H:%M:%S")

        import sqlite3
        try:
            self.mainwindow.database.Add("User", "Name,user_code,Number,subExpDate", (str(_name), str(_user_code), str(_number), str(_subExpDate)))
        except sqlite3.IntegrityError:
            if self.ChBox_automatic_code.isChecked():
                self.AddUser()
            else:
                showMessageBox("خطا!", "شناسه عضو نباید تکراری باشد!", icon="Warning")
                return None
        showMessageBox("موفقیت", "عضو مورد نظر با موفقیت اضافه شد.")
        self._clear(infoBox=True, delBox=True, renewBox=True, addBox=True)
        self._clearRows(self.tableWidget_search_results)

    def DeleteUser(self):
        if not self.__item_is_selected:
            showMessageBox("خطا!", "لطفا ابتدا یک عضو را انتخاب کنید.", icon="Critical")
            return None
        _user_code = self.lbl_delUser_user_code.text()
        self.mainwindow.database.Delete("User", "user_code", _user_code, "=")
        showMessageBox("موفقیت", "عضو مورد نظر با موفقیت حذف شد.")
        self._clear(infoBox=True, delBox=True, renewBox=True)
        self._clearRows(self.tableWidget_search_results)

    def RenewSub(self):
        if self.input_renewSub_amount.currentIndex() == 0:
            showMessageBox("خطا!", "لطفا ابتدا مدت تمدید را انتخاب کنید.", icon="Critical")
            return None
        _subRenewAmount = self.input_renewSub_amount.currentText()
        _user_code = self.lbl_renewSub_user_code.text()

        _targetVal = self.mainwindow.database.cached_sql_show("User", all=False, column="subExpDate", condition_columns=["user_code"], condition_values=[_user_code],  condition_oprs=["="])[1][0]
        _targetVal_year  = _targetVal.split(" ")[0].split("-")[0]
        _targetVal_month = _targetVal.split(" ")[0].split("-")[1]
        _targetVal_other = _targetVal.split(" ")[0].split("-")[2] + " " + _targetVal.split(" ")[1]

        if self.subAmount_Directives[_subRenewAmount]["Directive"] == "%Y":
            _subExpDate = int(_targetVal.split(" ")[0].split("-")[0]) + int(self.subAmount_Directives[_subRenewAmount]["Addition"])
            _subExpDate = f"{_subExpDate}-{_targetVal_month}-{_targetVal_other}"
        elif self.subAmount_Directives[_subRenewAmount]["Directive"] == "%m":
            _subExpDate = int(_targetVal.split(" ")[0].split("-")[1]) + int(self.subAmount_Directives[_subRenewAmount]["Addition"])
            _subExpDate = f'{_subExpDate:02}'
            _subExpDate = f"{_targetVal_year}-{_subExpDate}-{_targetVal_other}"
        
        self.mainwindow.database.Update("User", "subExpDate", _subExpDate, "user_code", "=", _user_code)
        showMessageBox("موفقیت", "مدت اشتراک عضو مورد نظر با موفقیت تمدید شد.")


# Transactions Screen Class -> Transaction UI
class Transactions_Screen(QDialog):
    def __init__(self, mainwindow):
        super().__init__()
        # set main
        self.mainwindow = mainwindow
        # load ui
        loadUi(f"{current_path}/UI/transaction-fa.ui", self)
        # loadUi(f"{current_path}/transaction-fa.ui", self)

        # define var
        self.SearchCategories = {
            "نام عضو": "user_id", 
            "نام کتاب": "book_id", 
            "وضعیت": "state_done", 
            "تاریخ امانت": "borrowDate", 
            "تاریخ تحویل": "retrieveDate", 
            "شناسه مبادله": "transaction_code"
        }
        self.renewAmount_Directives = {
            "یک روز":  1,
            "دو روز":  2,
            "یک هفته": 7,
            "ده روز":  10,
            "دو هفته": 14,
            "یک ماه":  30
        }
        self.info_widgets = {}
        self.__clear_in_progress = False
        self.__item_is_selected = False
        self._selected_user_code = ""
        self._selected_book_code = ""
        self._selected_transaction_state_done = False

        # define Widgets
        self.btn_menu_home = self.findChild(QtWidgets.QPushButton, "btn_menu_home")
        self.btn_menu_book = self.findChild(QtWidgets.QPushButton, "btn_menu_books")
        self.btn_menu_user = self.findChild(QtWidgets.QPushButton, "btn_menu_users")
        #                     Search widgets
        self.btn_search = self.findChild(QtWidgets.QPushButton, "btn_Search")
        self.inp_search_box = self.findChild(QtWidgets.QLineEdit, "inp_search_box")
        self.inp_search_category = self.findChild(QtWidgets.QComboBox, "inp_search_category")
        self.tableWidget_search_results = self.findChild(QtWidgets.QTableWidget, "tableWidget_search_results")
        #                     Lib Info widgets
        self.lbl_lib_name = self.findChild(QtWidgets.QLabel, "lbl_lib_name")
        #                     info widgets
        self.info_widgets["info"] = {}
        self.lbl_transaction_user_name = self.findChild(QtWidgets.QLabel, "lbl_transaction_user_name")
        self.info_widgets["info"]["user_id"] = self.lbl_transaction_user_name
        self.lbl_transaction_book_name = self.findChild(QtWidgets.QLabel, "lbl_transaction_book_name")
        self.info_widgets["info"]["book_id"] = self.lbl_transaction_book_name
        self.lbl_transaction_code = self.findChild(QtWidgets.QLabel, "lbl_transaction_code")
        self.info_widgets["info"]["transaction_code"] = self.lbl_transaction_code
        self.lbl_transaction_state_done = self.findChild(QtWidgets.QLabel, "lbl_transaction_state")
        self.info_widgets["info"]["state_done"] = self.lbl_transaction_state_done
        self.lbl_transaction_lend_date = self.findChild(QtWidgets.QLabel, "lbl_transaction_lend_date")
        self.info_widgets["info"]["borrowDate"] = self.lbl_transaction_lend_date
        self.lbl_transaction_retrieve_date = self.findChild(QtWidgets.QLabel, "lbl_transaction_retrieve_date")
        self.info_widgets["info"]["retrieveDate"] = self.lbl_transaction_retrieve_date
        self.btn_transaction_save = self.findChild(QtWidgets.QPushButton, "btn_transaction_save")
        #                     lend widgets
        self.lbl_lend_user_name = self.findChild(QtWidgets.QLabel, "lbl_lend_user_name")
        self.btn_lend_selectUser = self.findChild(QtWidgets.QPushButton, "btn_lend_selectUser")
        self.btn_lend_deseletUser = self.findChild(QtWidgets.QPushButton, "btn_lend_deselectUser")
        self.lbl_lend_book_name = self.findChild(QtWidgets.QLabel, "lbl_lend_book_name")
        self.btn_lend_selectBook = self.findChild(QtWidgets.QPushButton, "btn_lend_selectBook")
        self.btn_lend_deseletBook = self.findChild(QtWidgets.QPushButton, "btn_lend_deselectBook")
        self.input_lend_date = self.findChild(QtWidgets.QLineEdit, "input_lend_date")
        self.ChBox_lend_automatic_date = self.findChild(QtWidgets.QCheckBox, "ChBox_lend_today")
        self.btn_lend_submit = self.findChild(QtWidgets.QPushButton, "btn_lend_submit")
        #                     retrieve widgets
        self.info_widgets["retrieve"] = {}
        self.lbl_retrieve_transaction_code = self.findChild(QtWidgets.QLabel, "lbl_retrieve_transaction_code")
        self.info_widgets["retrieve"]["transaction_code"] = self.lbl_retrieve_transaction_code
        self.input_retrieve_date = self.findChild(QtWidgets.QLineEdit, "input_retrieve_date")
        self.ChBox_retrieve_automatic_date = self.findChild(QtWidgets.QCheckBox, "ChBox_retrieve_today")
        self.btn_retrieve_submit = self.findChild(QtWidgets.QPushButton, "btn_retrieve_submit")
        #                     bookRenew widgets
        self.info_widgets["bookRenew"] = {}
        self.lbl_bookRenew_transaction_code = self.findChild(QtWidgets.QLabel, "lbl_bookRenew_transaction_code")
        self.info_widgets["bookRenew"]["transaction_code"] = self.lbl_bookRenew_transaction_code
        self.input_bookRenew_amount = self.findChild(QtWidgets.QComboBox, "ComboBox_bookRenew_renewTime")
        self.btn_bookRenew_submit = self.findChild(QtWidgets.QPushButton, "btn_bookRenew_submit")
        #

        # Pre Start
        self._clearRows(self.tableWidget_search_results)
        #                     info
        self.btn_transaction_save.hide()
        self.lbl_lend_user_name.hide()
        self.btn_lend_deseletUser.hide()
        self.lbl_lend_book_name.hide()
        self.btn_lend_deseletBook.hide()
        self._clear()
        # Lib Info
        self.lbl_lib_name.setText(str(self.mainwindow.library[self.mainwindow._all_DB_Tables["Library"]["columns"].index("Name")]))

        # set Signals/Slots
        self.btn_menu_home.clicked.connect(lambda : Switch_Screen(main_widgets, "home"))
        self.btn_menu_book.clicked.connect(lambda : Switch_Screen(main_widgets, "book"))
        self.btn_menu_user.clicked.connect(lambda : Switch_Screen(main_widgets, "user"))
        # Search action
        self.btn_search.clicked.connect(lambda : self.TransactionSearch())
        # Transaction Select
        self.tableWidget_search_results.itemSelectionChanged.connect(lambda : self.ShowTransaction())
        # Lend
        self.btn_lend_selectUser.clicked.connect(lambda : self._selectUser())
        self.btn_lend_deseletUser.clicked.connect(lambda : self._deselectUser())
        self.btn_lend_selectBook.clicked.connect(lambda : self._selectBook())
        self.btn_lend_deseletBook.clicked.connect(lambda : self._deselectBook())
        self.btn_lend_submit.clicked.connect(lambda : self.Lend())
        # Retrieve
        self.btn_retrieve_submit.clicked.connect(lambda : self.Retrieve())
        # BookRenew
        self.btn_bookRenew_submit.clicked.connect(lambda : self.RenewBook())
        #

    def TransactionSearch(self, _search_category=None):
        self._clear()
        if self.inp_search_category.currentIndex() == 0 and _search_category == None:
            showMessageBox("خطا!", "لطفا ابتدا دسته بندی جستجو را انتخاب کنید.", icon="Critical")
            return None
        
        if not _search_category:
            _search_category = self.inp_search_category.currentText()
            if _search_category == "نام عضو":
                _search_category = "User.Name"
            elif _search_category == "نام کتاب":
                _search_category = "Book.Title"
            else:
                _search_category = self.SearchCategories[self.inp_search_category.currentText()]
        _search_text = self.inp_search_box.text()


        if _search_category == "state_done":
            print("state_done")
            if _search_text == "انجام شده":
                _search_text = 1
            elif _search_text == "منتظر تحویل":
                _search_text = 0
        
        _results = self.mainwindow.database.cur.execute(
            f"""
            SELECT 
                'Transaction'.id, 'Transaction'.transaction_code, User.Name, Book.Title, 'Transaction'.state_done, 'Transaction'.borrowDate, 'Transaction'.retrieveDate
            FROM 
                'Transaction' 
            INNER JOIN User ON 
                User.id = 'Transaction'.user_id 
            INNER JOIN Book ON 
                Book.id = 'Transaction'.book_id 
            WHERE {_search_category} LIKE '%{_search_text}%';
            """
        ).fetchall()
        if _results == None or _results == []:
            showMessageBox("", "هیچ مبادله ای با این مشخصات پیدا نشد!", icon="")
            self._clearRows(self.tableWidget_search_results)
            return None
        self.ShowSearchResults(_results)

    def _clear(self, infoBox=True, delBox=True, renewBox=True, addBox=False):
        if infoBox:
            self.lbl_transaction_code.setText("")
            self.lbl_transaction_user_name.setText("")
            self.lbl_transaction_book_name.setText("")
            self.lbl_transaction_state_done.setText("")
            self.lbl_transaction_lend_date.setText("")
            self.lbl_transaction_retrieve_date.setText("")
        
        # if delBox:
        #     self.__item_is_selected = False
        #     self.lbl_delUser_name.clear()
        #     self.lbl_delUser_user_code.clear()
        #     self.lbl_delUser_number.clear()
        
        # if renewBox:
        #     self.lbl_renewSub_name.clear()
        #     self.lbl_renewSub_user_code.clear()

        # if addBox:
        #     self.input_userAdd_name.clear()
        #     self.input_userAdd_user_code.clear()
        #     self.input_userAdd_number.clear()

    def _clearRows(self, table:QtWidgets.QTableWidget):
        self.__clear_in_progress = True
        rc = table.rowCount()
        for row in range(rc):
            table.removeRow(rc-row-1)
        self.__clear_in_progress = False

    def ShowSearchResults(self, results:list[tuple]):
        self._clearRows(self.tableWidget_search_results)

        for row in results:
            _pose = self.tableWidget_search_results.rowCount()
            self.tableWidget_search_results.insertRow(_pose)

            for column in [self.SearchCategories[key] for key in self.SearchCategories.keys()]:
                _col_index = self.mainwindow._all_DB_Tables["Transaction"]["columns"].index(column)
                _value = row[_col_index]
                if _value == None: _value = ""
                if column == "state_done":
                    if _value == "0" or _value == 0:
                        _value = "منتظر تحویل"
                    elif _value == "1" or _value == 1:
                        _value = "انجام شده"

                self.tableWidget_search_results.setItem(_pose , _col_index-1, QtWidgets.QTableWidgetItem(str(_value)))

    def _selectTransaction(self):
        _transaction_code = self.tableWidget_search_results.selectedItems()[0].text()
        self.__item_is_selected = True
        # return self.mainwindow.database.Search(text=_transaction_code, category="transaction_code", tableName="Transaction", opr="=")[1]
        return self.mainwindow.database.cur.execute(
            f"""
            SELECT 
                'Transaction'.id, 'Transaction'.transaction_code , User.Name, Book.Title, 'Transaction'.state_done, 'Transaction'.borrowDate, 'Transaction'.retrieveDate
            FROM 
                'Transaction' 
            INNER JOIN User ON 
                User.id = 'Transaction'.user_id 
            INNER JOIN Book ON 
                Book.id = 'Transaction'.book_id 
            WHERE 'Transaction'.'transaction_code' = '{_transaction_code}';
            """
        ).fetchone()

    def ShowTransaction(self):
        if self.__clear_in_progress:
            return None
        self._clear()
        _transaction = self._selectTransaction()

        for column in self.info_widgets["info"].keys():
            _col_index = self.mainwindow._all_DB_Tables["Transaction"]["columns"].index(column)
            _text = str(_transaction[_col_index])
            if column == "state_done":
                if _text == "0":
                    _text = "منتظر تحویل"
                elif _text == "1":
                    _text = "انجام شده"
            self.info_widgets["info"][column].setText(_text)
        
        for column in self.info_widgets["retrieve"].keys():
            _col_index = self.mainwindow._all_DB_Tables["Transaction"]["columns"].index(column)
            _text = str(_transaction[_col_index])
            self.info_widgets["retrieve"][column].setText(_text)
        _col_index = self.mainwindow._all_DB_Tables["Transaction"]["columns"].index("state_done")
        _text = str(_transaction[_col_index])
        if _text == "0":
            _text = False
        elif _text == "1":
            _text = True
        self._selected_transaction_state_done = _text

        for column in self.info_widgets["bookRenew"].keys():
            _col_index = self.mainwindow._all_DB_Tables["Transaction"]["columns"].index(column)
            _text = str(_transaction[_col_index])
            self.info_widgets["bookRenew"][column].setText(_text)

    def _selectUser(self):
        if self.mainwindow._user_select_in_progress == False:
            self.mainwindow._user_select_in_progress = True
            Switch_Screen(main_widgets, "user")
        else:
            _rVal = self.mainwindow._selected_user
            self.btn_lend_selectUser.hide()
            self.btn_lend_deseletUser.show()
            self.lbl_lend_user_name.setText(_rVal["Name"])
            self.lbl_lend_user_name.show()
            self._selected_user_code = _rVal["user_code"]
            self.mainwindow._selected_user = {}
            self.mainwindow._user_select_in_progress = False
    
    def _deselectUser(self):
        self.mainwindow._user_select_in_progress == False
        self.mainwindow._selected_user = {}
        self._selected_user_code
        self.lbl_lend_user_name.hide()
        self.btn_lend_selectUser.show()
        self.btn_lend_deseletUser.hide()

    def _selectBook(self):
        if self.mainwindow._book_select_in_progress == False:
            self.mainwindow._book_select_in_progress = True
            Switch_Screen(main_widgets, "book")
        else:
            _rVal = self.mainwindow._selected_book
            self.btn_lend_selectBook.hide()
            self.btn_lend_deseletBook.show()
            self.lbl_lend_book_name.setText(_rVal["Title"])
            self.lbl_lend_book_name.show()
            self._selected_book_code = _rVal["book_code"]
            self.mainwindow._selected_book = {}
            self.mainwindow._book_select_in_progress = False
    
    def _deselectBook(self):
        self.mainwindow._book_select_in_progress == False
        self.mainwindow._selected_book = {}
        self._selected_book_code
        self.lbl_lend_book_name.hide()
        self.btn_lend_selectBook.show()
        self.btn_lend_deseletBook.hide()

    def _codeCreate(self, user_id, book_id):
        _cat = "TRN"
        _num = ""
        import random
        for i in range(3):
            _num += str(random.randint(0, 9))
        return str(f"{_cat}{user_id}{book_id}{_num}")

    def Lend(self):
        _user_code = self._selected_user_code
        _book_code = self._selected_book_code
        _lendDate = self.input_lend_date.text()

        _u, state_hasBorrowed = self.mainwindow.database.cur.execute(f"SELECT User.id, User.state_hasBorrowed from User WHERE User.user_code='{_user_code}';").fetchone()
        _user_id = f"{_u:03}"
        _b, state_borrowed = self.mainwindow.database.cur.execute(f"SELECT Book.id, Book.state_borrowed from Book WHERE Book.book_code='{_book_code}';").fetchone()
        _book_id = f"{_b:03}"

        if state_hasBorrowed == 1:
            showMessageBox("خطا!", "کاربر توانایی امانت گرفتن کتاب را ندارد. هنوز کتاب هایی را باز نگردانده!", icon="Warning")
            return None
        if state_borrowed == 1:
            showMessageBox("خطا!", "کتاب انتخاب شده قبلا توسط کسی امانت گرفته شده.", icon="Warning")
            return None

        _transaction_code = self._codeCreate(_user_id, _book_id)

        if _user_code == "" or _book_code == "" or _lendDate == "" and not self.ChBox_lend_automatic_date.isChecked():
            showMessageBox("خطا!", "لطفا ابتدا اطلاعات را وارد کنید.", icon="Critical")
            return None
        
        import time
        if self.ChBox_lend_automatic_date.isChecked():
           _lendDate = time.strftime(f"%Y-%m-%d")

        import sqlite3
        try:
            self.mainwindow.database.Add(
                "'Transaction'", 
                "transaction_code,user_id,book_id,state_done,borrowDate", 
                (str(_transaction_code), str(int(_user_id)), str(int(_book_id)), 0, _lendDate)
            )
            _bC = int(self.mainwindow.database.cur.execute(f"SELECT User.currBorrowedCount from User WHERE User.user_code='{_user_code}';").fetchone()[0])
            self.mainwindow.database.Update("'User'", "state_hasBorrowed", 1, "user_code", "=", _user_code)
            self.mainwindow.database.Update("'User'", "currBorrowedCount", _bC+1, "user_code", "=", _user_code)
            _bC = int(self.mainwindow.database.cur.execute(f"SELECT Book.borrowedCount from Book WHERE Book.book_code='{_book_code}';").fetchone()[0])
            self.mainwindow.database.Update("'Book'", "state_borrowed", 1, "book_code", "=", _book_code)
            self.mainwindow.database.Update("'Book'", "borrowedCount", _bC+1, "book_code", "=", _book_code)

            
            showMessageBox("موفقیت", "مبادله(امانت دادن) کتاب با موفقیت انجام شد.")
            self.mainwindow.database._ExpireCache(hard=True)
            self._deselectUser()
            self._deselectBook()
            self._clear(infoBox=True, delBox=True, renewBox=True, addBox=True)
            self._clearRows(self.tableWidget_search_results)
        except sqlite3.IntegrityError:
            if self.ChBox_automatic_code.isChecked():
                self.Lend()
        
    def Retrieve(self):
        _retrieveDate = self.input_retrieve_date.text()
        _transaction_code = self.lbl_retrieve_transaction_code.text()

        ـstate_done, _user_id, _book_id = self.mainwindow.database.cur.execute(f"SELECT 'Transaction'.state_done, 'Transaction'.user_id, 'Transaction'.book_id  from 'Transaction' WHERE 'Transaction'.transaction_code='{_transaction_code}';").fetchone()

        if ـstate_done == 1:
            showMessageBox("خطا!", "کتاب قبلا تحویل گرفته شده.", icon="Warning")
            return None

        if not self.__item_is_selected:
            showMessageBox("خطا!", "لطفا ابتدا یک مبادله را انتخاب کنید.", icon="Critical")
            return None
        if self._selected_transaction_state_done == True:
            showMessageBox("خطا!", "مبادله ی انتخاب شده قبلا تحویل گرفته شده.", icon="Critical")
            return None
        if _retrieveDate == "" and not self.ChBox_retrieve_automatic_date.isChecked():
            showMessageBox("خطا!", "لطفا ابتدا تاریخ را وارد کنید.", icon="Critical")
            return None
        
        import time
        if self.ChBox_retrieve_automatic_date.isChecked():
           _retrieveDate = time.strftime(f"%Y-%m-%d")

        self.mainwindow.database.Update("'User'", "state_hasBorrowed", 0, "id", "=", _user_id)
        self.mainwindow.database.Update("'Book'", "state_borrowed", 1, "id", "=", _book_id)

        self.mainwindow.database.Update("'Transaction'", "retrieveDate", _retrieveDate, "transaction_code", "=", _transaction_code)
        self.mainwindow.database.Update("'Transaction'", "state_done", 1, "transaction_code", "=", _transaction_code)
        showMessageBox("موفقیت", "دریافت کتاب مورد نظر با موفقیت ثبت شد.")
        self._clear(infoBox=True, delBox=True, renewBox=True)
        self._clearRows(self.tableWidget_search_results)

    def RenewBook(self):
        _bookRenewAmount = self.input_bookRenew_amount.currentText()
        _transaction_code = self.lbl_bookRenew_transaction_code.text()
        
        ـstate_done = self.mainwindow.database.cur.execute(f"SELECT 'Transaction'.state_done from 'Transaction' WHERE 'Transaction'.transaction_code='{_transaction_code}';").fetchone()[0]

        if ـstate_done == 1:
            showMessageBox("خطا!", "کتاب قبلا تحویل گرفته شده.", icon="Warning")
            return None
        if self.input_bookRenew_amount.currentIndex() == 0:
            showMessageBox("خطا!", "لطفا ابتدا مدت تمدید را انتخاب کنید.", icon="Critical")
            return None
        if self._selected_transaction_state_done == True:
            showMessageBox("خطا!", "مبادله ی انتخاب شده تحویل گرفته شده.", icon="Critical")
            return None

        _renewCount = self.mainwindow.database.cached_sql_show("Transaction", all=False, column="renewCount", condition_columns=["transaction_code"], condition_values=[_transaction_code],  condition_oprs=["="])[1][0]
        _renewCount = int(_renewCount) + int(self.renewAmount_Directives[_bookRenewAmount])
        
        self.mainwindow.database.Update("'Transaction'", "renewCount", _renewCount, "transaction_code", "=", _transaction_code)
        showMessageBox("موفقیت", "مدت امانت مبادله مورد نظر با موفقیت تمدید شد.")




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
    screen_mainwindow.database.sql_close_connection()

if __name__ == "__main__":
    global screen_mainwindow, screen_book, screen_user, screen_transaction
    app = QApplication(sys.argv)
    main_widgets = QtWidgets.QStackedWidget()
    
    screen_mainwindow = MainWindow()
    screen_book = Books_Screen(screen_mainwindow)
    screen_user = Users_Screen(screen_mainwindow)
    screen_transaction = Transactions_Screen(screen_mainwindow)

    main_widgets.addWidget(screen_mainwindow)
    main_widgets.addWidget(screen_book)
    main_widgets.addWidget(screen_user)
    main_widgets.addWidget(screen_transaction)
    
    main_widgets.setFixedWidth(960)
    main_widgets.setFixedHeight(720)

    main_widgets.setWindowTitle("EasyLib - Library Management Application")
    main_widgets.show()

    Switch_Screen(main_widgets, "home")

    try:
        sys.exit(app.exec_())
    except:
        app_exit()
