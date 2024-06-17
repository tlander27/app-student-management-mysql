from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, \
    QWidget, QGridLayout, QLineEdit, QPushButton, \
    QMainWindow, QTableWidget, QTableWidgetItem, \
    QDialog, QVBoxLayout, QComboBox, QToolBar, \
    QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys, os
import mysql.connector


class DatabaseConnection:
    """Connects to a sqlite3 database storing student data"""
    mysql_password = os.getenv("mysql_password")

    def __init__(self, host="localhost", user="root", password=mysql_password, database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host,
                                             user=self.user,
                                             password=self.password,
                                             database=self.database)
        # cursor = connection.cursor()
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setFixedSize(480, 380)
        # Create root menu options
        file_menu_item = self.menuBar().addMenu("&File")
        edit_menu_item = self.menuBar().addMenu("&Edit")
        help_menu_item = self.menuBar().addMenu("&Help")

        # Add submenu items and actions
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        # Add edit/search items and actions
        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.about)
        help_menu_item.addAction(about_action)

        # Create table layout for data
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar and toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create status bar and elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        """Captures data from a clicked cell in the window table"""
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)
        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        # Remove buttons prior to each new record click
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        # Display buttons in statusbar
        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        """Loads existing student data"""
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("select * from students")
        results = cursor.fetchall()
        # Avoid overwriting entries
        self.table.setRowCount(0)
        # Loop results to add to table widget
        for row_num, row_data in enumerate(results):
            self.table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        """Initializes and executes InsertDialog"""
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        """Initializes and executes SearchDialog"""
        search_dialog = SearchDialog()
        search_dialog.exec()

    def edit(self):
        """Initializes and executes EditDialog"""
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        """Initializes and executes DeleteDialog"""
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        """Initializes and executes AboutDialog"""
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    """Displays about messagebox content"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = "Student management desktop application built with PyQt6.\n"\
                  "Demonstrates the use of OOP with a connection to a SQLite3 database."
        self.setText(content)


class EditDialog(QDialog):
    """Defines edit dialog layout and updates database records"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()
        # Get student name from selected row
        index = window.table.currentRow()
        student_name = window.table.item(index, 1).text()

        # Get student Id from selected row
        self.student_id = window.table.item(index, 0).text()

        # Edit student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Get course from selected row
        course_name = window.table.item(index, 2).text()
        # Add courses combobox list
        self.course_name = QComboBox()
        courses = sorted(["Biology", "Software Engineering",
                   "Math", "Astronomy", "Physics"])
        self.course_name.addItems(courses)
        # Set the selected course in combobox
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Get current mobile from selected row
        mobile = window.table.item(index, 3).text()
        # Add mobile widget
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add submit button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        """Updates selected student record"""
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("update students set name = %s, course = %s, mobile = %s"
                       "where id = %s", (self.student_name.text(),
                                        self.course_name.itemText(self.course_name.currentIndex()),
                                        self.mobile.text(),
                                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        window.load_data()


class DeleteDialog(QDialog):
    """Defines delete dialog layout and deletes student reccord"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure?")
        yes = QPushButton("Yes")
        yes.clicked.connect(self.delete_student)
        no = QPushButton("No")
        no.clicked.connect(self.close)

        layout.addWidget(confirmation, 0, 0)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

    def delete_student(self):
        """Captures selected student and deletes record from database"""
        # Get index and student Id from selected row
        index = window.table.currentRow()
        student_id = window.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("delete from students where id = %s", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        window.load_data()
        self.close()

        # Create success messagebox
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("Record successfully deleted.")
        confirmation_widget.exec()


class InsertDialog(QDialog):
    """Defines insert dialog layout and inserts student record in database"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add courses combobox list
        self.course_name = QComboBox()
        courses = sorted(["Biology", "Software Engineering",
                   "Math", "Astronomy", "Physics"])
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add submit button
        button = QPushButton("Submit")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        """Captures data from dialog and inserts student record in database"""
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("insert into students (name, course, mobile) "
                       "values (%s,%s,%s)", (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        window.load_data()
        # self.close()


class SearchDialog(QDialog):
    """Defines search dialog layout and queries database"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Search")
        self.setFixedSize(300, 100)

        layout = QVBoxLayout()

        # Add search widget
        self.search_string = QLineEdit()
        self.search_string.setPlaceholderText("Enter a student name")
        layout.addWidget(self.search_string)

        # Add search button
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search)
        layout.addWidget(search_button)

        self.setLayout(layout)

    def search(self):
        """Captures query parameters and highlights selected results within window table"""
        search_str = self.search_string.text().title()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        query = "select * from students where name = %s"
        cursor.execute(query, (search_str, ))
        results = cursor.fetchall()
        rows = list(results)
        print(rows)
        items = window.table.findItems(search_str, Qt.MatchFlag.MatchFixedString)

        for item in items:
            print(item)
            window.table.item(item.row(), 1).setSelected(True)


if __name__ == "__main__":
    # Initialize application window
    app = QApplication(sys.argv)
    window = MainWindow()
    # Initialize application loop
    window.show()
    window.load_data()
    sys.exit(app.exec())