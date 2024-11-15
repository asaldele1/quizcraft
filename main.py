import sys
from PyQt6 import QtWidgets, QtCore, QtSql
from ui_main_window import Ui_MainWindow
from ui_assignment_dialog import Ui_AssignmentDialog


class AssignmentDialog(QtWidgets.QDialog, Ui_AssignmentDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = ...) -> None:
        super().__init__(parent)
        self.setupUi(self)

    def get_data(self) -> None:
        return {
            "name": self.lineEditName.text(),
            "content": self.textEditContent.toPlainText()
        }


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.initialize_database()

        self.btnAddAssignment.clicked.connect(self.add_assignment)
        self.btnEditAssignment.clicked.connect(self.edit_assignment)

    def initialize_database(self) -> None:
        self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('quizcraft.db')
        self.db.open()

        query = QtSql.QSqlQuery()
        query.exec("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)

        self.assignment_model = QtSql.QSqlTableModel()
        self.assignment_model.setTable('assignments')
        self.assignment_model.select()

        self.tableAssignments.setModel(self.assignment_model)
        header = ('ID', 'Название', 'Содержание')
        for i in range(len(header)):
            self.assignment_model.setHeaderData(
                i, QtCore.Qt.Orientation.Horizontal, header[i])

        self.insert_query = QtSql.QSqlQuery()
        self.insert_query.prepare("""
            INSERT INTO assignments (name, content)
            VALUES (:name, :content)
        """)

        self.update_query = QtSql.QSqlQuery()
        self.update_query.prepare("""
            UPDATE assignments
            SET name = :name, content = :content
            WHERE id = :id
        """)

    def add_assignment(self) -> None:
        dialog = AssignmentDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.update_database(data)

    def edit_assignment(self) -> None:
        selected_row = self.tableAssignments.currentIndex().row()
        if selected_row == -1:
            return

        id = self.assignment_model.data(self.assignment_model.index(selected_row, 0))
        name = self.assignment_model.data(self.assignment_model.index(selected_row, 1))
        content = self.assignment_model.data(self.assignment_model.index(selected_row, 2))

        dialog = AssignmentDialog(self)
        dialog.lineEditName.setText(name)
        dialog.textEditContent.setPlainText(content)

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.update_database(data, id)

    def update_database(self, data: dict[str, str], update_assignment_id: int = None) -> None:
        if update_assignment_id is None:
            query = self.insert_query
        else:
            query = self.update_query
            query.bindValue(':id', update_assignment_id)
        query.bindValue(':name', data['name'])
        query.bindValue(':content', data['content'])
        query.exec()
        print(query.boundValues())
        print(query.lastError().text())
        self.assignment_model.select()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
