import sys
import requests
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QComboBox, QPushButton, QMessageBox, QDialog, QFormLayout, QLineEdit, QTextEdit

class CatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Информация о породах кошек")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Выпадающий список для фильтрации
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все")
        self.layout.addWidget(self.filter_combo)

        # Таблица для отображения данных
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Название", "Происхождение", "Характер"])
        self.table.doubleClicked.connect(self.open_detail_window)
        self.layout.addWidget(self.table)

        # Кнопка для удаления выбранной записи
        self.delete_button = QPushButton("Удалить выбранную породу")
        self.delete_button.clicked.connect(self.delete_cat)
        self.layout.addWidget(self.delete_button)

        # Загрузка данных из API
        self.load_data()

    def load_data(self):
        response = requests.get("https://api.thecatapi.com/v1/breeds")
        if response.status_code == 200:
            self.cats = response.json()
            self.update_table()
            self.update_filter_combo()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить данные из API")

    def update_table(self, origin_filter="Все"):
        self.table.setRowCount(0)
        for cat in self.cats:
            if origin_filter == "Все" or cat['origin'] == origin_filter:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem(cat['name']))
                self.table.setItem(row_position, 1, QTableWidgetItem(cat['origin']))
                self.table.setItem(row_position, 2, QTableWidgetItem(cat['temperament']))

    def update_filter_combo(self):
        origins = set(cat['origin'] for cat in self.cats)
        self.filter_combo.clear()
        self.filter_combo.addItem("Все")
        for origin in sorted(origins):
            self.filter_combo.addItem(origin)
        self.filter_combo.currentTextChanged.connect(self.filter_table)

    def filter_table(self):
        origin_filter = self.filter_combo.currentText()
        self.update_table(origin_filter)

    def open_detail_window(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            cat = self.cats[selected_row]
            self.detail_window = CatDetailWindow(cat, selected_row, self)
            self.detail_window.show()

    def delete_cat(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            reply = QMessageBox.question(self, 'Удаление', 'Вы уверены, что хотите удалить эту породу?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                del self.cats[selected_row]
                self.update_table(self.filter_combo.currentText())

    def update_cat(self, index, updated_cat):
        self.cats[index] = updated_cat
        self.update_table(self.filter_combo.currentText())

class CatDetailWindow(QDialog):
    def __init__(self, cat, index, parent):
        super().__init__(parent)
        self.setWindowTitle(f"Подробности о {cat['name']}")
        self.setModal(True)
        self.cat = cat
        self.index = index
        self.parent = parent

        self.layout = QFormLayout(self)

        # Поля для отображения и редактирования данных
        self.name_edit = QLineEdit(cat['name'])
        self.origin_edit = QLineEdit(cat['origin'])
        self.temperament_edit = QTextEdit(cat['temperament'])
        self.description_edit = QTextEdit(cat.get('description', ''))

        self.layout.addRow("Название:", self.name_edit)
        self.layout.addRow("Происхождение:", self.origin_edit)
        self.layout.addRow("Характер:", self.temperament_edit)
        self.layout.addRow("Описание:", self.description_edit)

        # Кнопка для сохранения изменений
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_changes)
        self.layout.addRow(self.save_button)

    def save_changes(self):
        # Обновляем данные кота
        self.cat['name'] = self.name_edit.text()
        self.cat['origin'] = self.origin_edit.text()
        self.cat['temperament'] = self.temperament_edit.toPlainText()
        self.cat['description'] = self.description_edit.toPlainText()

        # Сохраняем изменения в основном списке
        self.parent.update_cat(self.index, self.cat)

        # Закрываем модальное окно
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CatApp()
    window.show()
    sys.exit(app.exec())