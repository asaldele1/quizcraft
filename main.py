from PyQt6.QtWidgets import QDialog, QInputDialog, QMessageBox
from PyQt6 import uic
from PyQt6.QtCore import QStringListModel
import sys
from PyQt6 import QtWidgets, QtCore, QtSql
from database import Database
from ui_select_test_dialog import Ui_SelectTestDialog
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


class SelectTestDialog(QDialog, Ui_SelectTestDialog):
    def __init__(self, database: Database, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.database = database
        self.model = self.database.get_tests_model()
        self.listViewTests.setModel(self.model)
        self.listViewTests.setModelColumn(1)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.addButton("Создать", QtWidgets.QDialogButtonBox.ButtonRole.ActionRole).clicked.connect(
            self.create_test)

        self.listViewTests.clicked.connect(self.on_item_selected)

        self.selected_test = None

    def on_item_selected(self, index: QtCore.QModelIndex) -> None:
        if index.isValid():
            self.selected_test = self.model.data(index.siblingAtColumn(0))

    def accept(self) -> None:
        if self.selected_test:
            super().accept()
        else:
            QMessageBox.warning(
                self, "Ошибка", "Выберите тест из списка или создайте новый.")

    def create_test(self) -> None:
        text, ok = QInputDialog.getText(
            self, "Создание нового теста", "Введите название нового теста:")
        if ok and text:
            self.database.create_test(text)
            self.model.select()
        elif not text and ok:
            QMessageBox.warning(
                self, "Ошибка", "Название теста не может быть пустым.")


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.database = Database()
        self.assignment_model = None
        self.test_id = None
        self.select_test()

        self.action_select_test.triggered.connect(self.select_test)
        self.action_add_assignment.triggered.connect(self.add_assignment)
        self.action_edit_assignment.triggered.connect(self.edit_assignment)
        self.action_delete_assignment.triggered.connect(self.delete_assignment)

        self.tableAssignments.setModel(self.assignment_model)
        header = ('ID', 'Название')
        for n, i in enumerate(header):
            self.assignment_model.setHeaderData(
                n, QtCore.Qt.Orientation.Horizontal, i)
        self.tableAssignments.hideColumn(2)
        self.tableAssignments.hideColumn(3)

    def add_assignment(self) -> None:
        dialog = AssignmentDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.database.create_assignment(
                data["name"], self.test_id, data["content"])
            self.assignment_model.select()

    def edit_assignment(self) -> None:
        selected_row = self.tableAssignments.currentIndex().row()
        if selected_row == -1:
            return

        id = self.assignment_model.data(
            self.assignment_model.index(selected_row, 0))
        name = self.assignment_model.data(
            self.assignment_model.index(selected_row, 1))
        content = self.assignment_model.data(
            self.assignment_model.index(selected_row, 2))

        dialog = AssignmentDialog(self)
        dialog.lineEditName.setText(name)
        dialog.textEditContent.setPlainText(content)

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.database.edit_assignment(id, data["name"], data["content"])
            self.assignment_model.select()

    def delete_assignment(self) -> None:
        selected_row = self.tableAssignments.currentIndex().row()
        if selected_row == -1:
            return

        id = self.assignment_model.data(
            self.assignment_model.index(selected_row, 0))

        self.database.delete_assignment(id)
        self.assignment_model.select()

    def select_test(self):
        dialog = SelectTestDialog(self.database)
        if dialog.exec():
            self.test_id = dialog.selected_test
            if self.assignment_model is not None:
                self.database.change_model_test(
                    self.assignment_model, self.test_id)
            else:
                self.assignment_model = self.database.get_assignments_model(
                    self.test_id)
        else:
            if self.test_id is None:
                QMessageBox.warning(None, "Ошибка", "Тест не выбран.")
                self.select_test()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
