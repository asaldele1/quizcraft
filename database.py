from PyQt6 import QtSql

DB_FILE = "quizcraft.db"

class Database:
    def __init__(self):
        self.db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(DB_FILE)
        self.db.open()

        query = QtSql.QSqlQuery()
        query.exec("""
            CREATE TABLE tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT NOT NULL
            )
        """)
        query.exec("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                test_id INTEGER NOT NULL REFERENCES tests(id)
            )
        """)
        query.exec("""
            CREATE TABLE IF NOT EXISTS variants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assignment_id INTEGER NOT NULL REFERENCES assignments(id),
                content TEXT NOT NULL,
                correct_answer mTEXT NOT NULL
            )
        """)
    
    def __del__(self):
        self.db.close()
        QtSql.QSqlDatabase.removeDatabase("QSQLITE")
    
    def create_test(self, name: str) -> None:
        query = QtSql.QSqlQuery()
        query.prepare("INSERT INTO tests (name) VALUES (:name)")
        query.bindValue(":name", name)
        query.exec()

    def get_tests(self) -> list[dict[str, str]]:
        query = QtSql.QSqlQuery()
        query.exec("SELECT * FROM tests")
        result = []
        while query.next():
            result.append({
                "id": query.value("id"),
                "name": query.value("name")
            })
        return 
    
    def get_tests_model(self) -> QtSql.QSqlTableModel:
        model = QtSql.QSqlTableModel()
        model.setTable("tests")
        model.select()
        return model
    
    def create_assignment(self, name: str, test_id: int, content: str) -> None:
        query = QtSql.QSqlQuery()
        query.prepare("""
            INSERT INTO assignments (name, test_id)
            VALUES (:name, :test_id)
        """)
        query.bindValue(":name", name)
        query.bindValue(":test_id", test_id)
        query.exec()
    
    def get_assignments_model(self, test_id: int) -> QtSql.QSqlTableModel:
        model = QtSql.QSqlTableModel()
        model.setTable("assignments")
        self.change_model_test(model, test_id)
        return model
    
    def change_model_test(self, model: QtSql.QSqlTableModel, test_id: int) -> None:
        model.setFilter(f"test_id = {test_id}")
        model.select()
    
    def edit_assignment(self, id: int, name: str, content: str) -> None:
        query = QtSql.QSqlQuery()
        query.prepare("""
            UPDATE assignments
            SET name = :name
            WHERE id = :id
        """)
        query.bindValue(":name", name)
        query.bindValue(":id", id)
        query.exec()
    
    def delete_assignment(self, id: int) -> None:
        query = QtSql.QSqlQuery()
        query.prepare("DELETE FROM assignments WHERE id = :id")
        query.bindValue(":id", id)
        query.exec()
